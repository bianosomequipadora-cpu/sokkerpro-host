"""Sessão assinada m4 da API SokkerPro (handshake ECDH + HMAC + AES-GCM).

Contexto: o host ``m2`` removeu as rotas REST usadas pelo bot
(``/livescores`` e ``/fixture/*`` devolvem ``Cannot GET``) e o host ``m4``
exige assinatura em cada chamada REST fora de ``/m4/handshake``.
Protocolo extraído do bundle público do site (boot m4):

* ``POST {base}/m4/handshake`` com ``{"pub": <P-256 efêmera, base64>}``
  devolve ``{"kid", "pub", "salt", "now"}``;
* chave: ``HKDF-SHA256(salt, ECDH, info="m4/v1", 64B)`` — 32B AES + 32B HMAC;
* assinatura: ``HMAC-SHA256("MÉTODO\\npath[?query]\\nts_ms\\nnonce")`` nos
  headers ``X-M4-Kid/Ts/Nonce/Sig`` (base64 padrão);
* respostas podem vir em envelope ``{"__m4": 1, "kid", "iv", "d", "z?"}``
  (AES-256-GCM + gzip opcional);
* 401 força novo handshake (1 retry); 403 repete 1x com assinatura fresca.
"""
from __future__ import annotations

import base64
import gzip
import hashlib
import hmac
import json
import logging
import secrets
import threading
import time
from typing import Any, Callable
from urllib.parse import urlsplit

LOGGER = logging.getLogger(__name__)

M4_INFO = b"m4/v1"
M4_HOST = "m4.sokkerpro.com"


class M4Error(RuntimeError):
    """Falha no handshake, na assinatura ou no envelope m4."""


