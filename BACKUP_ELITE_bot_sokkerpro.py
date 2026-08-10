
def gerar_layout_relatorio(greens, reds, data_str):
    sep = "━━━━━━━━━━━━━━━━━━━━"
    total = greens + reds
    taxa = (greens / total * 100) if total > 0 else 0.0
    return (
        f"{sep}\n"
        f"<b>📊 RELATÓRIO DIÁRIO — {data_str}</b>\n"
        f"{sep}\n"
        f"✅ GREEN: <b>{greens}</b>\n"
        f"🔴 RED: <b>{reds}</b>\n"
        f"📈 TOTAL DE ENTRADAS: <b>{total}</b>\n"
        f"🎯 ASSERTIVIDADE: <b>{taxa:.1f}%</b>\n"
        f"{sep}\n"
        f"⚠️👆Resultados do dia👆⚠️"
    )
def gerar_layout_relatorio_mensal(greens, reds, mes_nome, dias_ativos):
    sep = "\u2501" * 20
    total = greens + reds
    taxa = (greens / total * 100) if total > 0 else 0.0
    msg = f"{sep}\n"
    msg += f"<b>\U0001f4ca RELAT\u00d3RIO MENSAL \u2014 {mes_nome}</b>\n"
    msg += f"{sep}\n"
    msg += f"\u2705 GREEN: <b>{greens}</b>\n"
    msg += f"\U0001f534 RED: <b>{reds}</b>\n"
    msg += f"\U0001f4c8 TOTAL DE ENTRADAS: <b>{total}</b>\n"
    msg += f"\U0001f3af ASSERTIVIDADE: <b>{taxa:.1f}%</b>\n"
    msg += f"{sep}\n"
    msg += f"\U0001f4c5 Dias com entradas: <b>{dias_ativos}</b>\n"
    msg += "\u26a0\ufe0f\U0001f446Resultados do m\u00eas\U0001f446\u26a0\ufe0f"
    return msg
def gerar_layout_radar(jogos_ao_vivo, jogos_na_janela):
    sep = "━━━━━━━━━━━━━━━━━━━━"
    texto_jan = ""
    for j in jogos_na_janela:
        h = j.get("home","") or getattr(j,"home","")
        a = j.get("away","") or getattr(j,"away","")
        m = j.get("minuto","") or getattr(j,"minuto","")
        sh = j.get("sh",0) or getattr(j,"sh",0)
        sa = j.get("sa",0) or getattr(j,"sa",0)
        liga = j.get("liga","") or getattr(j,"liga","")
        texto_jan += f"🎯 <b>{h} x {a}</b> | {m}' | {sh}x{sa} | {liga}\n"
    if not texto_jan:
        texto_jan = "Nenhum jogo na janela no momento."
    corpo = (
        f"{sep}\n"
        f"📡 RADAR — JOGOS AO VIVO\n"
        f"{sep}\n"
        f"🔴 Jogos na Janela:\n"
        f"{texto_jan}"
        f"{sep}\n"
        f"🟢 Ao Vivo: <b>{len(jogos_ao_vivo)}</b>"
    )
    return corpo
import requests
def obter_nome_liga(game, fonte):
    # apifootball: game['league']['name']
    # SokkerPro: game['league_name']
    liga = "Liga Não Identificada"
    
    if fonte == "apifootball":
        liga = game.get('league', {}).get('name', "Liga Não Identificada")
    elif fonte == "sokkerpro":
        # SokkerPro retorna camelCase: leagueName
        liga = game.get('leagueName') or game.get('league_name', "Liga Não Identificada")
    
    # Se ainda estiver vazio, busca em campos genéricos que as APIs costumam usar
    if liga == "Liga Não Identificada":
        liga = game.get('leagueName') or game.get('league_name') or game.get('competition_name') or game.get('league') or "Liga Não Identificada"
        
    return liga
# ═══════════════════════════════════════════════════════════════════════════════
# BOT MÁQUINA DE GREENS VIP - ZAPIA - VERSÃO ELITE 100% AUTOMÁTICA
# ═══════════════════════════════════════════════════════════════════════════════
import os, json, requests, time
APIFOOTBALL_KEY = os.getenv("APIFOOTBALL_KEY", "")
from datetime import datetime, timezone, timedelta
import hashlib, re, unicodedata
# ─── Normalização de nomes de times (acentos, abreviações, prefixos) ────────────
def norm_nome_time(nome):
    """Remove acentos, expande abreviações e limpa prefixos/sufixos de nome de time."""
    n = unicodedata.normalize('NFKD', nome).encode('ascii', 'ignore').decode().lower().strip()
    # Remove prefixos comuns: msk, hnk, nk, fk, sk, fc, etc
    n = re.sub(r'\b(msk|hnk|nk|fk|sk|fc|ac|ec|se|cf)\b', '', n)
    # Expande abreviações comuns da apifootball
    n = n.replace('u.', 'universitatea').replace('dyn.', 'dynamo').replace('s.n.', '').replace('c.s.', '')
    # Remove siglas de estados e outros prefixos genéricos
    n = re.sub(r'\b(rj|sp|mg|rs|pr|sc|ba|pe|ce|go|mt|ms|df|es|rn|pb|al|se|pi|ma|pa|am|ro|rr|ap|to|fr|ac|ec|se|cf)\b', '', n)
    return re.sub(r'\s+', ' ', n).strip()
# ─── Caminhos e Fuso ───────────────────────────────────────────────────────────
BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
SENT_FILE       = os.path.join(BASE_DIR, "sent_live_signals.json")
SINAIS_FILE     = os.path.join(BASE_DIR, "sinais_pendentes.json")
RESULTADO_FILE  = os.path.join(BASE_DIR, "resultados.json")
PERFORMANCE_FILE= os.path.join(BASE_DIR, "performance.json")
LAST_UPDATE_FILE= os.path.join(BASE_DIR, "last_update.json")
CONFIG_FILE     = os.path.join(BASE_DIR, "config.json")
CONFIG_API_PATH = "config.json"
BRT             = timezone(timedelta(hours=-3))
# ─── Credenciais ───────────────────────────────────────────────────────────────
TELEGRAM_TOKEN  = os.getenv("TG_TOKEN", "")
TG_TOKEN = TELEGRAM_TOKEN
CHAT_IDS = [int(id) for id in os.environ.get("TG_GROUP_ID", "").split(",") if id.strip()]
CHAT_ID = CHAT_IDS[0] if CHAT_IDS else ""  # BOOT IA INTELIGENTE (Zapia)
# apifootball — API PRINCIPAL para dados de jogos
API_FOOTBALL_KEYS = [
    os.getenv("APIFOOTBALL_KEY"),   # Chave Mestre protegida
]
API_FOOTBALL_URL = "https://apiv3.apifootball.com"
# RapidAPI (fallback de lista)
RAPIDAPI_URL     = "https://free-api-live-football-data.p.rapidapi.com"
RAPIDAPI_HEADERS = {
    "x-rapidapi-key":  os.getenv("APIFOOTBALL_KEY", ""),
    "x-rapidapi-host": "free-api-live-football-data.p.rapidapi.com"
}
# URLs Oficiais das APIs (Conforme Documentação)
SOKKERPRO_URL = "https://m2.sokkerpro.com/livescores"
APIFOOTBALL_URL  = "https://apiv3.apifootball.com"
# APIs Secundárias (Ativas)
APIFOOTBALL_COM_KEY = os.getenv("APIFOOTBALL_KEY")
SOKKERPRO_URL = "https://m2.sokkerpro.com/livescores"
# URLs Oficiais das APIs (Conforme Documentação)
SOKKERPRO_URL = "https://m2.sokkerpro.com/livescores"
APIFOOTBALL_URL  = "https://apiv3.apifootball.com"
# APIs Secundárias (Ativas)
APIFOOTBALL_COM_KEY = os.getenv("APIFOOTBALL_KEY")
SOKKERPRO_URL = "https://m2.sokkerpro.com/livescores"
# URLs Oficiais das APIs (Conforme Documentação)
SOKKERPRO_URL = "https://m2.sokkerpro.com/livescores"
APIFOOTBALL_URL  = "https://apiv3.apifootball.com"
# APIs Secundárias (Ativas)
APIFOOTBALL_COM_KEY = os.getenv("APIFOOTBALL_KEY")
SOKKERPRO_URL = "https://m2.sokkerpro.com/livescores"
# ═══════════════+++
# TELEGRAM
# ═══════════════════════════════════════════════════════════════════════════════
def send_telegram(msg_data, reply_to=None, marca=None, home="", away="", odd_b365_val=None, odd_bano_val=None):
    """Envia mensagem formatada com botões inline."""
    if isinstance(msg_data, tuple):
        text, keyboard = msg_data
    else:
        text = msg_data
        keyboard = None
    url_send = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    last_mid = None
    for chat_id in CHAT_IDS:
        payload = {
            "chat_id": chat_id, 
            "text": text, 
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }
        if reply_to:
            payload["reply_to_message_id"] = reply_to
        if keyboard:
            payload["reply_markup"] = json.dumps(keyboard)
            
        try:
            r = requests.post(url_send, json=payload, timeout=10)
            res = r.json()
            if res.get("ok"):
                last_mid = res.get("result", {}).get("message_id")
        except:
            pass
    return last_mid
# ═══════════════════════════════════════════════════════════════════════════════
# ARQUIVOS LOCAIS
# ═══════════════════════════════════════════════════════════════════════════════
GITHUB_TOKEN = os.environ.get("GH_PAT", "")
GITHUB_REPO  = os.environ.get("GITHUB_REPOSITORY", "cleubianodasilva-png/maquina-de-greens-vip")
SENT_API_PATH        = "sent_live_signals.json"
RESULTADO_API_PATH   = "resultados.json"
PERFORMANCE_API_PATH = "performance.json"
def _crit(mercado, geral, key, default):
    """Pega valor de critério: mercado > geral > default."""
    c = mercado.get("criterios", {})
    if key in c:
        return c[key]
    if key in geral:
        v = geral[key]
        if isinstance(v, str) and not v.strip():
            return default
        return v
    return default
def _crit_val(criterios, geral, key, default):
    """Pega valor de critério de um dict de critérios: criterios > geral > default."""
    if key in criterios:
        return criterios[key]
    if key in geral:
        v = geral[key]
        if isinstance(v, str) and not v.strip():
            return default
        return v
    return default
def _validar_criterios_gerais(mercado_obj, stats, fav_final):
    """Valida todos os critérios do config.json para um mercado.
    Recebe o dict do mercado (mc) diretamente — SEM carregar config.json.
    Retorna (ok: bool, motivos: list)."""
    crit = mercado_obj.get("criterios", {})
    motivos = []
    fav_prefix = "h" if fav_final == "h" else "a"
    
    # Mapeamento: nome no config → (stats_field, lado, operador)
    mapa = {
        "chutes_alvo_min": ("chutes_gol", "sum", "min"),
        "chutes_totais_min": ("chutes_tot", "sum", "min"),
        "escanteios_minimos": ("escanteios", "sum", "min"),
        "ataques_perigosos_min": ("ataques_perigosos", "max", "min"),
        "appm_min_por_time": ("dapm_total", "max", "min"),
        "dapm_5_min": ("dapm5", "fav", "min"),
        "appm_total_min": ("dapm_total", "max", "min"),
        "dapm_total_orig_min": ("dapm_total", "fav", "min"),
        "media_gols_partida_min": ("medias_goal", "sum", "min"),
        "media_gols_ht_min": ("media_gols_ht", "sum", "min"),
        "media_gols_ft_min": ("media_gols_ft", "sum", "min"),
        "btts_probabilidade_min": ("btts_probabilidade", "total", "min"),
        "diferenca_gols_fav_max": ("goals", "diff", "max"),
        "max_red_card_fav": ("red_cards", "fav", "max"),
        "chutes_inside_min": ("chutes_inside", "fav", "min"),
        "chutes_outside_min": ("chutes_outside", "fav", "min"),
        "goal_attempts_min": ("goal_attempts", "fav", "min"),
        "chutes_bloq_max": ("chutes_bloq", "fav", "max"),
        "defesas_min": ("defesas", "fav", "min"),
        "faltas_min": ("faltas", "fav", "min"),
        "yellow_max": ("yellow_cards", "fav", "max"),
        "impedimentos_min": ("impedimentos", "fav", "min"),
        "pressure_bar_min": ("pressure_bar", "fav", "min"),
        "ball_safe_min": ("ball_safe", "fav", "min"),
        "xg_total_min": ("xg", "sum", "min"),
        "xg_casa_min": ("xg", "h", "min"),
        "xg_fora_min": ("xg", "a", "min"),
        "posse_bola_min": ("posse", "fav", "min"),
        "media_corners_total_min": ("medias_corners", "sum", "min"),
        "media_corners_casa_min": ("medias_corners", "h", "min"),
        "media_corners_fora_min": ("medias_corners", "a", "min"),
    }
    
    for campo, (base, lado, oper) in mapa.items():
        valor_cfg = crit.get(campo)
        if valor_cfg is None or valor_cfg == "": continue
        valor_cfg = float(valor_cfg)
        
        valor_stats = 0.0
        if lado == "sum":
            v_h = stats.get(f"{base}_h", 0)
            v_a = stats.get(f"{base}_a", 0)
            valor_stats = float(v_h or 0) + float(v_a or 0)
        elif lado == "fav":
            v = stats.get(f"{base}_{fav_prefix}", 0)
            valor_stats = float(v or 0)
        elif lado == "h":
            v = stats.get(f"{base}_h", 0)
            valor_stats = float(v or 0)
        elif lado == "a":
            v = stats.get(f"{base}_a", 0)
            valor_stats = float(v or 0)
        elif lado == "total":
            v = stats.get(base, 0)
            valor_stats = float(v or 0)
        elif lado == "diff":
            v_h = stats.get(f"{base}_h", 0)
            v_a = stats.get(f"{base}_a", 0)
            valor_stats = abs(float(v_h or 0) - float(v_a or 0))
        elif lado == "max":
            v_h = stats.get(f"{base}_h", 0)
            v_a = stats.get(f"{base}_a", 0)
            valor_stats = float(max(float(v_h or 0), float(v_a or 0)))
        
        if oper == "min":
            if valor_stats < valor_cfg:
                motivos.append(f"{campo}={valor_stats:.1f}<{valor_cfg:.1f}")
        elif oper == "max":
            if valor_stats > valor_cfg:
                motivos.append(f"{campo}={valor_stats:.1f}>{valor_cfg:.1f}")
                
    return len(motivos) == 0, motivos


