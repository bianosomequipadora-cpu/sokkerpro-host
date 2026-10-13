from __future__ import annotations
import json
import os
import socket
import sys
from pathlib import Path
import requests
from urllib3.util import connection as urllib3_connection
from m4 import M4Session

BASE = "https://m4.sokkerpro.com"
urllib3_connection.allowed_gai_family = lambda: socket.AF_INET
http = requests.Session()
http.headers.update({
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://sokkerpro.com",
    "Referer": "https://sokkerpro.com/",
    "User-Agent": "sokkerpro-monitor/0.1",
})
meta: dict[str, object] = {}

def report(line: str) -> None:
    print("M4_PROBE " + line, flush=True)
    summary = Path(os.environ.get("GITHUB_STEP_SUMMARY", "/dev/null"))
    try:
        with summary.open("a", encoding="utf-8") as out:
            out.write(line + "\n")
    except OSError:
        pass

def post_json(url: str, body: dict) -> object:
    response = http.post(url, json=body, timeout=20)
    meta.update({
        "status": response.status_code,
        "cf_ray": response.headers.get("CF-Ray"),
        "retry_after": response.headers.get("Retry-After"),
    })
    response.raise_for_status()
    return response.json()

m4 = M4Session(BASE)
try:
    m4.handshake(post_json)
except Exception as exc:
    report(f"handshake=FAILED http={meta.get('status', 'no-response')} cf_ray={meta.get('cf_ray') or 'none'} retry_after={meta.get('retry_after') or 'none'} error={type(exc).__name__}")
    sys.exit(2)
report(f"handshake=OK http={meta.get('status', 'unknown')}")
url = BASE + "/livescores"
try:
    response = http.get(url, headers=m4.headers_for("GET", url), timeout=20)
except requests.RequestException as exc:
    report(f"livescores=FAILED error={type(exc).__name__}")
    sys.exit(2)
report(f"livescores_http={response.status_code} cf_ray={response.headers.get('CF-Ray') or 'none'} retry_after={response.headers.get('Retry-After') or 'none'}")
if not response.ok:
    report("fixture_count=unavailable (HTTP request was not successful)")
    sys.exit(2)
try:
    payload = m4.decrypt(response.json())
except Exception as exc:
    report(f"decode=FAILED error={type(exc).__name__}")
    sys.exit(2)
root = payload.get("data") if isinstance(payload, dict) and "data" in payload else payload
if isinstance(root, str):
    try:
        root = json.loads(root)
    except ValueError:
        report("response_shape=unrecognized-text fixture_count=unavailable")
        sys.exit(2)
rows: list[dict] = []
category_count = 0
if isinstance(root, dict) and isinstance(root.get("sortedCategorizedFixtures"), list):
    categories = root["sortedCategorizedFixtures"]
    category_count = len(categories)
    for category in categories:
        if isinstance(category, dict) and isinstance(category.get("fixtures"), list):
            rows.extend(row for row in category["fixtures"] if isinstance(row, dict))
elif isinstance(root, list):
    rows = [row for row in root if isinstance(row, dict)]
else:
    keys = sorted(root.keys())[:12] if isinstance(root, dict) else []
    report(f"response_shape=unexpected root_type={type(root).__name__} keys={','.join(keys) or 'none'} fixture_count=unavailable")
    sys.exit(2)
report(f"fixture_count={len(rows)} categories={category_count}")
for row in rows[:5]:
    home = str(row.get("localTeamName") or "?").replace("\n", " ").replace("\r", " ")[:70]
    away = str(row.get("visitorTeamName") or "?").replace("\n", " ").replace("\r", " ")[:70]
    fid = str(row.get("fixtureId") or row.get("fixture_id") or "?")[:30]
    report(f"fixture id={fid} match={home} x {away}")