def _b64encode(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")


def _b64decode(text: str) -> bytes:
    return base64.b64decode(text)


def hkdf_sha256(ikm: bytes, salt: bytes, info: bytes, length: int) -> bytes:
    """HKDF RFC 5869 com SHA-256 (extract + expand)."""
    if length <= 0 or length > 255 * 32:
        raise M4Error(f"tamanho HKDF inválido: {length}")
    pseudo = hmac.new(salt, ikm, hashlib.sha256).digest()
    output = b""
    block = b""
    counter = 1
    while len(output) < length:
        block = hmac.new(pseudo, block + info + bytes([counter]), hashlib.sha256).digest()
        output += block
        counter += 1
    return output[:length]


def _require_cryptography() -> tuple[Any, Any, Any]:
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    except ImportError as exc:
        raise M4Error(
            "a API m4 exige o pacote 'cryptography' (pip install cryptography)"
        ) from exc
    return serialization, ec, AESGCM


def parse_handshake(payload: Any) -> dict[str, Any]:
    """Valida o JSON do ``/m4/handshake``; levanta ``M4Error`` se incompleto."""
    if not isinstance(payload, dict):
        raise M4Error("resposta do handshake m4 inválida")
    kid = payload.get("kid")
    pub = payload.get("pub")
    salt = payload.get("salt")
    if not kid or not pub or not salt:
        raise M4Error("resposta do handshake m4 incompleta")
    return {"kid": str(kid), "pub": str(pub), "salt": str(salt), "now": payload.get("now")}


def sign_headers(*, method: str, url: str, timestamp_ms: str, nonce_b64: str,
                 kid: str, hmac_key: bytes) -> dict[str, str]:
    """Monta os headers ``X-M4-*`` exatamente no formato do site."""
    parts = urlsplit(url)
    resource = parts.path + (("?" + parts.query) if parts.query else "")
    message = f"{method.upper()}\n{resource}\n{timestamp_ms}\n{nonce_b64}".encode("utf-8")
    signature = hmac.new(hmac_key, message, hashlib.sha256).digest()
    return {
        "X-M4-Kid": kid,
        "X-M4-Ts": timestamp_ms,
        "X-M4-Nonce": nonce_b64,
        "X-M4-Sig": _b64encode(signature),
    }


def is_auth_rejection(payload: Any) -> bool:
    """Detecta a recusa de autenticação em corpo 200 (``{"error": 1}``)."""
    return isinstance(payload, dict) and bool(payload.get("error")) and "data" not in payload


def is_envelope(payload: Any) -> bool:
    return (
        isinstance(payload, dict)
        and payload.get("__m4") == 1
        and bool(payload.get("iv"))
        and bool(payload.get("d"))
    )


class M4Session:
    """Guarda as chaves da sessão m4 (thread-safe; handshake preguiçoso)."""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self._lock = threading.Lock()
        self._keys: dict[str, tuple[bytes, bytes]] = {}
        self._active_kid: str | None = None
        self._clock_offset_ms = 0.0

    def _derive(self, server_pub_b64: str, salt_b64: str, private_key: Any, ec: Any) -> tuple[bytes, bytes]:
        server_key = ec.EllipticCurvePublicKey.from_encoded_point(
            ec.SECP256R1(), _b64decode(server_pub_b64)
        )
        shared = private_key.exchange(ec.ECDH(), server_key)
        material = hkdf_sha256(shared, _b64decode(salt_b64), M4_INFO, 64)
        return material[:32], material[32:64]

    def handshake(self, http_post: Callable[[str, dict], Any], *, force: bool = False) -> str:
        """Executa o handshake (ou reutiliza a sessão) e devolve o ``kid`` ativo."""
        serialization, ec, _ = _require_cryptography()
        with self._lock:
            if not force and self._active_kid in self._keys:
                return str(self._active_kid)
        private_key = ec.generate_private_key(ec.SECP256R1())
        public_raw = private_key.public_key().public_bytes(
            serialization.Encoding.X962,
            serialization.PublicFormat.UncompressedPoint,
        )
        try:
            payload = http_post(f"{self.base_url}/m4/handshake", {"pub": _b64encode(public_raw)})
        except Exception as exc:
            raise M4Error(f"handshake m4 falhou: {exc}") from exc
        parsed = parse_handshake(payload)
        aes_key, hmac_key = self._derive(parsed["pub"], parsed["salt"], private_key, ec)
        with self._lock:
            self._keys[parsed["kid"]] = (aes_key, hmac_key)
            if len(self._keys) > 12:
                oldest = next(iter(self._keys))
                if oldest != parsed["kid"]:
                    del self._keys[oldest]
            self._active_kid = parsed["kid"]
            now = parsed.get("now")
            if isinstance(now, (int, float)) and now == now:  # finito
                self._clock_offset_ms = float(now) - time.time() * 1000.0
        return parsed["kid"]

    def headers_for(self, method: str, url: str) -> dict[str, str]:
        """Headers assinados para uma chamada (exige handshake prévio)."""
        with self._lock:
            kid = self._active_kid
            keys = self._keys.get(kid) if kid else None
            offset = self._clock_offset_ms
        if kid is None or keys is None:
            raise M4Error("sessão m4 sem handshake")
        timestamp_ms = str(int(time.time() * 1000.0 + offset))
        nonce_b64 = _b64encode(secrets.token_bytes(12))
        return sign_headers(method=method, url=url, timestamp_ms=timestamp_ms,
                            nonce_b64=nonce_b64, kid=kid, hmac_key=keys[1])

    def decrypt(self, payload: Any) -> Any:
        """Desfaz o envelope ``__m4``; devolve o payload intacto se não for envelope."""
        if not is_envelope(payload):
            return payload
        _, _, AESGCM = _require_cryptography()
        with self._lock:
            keys = self._keys.get(str(payload.get("kid"))) or (
                self._keys.get(str(self._active_kid)) if self._active_kid else None
            )
        if keys is None:
            raise M4Error("envelope m4 com sessão desconhecida")
        try:
            raw = AESGCM(keys[0]).decrypt(_b64decode(str(payload["iv"])), _b64decode(str(payload["d"])), None)
        except Exception as exc:
            raise M4Error(f"falha ao decifrar envelope m4: {exc}") from exc
        if payload.get("z"):
            try:
                raw = gzip.decompress(raw)
            except OSError as exc:
                raise M4Error(f"falha ao descomprimir envelope m4: {exc}") from exc
        try:
            return json.loads(raw.decode("utf-8"))
        except ValueError:
            return raw.decode("utf-8")