def _situacao_fav_ok(mercado, geral, fav_gols, adv_gols):
    """Verifica se a situação do favorito é válida conforme config.
    Opções: perdendo | empatando | perdendo_ou_empatando | zebra"""
    valor = _crit(mercado, geral, "situacao_favorito", None)
    if not valor:
        return True  # sem config = permite tudo (compatibilidade)
    if valor == "ganhando":
        return fav_gols > adv_gols
    if valor == "empatando":
        return fav_gols == adv_gols
    if valor == "perdendo":
        return fav_gols < adv_gols
    if valor == "perdendo_ou_empatando":
        return fav_gols <= adv_gols
    if valor == "zebra_ganhando":
        return fav_gols < adv_gols
    return True
def _github_headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG DINÂMICA — carrega parâmetros do config.json (GitHub + local)
# ═══════════════════════════════════════════════════════════════════════════════
def _load_config():
    """
    Carrega config.json do GitHub (fonte de verdade) + local como fallback.
    Retorna dict com defaults se nada disponível.
    """
    default = {
        "geral": {"appm_min_por_time": 0.7, "media_gols_minima": 2.2},
        "mercados": {}
    }
    try:
        if GITHUB_TOKEN and GITHUB_REPO:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{CONFIG_API_PATH}"
            r = requests.get(url, headers=_github_headers(), timeout=8)
            if r.status_code == 200:
                import base64 as _b64
                data = json.loads(_b64.b64decode(r.json()["content"]).decode())
                # Salva localmente
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"[CONFIG] Carregado do GitHub: {len(data.get('mercados', {}))} mercados")
                return data
    except Exception as e:
        print(f"[CONFIG] Erro GitHub load: {e}")
    # Fallback local
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                print(f"[CONFIG] Carregado local: {len(data.get('mercados', {}))} mercados")
                return data
        except: pass
    print("[CONFIG] Usando defaults")
    return default
def load_sent():
    """Carrega sent do GitHub (fonte de verdade) + arquivo local como fallback."""
    # Tenta GitHub API primeiro
    if GITHUB_TOKEN and GITHUB_REPO:
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{SENT_API_PATH}"
            r = requests.get(url, headers=_github_headers(), timeout=8)
            if r.status_code == 200:
                import base64 as _b64
                data = json.loads(_b64.b64decode(r.json()["content"]).decode())
                sent = set(data)
                # Limpa chaves antigas (> 2 dias) para não crescer infinito
                hoje = datetime.now(BRT).strftime('%Y%m%d')
                ontem = (datetime.now(BRT) - timedelta(days=1)).strftime('%Y%m%d')
                sent = {k for k in sent if hoje in k or ontem in k}
                # Salva localmente também
                with open(SENT_FILE, 'w') as f: json.dump(list(sent), f)
                print(f"[SENT] Carregado do GitHub: {len(sent)} chaves")
                return sent
        except Exception as e:
            print(f"[SENT] Erro GitHub load: {e}")
    # Fallback: arquivo local
    if os.path.exists(SENT_FILE):
        try:
            with open(SENT_FILE, 'r') as f: return set(json.load(f))
        except: pass
    return set()
def save_sent(sent):
    """Salva sent localmente E no GitHub (fonte de verdade)."""
    with open(SENT_FILE, 'w') as f: json.dump(list(sent), f)
    if GITHUB_TOKEN and GITHUB_REPO:
        try:
            import base64 as _b64
            url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{SENT_API_PATH}"
            # Pega SHA atual
            r = requests.get(url, headers=_github_headers(), timeout=8)
            sha = r.json().get("sha", "") if r.status_code == 200 else ""
            content_b64 = _b64.b64encode(json.dumps(list(sent)).encode()).decode()
            payload = {"message": "state: atualiza sent [skip ci]", "content": content_b64}
            if sha: payload["sha"] = sha
            r2 = requests.put(url, headers=_github_headers(), json=payload, timeout=10)
            if r2.status_code in (200, 201):
                print(f"[SENT] Salvo no GitHub: {len(sent)} chaves")
            else:
                print(f"[SENT] Erro GitHub save: {r2.status_code}")
        except Exception as e:
            print(f"[SENT] Erro GitHub save: {e}")
def _load_sinais_github():
    """Carrega sinais_pendentes.json do GitHub."""
    import base64 as _b64
    if GITHUB_TOKEN and GITHUB_REPO:
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/sinais_pendentes.json"
            r = requests.get(url, headers=_github_headers(), timeout=8)
            if r.status_code == 200:
                return json.loads(_b64.b64decode(r.json()["content"]).decode())
        except Exception as e:
            print(f"[SINAIS] Erro load GitHub: {e}")
    if os.path.exists(SINAIS_FILE):
        try:
            with open(SINAIS_FILE, 'r') as f: return json.load(f)
        except: pass
    return []
def _save_sinais_github(sinais):
    """Salva sinais_pendentes.json no GitHub E localmente."""
    import base64 as _b64
    with open(SINAIS_FILE, 'w') as f: json.dump(sinais, f)
    if GITHUB_TOKEN and GITHUB_REPO:
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/sinais_pendentes.json"
            r = requests.get(url, headers=_github_headers(), timeout=8)
            sha = r.json().get("sha", "") if r.status_code == 200 else ""
            content_b64 = _b64.b64encode(json.dumps(sinais).encode()).decode()
            payload = {"message": "state: atualiza sinais_pendentes [skip ci]", "content": content_b64}
            if sha: payload["sha"] = sha
            r2 = requests.put(url, headers=_github_headers(), json=payload, timeout=10)
            if r2.status_code in (200, 201):
                print(f"[SINAIS] Salvo no GitHub: {len(sinais)} pendentes")
            else:
                print(f"[SINAIS] Erro GitHub save: {r2.status_code}")
        except Exception as e:
            print(f"[SINAIS] Erro save GitHub: {e}")
def registrar_sinal(fid, mercado, home, away, message_id, extra_val=None, tipo=None):
    sinais = _load_sinais_github()
    sinais.append({
        "fixture_id": fid, "mercado": mercado,
        "home": home, "away": away,
        "message_id": message_id, "extra_val": extra_val,
        "tipo": tipo,
        "timestamp": datetime.now(BRT).isoformat()
    })
    _save_sinais_github(sinais)
def _load_resultados_github():
    """Carrega resultados.json do GitHub. Retorna lista de registros."""
    import base64 as _b64
    if GITHUB_TOKEN and GITHUB_REPO:
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{RESULTADO_API_PATH}"
            r = requests.get(url, headers=_github_headers(), timeout=8)
            if r.status_code == 200:
                data = json.loads(_b64.b64decode(r.json()["content"]).decode())
                if isinstance(data, list):
                    return data
        except Exception as e:
            print(f"[RESULTADO] Erro load GitHub: {e}")
    # Fallback local
    if os.path.exists(RESULTADO_FILE):
        try:
            with open(RESULTADO_FILE, 'r') as f:
                return json.load(f)
        except: pass
    return []
def _save_resultados_github(registros):
    """Salva resultados.json no GitHub E localmente."""
    import base64 as _b64
    with open(RESULTADO_FILE, 'w') as f: json.dump(registros, f, indent=2)
    if GITHUB_TOKEN and GITHUB_REPO:
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{RESULTADO_API_PATH}"
            r = requests.get(url, headers=_github_headers(), timeout=8)
            sha = r.json().get("sha", "") if r.status_code == 200 else ""
            content_b64 = _b64.b64encode(json.dumps(registros, indent=2).encode()).decode()
            payload = {"message": "state: atualiza resultados [skip ci]", "content": content_b64}
            if sha: payload["sha"] = sha
            r2 = requests.put(url, headers=_github_headers(), json=payload, timeout=10)
            if r2.status_code in (200, 201):
                print(f"[RESULTADO] Salvo no GitHub: {len(registros)} registros")
            else:
                print(f"[RESULTADO] Erro GitHub save: {r2.status_code}")
        except Exception as e:
            print(f"[RESULTADO] Erro save GitHub: {e}")
def salvar_resultado(resultado, mercado=None):
    hoje = datetime.now(BRT).strftime("%Y-%m-%d")
    registros = _load_resultados_github()
    registros.append({
        "data": hoje, "resultado": resultado,
        "mercado": mercado,
        "timestamp": datetime.now(BRT).isoformat()
    })
    _save_resultados_github(registros)
def get_relatorio_mensal():
    hoje = datetime.now(BRT)
    mes_str = hoje.strftime("%Y-%m")
    greens, reds = 0, 0
    registros = _load_resultados_github()
    dias_ativos = set()
    for r in registros:
        data_reg = r.get("data", "")
        if data_reg.startswith(mes_str):
            dias_ativos.add(data_reg)
            if r.get("resultado") == "green": greens += 1
            else: reds += 1
    return greens, reds, len(dias_ativos)
def get_relatorio_hoje():
    hoje = datetime.now(BRT).strftime("%Y-%m-%d")
    greens, reds = 0, 0
    registros = _load_resultados_github()
    for r in registros:
        if r.get("data") == hoje:
            if r.get("resultado") == "green": greens += 1
            else: reds += 1
    return greens, reds
def enviar_relatorio_mensal():
    hoje = datetime.now(BRT)
    meses_pt = ["Janeiro","Fevereiro","Mar\u00e7o","Abril","Maio","Junho","Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"]
    mes_nome = f"{meses_pt[hoje.month-1]}/{hoje.year}"
    greens, reds, dias_ativos = get_relatorio_mensal()
    msg = gerar_layout_relatorio_mensal(greens, reds, mes_nome, dias_ativos)
    return msg
def enviar_relatorio_diario():
    hoje_key = f"relatorio_{datetime.now(BRT).strftime('%Y-%m-%d')}"
    hoje = datetime.now(BRT).strftime("%d/%m/%Y")
    greens, reds = get_relatorio_hoje()
    msg = gerar_layout_relatorio(greens, reds, hoje)
    sent = load_sent()
    if send_telegram(msg):
        sent.add(hoje_key)
        save_sent(sent)
        print(f"[Relatório] Enviado ({hoje_key})")
# ─── Performance por Mercado ────────────────────────────────────────────────────
def _gerar_mapa_mercados():
    try:
        cfg = _load_config()
        mercados = cfg.get("mercados", {})
        m = {}
        for cod, info in mercados.items():
            nome = info.get("nome", cod)
            m[cod] = nome
        if m:
            return m
    except:
        pass
    return {
        "HT": "⚽️🔥OVER GOL INTERVALO🔥⚽️",
        "BTTS": "⚽🔥AMBAS MARCAM🔥⚽️",
        "OFT": "⚽🔥OVER 1.5 GOLS FT🔥⚽️",
        "OVERGOAL": "⚽🔥OVER GOL PARTIDA🔥⚽️",
        "CORNER_HT": "🚩🔥ESCANTEIO ÁSIAT/LMT HT🔥🚩",
        "CORNER_FT": "🚩🔥ESCANTEIO ÁSIAT/LMT FT🔥🚩"
    }
MAPA_MERCADO = _gerar_mapa_mercados()
def _load_performance_github():
    """Carrega performance.json do GitHub. Retorna dict {mercado: {green, red, total}}."""
    import base64 as _b64
    if GITHUB_TOKEN and GITHUB_REPO:
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{PERFORMANCE_API_PATH}"
            r = requests.get(url, headers=_github_headers(), timeout=8)
            if r.status_code == 200:
                data = json.loads(_b64.b64decode(r.json()["content"]).decode())
                if isinstance(data, dict):
                    return data
        except Exception as e:
            print(f"[PERFORMANCE] Erro load GitHub: {e}")
    if os.path.exists(PERFORMANCE_FILE):
        try:
            with open(PERFORMANCE_FILE, 'r') as f:
                return json.load(f)
        except: pass
    return {}
def _save_performance_github(perf):
    """Salva performance.json no GitHub E localmente."""
    with open(PERFORMANCE_FILE, 'w') as f:
        json.dump(perf, f, indent=2)
    if GITHUB_TOKEN and GITHUB_REPO:
        try:
            import base64 as _b64
            url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{PERFORMANCE_API_PATH}"
            r = requests.get(url, headers=_github_headers(), timeout=8)
            sha = r.json().get("sha", "") if r.status_code == 200 else ""
            content_b64 = _b64.b64encode(json.dumps(perf, indent=2).encode()).decode()
            payload = {"message": "state: atualiza performance [skip ci]", "content": content_b64}
            if sha: payload["sha"] = sha
            r2 = requests.put(url, headers=_github_headers(), json=payload, timeout=10)
            if r2.status_code in (200, 201):
                print(f"[PERFORMANCE] Salvo no GitHub: {sum(v.get('total',0) for v in perf.values())} registros")
            else:
                print(f"[PERFORMANCE] Erro GitHub save: {r2.status_code}")
        except Exception as e:
            print(f"[PERFORMANCE] Erro save GitHub: {e}")
def registrar_performance(mercado, resultado):
    """Registra resultado de um mercado específico no performance.json."""
    perf = _load_performance_github()
    if mercado not in perf:
        perf[mercado] = {"green": 0, "red": 0, "total": 0}
    perf[mercado]["total"] += 1
    if resultado == "green":
        perf[mercado]["green"] += 1
    else:
        perf[mercado]["red"] += 1
    _save_performance_github(perf)
    total = perf[mercado]["total"]
    greens = perf[mercado]["green"]
    pct = greens / total * 100 if total > 0 else 0
    print(f"[PERFORMANCE] {MAPA_MERCADO.get(mercado, mercado)}: {resultado} ({greens}/{total} = {pct:.1f}%)")
def get_performance():
    """Retorna dict com performance e % por mercado, e validação 70%/1000."""
    perf = _load_performance_github()
    resultado = {}
    for cod, nome in MAPA_MERCADO.items():
        p = perf.get(cod, {"green": 0, "red": 0, "total": 0})
        total = p["total"]
        greens = p["green"]
        reds = p["red"]
        pct = (greens / total * 100) if total > 0 else 0
        valido = total >= 1000 and pct >= 70
        resultado[cod] = {
            "nome": nome, "green": greens, "red": reds,
            "total": total, "pct": pct, "valido": valido
        }
    # Inclui mercados custom do config.json (só custom_)
    cfg = _load_config()
    merc_cfg = cfg.get("mercados", {})
    for cod, m in merc_cfg.items():
        if cod not in resultado and cod.startswith("custom_"):
            nome = m.get("nome", cod)
            p = perf.get(cod, {"green": 0, "red": 0, "total": 0})
            total = p["total"]
            greens = p["green"]
            reds = p["red"]
            pct = (greens / total * 100) if total > 0 else 0
            valido = total >= 1000 and pct >= 70
            resultado[cod] = {
                "nome": nome, "green": greens, "red": reds,
                "total": total, "pct": pct, "valido": valido
            }
    return resultado
def gerar_layout_performance():
    """Gera layout do relatório de performance por mercado."""
    dados = get_performance()
    sep = "━" * 20
    blocos = []
    for cod, info in dados.items():
        nome = info["nome"]
        g = info["green"]
        r = info["red"]
        t = info["total"]
        pct = info["pct"]
        blocos.append(
            f"<b>{nome}</b>\n"
            f"   ⏳ Total: {t} | 🟢 {g} | 🔴 {r}\n"
            f"   🎯 Acerto: {pct:.1f}%"
        )
    total_g = sum(d["green"] for d in dados.values())
    total_r = sum(d["red"] for d in dados.values())
    total_t = total_g + total_r
    total_pct = (total_g / total_t * 100) if total_t > 0 else 0
    msg = (
        f"{sep}\n"
        f"📊<b>RELATÓRIO DE PERFORMANCE</b>📊\n"
        f"{sep}\n"
        f"{f'{chr(10)}{sep}{chr(10)}'.join(blocos)}{chr(10)}"
        f"{sep}\n"
        f"📌 <b>TOTAL GERAL: {total_t} Sinais</b>\n"
        f"      | 🟢 {total_g} | 🔴 {total_r} | {total_pct:.1f}%|\n"
        f"{sep}\n"
        f"Regras de Validação:\n"
        f"✅ Mínimo 1000 entradas + ≥70%\n"
        f"{sep}"
    )
    return msg
def enviar_relatorio_performance():
    """Gera o relatório de performance. Retorna o texto da mensagem (sem enviar)."""
    return gerar_layout_performance()
def get_performance_24h():
    """Retorna performance por mercado nas últimas 24h a partir dos resultados salvos."""
    registros = _load_resultados_github()
    agora = datetime.now(BRT)
    corte = agora - timedelta(hours=24)
    
    perf = {}
    for cod, nome in MAPA_MERCADO.items():
        perf[cod] = {"nome": nome, "green": 0, "red": 0, "total": 0}
    
    # Adiciona mercados customizados do config.json (mesmo sem registros)
    cfg = _load_config()
    merc_cfg = cfg.get("mercados", {})
    for cod, m in merc_cfg.items():
        if cod not in perf and cod.startswith("custom_"):
            nome = m.get("nome", cod)
            perf[cod] = {"nome": nome, "green": 0, "red": 0, "total": 0}
    
    # Inclui mercados personalizados com registros
    for r in registros:
        ts_str = r.get("timestamp", "")
        mercado = r.get("mercado", "")
        resultado = r.get("resultado", "")
        if not ts_str or not mercado or not resultado:
            continue
        if mercado not in perf:
            continue
        try:
            ts = datetime.fromisoformat(ts_str)
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone(timedelta(hours=-3)))
            if ts < corte:
                continue
        except:
            continue
        perf[mercado]["total"] += 1
        if resultado == "green":
            perf[mercado]["green"] += 1
        else:
            perf[mercado]["red"] += 1
    
    for cod, info in perf.items():
        t = info["total"]
        g = info["green"]
        info["pct"] = (g / t * 100) if t > 0 else 0
    
    return perf
def gerar_layout_mercados24h():
    """Gera layout do relatório de performance por mercado nas últimas 24h."""
    dados = get_performance_24h()
    sep = "━" * 20
    blocos = []
    for cod, info in dados.items():
        nome = info["nome"]
        g = info["green"]
        r = info["red"]
        t = info["total"]
        pct = info["pct"]
        blocos.append(
            f"<b>{nome}</b>\n"
            f"   Total: {t} | 🟢 {g} | 🔴 {r}\n"
            f"   🎯 Acerto: {pct:.1f}%"
        )
    total_g = sum(d["green"] for d in dados.values())
    total_r = sum(d["red"] for d in dados.values())
    total_t = total_g + total_r
    total_pct = (total_g / total_t * 100) if total_t > 0 else 0
    msg = (
        f"{sep}\n"
        f"📊<b>MERCADOS — ÚLTIMAS 24H</b>📊\n"
        f"{sep}\n"
        f"{f'{chr(10)}{sep}{chr(10)}'.join(blocos)}{chr(10)}"
        f"{sep}\n"
        f"📌 <b>TOTAL GERAL: {total_t} Sinais</b>\n"
        f"      | 🟢 {total_g} | 🔴 {total_r} | {total_pct:.1f}%|\n"
        f"{sep}"
    )
    return msg
def enviar_relatorio_mercados24h():
    """Gera o relatório de mercados 24h. Retorna o texto da mensagem (sem enviar)."""
    return gerar_layout_mercados24h()
# ESPN removido — usa apenas SokkerPro
# ═══════════════════════════════════════════════════════════════════════════════
# API 1B — apifootball: jogos ao vivo
# ═══════════════════════════════════════════════════════════════════════════════
def get_jogos_apifootball(fids_apifootball):
    """Busca todos os jogos ao vivo na apifootball."""
    for key in [APIFOOTBALL_COM_KEY]:
        try:
            r = requests.get(
                f"{API_FOOTBALL_URL}/fixtures",
                params={"live": "all"},
                headers={"x-apisports-key": key},
                timeout=15
            )
            rjson = r.json()
            erros = rjson.get("errors", {})
            if erros and (erros.get("requests") or erros.get("access") or erros.get("token")):
                print(f"[apifootball] Chave {key[:8]}... sem acesso: {erros}")
                continue
            fixtures = rjson.get("response", [])
            if not fixtures:
                print(f"[apifootball] Chave {key[:8]}... retornou 0 jogos")
                continue
            jogos = []
            for f in fixtures:
                try:
                    fid    = str(f["fixture"]["id"])
                    # Pula se apifootball já tem
                    if fid in fids_apifootball:
                        continue
                    status = f["fixture"]["status"]
                    state  = status.get("short", "")
                    # Só jogos ao vivo (1H, HT, 2H, ET, P, BT)
                    if state not in ("1H", "HT", "2H", "ET", "P", "BT"):
                        continue
                    minuto = status.get("elapsed", 0) or 0
                    period = 1 if state in ("1H", "HT") or minuto <= 45 else 2
                    home   = f["teams"]["home"]["name"]
                    away   = f["teams"]["away"]["name"]
                    sh     = f["goals"]["home"] or 0
                    sa     = f["goals"]["away"] or 0
                    liga   = f["league"]["name"]
                    jogos.append({
                        "fid": fid, "home": home, "away": away,
                        "sh": sh, "sa": sa, "minuto": minuto,
                        "period": period, "liga": liga, "source": "apifootball"
                    })
                except:
                    continue
            print(f"[apifootball] {len(jogos)} jogos novos (chave {key[:8]}...)")
            return jogos
        except Exception as e:
            print(f"[apifootball] Erro chave {key[:8]}...: {e}")
            continue
    print("[apifootball] Todas as chaves falharam")
    return []
# ═══════════════════════════════════════════════════════════════════════════════
# apifootball: estatísticas de um jogo específico
# ═══════════════════════════════════════════════════════════════════════════════
def get_stats_apifootball_live(fid):
    """Busca stats ao vivo via action=get_statistics da apifootball."""
    try:
        params = {"action": "get_statistics", "match_id": fid, "APIkey": APIFOOTBALL_COM_KEY}
        r = requests.get(APIFOOTBALL_URL, params=params, timeout=10)
        data = r.json()
        if not data or str(fid) not in data:
            return {}
        raw = data[str(fid)].get("statistics", [])
        stats = {}
        for s in raw:
            tipo = s.get("type", "").lower()
            h_val = s.get("home", "").replace("%", "").strip()
            a_val = s.get("away", "").replace("%", "").strip()
            if not h_val or not a_val:
                continue
            if "corner" in tipo:
                stats["escanteios_h"], stats["escanteios_a"] = int(h_val), int(a_val)
            elif "on target" in tipo:
                stats["chutes_gol_h"], stats["chutes_gol_a"] = int(h_val), int(a_val)
            elif "off target" in tipo:
                stats["chutes_tot_h"] = stats.get("chutes_tot_h", 0) + int(h_val)
                stats["chutes_tot_a"] = stats.get("chutes_tot_a", 0) + int(a_val)
            elif "shots total" in tipo:
                stats["chutes_tot_h"] = max(stats.get("chutes_tot_h", 0), int(h_val))
                stats["chutes_tot_a"] = max(stats.get("chutes_tot_a", 0), int(a_val))
            elif "red cards" in tipo:
                stats["red_cards_h"], stats["red_cards_a"] = int(h_val), int(a_val)
            elif tipo == "attacks":
                stats["ataques_h"], stats["ataques_a"] = int(h_val), int(a_val)
            elif tipo == "dangerous attacks":
                stats["ataques_perigosos_h"], stats["ataques_perigosos_a"] = int(h_val), int(a_val)
            elif "possession" in tipo or "ball possession" in tipo:
                stats["posse_h"], stats["posse_a"] = float(h_val), float(a_val)
        # Garantir chutes_tot se tivermos chutes_gol mas nao chutes_tot
        if "chutes_gol_h" in stats and "chutes_tot_h" not in stats:
            stats["chutes_tot_h"] = stats["chutes_gol_h"]
            stats["chutes_tot_a"] = stats["chutes_gol_a"]
        elif "chutes_gol_h" in stats:
            stats["chutes_tot_h"] = max(stats.get("chutes_tot_h", 0), stats["chutes_gol_h"])
            stats["chutes_tot_a"] = max(stats.get("chutes_tot_a", 0), stats["chutes_gol_a"])
        for side in ["h", "a"]:
            for k in ["chutes_tot", "chutes_gol", "red_cards", "ataques", "ataques_perigosos", "posse",
                       "chutes_inside", "chutes_outside", "chutes_bloq", "goal_attempts",
                       "faltas", "yellow_cards", "impedimentos", "defesas", "pressure_bar", "ball_safe",
                       "dapm5", "dapm10", "dapm_total", "xg"]:
                stats.setdefault(f"{k}_{side}", 0)
            stats.setdefault(f"escanteios_{side}", -1)
        print(f"[apifootball Stats] action=get_statistics fid {fid} OK")
        return stats
    except Exception as e:
        print(f"[apifootball Stats] Erro: {e}")
        return {}
def get_stats_apifootball_v3(match_id):
    try:
        params = {"action": "get_statistics", "match_id": match_id, "APIkey": APIFOOTBALL_COM_KEY}
        r = requests.get(APIFOOTBALL_URL, params=params, timeout=10)
        data = r.json()
        if not data or str(match_id) not in data: return {}
        raw = data[str(match_id)].get("statistics", [])
        stats = {}
        for s in raw:
            tipo = s.get("type", "").lower()
            h_val = s.get("home", "").replace("%", "").strip()
            a_val = s.get("away", "").replace("%", "").strip()
            if not h_val or not a_val:
                continue
            if "corner" in tipo:
                stats["escanteios_h"], stats["escanteios_a"] = int(h_val), int(a_val)
            elif "on target" in tipo:
                stats["chutes_gol_h"], stats["chutes_gol_a"] = int(h_val), int(a_val)
            elif "off target" in tipo:
                stats["chutes_tot_h"] = stats.get("chutes_tot_h", 0) + int(h_val)
                stats["chutes_tot_a"] = stats.get("chutes_tot_a", 0) + int(a_val)
            elif "shots total" in tipo:
                stats["chutes_tot_h"] = max(stats.get("chutes_tot_h", 0), int(h_val))
                stats["chutes_tot_a"] = max(stats.get("chutes_tot_a", 0), int(a_val))
            elif "red cards" in tipo:
                stats["red_cards_h"], stats["red_cards_a"] = int(h_val), int(a_val)
            elif tipo == "attacks":
                stats["ataques_h"], stats["ataques_a"] = int(h_val), int(a_val)
            elif tipo == "dangerous attacks":
                stats["ataques_perigosos_h"], stats["ataques_perigosos_a"] = int(h_val), int(a_val)
            elif "possession" in tipo or "ball possession" in tipo:
                stats["posse_h"], stats["posse_a"] = float(h_val), float(a_val)
        if "chutes_gol_h" in stats and "chutes_tot_h" not in stats:
            stats["chutes_tot_h"] = stats["chutes_gol_h"]
            stats["chutes_tot_a"] = stats["chutes_gol_a"]
        elif "chutes_gol_h" in stats:
            stats["chutes_tot_h"] = max(stats.get("chutes_tot_h", 0), stats["chutes_gol_h"])
            stats["chutes_tot_a"] = max(stats.get("chutes_tot_a", 0), stats["chutes_gol_a"])
        return stats
    except: return {}
def get_stats_sokkerpro(fid_raw, home, away):
    try:
        headers = {}  # SokkerPro
        data = r.json()
        raw_stats = data.get("stats", {})
        stats = {}
        for side, key in [("home", "h"), ("away", "a")]:
            side_data = raw_stats.get(side, {})
            stats[f"chutes_tot_{key}"] = int(side_data.get("total_shots", 0) or 0)
            stats[f"chutes_gol_{key}"] = int(side_data.get("shots_on_target", 0) or 0)
            stats[f"escanteios_{key}"] = int(side_data.get("corner_kicks", 0) or 0)
            cards = side_data.get("cards", {})
            if isinstance(cards, dict):
                stats[f"red_cards_{key}"] = int(cards.get("red", 0) or 0)
        return stats
    except: return {}
def get_jogos_apifootball_v3(fids_existentes):
    try:
        hoje = datetime.now().strftime("%Y-%m-%d")
        params = {"action": "get_events", "match_live": "1", "APIkey": APIFOOTBALL_COM_KEY}
        r = requests.get(APIFOOTBALL_URL, params=params, timeout=15)
        data = r.json()
        if not isinstance(data, list): return []
        # Busca odds de UMA vez (from=hoje&to=hoje) e indexa por match_id + bookmaker
        odds_idx = {}
        try:
            params_odd = {"action": "get_odds", "from": hoje, "to": hoje, "APIkey": APIFOOTBALL_COM_KEY}
            ro = requests.get(APIFOOTBALL_URL, params=params_odd, timeout=15)
            odds_raw = ro.json()
            if isinstance(odds_raw, list):
                for odd in odds_raw:
                    mid = odd.get("match_id")
                    bk = odd.get("odd_bookmakers", "").lower()
                    if mid and bk and odd.get("odd_1") and odd.get("odd_2"):
                        if mid not in odds_idx:
                            odds_idx[mid] = {}
                        odds_idx[mid][bk] = odd
        except:
            pass
        print(f"[APIF-ODDS] {len(odds_idx)} jogos com odds carregadas")
        jogos = []
        for ev in data:
            status_raw = str(ev.get("match_status", "0") or "0").replace("'","").strip()
            if status_raw.lower() == "finished":
                continue
            fid = "apif_" + str(ev.get("match_id", ""))
            if fid in fids_existentes: continue
            status_digits = __import__('re').findall(r'\d+', status_raw)
            minuto = int(status_digits[0]) if status_digits else 0
            liga_nome = (ev.get("league_name", "") or "").strip()
            country = (ev.get("country_name", "") or "").strip()
            if country and liga_nome and " " + country not in (" " + liga_nome):
                liga_nome = f"{liga_nome} {country}"
            if not liga_nome:
                liga_nome = ev.get("league", "") or ev.get("competition_name", "") or "Liga"
            fid_raw = str(ev.get("match_id", ""))
            odd_h = odd_a = None
            odds_b365 = {}
            odds_bano = {}
            if fid_raw in odds_idx:
                bks = odds_idx[fid_raw]
                # Moneyline odd_h/odd_a: prioridade Bet365 > Betano > qualquer outra
                odd_h = odd_a = None
                for bk_alvo in ("bet365", "betano"):
                    if bk_alvo in bks:
                        oh = bks[bk_alvo].get("odd_1")
                        oa = bks[bk_alvo].get("odd_2")
                        if oh and oa:
                            odd_h = float(oh)
                            odd_a = float(oa)
                            break
                if not (odd_h and odd_a):
                    for bk, od in bks.items():
                        oh = od.get("odd_1")
                        oa = od.get("odd_2")
                        if oh and oa:
                            odd_h = float(oh)
                            odd_a = float(oa)
                            break
                for bk_alvo, dest in [("bet365", odds_b365), ("betano", odds_bano)]:
                    if bk_alvo in bks:
                        entry = bks[bk_alvo]
                        for campo in ("o+0.5","o+1","o+1.5","o+2","o+2.5","bts_yes","bts_no","odd_1","odd_2"):
                            v = entry.get(campo)
                            if v: dest[campo] = float(v)
            jogos.append({
                "fid": fid, "fid_raw": fid_raw,
                "home": ev.get("match_hometeam_name", ""),
                "away": ev.get("match_awayteam_name", ""),
                "sh": int(ev.get("match_hometeam_score", 0) or 0),
                "sa": int(ev.get("match_awayteam_score", 0) or 0),
                "minuto": minuto,
                "liga": liga_nome,
                "period": 2 if minuto >= 45 else 1,
                "source": "apifootball",
                "home_id": str(ev.get("match_hometeam_id", "")),
                "away_id": str(ev.get("match_awayteam_id", "")),
                "odd_h": odd_h,
                "odd_a": odd_a,
                "odds_b365": odds_b365,
                "odds_bano": odds_bano
            })
        print(f"[APIF-v3] {len(jogos)} novos jogos (de {len(data)} totais)")
        return jogos
    except Exception as e:
        print(f"[APIF-v3 ERRO] {e}")
        return []
_CACHED_DATA = None
def _get_data():
    """Busca dados do SokkerPro com cache — UMA chamada HTTP por execução."""
    global _CACHED_DATA
    if _CACHED_DATA is not None:
        return _CACHED_DATA
    try:
        r = requests.get(SOKKERPRO_URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        _CACHED_DATA = r.json()
        return _CACHED_DATA
    except Exception as e:
        print(f"[SKP] Erro ao buscar dados: {e}")
        return None
def _get_float(val, default=0.0):
    if not val or str(val).strip() in ('', 'None'): return default
    try: return float(str(val).split('#')[0].strip())
    except: return default
def _get_int(val, default=0):
    if not val or str(val).strip() in ('', 'None'): return default
    try: return int(float(str(val)))
    except: return default

def _extrair_stats_sokkerpro(fix):
    """Extrai TODOS os stats disponíveis de uma fixture SokkerPro."""
    def g(k, d=0):
        return _get_int(fix.get(k, d))
    def gf(k, d=0.0):
        return _get_float(fix.get(k, d))
    
    # Parse prognosticos (JSON string com previsões estatísticas)
    btts_prob = 0.0
    media_gols_ht_h = 0.0
    media_gols_ht_a = 0.0
    media_gols_ft_h = 0.0
    media_gols_ft_a = 0.0
    try:
        prog_raw = fix.get('prognosticos', '')
        if prog_raw and isinstance(prog_raw, str) and prog_raw.strip() and prog_raw != '""':
            prog = json.loads(prog_raw)
            # BTTS Probabilidade
            if 'mercado_ambos_marcam' in prog and 'ambos_sim' in prog['mercado_ambos_marcam']:
                btts_prob = gf(prog['mercado_ambos_marcam']['ambos_sim'].get('probabilidade', 0))
            # Media Gols HT (primeiro tempo)
            if 'mercado_gols_primeiro_tempo' in prog:
                det = prog['mercado_gols_primeiro_tempo'].get('over_0_5', {}).get('detalhes', {})
                media_gols_ht_h = gf(det.get('media_casa_pt', 0))
                media_gols_ht_a = gf(det.get('media_fora_pt', 0))
            # Media Gols FT (partida completa)
            if 'mercado_gols' in prog:
                det = prog['mercado_gols'].get('over_0_5', {}).get('detalhes', {})
                media_gols_ft_h = gf(det.get('media_casa', 0))
                media_gols_ft_a = gf(det.get('media_fora', 0))
    except Exception:
        pass
    
    _dapm_h = gf('localDapmTotal')
    _dapm_a = gf('visitorDapmTotal')
    dapm_max = max(_dapm_h, _dapm_a)
    
    def _corners(k):
        """Trata corners: 'x' ou string vazia = sem dados (-1)."""
        raw = fix.get(k)
        if raw is None or str(raw).strip() in ('', 'x', 'X', 'None'):
            return -1
        try: return int(float(str(raw)))
        except: return -1
    
    return {
        "chutes_tot_h": g('localShotsTotal'),
        "chutes_tot_a": g('visitorShotsTotal'),
        "chutes_gol_h": g('localShotsOnGoal'),
        "chutes_gol_a": g('visitorShotsOnGoal'),
        "escanteios_h": _corners('localCorners'),
        "escanteios_a": _corners('visitorCorners'),
        "ataques_perigosos_h": g('localAttacksDangerousAttacks'),
        "ataques_perigosos_a": g('visitorAttacksDangerousAttacks'),
        "red_cards_h": g('localRedCards'),
        "red_cards_a": g('visitorRedCards'),
        "dapm5_h": gf('localDapm5'),
        "dapm5_a": gf('visitorDapm5'),
        "dapm10_h": gf('localDapm10'),
        "dapm10_a": gf('visitorDapm10'),
        "dapm_total_h": gf('localDapmTotal'),
        "dapm_total_a": gf('visitorDapmTotal'),
        "medias_goal_h": gf('medias_home_goal'),
        "medias_goal_a": gf('medias_away_goal'),
        "medias_corners_h": gf('medias_home_corners'),
        "medias_corners_a": gf('medias_away_corners'),
        "goals_h": g('localTeamScore', 0),
        "goals_a": g('visitorTeamScore', 0),
        "chutes_inside_h": g('localShotsInsideBox'),
        "chutes_inside_a": g('visitorShotsInsideBox'),
        "chutes_outside_h": g('localShotsOutsideBox'),
        "chutes_outside_a": g('visitorShotsOutsideBox'),
        "chutes_bloq_h": g('localShotsBlocked'),
        "chutes_bloq_a": g('visitorShotsBlocked'),
        "goal_attempts_h": g('localGoalAttempts'),
        "goal_attempts_a": g('visitorGoalAttempts'),
        "faltas_h": g('localFouls'),
        "faltas_a": g('visitorFouls'),
        "yellow_cards_h": g('localYellowCards'),
        "yellow_cards_a": g('visitorYellowCards'),
        "impedimentos_h": g('localOffsides'),
        "impedimentos_a": g('visitorOffsides'),
        "defesas_h": g('localSaves'),
        "defesas_a": g('visitorSaves'),
        "pressure_bar_h": g('localPressureBar'),
        "pressure_bar_a": g('visitorPressureBar'),
        "ball_safe_h": g('localBallSafe'),
        "ball_safe_a": g('visitorBallSafe'),
        "xg_h": gf('localXg'),
        "xg_a": gf('visitorXg'),
        "posse_h": gf('localBallPossession'),
        "posse_a": gf('visitorBallPossession'),
        "ataques_h": g('localAttacksAttacks'),
        "ataques_a": g('visitorAttacksAttacks'),
        "btts_probabilidade": btts_prob,
        "media_gols_ht_h": media_gols_ht_h,
        "media_gols_ht_a": media_gols_ht_a,
        "media_gols_ft_h": media_gols_ft_h,
        "media_gols_ft_a": media_gols_ft_a,
        "dapm_max_h": dapm_max,
        "dapm_max_a": dapm_max,
    }

def get_jogos_sokkerpro(fids_existentes):
    data = _get_data()
    if not data: return []
    jogos = []
    try:
        for cat in data['data']['sortedCategorizedFixtures']:
            for fix in cat['fixtures']:
                fid = str(fix.get('fixtureId', ''))
                if not fid or fid in fids_existentes: continue
                status = fix.get('status', '')
                minuto = _get_int(fix.get('minute', 0))
                # Mapear status para period numerico
                if status in ('FT', 'PEN'): continue  # ignorar finalizados
                if status == '2nd': period = 2
                elif status == '1st': period = 1
                elif status == 'HT': period = 1
                elif status == 'NS': period = 0
                else: period = 0
                # Só incluir se tiver dados basicos
                if status == 'NS' and not minuto: continue
                jogos.append({
                    "fid": fid,
                    "home": fix.get('localTeamName', 'Home'),
                    "away": fix.get('visitorTeamName', 'Away'),
                    "minuto": minuto or _get_int(fix.get('minutePrimeiroTempo', 0)) or _get_int(fix.get('minuteSegundoTempo', 0)),
                    "period": period,
                    "sh": _get_int(fix.get('scoresLocalTeam', 0)),
                    "sa": _get_int(fix.get('scoresVisitorTeam', 0)),
                    "liga": fix.get('leagueName', 'Liga'),
                    "pais": fix.get('countryName', ''),
                    "source": "sokkerpro"
                })
    except: pass
    return jogos
def get_stats_sokkerpro(fid_raw, home="", away=""):
    data = _get_data()
    if not data: return {}
    try:
        for cat in data['data']['sortedCategorizedFixtures']:
            for fix in cat['fixtures']:
                if str(fix.get('fixtureId', '')) == str(fid_raw):
                    return _extrair_stats_sokkerpro(fix)
    except: pass
    return {}
def get_odds_sokkerpro(fid_raw):
    data = _get_data()
    if not data: return (None, None)
    try:
        for cat in data['data']['sortedCategorizedFixtures']:
            for fix in cat['fixtures']:
                if str(fix.get('fixtureId', '')) == str(fid_raw):
                    # XBET_VENCEDOR_HOME/AWAY = odds pré-live (disponível sempre)
                    oh = _get_float(fix.get('XBET_VENCEDOR_HOME'))
                    oa = _get_float(fix.get('XBET_VENCEDOR_AWAY'))
                    if oh > 1 and oa > 1:
                        return (oh, oa)
                    # Fallback: BET365_VENCEDOR_1_LIVE/2_LIVE = odds ao vivo
                    oh = _get_float(fix.get('BET365_VENCEDOR_1_LIVE'))
                    oa = _get_float(fix.get('BET365_VENCEDOR_2_LIVE'))
                    if oh > 1 and oa > 1:
                        return (oh, oa)
                    return (None, None)
    except: pass
    return (None, None)
# --- REPLICANDO FUN\u00c7\u00d5ES DE LAYOUT E L\u00d3GICA ---def get_stats_apifootball_v3(match_id):
    try:
        params = {"action": "get_statistics", "match_id": match_id, "APIkey": APIFOOTBALL_COM_KEY}
        r = requests.get(APIFOOTBALL_URL, params=params, timeout=10)
        data = r.json()
        if not data or str(match_id) not in data: return {}
        raw = data[str(match_id)].get("statistics", [])
        stats = {}
        for s in raw:
            tipo = s.get("type", "").lower()
            h_val = s.get("home", "").replace("%", "").strip()
            a_val = s.get("away", "").replace("%", "").strip()
            if not h_val or not a_val:
                continue
            if "corner" in tipo:
                stats["escanteios_h"], stats["escanteios_a"] = int(h_val), int(a_val)
            elif "on target" in tipo:
                stats["chutes_gol_h"], stats["chutes_gol_a"] = int(h_val), int(a_val)
            elif "off target" in tipo:
                stats["chutes_tot_h"] = stats.get("chutes_tot_h", 0) + int(h_val)
                stats["chutes_tot_a"] = stats.get("chutes_tot_a", 0) + int(a_val)
            elif "shots total" in tipo:
                stats["chutes_tot_h"] = max(stats.get("chutes_tot_h", 0), int(h_val))
                stats["chutes_tot_a"] = max(stats.get("chutes_tot_a", 0), int(a_val))
            elif "red cards" in tipo:
                stats["red_cards_h"], stats["red_cards_a"] = int(h_val), int(a_val)
            elif tipo == "attacks":
                stats["ataques_h"], stats["ataques_a"] = int(h_val), int(a_val)
            elif tipo == "dangerous attacks":
                stats["ataques_perigosos_h"], stats["ataques_perigosos_a"] = int(h_val), int(a_val)
            elif "possession" in tipo or "ball possession" in tipo:
                stats["posse_h"], stats["posse_a"] = float(h_val), float(a_val)
        if "chutes_gol_h" in stats and "chutes_tot_h" not in stats:
            stats["chutes_tot_h"] = stats["chutes_gol_h"]
            stats["chutes_tot_a"] = stats["chutes_gol_a"]
        elif "chutes_gol_h" in stats:
            stats["chutes_tot_h"] = max(stats.get("chutes_tot_h", 0), stats["chutes_gol_h"])
            stats["chutes_tot_a"] = max(stats.get("chutes_tot_a", 0), stats["chutes_gol_a"])
        return stats
    except: return {}
def get_stats_sokkerpro_by_name(home, away):
    """Fallback: busca stats no SokkerPro pelo nome dos times."""
    try:
        data = _get_data()
        if not data: return {}
        for cat in data['data']['sortedCategorizedFixtures']:
            for fix in cat['fixtures']:
                if fix.get('localTeamName', '').lower() == home.lower() and fix.get('visitorTeamName', '').lower() == away.lower():
                    return _extrair_stats_sokkerpro(fix)
    except: pass
    return {}
def get_stats_apifootball_by_name(home, away):
    """Fallback: busca jogo na apifootball pelo nome dos times e retorna stats."""
    import unicodedata
    def norm(s):
        return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower().strip()
    try:
        r = requests.get(APIFOOTBALL_URL, params={"action": "get_events", "match_live": "1", "APIkey": APIFOOTBALL_COM_KEY}, timeout=15)
        data = r.json()
        if not isinstance(data, list): return {}
        h_busca = norm(home)
        a_busca = norm(away)
        # Procura jogo onde os nomes dos times batem (parcialmente)
        for ev in data:
            h_nome = norm(ev.get("match_hometeam_name", ""))
            a_nome = norm(ev.get("match_awayteam_name", ""))
            if (h_busca in h_nome or h_nome in h_busca) and (a_busca in a_nome or a_nome in a_busca):
                mid = str(ev.get("match_id", ""))
                if mid:
                    print(f"[APIF-NAME] Match por nome: {ev['match_hometeam_name']} x {ev['match_awayteam_name']} → ID {mid}")
                    return get_stats_apifootball_v3(mid)
        # Tenta também ao contrário (home/away invertido)
        for ev in data:
            h_nome = norm(ev.get("match_hometeam_name", ""))
            a_nome = norm(ev.get("match_awayteam_name", ""))
            if (h_busca in a_nome or a_nome in h_busca) and (a_busca in h_nome or h_nome in a_busca):
                mid = str(ev.get("match_id", ""))
                if mid:
                    print(f"[APIF-NAME] Match invertido: {ev['match_hometeam_name']} x {ev['match_awayteam_name']} → ID {mid}")
                    stats = get_stats_apifootball_v3(mid)
                    if stats:
                        # Inverter os lados quando o match for invertido
                        for campo in ["escanteios_h","escanteios_a","chutes_tot_h","chutes_tot_a","chutes_gol_h","chutes_gol_a","red_cards_h","red_cards_a","posse_h","posse_a"]:
                            campo_inv = campo.replace("_h","_x").replace("_a","_h").replace("_x","_a")
                            if campo in stats: stats[campo_inv] = stats.pop(campo)
                    return stats
        return {}
    except: return {}
def _moneyline_to_decimal(ml):
    """Converte moneyline americano para decimal."""
    try:
        ml = float(ml)
        if ml > 0:
            return round(ml / 100 + 1, 3)
        else:
            return round(100 / abs(ml) + 1, 3)
    except:
        return 99.0
def get_favorito_odds(home, away, fid=None, league=None):
    """Retorna ('h'|'a', odd_h, odd_a) baseado na menor odd. Usa apifootball e SokkerPro."""
    # Fallback 1: SokkerPro odds
    if fid:
        try:
            oh, oa = get_odds_sokkerpro(fid)
            if oh and oa and oh > 1 and oa > 1:
                fav = "h" if oh <= oa else "a"
                print(f"[ODDS-SKP] {home} x {away} | Casa:{oh} Fora:{oa} -> Fav:{fav}")
                return (fav, oh, oa)
        except Exception as e:
            print(f"[ODDS-SKP] Erro: {e}")
    # Fallback 3: APIfootball.com odds (quando fid for do apifootball)
    if fid and str(fid).replace("apif_","").isdigit():
        try:
            match_id = str(fid).replace("apif_","")
            r = requests.get("https://apiv3.apifootball.com/",
                             params={"action": "get_odds", "match_id": match_id,
                                     "APIkey": APIFOOTBALL_COM_KEY}, timeout=8)
            odds_data = r.json()
            if isinstance(odds_data, list) and odds_data:
                # Prioridade: Bet365 > Betano > qualquer outra
                odd_ml = None
                for bk_alvo in ("bet365", "betano"):
                    for od in odds_data:
                        if str(od.get("odd_bookmakers", "")).lower() == bk_alvo:
                            odd_ml = od
                            break
                    if odd_ml:
                        break
                if not odd_ml:
                    odd_ml = odds_data[0]
                try:
                    odd_h = float(odd_ml.get("odd_1", 0) or 0)
                    odd_a = float(odd_ml.get("odd_2", 0) or 0)
                    if odd_h > 1 and odd_a > 1:
                        fav = "h" if odd_h <= odd_a else "a"
                        print(f"[ODDS-APFC] {home} x {away} | Casa:{odd_h} Fora:{odd_a} → Fav:{fav}")
                        return (fav, odd_h, odd_a)
                except:
                    pass
        except Exception as e:
            print(f"[ODDS-APFC] Erro: {e}")
    # Fallback 3: Odds API (quando tiver cota)
    try:
        r = requests.get("https://api.the-odds-api.com/v4/sports/soccer/odds/",
                         params={"apiKey": ODDS_API_KEY, "regions": "eu",
                                 "markets": "h2h", "oddsFormat": "decimal"}, timeout=10)
        if r.status_code == 200:
            for evento in r.json():
                nomes = [evento.get("home_team","").lower(), evento.get("away_team","").lower()]
                if home.lower() in nomes and away.lower() in nomes:
                    for book in evento.get("bookmakers", []):
                        for mkt in book.get("markets", []):
                            if mkt["key"] == "h2h":
                                outcomes = {o["name"].lower(): o["price"] for o in mkt["outcomes"]}
                                odd_h = outcomes.get(home.lower(), 99)
                                odd_a = outcomes.get(away.lower(), 99)
                                fav = "h" if odd_h <= odd_a else "a"
                                print(f"[ODDS-API] {home} x {away} | Casa:{odd_h} Fora:{odd_a} → Fav:{fav}")
                                return (fav, odd_h, odd_a)
    except:
        pass
    return (None, None, None)
# ═══════════════════════════════════════════════════════════════════════════════
# FILTRO DE JANELAS
# ═══════════════════════════════════════════════════════════════════════════════
def get_odd_favorito_num(home, away, fid=None, league=None, fid_raw=None):
    """Retorna a odd decimal do favorito (numero). Usa SokkerPro ou apifootball."""
    if fid_raw:
        try:
            headers = {}  # SokkerPro
            if r.status_code == 200:
                odds = r.json().get("odds", {})
                oh = float(odds.get("home_win") or 99)
                oa = float(odds.get("away_win") or 99)
                if oh < 90 and oa < 90:
                    return min(oh, oa)
        except: pass
    
    if fid:
        try:
            # SokkerPro odds
            oh, oa = get_odds_sokkerpro(fid)
            if oh and oa and oh > 1 and oa > 1:
                return min(oh, oa)
        except: pass
    
    try:
        r = requests.get("https://api.the-odds-api.com/v4/sports/soccer/odds/",
                         params={"apiKey": ODDS_API_KEY, "regions": "eu",
                                 "markets": "h2h", "oddsFormat": "decimal"}, timeout=10)
        if r.status_code == 200:
            for evento in r.json():
                nomes = [evento.get("home_team","").lower(), evento.get("away_team","").lower()]
                if home.lower() in nomes and away.lower() in nomes:
                    for book in evento.get("bookmakers", []):
                        for mkt in book.get("markets", []):
                            if mkt["key"] == "h2h":
                                outcomes = {o["name"].lower(): o["price"] for o in mkt["outcomes"]}
                                odd_h = outcomes.get(home.lower(), 99)
                                odd_a = outcomes.get(away.lower(), 99)
                                return min(odd_h, odd_a)
    except:
        pass
    return 99
def calcular_prob_gols_ht(chutes_tot, chutes_gol, minuto):
    """Estima prob de gols usando taxa de chutes como proxy de xG."""
    import math as _math
    taxa_conversao = 0.10
    xg = chutes_gol * taxa_conversao + chutes_tot * 0.04
    min_restantes_ht = max(45 - minuto, 1)
    min_restantes_ft = max(90 - minuto, 1)
    taxa_por_min = xg / max(minuto, 1)
    xg_rest_ht = taxa_por_min * min_restantes_ht
    xg_rest_ft = taxa_por_min * min_restantes_ft
    xg_total_ft = xg + xg_rest_ft
    prob_05_ht = round((1 - _math.exp(-max(xg_rest_ht, 0.05))) * 100, 1)
    prob_15_ft = round((1 - _math.exp(-max(xg_total_ft - 1, 0.1))) * 100, 1)
    return prob_15_ft, prob_05_ht
def filtrar_janelas(jogos, cfg=None):
    resultado = []
    # Coleta ranges dos mercados personalizados
    custom_ranges = []
    if cfg:
        merc = cfg.get("mercados", {})
        for key, md in merc.items():
            if key in ("over_05_ht","ambas_marcam","over_15_ft","over_gol_partida","escanteio_ht","escanteio_ft"):
                continue
            if md.get("ativo"):
                ini = md.get("minuto_inicio", 0)
                fim = md.get("minuto_fim", 99)
                per = md.get("periodo", 0)
                custom_ranges.append((ini, fim, per))
    for j in jogos:
        m = j["minuto"]
        p_raw = j["period"]
        if isinstance(p_raw, str):
            p = 2 if '2' in p_raw else 1
        else:
            p = p_raw
            
        em_janela = (
            (p == 1 and 15 <= m <= 27) or
            (p == 1 and 28 <= m <= 38) or
            (p == 2 and 55 <= m <= 77) or
            (p == 2 and 78 <= m <= 88)
        )
        # Também verifica ranges de mercados personalizados
        if not em_janela:
            for (ini, fim, per) in custom_ranges:
                if per == 0 or p == per:
                    if ini <= m <= fim:
                        em_janela = True
                        break
        if em_janela:
            resultado.append(j)
    return resultado
# ═══════════════════════════════════════════════════════════════════════════════
# MENSAGEM PADRÃO
# ═══════════════════════════════════════════════════════════════════════════════
def gerar_motivo(mercado, stats, sh, sa, fav_final, minuto, cantos_atual=0):
    chutes_h          = stats.get("chutes_tot_h", 0) if stats else 0
    chutes_a          = stats.get("chutes_tot_a", 0) if stats else 0
    chutes_gol_h      = stats.get("chutes_gol_h", 0) if stats else 0
    chutes_gol_a      = stats.get("chutes_gol_a", 0) if stats else 0
    cantos_h          = max(0, stats.get("escanteios_h", 0)) if stats else 0
    cantos_a          = max(0, stats.get("escanteios_a", 0)) if stats else 0
    red_h             = stats.get("red_cards_h", 0) if stats else 0
    red_a             = stats.get("red_cards_a", 0) if stats else 0
    posse_h_raw       = stats.get("posse_h", 0.0) if stats else 0.0
    posse_a_raw       = stats.get("posse_a", 0.0) if stats else 0.0
    atq_perig_h       = stats.get("ataques_perigosos_h", 0) if stats else 0
    atq_perig_a       = stats.get("ataques_perigosos_a", 0) if stats else 0
    posse_h = int(round(float(posse_h_raw) * 100)) if float(posse_h_raw) <= 1 else int(round(float(posse_h_raw)))
    posse_a = int(round(float(posse_a_raw) * 100)) if float(posse_a_raw) <= 1 else int(round(float(posse_a_raw)))
    total_chutes      = chutes_h + chutes_a
    total_cantos      = cantos_h + cantos_a
    total_atq_perig   = atq_perig_h + atq_perig_a
    tem_dados         = total_chutes > 0 or total_cantos > 0 or total_atq_perig > 0
    if not tem_dados:
        return "Estatísticas não disponíveis para esta liga"
    # Labels
    if fav_final == "h":
        fav_label   = "Favorito"
        zebra_label = "Zebra"
        fav_chutes  = chutes_h; fav_gol = chutes_gol_h
        adv_chutes  = chutes_a; adv_gol = chutes_gol_a
        fav_atq     = atq_perig_h
        adv_atq     = atq_perig_a
    elif fav_final == "a":
        fav_label   = "Favorito"
        zebra_label = "Zebra"
        fav_chutes  = chutes_a; fav_gol = chutes_gol_a
        adv_chutes  = chutes_h; adv_gol = chutes_gol_h
        fav_atq     = atq_perig_a
        adv_atq     = atq_perig_h
    else:
        fav_label   = "Casa"
        zebra_label = "Fora"
        fav_chutes  = chutes_h; fav_gol = chutes_gol_h
        adv_chutes  = chutes_a; adv_gol = chutes_gol_a
        fav_atq     = atq_perig_h
        adv_atq     = atq_perig_a
    jogo_aberto    = sh == 0 and sa == 0
    fav_perdendo   = (fav_final == "h" and sh < sa) or (fav_final == "a" and sa < sh)
    fav_ganhando   = (fav_final == "h" and sh > sa) or (fav_final == "a" and sa > sh)
    zebra_dominando = adv_chutes > fav_chutes
    minuto_seguro  = max(minuto, 1)
    fav_atq_por_min = round(fav_atq / minuto_seguro, 2)
    adv_atq_por_min = round(adv_atq / minuto_seguro, 2)
    fav_amassando   = fav_atq_por_min >= 0.70 and adv_atq_por_min < 0.70
    adv_amassando   = adv_atq_por_min >= 0.70 and fav_atq_por_min < 0.70
    ambos_pressionando = fav_atq_por_min >= 0.70 and adv_atq_por_min >= 0.70
    vermelho = ""
    if red_h > 0 or red_a > 0:
        vermelho = " 🟥 Vermelho: " + ("Casa" if red_h > 0 else "Fora")
    posse_txt = ""
    if posse_h >= 55:
        posse_txt = f", Casa com {posse_h}% de posse"
    elif posse_a >= 55:
        posse_txt = f", Fora com {posse_a}% de posse"
    # ════════════════════════════════════════════════════════════════
    # ALERTAS POR MERCADO — motivo da entrada
    # ════════════════════════════════════════════════════════════════
    if "CORNER" in mercado or "ESCANTEIO" in mercado:
        if "HT" in mercado:
            if total_atq_perig >= 12:
                return f"Pressão ofensiva muito alta no 1º tempo{vermelho}"
            elif total_atq_perig >= 8:
                return f"Pressão ofensiva elevada no 1º tempo{vermelho}"
            return f"Pressão ofensiva em crescimento no 1º tempo{vermelho}"
        else:
            if total_atq_perig >= 25:
                return f"Pressão ofensiva constante durante a partida{vermelho}"
            elif total_atq_perig >= 15:
                return f"Pressão ofensiva sustentada na partida{vermelho}"
            return f"Pressão ofensiva contínua na partida{vermelho}"
    if mercado == "HT":
        if chutes_gol_h >= 1 and chutes_gol_a >= 1:
            return f"Ambas equipes finalizando no alvo{vermelho}"
        if chutes_gol_h >= 1:
            return f"{fav_label if fav_final=='h' else 'Casa'} finalizando no alvo{vermelho}"
        if chutes_gol_a >= 1:
            return f"{fav_label if fav_final=='a' else 'Fora'} finalizando no alvo{vermelho}"
        if total_chutes >= 8:
            return f"Alta intensidade de chutes no 1º tempo{vermelho}"
        if fav_amassando:
            return f"{fav_label} dominando as ações ofensivas no 1º tempo{vermelho}"
        if ambos_pressionando:
            return f"Ambas equipes pressionando no campo de ataque{vermelho}"
        return f"Jogo movimentado com chances nos dois lados{vermelho}"
    if mercado == "BTTS":
        if chutes_gol_h >= 2 and chutes_gol_a >= 1:
            return f"Ambas equipes com finalizações no alvo{vermelho}"
        if fav_chutes >= 6 and adv_chutes >= 4:
            return f"Ambas equipes atacando com frequência{vermelho}"
        if ambos_pressionando:
            return f"Pressão ofensiva dos dois lados{vermelho}"
        if fav_amassando and adv_chutes >= 4:
            return f"{fav_label} dominando mas {zebra_label} também responde no ataque{vermelho}"
        return f"Ambas equipes com volume de ataque{vermelho}"
    if mercado == "OFT":
        if sh + sa == 1:
            return f"Placar em {sh}x{sa} com movimentação — {total_chutes} chutes | Mais um gol esperado para Over 1.5{vermelho}"
        if total_chutes >= 12:
            return f"Jogo com {total_chutes} finalizações — forte tendência de mais gols no 2º tempo{vermelho}"
        if ambos_pressionando:
            return f"Pressão total — {total_atq_perig} ataques perigosos | Over 1.5 FT com boa projeção{vermelho}"
        if total_atq_perig >= 10:
            return f"{total_atq_perig} ataques perigosos — placar deve se mover para Over 1.5{vermelho}"
        return f"Partida com bons números ofensivos — {total_chutes} chutes em {minuto}' | Over 1.5{vermelho}"
    if mercado == "OVERGOAL":
        if jogo_aberto:
            return f"Jogo 0x0 mas aberto — {total_chutes} chutes, {total_atq_perig} ataques perigosos | Gol esperado{vermelho}"
        if fav_amassando or adv_amassando:
            return f"Time amassando e placar ainda baixo — {total_atq_perig} atq. perigosos | Over Gol Partida{vermelho}"
        if total_atq_perig >= 12:
            return f"Pressão ofensiva muito alta — {total_atq_perig} ataques perigosos | Gol no FT{vermelho}"
        return f"Expectativa de gol com base no volume — {total_chutes} chutes, {total_atq_perig} ataques{vermelho}"
    # ── Fallback: análise geral (pra segurança) ──
    if jogo_aberto:
        if chutes_gol_h >= 3 and chutes_gol_a >= 3:
            return f"Jogo aberto com grandes chances de gol dos dois lados — {chutes_gol_h} finalizações de Casa, {chutes_gol_a} de Fora{posse_txt}{vermelho}"
        if fav_chutes >= 8 and fav_gol >= 3:
            return f"Jogo aberto, {fav_label} criando grandes chances — {fav_chutes} chutes, {fav_gol} no alvo{posse_txt}{vermelho}"
        if zebra_dominando and adv_chutes >= 6 and adv_gol >= 2:
            return f"Jogo aberto, {zebra_label} surpreendendo — {adv_chutes} chutes, {adv_gol} no alvo{posse_txt}{vermelho}"
        if total_chutes >= 12:
            return f"Jogo aberto e bastante movimentado — {chutes_h} chutes de Casa, {chutes_a} de Fora, sem gols ainda{posse_txt}{vermelho}"
        if fav_chutes > adv_chutes and fav_gol > 0:
            return f"Jogo aberto, {fav_label} dominando com {fav_chutes} chutes ({fav_gol} no alvo){posse_txt}{vermelho}"
        if fav_amassando:
            return f"Jogo aberto, {fav_label} amassando — {fav_atq} ataques perigosos x {adv_atq}{posse_txt}{vermelho}"
        if adv_amassando:
            return f"Jogo aberto, {zebra_label} pressionando muito — {adv_atq} ataques perigosos x {fav_atq}{posse_txt}{vermelho}"
        if ambos_pressionando:
            return f"Jogo aberto, ambas equipes pressionando forte — {total_atq_perig} ataques perigosos no total{posse_txt}{vermelho}"
        return f"Jogo aberto, ambas buscando o primeiro gol — {chutes_h} chutes x {chutes_a}{posse_txt}{vermelho}"
    if fav_perdendo:
        if fav_chutes >= 8 and fav_gol >= 3:
            return f"Grandes chances do {fav_label} empatar — chegando constantemente com {fav_chutes} chutes, {fav_gol} no alvo{posse_txt}{vermelho}"
        if fav_chutes >= 6 and fav_gol >= 2:
            return f"{fav_label} em busca do empate, criando boas chances — {fav_chutes} chutes, {fav_gol} no alvo{posse_txt}{vermelho}"
        if fav_amassando:
            return f"{fav_label} perdendo mas amassando! — {fav_atq} ataques perigosos x {adv_atq}{posse_txt}{vermelho}"
        if zebra_dominando and adv_chutes >= 8:
            return f"{zebra_label} dominando e ameaçando ampliar — {adv_chutes} chutes, {adv_gol} no alvo{posse_txt}{vermelho}"
        if adv_amassando:
            return f"{zebra_label} com mais volume de ataque — {adv_atq} ataques perigosos x {fav_atq}{posse_txt}{vermelho}"
        if ambos_pressionando:
            return f"Ambas pressionando — {total_atq_perig} ataques perigosos, jogo aberto{posse_txt}{vermelho}"
        if fav_chutes > adv_chutes:
            return f"{fav_label} em busca do empate, pressionando com {fav_chutes} chutes x {adv_chutes}{posse_txt}{vermelho}"
        return f"{fav_label} perdendo e tentando reagir — {fav_chutes} chutes x {adv_chutes} da {zebra_label}{posse_txt}{vermelho}"
    if fav_ganhando:
        if adv_chutes >= 8 and adv_gol >= 3:
            return f"{zebra_label} pressionando forte em busca do empate — {adv_chutes} chutes, {adv_gol} no alvo{posse_txt}{vermelho}"
        if adv_amassando:
            return f"{zebra_label} amassando mesmo perdendo — {adv_atq} ataques perigosos x {fav_atq}{posse_txt}{vermelho}"
        if fav_chutes >= 8:
            return f"{fav_label} controlando e ampliando a pressão — {fav_chutes} chutes, {fav_gol} no alvo{posse_txt}{vermelho}"
        if fav_amassando:
            return f"{fav_label} na frente e amassando — {fav_atq} ataques perigosos x {adv_atq}{posse_txt}{vermelho}"
        if ambos_pressionando:
            return f"Ambas pressionando, placar aberto — {total_atq_perig} ataques perigosos{posse_txt}{vermelho}"
        return f"{fav_label} vencendo, jogo controlado — {chutes_h} chutes de Casa x {chutes_a} de Fora{posse_txt}{vermelho}"
    if chutes_gol_h >= 3 and chutes_gol_a >= 3:
        return f"Jogo bastante movimentado, ambas chutando no alvo — {chutes_gol_h} finalizações de Casa, {chutes_gol_a} de Fora{posse_txt}{vermelho}"
    if chutes_h >= 8 and chutes_a >= 8:
        return f"Jogo intenso dos dois lados — {chutes_h} chutes de Casa, {chutes_a} de Fora{posse_txt}{vermelho}"
    if fav_chutes >= 8 and fav_gol >= 3:
        return f"{fav_label} chegando constantemente na área — {fav_chutes} chutes, {fav_gol} no alvo{posse_txt}{vermelho}"
    if zebra_dominando and adv_chutes >= 6:
        return f"{zebra_label} surpreendendo com mais volume — {adv_chutes} chutes ({adv_gol} no alvo) x {fav_chutes} do {fav_label}{posse_txt}{vermelho}"
    if fav_chutes > adv_chutes and fav_gol > 0:
        return f"{fav_label} criando mais chances — {fav_chutes} chutes ({fav_gol} no alvo) x {adv_chutes}{posse_txt}{vermelho}"
    if fav_amassando:
        return f"{fav_label} amassando em busca da virada — {fav_atq} ataques perigosos x {adv_atq}{posse_txt}{vermelho}"
    if adv_amassando:
        return f"{zebra_label} pressionando para virar — {adv_atq} ataques perigosos x {fav_atq}{posse_txt}{vermelho}"
    if ambos_pressionando:
        return f"Jogo eletrizante, ambas pressionando — {total_atq_perig} ataques perigosos{posse_txt}{vermelho}"
    if total_cantos >= 6:
        return f"Jogo bastante movimentado pelas laterais — {total_cantos} escanteios, {total_chutes} chutes{posse_txt}{vermelho}"
    return f"Jogo equilibrado, ambas criando chances — {chutes_h} chutes de Casa x {chutes_a} de Fora{posse_txt}{vermelho}"
def msg_universal(home, away, minuto, liga, pais, n, mercado, entrada, placar, extra_val=None, cantos_atual=0, stats=None, sh=0, sa=0, fav_final="h", odd_h=None, odd_a=None, odd_b365=None, odd_bano=None, nome=None, tipo=""):
    # Definir a entrada conforme os layouts das imagens
    # Lógica universal baseada no campo "tipo" do config.json
    if tipo in ("escanteio", "corner", "escanteio_ht", "escanteio_ft"):
        linha = cantos_atual + 0.5
        entrada = f"Mais de {linha}🚩"
    elif tipo in ("gol_intervalo", "over_gol", "over_15", "ambas_marcam", "over", "gol_partida"):
        if "Over" not in str(entrada) and "Ambas" not in str(entrada):
            if tipo == "over_15": entrada = "Over 1.5"
            elif tipo == "ambas_marcam": entrada = "Ambas Marcam"
            elif tipo == "gol_intervalo": entrada = "Over 0.5"
            elif tipo in ("over_gol", "over", "gol_partida"):
                linha = sh + sa + 0.5
                entrada = f"Mais de {linha}"
        entrada = f"{entrada}⚽️"
    # Fallback para detecção por string (mercados antigos)
    elif "CORNER" in mercado or "ESCANTEIO" in mercado or (nome and "CANTO" in nome.upper()):
        linha = cantos_atual + 0.5
        entrada = f"Mais de {linha}🚩"
    elif mercado in ("HT", "BTTS", "OFT", "OVERGOAL"):
        if "Over" not in str(entrada) and "Ambas" not in str(entrada):
            if mercado == "OFT": entrada = "Over 1.5"
            elif mercado == "BTTS": entrada = "Ambas Marcam"
            elif mercado == "HT": entrada = "Over 0.5"
        entrada = f"{entrada}⚽️"
    # Extração de estatísticas
    chutes_h = stats.get("chutes_tot_h", 0) if stats else 0
    chutes_a = stats.get("chutes_tot_a", 0) if stats else 0
    alvo_h   = stats.get("chutes_gol_h", 0) if stats else 0
    alvo_a   = stats.get("chutes_gol_a", 0) if stats else 0
    cant_h   = stats.get("escanteios_h", 0) if stats else 0
    cant_a   = stats.get("escanteios_a", 0) if stats else 0
    atq_per_h = stats.get("ataques_perigosos_h", 0) if stats else 0
    atq_per_a = stats.get("ataques_perigosos_a", 0) if stats else 0
    dapm10_h = _get_float(stats.get("dapm10_h", 0)) if stats else 0
    dapm10_a = _get_float(stats.get("dapm10_a", 0)) if stats else 0
    dapm5_h = _get_float(stats.get("dapm5_h", 0)) if stats else 0
    dapm5_a = _get_float(stats.get("dapm5_a", 0)) if stats else 0
    
    # ════════════════════════════════════════════════════════════════
    # SISTEMA DE ALERTAS UNIFICADO
    # ════════════════════════════════════════════════════════════════
    # Cleubiano thresholds (APPM puro) — definem a intensidade da pressão
    # Zapia thresholds (APPM + mercado + stats) — refinam o contexto
    # ════════════════════════════════════════════════════════════════
    
    atq_max = max(atq_per_h, atq_per_a)
    appm_val = round(atq_max / minuto, 2) if minuto > 0 else 0
    
    # — Quem está pressionando —
    if atq_per_h > atq_per_a:
        quem = "do Mandante"
        dominante = home
    elif atq_per_a > atq_per_h:
        quem = "do Visitante"
        dominante = away
    else:
        quem = "de ambas equipes"
        dominante = "Ambos"
    
    periodo = "1º tempo" if minuto <= 45 else "2º tempo"
    
    # — Variáveis auxiliares —
    total_chutes = chutes_h + chutes_a
    total_alvo = alvo_h + alvo_a
    total_atq = atq_per_h + atq_per_a
    total_cant = cant_h + cant_a
    jogo_aberto = placar == "0x0"
    fav_nome = home if fav_final == "h" else (away if fav_final == "a" else "—")
    
    # ════════════════════════════════════════════════════════════════
    # THRESHOLDS CLEUBIANO — APPM PURO (ÚNICO SISTEMA DE ALERTA)
    # ════════════════════════════════════════════════════════════════
    if appm_val >= 2.0:
        alerta = "Partida Com Pressão Constante."
    elif appm_val >= 1.5:
        alerta = "Partida Pegando Fogo."
    elif appm_val >= 1.0:
        alerta = "Partida Com Ritmo Intenso."
    elif appm_val >= 0.8:
        alerta = f"Partida Com Pressão {quem}."
    elif appm_val >= 0.7:
        alerta = "Partida Com Ritmo Moderado."
    elif appm_val >= 0.5:
        alerta = "Partida Com Ritmo Médio."
    elif appm_val >= 0.3:
        alerta = "Partida Com Ritmo Fraco."
    else:
        alerta = "Partida Com Ritmo Muito Baixo."
    # APPM para exibição no layout
    appm = appm_val
    dapm10 = max(dapm10_h, dapm10_a)
    dapm5 = max(dapm5_h, dapm5_a)
    # Emojis EXATOS do print 1784355796901
    seta = "🚩" # No print é a seta vermelha que o Telegram renderiza como o emoji 🚩 ou similar
    seta_v = "🚩" 
    if nome:
        title = nome
    elif "CORNER" in mercado or "ESCANTEIO" in mercado or (nome and "CANTO" in nome.upper()):
        nome_m = mercado.replace('CORNER_', 'ESCANTEIO ÁSIAT/LMT ')
        title = f"🚩🔥{nome_m}🔥🚩"
    else:
        titles_map = {
            "HT": "OVER GOL INTERVALO",
            "BTTS": "AMBAS MARCAM",
            "OFT": "OVER 1.5 GOLS PARTIDA",
            "OVERGOAL": "OVER GOL PARTIDA"
        }
        title = f"⚽️🔥{titles_map.get(mercado, mercado)}🔥⚽️"
    odd_rec = "1.70"
    sep = "━━━━━━━━━━━━━━━━━━━━"
    # Monta texto da liga (com país se disponível)
    liga_texto = f"<b>🌍 Liga: {liga}</b>"
    if pais:
        liga_texto = f"<b>🌍 Liga: {liga} ({pais})</b>"
    # Layout EXATO dos 6 templates - tudo em negrito, sem "OPORTUNIDADE IDENTIFICADA"
    msg = (
        f"{sep}\n"
        f"<b>{title}</b>\n"
        f"{sep}\n"
        f"<b>⚽️ Placar: {placar}</b>\n"
        f"{liga_texto}\n"
        f"<b>📡 {home} x {away}</b>\n"
        f"<b>👀 ODDs: Casa {odd_h or '—'} / Fora {odd_a or '—'}</b>\n"
        f"<b>⏰️ Minuto: {minuto}'</b>\n"
        f"{sep}\n"
        f"<b>📊 Estatísticas ao Vivo da Partida:</b>\n"
        f"<b>🚀 Chutes Totais: {chutes_h} | {chutes_a}</b>\n"
        f"<b>🎯 Chutes No Alvo: {alvo_h} | {alvo_a}</b>\n"
        f"<b>⚔️ Ataques Perigosos: {atq_per_h} | {atq_per_a}</b>\n"
        f"<b>🚩 Escanteios: {cant_h} | {cant_a}</b>\n"
        f"<b>🔥 APPM da Partida: {appm}</b>\n"
        f"<b>🔥 APPM Últ 10 Min: {dapm10}</b>\n"
        f"<b>🔥 APPM Últ 5 Min: {dapm5}</b>\n"
        f"{sep}\n"
        f"<b>💡 Análise Técnica da Partida:</b>\n"
        f"<b>🎯 Favorito: {fav_nome}</b>\n"
        f"<b>🚨 Alerta: {alerta}</b>\n"
        f"{sep}\n"
        f"<b>📌 Entrada: {entrada}</b>\n"
        f"<b>💰 ODD Recomendada: {odd_rec}+</b>\n"
        f"{sep}\n"
        "<b>🔔Jogue com Responsabilidade🔔</b>"
    )
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🟣BET365🟣", "url": "https://www.bet365.bet.br/#/AX/"},
                {"text": "🔵PARIPESA🔵", "url": "https://paripesa.com/mobile?bf=667237b941dd4_5426307053"}
            ]
        ]
    }
    return msg, keyboard
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🟣BET365🟣", "url": "https://www.bet365.bet.br/#/AX/"},
                {"text": "🔵PARIPESA🔵", "url": "https://paripesa.com/mobile?bf=667237b941dd4_5426307053"}
            ]
        ]
    }
    
    return msg, keyboard
def checar_resultado(sinal):
    """Verifica se um sinal já enviado deu green ou red usando SokkerPro."""
    try:
        fid_raw = str(sinal.get("fixture_id", "")).replace("skp_", "")
        mercado = sinal.get("mercado")
        
        # Busca dados do jogo via SokkerPro
        data = _get_data()
        if not data: return None
        
        # Procura a fixture pelo ID
        fixture = None
        for cat in data['data']['sortedCategorizedFixtures']:
            for fix in cat['fixtures']:
                if str(fix.get('fixtureId', '')) == str(fid_raw):
                    fixture = fix
                    break
            if fixture: break
        
        if not fixture: return None
        
        status = fixture.get('status', '')
        minute = int(fixture.get('minute', 0) or 0)
        is_final = status in ('FT', 'PEN')
        # So confirma HT se estiver no 2o tempo (minuto >= 50) ou status HT/2nd
        # Evita confirmar durante acrescimos do 1T (minuto 45-49 com status 1st)
        is_2h = (status in ('2nd', 'HT')) or (minute >= 50)
        
        # Mercados de HT/1T podem confirmar após o intervalo
        mercados_ht = ["HT", "CORNER_HT", "BTTS"]
        eh_mercado_ht = mercado in mercados_ht or (
            mercado and mercado.startswith("custom_") and 
            sinal.get("tipo") in ("gol_intervalo", "escanteio_ht")
        )
        
        if not (is_final or (eh_mercado_ht and is_2h)):
            return None
        
        # Placar atual
        gh = int(fixture.get('scoresLocalTeam', 0) or 0)
        ga = int(fixture.get('scoresVisitorTeam', 0) or 0)
        total_final = gh + ga
        
        # Placar HT (scoresHT = total de gols no intervalo)
        scores_ht = int(fixture.get('scoresHT', 0) or 0)
        # Estima HT individual: busca o placar mais recente antes do HT
        # SokkerPro não separa home/away no HT, mas scoresHT já é o total
        # Para mercado HT, precisamos apenas saber se houve gol
        total_ht = scores_ht
        
        # Lógica por Mercado
        if mercado in ["HT"]:
            return "green" if total_ht >= 1 else ("red" if (is_2h or is_final) else None)
        
        elif mercado == "BTTS":
            return "green" if (gh >= 1 and ga >= 1) else ("red" if is_final else None)
        
        elif mercado == "OFT":
            return "green" if total_final >= 2 else ("red" if is_final else None)
            
        elif mercado == "OVERGOAL":
            gols_entrada = sinal.get("extra_val", 0)
            return "green" if total_final > gols_entrada else ("red" if is_final else None)
            
        elif mercado in ["CORNER_HT"]:
            c_h = _get_int(fixture.get('localCorners', 0))
            c_a = _get_int(fixture.get('visitorCorners', 0))
            c_final = max(0, c_h) + max(0, c_a)
            c_entrada = sinal.get("extra_val", 0)
            if c_final > c_entrada: return "green"
            # RED se já entrou no 2º tempo (escanteios do 1º tempo já estão finalizados)
            return "red" if is_2h else None
        elif mercado == "CORNER_FT":
            c_h = _get_int(fixture.get('localCorners', 0))
            c_a = _get_int(fixture.get('visitorCorners', 0))
            c_final = max(0, c_h) + max(0, c_a)
            c_entrada = sinal.get("extra_val", 0)
            if c_final > c_entrada: return "green"
            return "red" if is_final else None
        # Mercados personalizados: auditoria por tipo
        elif mercado and mercado.startswith("custom_"):
            extra = sinal.get("extra_val")
            tipo_mkt = sinal.get("tipo", "")
            
            if tipo_mkt == "gol_intervalo":
                # Over 0.5 gols HT: gol no 1° tempo
                return "green" if total_ht >= 1 else ("red" if (is_2h or is_final) else None)
            
            elif tipo_mkt == "gol_partida":
                # Over X gols partida
                return "green" if total_final > extra else ("red" if is_final else None)
            
            elif tipo_mkt == "escanteio_ht":
                # Escanteio HT: ver corners no 1° tempo
                c_h = _get_int(fixture.get('localCorners', 0))
                c_a = _get_int(fixture.get('visitorCorners', 0))
                c_final = max(0, c_h) + max(0, c_a)
                c_entrada = extra if extra is not None else 0
                if c_final > c_entrada: return "green"
                return "red" if is_2h else None
            
            elif tipo_mkt == "escanteio_ft":
                # Escanteio FT: corners até o fim
                c_h = _get_int(fixture.get('localCorners', 0))
                c_a = _get_int(fixture.get('visitorCorners', 0))
                c_final = max(0, c_h) + max(0, c_a)
                c_entrada = extra if extra is not None else 0
                if c_final > c_entrada: return "green"
                return "red" if is_final else None
            
            # Fallback genérico: extra_val como linha de gols
            if extra is not None:
                if total_final > extra: return "green"
                return "red" if is_final else None
            # Sem info extra, não confirma
            return None
        return None
    except: return None
# ═══════════════════════════════════════════════════════════════════════════════
# COMANDOS TELEGRAM (/relatoriodiario e /radar)
# ═══════════════════════════════════════════════════════════════════════════════
def check_status_command(total_jogos_live=0, jogos_live=None, jogos_na_janela=None):
    import base64 as _b64
    last_id = 0
    # Lê last_update do GitHub para persistir entre execuções
    if GITHUB_TOKEN and GITHUB_REPO:
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/last_update.json"
            r = requests.get(url, headers=_github_headers(), timeout=6)
            if r.status_code == 200:
                last_id = json.loads(_b64.b64decode(r.json()["content"]).decode()).get("last_id", 0)
        except: pass
    elif os.path.exists(LAST_UPDATE_FILE):
        try:
            with open(LAST_UPDATE_FILE, 'r') as f: last_id = json.load(f).get("last_id", 0)
        except: pass
    try:
        sep = "━━━━━━━━━━━━━━━━━━━━"
        r   = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates",
                           params={"offset": last_id + 1, "timeout": 5}, timeout=10).json()
        if not r.get("ok"): return
        new_last_id = last_id
        radar_respondido = False
        relatorio_respondido = False
        agora_ts = datetime.now(timezone.utc).timestamp()
        for update in r.get("result", []):
            new_last_id = update["update_id"]
            msg     = update.get("message", {})
            text    = msg.get("text", "")
            chat_orig = msg.get("chat", {}).get("id", 0)
            msg_ts  = msg.get("date", 0)
            # Ignora comandos com mais de 30 minutos (evita processar acúmulo muito antigo)
            if agora_ts - msg_ts > 600: # Ignora comandos com mais de 10 minutos
                continue
            pass  # responde em qualquer chat
            if text == "/relatoriomensal" and not relatorio_respondido:
                msg = enviar_relatorio_mensal()
                requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                              json={"chat_id": chat_orig, "text": msg, "parse_mode": "HTML"})
                relatorio_respondido = True
            if text == "/relatoriodiario" and not relatorio_respondido:
                enviar_relatorio_diario()
                relatorio_respondido = True
            elif text == "/mercados" or text == "/mercados24h":
                try:
                    if text == "/mercados24h":
                        msg = enviar_relatorio_mercados24h()
                    else:
                        msg = enviar_relatorio_performance()
                    if msg:
                        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                                      json={"chat_id": chat_orig, "text": msg, "parse_mode": "HTML"})
                    else:
                        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                                      json={"chat_id": chat_orig, "text": "Ainda sem dados de performance registrados.", "parse_mode": "HTML"})
                except Exception as e:
                    print(f"[PERFORMANCE] Erro: {e}")
            elif text == "/radar" and not radar_respondido:
                jogos_live = jogos_live or []
                jogos_na_janela = jogos_na_janela or []
                # Monta lista de jogos na janela
                if jogos_na_janela:
                    linhas_janela = ""
                    for j in jogos_na_janela:
                        h = j.get("home", "")
                        a = j.get("away", "")
                        m = j.get("minuto", 0)
                        sh = j.get("sh", 0)
                        sa = j.get("sa", 0)
                        liga = j.get("liga", "")
                        linhas_janela += f"🎯 <b>{h} x {a}</b> | {m}' | {sh}x{sa} | {liga}\n"
                else:
                    linhas_janela = "Nenhum jogo na janela no momento."
                # Monta lista de jogos ao vivo fora da janela (até 10)
                fora_janela = [j for j in jogos_live if j not in jogos_na_janela]
                if fora_janela:
                    linhas_fora = ""
                    for j in fora_janela[:10]:
                        h = j.get("home", "")
                        a = j.get("away", "")
                        m = j.get("minuto", 0)
                        sh = j.get("sh", 0)
                        sa = j.get("sa", 0)
                        linhas_fora += f"⏳ {h} x {a} | {m}' | {sh}x{sa}\n"
                    if len(fora_janela) > 10:
                        linhas_fora += f"... e mais {len(fora_janela)-10} jogos"
                else:
                    linhas_fora = "—"
                msg_radar = (
                    f"{sep}\n"
                    f"📡👉<b>RADAR DE JOGOS AO VIVO</b>👈📡\n"
                    f"{sep}\n"
                    f"🔴 <b>{total_jogos_live} jogos ao vivo</b>\n"
                    f"🎯 <b>{len(jogos_na_janela)} na janela alvo</b>\n"
                    f"{sep}\n"
                    f"🚨<b>JOGOS NO ALVO:</b>\n{linhas_janela}"
                    f"{sep}\n"
                    f"<b>⏳ FORA DA JANELA:</b>\n{linhas_fora}"
                    f"{sep}"
                )
                requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={"chat_id": chat_orig, "text": msg_radar, "parse_mode": "HTML"}, timeout=10)
                radar_respondido = True
        if new_last_id > last_id:
            with open(LAST_UPDATE_FILE, 'w') as f: json.dump({"last_id": new_last_id}, f)
            # Salva no GitHub para persistir entre execuções
            import base64 as _b64
            url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/last_update.json"
            r_get = requests.get(url, headers=_github_headers(), timeout=6)
            sha_lu = r_get.json().get("sha", "") if r_get.status_code == 200 else ""
            content_b64 = _b64.b64encode(json.dumps({"last_id": new_last_id}).encode()).decode()
            payload = {"message": "state: last_update [skip ci]", "content": content_b64}
            if sha_lu: payload["sha"] = sha_lu
            r_put = requests.put(url, headers=_github_headers(), json=payload, timeout=8)
            print(f"[CMD] last_id salvo: {new_last_id} | status: {r_put.status_code} | token_ok: {bool(GITHUB_TOKEN)}")
    except Exception as e:
        print(f"[CMD] Erro ao processar comandos: {e}")
# ═══════════════════════════════════════════════════════════════════════════════
# HISTÓRICO — Média de gols (SokkerPro)
# ═══════════════════════════════════════════════════════════════════════════════
_HIST_CACHE = {}
def get_media_gols_historica_skp(home, away, stats):
    """Retorna a média de gols usando os campos medias da própria API SokkerPro.
    As médias são fornecidas pela SokkerPro (mínimo 10 jogos).
    Sem dados = retorna -1 (bloqueia: -1 < 2.2 = False).
    Aplicado APENAS nos mercados de gol (escanteios livres)."""
    chave = f"{home}_{away}"
    if chave in _HIST_CACHE:
        return _HIST_CACHE[chave]
    if not stats:
        _HIST_CACHE[chave] = -1.0
        return -1.0
    try:
        media_h = stats.get("medias_home_goal", 0)
        media_a = stats.get("medias_away_goal", 0)
        # Sem dados de média → retorna -1 (bloqueia na prática)
        if media_h <= 0 and media_a <= 0:
            _HIST_CACHE[chave] = -1.0
            return -1.0
        media_total = media_h + media_a
        _HIST_CACHE[chave] = media_total
        return media_total
    except:
        _HIST_CACHE[chave] = -1.0
        return -1.0
# ═══════════════════════════════════════════════════════════════════════════════
# LOOP PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════════════
def run_ciclo(cfg, GERAL, MERCADOS, sent, total_env, confirmed_ids=None):
    """Executa um ciclo completo de coleta, análise e envio."""
    # Limpa cache do SokkerPro para buscar dados frescos
    global _CACHED_DATA
    _CACHED_DATA = None
    # ─── ISOLAMENTO POR REPOSITÓRIO: cada bot usa SÓ sua fonte ───
    _repo_atual = os.environ.get("GITHUB_REPOSITORY", "").lower()
    BOT_SOURCE = "sokkerpro"
    print(f"[Ciclo] Coletando dados...")
    # ─────────────────────────────────────────────────────────────
    # PASSO 1: Coleta APENAS da fonte designada do bot
    # ─────────────────────────────────────────────────────────────
    jogos_live = []
    if BOT_SOURCE == "apifootball":
        jogos_live = get_jogos_apifootball_v3(set())
        print(f"[apifootball] {len(jogos_live)} jogos ao vivo")
    elif BOT_SOURCE == "sokkerpro":
        jogos_live = get_jogos_sokkerpro(set())
        print(f"[SokkerPro] {len(jogos_live)} jogos ao vivo")
    # PASSO 2: Filtra janelas alvo
    jogos_na_janela = filtrar_janelas(jogos_live, cfg)
    print(f"[Janela] {len(jogos_na_janela)} jogos nas janelas alvo")
    check_status_command(total_jogos_live=len(jogos_live), jogos_live=jogos_live, jogos_na_janela=jogos_na_janela)
    # ═══════════════════════════════════════════════════════════════════════════
    # VALIDAÇÃO DE SINAIS PENDENTES — roda SEMPRE, mesmo sem jogos na janela
    # ═══════════════════════════════════════════════════════════════════════════
    try:
        if confirmed_ids is None:
            confirmed_ids = set()
        sinais_p = _load_sinais_github()
        rest = []
        for s in sinais_p:
            # Gera ID unico: fixture_id + mercado
            s_id = f"{s.get('fixture_id','')}_{s.get('mercado','')}"
            res = checar_resultado(s)
            if res and s_id not in confirmed_ids:
                confirmed_ids.add(s_id)
                emoji = "🟢GREEN CONFIRMADO🟢" if res == "green" else "🔴RED CONFIRMADO🔴"
                send_telegram(emoji, reply_to=s.get("message_id"))
                salvar_resultado(res, mercado=s.get("mercado"))
                registrar_performance(s.get("mercado"), res)
            elif res:
                print(f"[SINAIS-DUP] Pulando {s_id} — já confirmado neste ciclo")
            else:
                rest.append(s)
        # Nao remove sinais confirmados se estao duplicados no GitHub
        # So remove os que estao em rest (nao resolvidos)
        # Sinais ja confirmados permanecem ate resolucao real
        _save_sinais_github(rest)
        print(f"[SINAIS] {len(sinais_p) - len(rest)} resultados confirmados, {len(rest)} ainda pendentes")
    except Exception as e:
        print(f"[SINAIS] Erro validação: {e}")
    if not jogos_na_janela:
        print("[OK] Nenhum jogo na janela — aguardando próximo ciclo")
        save_sent(sent)
        return sent, total_env
    # PASSO 3: Dedup simples
    jogos_dedup = []
    vistos_chaves = set()
    for j in jogos_na_janela:
        hn_j = norm_nome_time(j["home"])
        an_j = norm_nome_time(j["away"])
        chave = hashlib.md5(f"{hn_j}-{an_j}".encode()).hexdigest()[:16]
        if chave not in vistos_chaves:
            vistos_chaves.add(chave)
            jogos_dedup.append(j)
    print(f"[Dedup] {len(jogos_na_janela)} -> {len(jogos_dedup)} jogos unicos")
    for j in jogos_dedup:
        fid    = j["fid"]
        h, a   = j["home"], j["away"]
        hn = norm_nome_time(h)
        an = norm_nome_time(a)
        dedup_id = hashlib.md5(f"{hn}-{an}".encode()).hexdigest()[:12]
        m, p   = j["minuto"], j["period"]
        sh, sa = j["sh"], j["sa"]
        liga   = str(j["liga"])
        pais   = j.get("pais", "")
        stot   = sh + sa
        placar = f"{sh}x{sa}"
        print(f"[Analisando] {h} x {a} | {placar} | {m}min")
        # Coleta de odds
        odd_h, odd_a = None, None
        if BOT_SOURCE == "sokkerpro":
            try:
                so = get_odds_sokkerpro(fid)
                if so and so[0] and so[1]:
                    odd_h, odd_a = so
            except: pass
        else:
            try:
                so = get_odds_sokkerpro(fid)
                if so and so[0] and so[1]:
                    odd_h, odd_a = so
            except: pass
        if not odd_h or not odd_a or odd_h <= 1 or odd_a <= 1:
            print(f"[ODDS] {h} x {a} — odds inválidas ({odd_h}/{odd_a}), pulando")
            continue
        # Identifica favorito
        fav_final = "h" if odd_h <= odd_a else "a"
        fav_gols = sh if fav_final == "h" else sa
        adv_gols = sa if fav_final == "h" else sh
        red_fav = 0
        print(f"[ODDS] {h} x {a} — odd Casa:{odd_h:.2f} Fora:{odd_a:.2f} | Favorito: {'Casa' if fav_final=='h' else 'Fora'}")
        # Stats
        stats = None
        try:
            sb = get_stats_sokkerpro(fid, h, a)
            if isinstance(sb, dict) and sb: stats = sb
        except: pass
        if not stats:
            print(f"[STATS] {h} x {a} — sem stats, pulando")
            continue
        # Valores brutos
        _aph_val = stats.get("ataques_perigosos_h", 0) if stats else 0
        _apa_val = stats.get("ataques_perigosos_a", 0) if stats else 0
        _apt_val = _aph_val + _apa_val
        _appm_total = round(_apt_val / m, 2) if m > 0 else 0
        _appm_h = round(_aph_val / m, 2) if m > 0 else 0
        _appm_a = round(_apa_val / m, 2) if m > 0 else 0
        _chutes_alvo_h = stats.get("chutes_gol_h", 0) if stats else 0
        _chutes_alvo_a = stats.get("chutes_gol_a", 0) if stats else 0
        _chutes_tot_h = stats.get("chutes_tot_h", 0) if stats else 0
        _chutes_tot_a = stats.get("chutes_tot_a", 0) if stats else 0
        _escanteios_h = stats.get("escanteios_h", -1) if stats else -1
        _escanteios_a = stats.get("escanteios_a", -1) if stats else -1
        _posse_h = stats.get("posse_h", 0.0) if stats else 0.0
        _posse_a = stats.get("posse_a", 0.0) if stats else 0.0
        _ataques_perigosos_h = stats.get("ataques_perigosos_h", 0)
        _ataques_perigosos_a = stats.get("ataques_perigosos_a", 0)
        # HISTÓRICO — Média de gols
        media_hist = get_media_gols_historica_skp(h, a, stats)
        diff_gols = adv_gols - fav_gols
# LOOP GENÉRICO DE MERCADOS — processa TODOS do config.json
        # ═══════════════════════════════════════════════════════════════
        for mk, mc in MERCADOS.items():
            if not mc.get("ativo", True): continue
            cper = mc.get("periodo", 0)
            if cper > 0 and p != cper: continue
            cini = mc.get("minuto_inicio", 0)
            cfim = mc.get("minuto_fim", 99)
            if not (cini <= m <= cfim): continue
            
            # Placar válido
            cplacar = mc.get("placar_valido", "")
            if cplacar:
                pv = [x.strip().replace("_","x") for x in cplacar.split(",")]
                if placar not in pv:
                    print(f"[DIAG-{mk}-BARRA] {h} x {a} — placar {placar} não atende ({cplacar}), pulando")
                    continue
            
            # Situação do favorito
            if not _situacao_fav_ok(mc, GERAL, fav_gols, adv_gols):
                print(f"[DIAG-{mk}-BARRA] {h} x {a} — situação do favorito não atende, pulando")
                continue
            
            # Diferença de gols
            diff_max = _crit(mc, GERAL, "diferenca_gols_fav_max", 99)
            if diff_max < 99 and diff_gols > diff_max:
                print(f"[DIAG-{mk}-BARRA] {h} x {a} — diferença de gols ({diff_gols}) > max ({diff_max}), pulando")
                continue
            
            # Cartão vermelho
            red_max = _crit(mc, GERAL, "max_red_card_fav", 99)
            if red_max < 99 and red_fav > red_max:
                print(f"[DIAG-{mk}-BARRA] {h} x {a} — favorito com cartão vermelho ({red_fav} > {red_max}), pulando")
                continue
            
            # Validação de critérios gerais (config.json)
            ok, motivos = _validar_criterios_gerais(mc, stats, fav_final)
            if not ok:
                for motivo in motivos:
                    print(f"[DIAG-{mk}-BARRA] {h} x {a} — {motivo}")
                continue
            
            # Tudo ok — enviar sinal
            hoje = datetime.now(BRT).strftime('%Y%m%d')
            key = f"{dedup_id}_{mk}_{hoje}"
            if key in sent:
                print(f"[DIAG-{mk}-DUP] {h} x {a} — já enviado hoje ({key}), pulando")
                continue
            
            cnome = mc.get("nome", mk)
            c_tipo = mc.get("tipo", "")
            
            # Calcula extra_val e linha para odds
            extra_val = 0
            linha_str = ""
            if c_tipo in ("escanteio_ht", "escanteio_ft", "corner", "escanteio"):
                _eh = stats.get("escanteios_h", -1) if stats else -1
                _ea = stats.get("escanteios_a", -1) if stats else -1
                if _eh < 0 or _ea < 0:
                    print(f"[DIAG-{mk}-ESC] {h} x {a} — sem dados de escanteio (disponível), pulando")
                    continue
                cantos_h = max(0, _eh)
                cantos_a = max(0, _ea)
                extra_val = cantos_h + cantos_a
                linha_str = f"o+{extra_val + 0.5}"
            elif c_tipo in ("gol_partida", "over_gol", "over"):
                extra_val = sh + sa
                linha_str = f"o+{extra_val + 0.5}"
            elif c_tipo == "gol_intervalo":
                extra_val = 0
                linha_str = "o+0.5"
            elif c_tipo == "over_15":
                extra_val = sh + sa
                linha_str = "o+1.5"
            elif c_tipo == "ambas_marcam":
                linha_str = "bts_yes"
            
            # Odds
            ob365 = j.get("odds_b365", {}).get(linha_str) if j.get("odds_b365") and linha_str else None
            obano = j.get("odds_bano", {}).get(linha_str) if j.get("odds_bano") and linha_str else None
            
            mid = send_telegram(
                msg_universal(h, a, m, liga, pais, 5, mk, cnome, placar,
                    cantos_atual=extra_val if "escanteio" in c_tipo else 0,
                    stats=stats, sh=sh, sa=sa, fav_final=fav_final,
                    odd_h=odd_h, odd_a=odd_a, odd_b365=ob365, odd_bano=obano,
                    nome=cnome, tipo=c_tipo),
                marca=key, home=h, away=a, odd_b365_val=ob365, odd_bano_val=obano
            )
            if mid:
                sent.add(key)
                total_env += 1
                save_sent(sent)
                registrar_sinal(fid, mk, h, a, mid, extra_val=extra_val, tipo=c_tipo)
        
        save_sent(sent)
    return sent, total_env
def run():
    # Carrega config dinâmico
    cfg = _load_config()
    GERAL = cfg.get("geral", {})
    MERCADOS = cfg.get("mercados", {})
    sent      = load_sent()
    total_env = 0
    confirmed_ids = set()
    # Sincroniza performance.json com mercados do config.json
    try:
        perf = _load_performance_github()
        mudou = False
        for cod, m in MERCADOS.items():
            if cod not in perf:
                perf[cod] = {"green": 0, "red": 0, "total": 0}
                mudou = True
                print(f"[PERF] Novo mercado adicionado: {cod} ({m.get('nome', cod)})")
        if mudou:
            _save_performance_github(perf)
            print(f"[PERF] performance.json sincronizado com {len(perf)} mercados")
    except Exception as e:
        print(f"[PERF] Erro na sincronização: {e}")
    print(f"[Iniciando] Monitoramento com 5 ciclos de 1 minuto cada")
    # ─── LOOP DE CICLOS (1 min cada) — recarrega config a cada ciclo ───
    for ciclo in range(5):
        # Recarrega config a cada ciclo para pegar alterações do painel
        cfg = _load_config()
        GERAL = cfg.get("geral", {})
        MERCADOS = cfg.get("mercados", {})
        print(f"\n{'='*50}")
        print(f"=== CICLO {ciclo+1}/5 ===")
        print(f"{'='*50}")
        sent, total_env = run_ciclo(cfg, GERAL, MERCADOS, sent, total_env, confirmed_ids)
        # Se não for o último ciclo, espera 60 segundos
        if ciclo < 4:
            print(f"[Aguardando 60s para próximo ciclo...]")
            time.sleep(60)
    # AUTO-DISPATCH: /relatoriodiario + /mercados24h às 23:55
    try:
        agora_hora = datetime.now(BRT)
        if agora_hora.hour == 23 and agora_hora.minute >= 55:
            print(f"[AUTO] 23:55 — disparando relatório diário + mercados 24h")
            enviar_relatorio_diario()
            msg_mercados = enviar_relatorio_mercados24h()
            if msg_mercados:
                send_telegram(msg_mercados)
    except Exception as e:
        print(f"[AUTO] Erro auto-dispatch: {e}")
    print(f"\n{'='*50}")
    print(f"=== EXECUÇÃO COMPLETA ===")
    print(f"Total de sinais enviados: {total_env}")
    print(f"{'='*50}")
if __name__ == "__main__":
    run()