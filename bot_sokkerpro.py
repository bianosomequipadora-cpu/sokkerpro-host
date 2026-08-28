import os, sys, base64, requests as req
def analisar_e_disparar(game, stats, p, m, sh, sa, odd_h, odd_a, sent_vistos):
    try:
        oh = float(odd_h) if odd_h else 3.0
        oa = float(odd_a) if odd_a else 3.0
        fav_side = 'h' if oh < oa else 'a'
    except:
        fav_side = 'h'
    fav_gols = sh if fav_side == 'h' else sa
    adv_gols = sa if fav_side == 'h' else sh
    red_fav = stats.get(f'red_cards_{fav_side}', 0)
    if p == 1 and 15 <= m <= 27:
        if sh == 0 and sa == 0 and (red_fav == 0):
            return ('HT', 'Over 0.5 Gols HT')
    if p == 2 and 55 <= m <= 75:
        if fav_gols <= adv_gols and adv_gols - fav_gols <= 1 and (red_fav == 0):
            total_gols = sh + sa
            return ('OVERGOAL', f'Mais de {total_gols + 0.5} Gols')
    if p == 2 and 55 <= m <= 75:
        if sh + sa == 1 and (fav_gols == 0 and adv_gols == 1) and (red_fav == 0):
            return ('BTTS', 'Ambas Marcam')
    if p == 2 and 55 <= m <= 75:
        if sh + sa == 1 and (fav_gols == 0 and adv_gols == 1) and (red_fav == 0):
            return ('OFT', 'Mais de 1.5 Gols Partida')
    if p == 1 and 28 <= m <= 38:
        if fav_gols <= adv_gols and adv_gols - fav_gols <= 1 and (red_fav == 0):
            return ('CORNER_HT', 'Escanteio Limite HT')
    if p == 2 and 78 <= m <= 88:
        if fav_gols <= adv_gols and adv_gols - fav_gols <= 1 and (red_fav == 0):
            return ('CORNER_FT', 'Escanteio Limite FT')
    return ((None, None, None), None)

def gerar_layout_relatorio(greens, reds, data_str, refunds=0):
    sep = '━━━━━━━━━━━━━━━━━━━━━━'
    total = greens + reds
    taxa = greens / total * 100 if total > 0 else 0.0
    return f'{sep}\n<b>📊 RELATÓRIO DIÁRIO — {data_str}</b>\n{sep}\n🟢 GREEN: <b>{greens}</b>\n🔴 RED: <b>{reds}</b>\n🔵REEMBOLSO: <b>{refunds}</b>\n📈 TOTAL DE ENTRADAS: <b>{total}</b>\n🎯 ASSERTIVIDADE: <b>{taxa:.1f}%</b>\n{sep}\n⚠️👆Resultados do dia👆⚠️'

def gerar_layout_relatorio_mensal(greens, reds, mes_nome, dias_ativos, refunds=0):
    sep = '━' * 22
    total = greens + reds + refunds
    avaliados = greens + reds
    taxa = greens / avaliados * 100 if avaliados > 0 else 0.0
    msg = f'{sep}\n'
    msg += f'<b>📊 RELATÓRIO MENSAL — {mes_nome}</b>\n'
    msg += f'{sep}\n'
    msg += f'🟢 GREEN: <b>{greens}</b>\n'
    msg += f'🔴 RED: <b>{reds}</b>\n'
    msg += f'🔵REEMBOLSO: <b>{refunds}</b>\n'
    msg += f'📈 TOTAL DE ENTRADAS: <b>{total}</b>\n'
    msg += f'🎯 ASSERTIVIDADE: <b>{taxa:.1f}%</b>\n'
    msg += f'{sep}\n'
    msg += f'📅 Dias com entradas: <b>{dias_ativos}</b>\n'
    msg += '⚠️👆Resultados do mês👆⚠️'
    return msg

def gerar_layout_radar(jogos_ao_vivo, jogos_na_janela):
    sep = '━━━━━━━━━━━━━━━━━━━━━━'
    texto_jan = ''
    for j in jogos_na_janela:
        h = j.get('home', '') or getattr(j, 'home', '')
        a = j.get('away', '') or getattr(j, 'away', '')
        m = j.get('minuto', '') or getattr(j, 'minuto', '')
        sh = j.get('sh', 0) or getattr(j, 'sh', 0)
        sa = j.get('sa', 0) or getattr(j, 'sa', 0)
        liga = j.get('liga', '') or getattr(j, 'liga', '')
        texto_jan += f"🎯 <b>{h} x {a}</b> | {m}' | {sh}x{sa} | {liga}\n"
    if not texto_jan:
        texto_jan = 'Nenhum jogo na janela no momento.'
    corpo = f'{sep}\n📡 RADAR — JOGOS AO VIVO\n{sep}\n🔴 Jogos na Janela:\n{texto_jan}{sep}\n🟢 Ao Vivo: <b>{len(jogos_ao_vivo)}</b>'
    return corpo
import requests
import os, json, requests, time
from urllib import request, error
import base64
from datetime import datetime, timezone, timedelta
import hashlib, re, unicodedata

def norm_nome_time(nome):
    """Remove acentos, expande abreviações e limpa prefixos/sufixos de nome de time."""
    n = unicodedata.normalize('NFKD', nome).encode('ascii', 'ignore').decode().lower().strip()
    n = re.sub('\\b(msk|hnk|nk|fk|sk|fc|ac|ec|se|cf)\\b', '', n)
    n = n.replace('u.', 'universitatea').replace('dyn.', 'dynamo').replace('s.n.', '').replace('c.s.', '')
    n = re.sub('\\b(rj|sp|mg|rs|pr|sc|ba|pe|ce|go|mt|ms|df|es|rn|pb|al|se|pi|ma|pa|am|ro|rr|ap|to|fr|ac|ec|se|cf)\\b', '', n)
    return re.sub('\\s+', ' ', n).strip()
CONFIG_MERCADOS = {}

def carregar_config_github():
    """Carrega config.json do GitHub e retorna dict de mercados com critérios."""
    try:
        url = f'https://api.github.com/repos/{GITHUB_REPO}/contents/config.json'
        req = request.Request(url, headers={'Authorization': f'Bearer {GITHUB_TOKEN}', 'Accept': 'application/vnd.github+json'})
        resp = request.urlopen(req, timeout=10)
        raw = json.loads(resp.read())['content']
        cfg = json.loads(base64.b64decode(raw).decode())
        return cfg.get('mercados', {})
    except:
        print('[CONFIG] Erro ao carregar config.json do GitHub, usando valores padrão')
        return {}
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SENT_FILE = os.path.join(BASE_DIR, 'sent_live_signals.json')
SINAIS_FILE = os.path.join(BASE_DIR, 'sinais_pendentes.json')
RESULTADO_FILE = os.path.join(BASE_DIR, 'resultados.json')
PERFORMANCE_FILE = os.path.join(BASE_DIR, 'performance.json')
LAST_UPDATE_FILE = os.path.join(BASE_DIR, 'last_update.json')
BRT = timezone(timedelta(hours=-3))
TELEGRAM_TOKEN = os.getenv('TG_TOKEN', '')
TG_TOKEN = TELEGRAM_TOKEN
CHAT_IDS = [int(id) for id in os.environ.get('TG_GROUP_ID', '').split(',') if id.strip()]
CHAT_ID = CHAT_IDS[0] if CHAT_IDS else ''
SOKKERPRO_URL = 'https://r.jina.ai/http://m2.sokkerpro.com/livescores'
SOKKERPRO_URL = 'https://r.jina.ai/http://m2.sokkerpro.com/livescores'
SOKKERPRO_URL = 'https://r.jina.ai/http://m2.sokkerpro.com/livescores'
SOKKERPRO_URL = 'https://r.jina.ai/http://m2.sokkerpro.com/livescores'
SOKKERPRO_URL = 'https://r.jina.ai/http://m2.sokkerpro.com/livescores'
SOKKERPRO_URL = 'https://r.jina.ai/http://m2.sokkerpro.com/livescores'

def send_telegram(msg_data, reply_to=None, marca=None, home='', away='', odd_b365_val=None, odd_bano_val=None):
    """Envia mensagem formatada com botões inline."""
    if isinstance(msg_data, tuple):
        text, keyboard = msg_data
    else:
        text = msg_data
        keyboard = None
    url_send = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    last_mid = None
    for chat_id in CHAT_IDS:
        payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML', 'disable_web_page_preview': False}
        if reply_to:
            payload['reply_to_message_id'] = reply_to
        if keyboard:
            payload['reply_markup'] = json.dumps(keyboard)
        try:
            r = requests.post(url_send, json=payload, timeout=10)
            res = r.json()
            if res.get('ok'):
                last_mid = res.get('result', {}).get('message_id')
        except:
            pass
    return last_mid
GITHUB_TOKEN = os.environ.get('GH_PAT', '')
GITHUB_REPO = os.environ.get('GITHUB_REPOSITORY', 'cleubianodasilva-png/boot-ia-inteligente-bot')
SENT_API_PATH = 'sent_live_signals.json'
RESULTADO_API_PATH = 'resultados.json'
PERFORMANCE_API_PATH = 'performance.json'

def _git_commit_push(msg):
    """Faz git add, commit e push de todos os arquivos de estado."""
    import subprocess
    try:
        subprocess.run(['git', 'config', 'user.name', 'bot-sokkerpro'], capture_output=True, timeout=10)
        subprocess.run(['git', 'config', 'user.email', 'bot@sokkerpro.com'], capture_output=True, timeout=10)
        subprocess.run(['git', 'add', '-A', '--', '*.json'], capture_output=True, timeout=10)
        r = subprocess.run(['git', 'diff', '--cached', '--quiet'], capture_output=True, timeout=10)
        if r.returncode == 0:
            print(f'[GIT] Nada a commitar, skip')
            return
        subprocess.run(['git', 'commit', '-m', msg], capture_output=True, timeout=10)
        subprocess.run(['git', 'push', f'https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git'], capture_output=True, timeout=30)
        print(f'[GIT] Commit+push OK: {msg}')
    except Exception as e:
        print(f'[GIT] Erro no commit+push: {e}')

def load_sent():
    """Carrega sent do GitHub API (sempre a versão mais recente do repositório)."""
    if GITHUB_TOKEN and GITHUB_REPO:
        try:
            url = f'https://api.github.com/repos/{GITHUB_REPO}/contents/sent_live_signals.json'
            req = request.Request(url, headers={'Authorization': f'Bearer {GITHUB_TOKEN}', 'Accept': 'application/vnd.github+json'})
            resp = request.urlopen(req, timeout=10)
            raw = json.loads(resp.read())['content']
            sent = set(json.loads(base64.b64decode(raw).decode()))
            hoje = datetime.now(BRT).strftime('%Y%m%d')
            ontem = (datetime.now(BRT) - timedelta(days=1)).strftime('%Y%m%d')
            sent = {k for k in sent if hoje in k or ontem in k}
            with open(SENT_FILE, 'w') as f:
                json.dump(list(sent), f)
            print(f'[SENT] Carregado do GitHub API: {len(sent)} chaves')
            return sent
        except error.HTTPError as e:
            if e.code == 404:
                print(f'[SENT] sent_live_signals.json ainda não existe no repositório')
            else:
                print(f'[SENT] Erro HTTP {e.code} ao buscar do GitHub')
        except Exception as e:
            print(f'[SENT] Erro ao buscar do GitHub API: {e}')
    if os.path.exists(SENT_FILE):
        try:
            with open(SENT_FILE, 'r') as f:
                sent = set(json.load(f))
            hoje = datetime.now(BRT).strftime('%Y%m%d')
            ontem = (datetime.now(BRT) - timedelta(days=1)).strftime('%Y%m%d')
            sent = {k for k in sent if hoje in k or ontem in k}
            print(f'[SENT] Carregado do arquivo local (fallback): {len(sent)} chaves')
            return sent
        except Exception as e:
            print(f'[SENT] Erro load local: {e}')
    return set()

def _save_json_api(path, data, msg='state: atualiza [skip ci]'):
    """Salva qualquer JSON no GitHub via API PUT direta (instantânea e síncrona)."""
    try:
        url = f'https://api.github.com/repos/{GITHUB_REPO}/contents/{path}'
        b64 = base64.b64encode(json.dumps(data).encode()).decode()
        req = request.Request(url, headers={'Authorization': f'Bearer {GITHUB_TOKEN}', 'Accept': 'application/vnd.github+json'})
        sha = None
        try:
            resp = request.urlopen(req, timeout=10)
            sha = json.loads(resp.read())['sha']
        except error.HTTPError as e:
            if e.code != 404:
                raise
        payload = {'message': msg, 'content': b64}
        if sha:
            payload['sha'] = sha
        req = request.Request(url, data=json.dumps(payload).encode(), headers={'Authorization': f'Bearer {GITHUB_TOKEN}', 'Content-Type': 'application/json'}, method='PUT')
        request.urlopen(req, timeout=15)
        print(f'[API-PUT] Salvo {path} via API')
        return True
    except Exception as e:
        print(f'[API-PUT] Erro {path}: {e}')
        return False

def _claim_report_slot(chave):
    """Tenta reservar um relatório uma única vez usando PUT condicional no GitHub."""
    if not (GITHUB_TOKEN and GITHUB_REPO):
        return False
    caminho = 'relatorios_enviados.json'
    url = f'https://api.github.com/repos/{GITHUB_REPO}/contents/{caminho}'
    headers = {'Authorization': f'Bearer {GITHUB_TOKEN}', 'Accept': 'application/vnd.github+json'}
    try:
        sha = None
        dados = []
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            item = resp.json()
            sha = item.get('sha')
            dados = json.loads(base64.b64decode(item.get('content', '')).decode())
        elif resp.status_code != 404:
            return False
        if chave in dados:
            return False
        dados.append(chave)
        payload = {'message': f'state: reserva relatório {chave} [skip ci]', 'content': base64.b64encode(json.dumps(dados).encode()).decode()}
        if sha:
            payload['sha'] = sha
        resposta = requests.put(url, headers={**headers, 'Content-Type': 'application/json'}, json=payload, timeout=15)
        return resposta.status_code in (200, 201)
    except Exception as e:
        print(f'[RELATORIO] Não foi possível reservar {chave}: {e}')
        return False

def _save_sent_api(sent):
    """Salva sent no GitHub via API PUT direta (instantânea e síncrona)."""
    try:
        url = f'https://api.github.com/repos/{GITHUB_REPO}/contents/{SENT_API_PATH}'
        data = json.dumps(list(sent))
        b64 = base64.b64encode(data.encode()).decode()
        req = request.Request(url, headers={'Authorization': f'Bearer {GITHUB_TOKEN}', 'Accept': 'application/vnd.github+json'})
        sha = None
        try:
            resp = request.urlopen(req, timeout=10)
            sha = json.loads(resp.read())['sha']
        except error.HTTPError as e:
            if e.code != 404:
                raise
        payload = {'message': 'state: atualiza sent [skip ci]', 'content': b64}
        if sha:
            payload['sha'] = sha
        req = request.Request(url, data=json.dumps(payload).encode(), headers={'Authorization': f'Bearer {GITHUB_TOKEN}', 'Content-Type': 'application/json'}, method='PUT')
        request.urlopen(req, timeout=15)
        print(f'[SENT-API] Salvo no GitHub: {len(sent)} chaves')
        return True
    except Exception as e:
        print(f'[SENT-API] Erro: {e}')
        return False

def save_sent(sent):
    """Salva sent localmente E no GitHub via API PUT direta (síncrono e instantâneo)."""
    with open(SENT_FILE, 'w') as f:
        json.dump(list(sent), f)
    if GITHUB_TOKEN and GITHUB_REPO:
        if not _save_sent_api(sent):
            print('[SENT] Fallback para git commit+push')
            _git_commit_push('state: atualiza sent [skip ci]')

def _load_sinais_github():
    """Carrega sinais_pendentes.json do GitHub API (fonte da verdade) com fallback local."""
    if GITHUB_TOKEN and GITHUB_REPO:
        try:
            url = f'https://api.github.com/repos/{GITHUB_REPO}/contents/sinais_pendentes.json'
            r = requests.get(url, headers={'Authorization': f'Bearer {GITHUB_TOKEN}', 'Accept': 'application/vnd.github+json'}, timeout=8)
            if r.status_code == 200:
                return json.loads(base64.b64decode(r.json()['content']).decode())
        except Exception as e:
            print(f'[SINAIS] Erro load GitHub: {e}')
    if os.path.exists(SINAIS_FILE):
        try:
            with open(SINAIS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return []

def _save_sinais_github(sinais):
    """Salva sinais_pendentes.json localmente + GitHub API PUT (síncrono)."""
    with open(SINAIS_FILE, 'w') as f:
        json.dump(sinais, f)
    if GITHUB_TOKEN and GITHUB_REPO:
        _save_json_api('sinais_pendentes.json', sinais, 'state: atualiza sinais_pendentes [skip ci]')
    print(f'[SINAIS] Salvo localmente: {len(sinais)} pendentes')
ENTRADAS_FILE = os.path.join(BASE_DIR, 'entradas.json')
ENTRADAS_API_PATH = 'entradas.json'

def _load_entradas():
    try:
        if os.path.exists(ENTRADAS_FILE):
            with open(ENTRADAS_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f'[ENTRADAS] Erro leitura: {e}')
    return []

def _save_entradas(registros):
    with open(ENTRADAS_FILE, 'w') as f:
        json.dump(registros, f, ensure_ascii=False, indent=2)
    if GITHUB_TOKEN and GITHUB_REPO:
        _save_json_api(ENTRADAS_API_PATH, registros, 'state: atualiza entradas [skip ci]')

def atualizar_entrada_historico(sinal, resultado):
    registros = _load_entradas()
    message_id = sinal.get('message_id')
    fid = str(sinal.get('fixture_id', ''))
    mercado = sinal.get('mercado')
    atualizado = False
    # Primeiro identifica a entrada exata pela mensagem enviada ao Telegram.
    if message_id:
        for r in registros:
            if str(r.get('message_id', '')) == str(message_id):
                r['resultado'] = resultado
                atualizado = True
                break
    # Fallback somente para sinais antigos sem message_id: prioriza o pendente mais recente.
    if not atualizado:
        for r in reversed(registros):
            if str(r.get('fixture_id', '')) == fid and r.get('mercado') == mercado and r.get('resultado') == 'pendente':
                r['resultado'] = resultado
                atualizado = True
                break
    if not atualizado:
        for r in reversed(registros):
            if str(r.get('fixture_id', '')) == fid and r.get('mercado') == mercado:
                r['resultado'] = resultado
                break
    _save_entradas(registros)

def registrar_sinal(fid, mercado, home, away, message_id, extra_val=None, tipo=None, entry_sh=None, entry_sa=None, odd_b365=None, odd_bano=None):
    sinais = _load_sinais_github()
    sinais.append({'fixture_id': fid, 'mercado': mercado, 'home': home, 'away': away, 'message_id': message_id, 'extra_val': extra_val, 'tipo': tipo, 'entry_sh': entry_sh, 'entry_sa': entry_sa, 'entry_total': (entry_sh + entry_sa) if entry_sh is not None and entry_sa is not None else None, 'odd_b365': odd_b365, 'odd_bano': odd_bano, 'timestamp': datetime.now(BRT).isoformat()})
    _save_sinais_github(sinais)
    historico = _load_entradas()
    historico.append({'fixture_id': fid, 'mercado': mercado, 'tipo': tipo, 'home': home, 'away': away, 'message_id': message_id, 'extra_val': extra_val, 'entry_sh': entry_sh, 'entry_sa': entry_sa, 'entry_total': (entry_sh + entry_sa) if entry_sh is not None and entry_sa is not None else None, 'odd_b365': odd_b365, 'odd_bano': odd_bano, 'timestamp': datetime.now(BRT).isoformat(), 'resultado': 'pendente'})
    _save_entradas(historico)

def _load_resultados_github():
    """Carrega resultados.json do GitHub API (fonte da verdade) com fallback local."""
    if GITHUB_TOKEN and GITHUB_REPO:
        try:
            url = f'https://api.github.com/repos/{GITHUB_REPO}/contents/resultados.json'
            r = requests.get(url, headers={'Authorization': f'Bearer {GITHUB_TOKEN}', 'Accept': 'application/vnd.github+json'}, timeout=8)
            if r.status_code == 200:
                return json.loads(base64.b64decode(r.json()['content']).decode())
        except Exception as e:
            print(f'[RESULTADO] Erro load GitHub: {e}')
    if os.path.exists(RESULTADO_FILE):
        try:
            with open(RESULTADO_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return []

def _save_resultados_github(registros):
    """Salva resultados.json localmente + GitHub API PUT (síncrono)."""
    with open(RESULTADO_FILE, 'w') as f:
        json.dump(registros, f, indent=2)
    if GITHUB_TOKEN and GITHUB_REPO:
        _save_json_api('resultados.json', registros, 'state: atualiza resultados [skip ci]')
    print(f'[RESULTADO] Salvo localmente: {len(registros)} registros')

def _claim_auditoria_slot(chave):
    """Reserva uma auditoria única por fixture e mercado via PUT condicional."""
    if not (GITHUB_TOKEN and GITHUB_REPO):
        return False
    caminho = 'auditorias_confirmadas.json'
    url = f'https://api.github.com/repos/{GITHUB_REPO}/contents/{caminho}'
    headers = {'Authorization': f'Bearer {GITHUB_TOKEN}', 'Accept': 'application/vnd.github+json'}
    try:
        sha = None
        chaves = []
        resposta = requests.get(url, headers=headers, timeout=10)
        if resposta.status_code == 200:
            item = resposta.json()
            sha = item.get('sha')
            chaves = json.loads(base64.b64decode(item.get('content', '')).decode())
        elif resposta.status_code != 404:
            return False
        if chave in chaves:
            return False
        chaves.append(chave)
        payload = {'message': f'state: reserva auditoria {chave} [skip ci]', 'content': base64.b64encode(json.dumps(chaves).encode()).decode()}
        if sha:
            payload['sha'] = sha
        r = requests.put(url, headers={**headers, 'Content-Type': 'application/json'}, json=payload, timeout=15)
        return r.status_code in (200, 201)
    except Exception as e:
        print(f'[AUDITORIA] Falha ao reservar {chave}: {e}')
        return False

def salvar_resultado(resultado, mercado=None, fixture_id=None):
    hoje = datetime.now(BRT).strftime('%Y-%m-%d')
    registros = _load_resultados_github()
    registros.append({'data': hoje, 'resultado': resultado, 'mercado': mercado, 'fixture_id': fixture_id, 'timestamp': datetime.now(BRT).isoformat()})
    _save_resultados_github(registros)

def _agregar_resultados(filtro_data=None):
    """Agrega resultados usando somente os códigos do MAPA_MERCADO vigente.

    ``filtro_data`` recebe uma função que retorna True para os registros a
    considerar; None significa todas as datas disponíveis. Esta é a fonte
    compartilhada pelos relatórios mensal e geral, evitando incluir mercados
    históricos que já não estão no painel ativo.
    """
    dados = {cod: {'nome': nome, 'green': 0, 'red': 0, 'refund': 0, 'total': 0}
             for cod, nome in MAPA_MERCADO.items()}
    dias_ativos = set()
    for registro in _load_resultados_github():
        if filtro_data is not None and not filtro_data(registro):
            continue
        resultado = str(registro.get('resultado', '')).strip().lower()
        if resultado not in ('green', 'red', 'refund', 'reembolso'):
            continue
        mercado = registro.get('mercado')
        if mercado not in dados:
            continue
        data_reg = str(registro.get('data', ''))
        if data_reg:
            dias_ativos.add(data_reg)
        campo = 'refund' if resultado in ('refund', 'reembolso') else resultado
        dados[mercado][campo] += 1
    for grupo in dados.values():
        grupo['total'] = grupo['green'] + grupo['red'] + grupo['refund']
        avaliados = grupo['green'] + grupo['red']
        grupo['pct'] = grupo['green'] / avaliados * 100 if avaliados > 0 else 0.0
    return dados, dias_ativos

def _agregar_resultados_mensais(mes_str):
    """Agrega resultados do mês usando o MAPA_MERCADO vigente."""
    return _agregar_resultados(
        lambda registro: str(registro.get('data', '')).startswith(mes_str)
    )

def _agregar_resultados_gerais():
    """Agrega resultados de todas as datas disponíveis no arquivo histórico."""
    return _agregar_resultados()

def get_relatorio_mensal():
    mes_str = datetime.now(BRT).strftime('%Y-%m')
    dados, dias_ativos = _agregar_resultados_mensais(mes_str)
    greens = sum(grupo['green'] for grupo in dados.values())
    reds = sum(grupo['red'] for grupo in dados.values())
    refunds = sum(grupo['refund'] for grupo in dados.values())
    return (greens, reds, len(dias_ativos), refunds)

def get_relatorio_hoje():
    hoje = datetime.now(BRT).strftime('%Y-%m-%d')
    greens, reds, refunds = (0, 0, 0)
    registros = _load_resultados_github()
    for r in registros:
        if r.get('data') == hoje:
            if r.get('resultado') == 'green':
                greens += 1
            elif r.get('resultado') == 'red':
                reds += 1
            elif r.get('resultado') == 'refund':
                refunds += 1
    return (greens, reds, refunds)

def enviar_relatorio_mensal():
    hoje = datetime.now(BRT)
    meses_pt = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
    mes_nome = f'{meses_pt[hoje.month - 1]}/{hoje.year}'
    greens, reds, dias_ativos, refunds = get_relatorio_mensal()
    msg = gerar_layout_relatorio_mensal(greens, reds, mes_nome, dias_ativos, refunds)
    return msg

def enviar_relatorio_diario():
    hoje_key = f"relatorio_{datetime.now(BRT).strftime('%Y-%m-%d')}"
    hoje = datetime.now(BRT).strftime('%d/%m/%Y')
    greens, reds, refunds = get_relatorio_hoje()
    msg = gerar_layout_relatorio(greens, reds, hoje, refunds)
    confirmed_ids = set()
    sent = load_sent()
    if send_telegram(msg):
        sent.add(hoje_key)
        save_sent(sent)
        print(f'[Relatório] Enviado ({hoje_key})')

def _gerar_mapa_mercados():
    """Gera MAPA_MERCADO dinamicamente a partir do config.json + fallback fixo."""
    try:
        mercados = carregar_config_github()
        m = {}
        for cod, info in mercados.items():
            nome = info.get('nome', cod)
            m[cod] = nome
        if m:
            return m
    except:
        pass
    return {'HT': '⚽️🔥OVER GOL INTERVALO🔥⚽️', 'BTTS': '⚽🔥AMBAS MARCAM🔥⚽️', 'OFT': '⚽🔥OVER 1.5 GOLS FT🔥⚽️', 'OVERGOAL': '⚽🔥OVER GOL PARTIDA🔥⚽️', 'CORNER_HT': '🚩🔥ESCANTEIO ÁSIAT/LMT HT🔥🚩', 'CORNER_FT': '🚩🔥ESCANTEIO ÁSIAT/LMT FT🔥🚩'}
MAPA_MERCADO = _gerar_mapa_mercados()

def _load_performance_github():
    """Carrega performance.json do GitHub API (fonte da verdade) com fallback local."""
    if GITHUB_TOKEN and GITHUB_REPO:
        try:
            url = f'https://api.github.com/repos/{GITHUB_REPO}/contents/performance.json'
            r = requests.get(url, headers={'Authorization': f'Bearer {GITHUB_TOKEN}', 'Accept': 'application/vnd.github+json'}, timeout=8)
            if r.status_code == 200:
                return json.loads(base64.b64decode(r.json()['content']).decode())
        except Exception as e:
            print(f'[PERF] Erro load GitHub: {e}')
    if os.path.exists(PERFORMANCE_FILE):
        try:
            with open(PERFORMANCE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {}

def _save_performance_github(perf):
    """Salva performance.json localmente + GitHub API PUT (síncrono)."""
    with open(PERFORMANCE_FILE, 'w') as f:
        json.dump(perf, f, indent=2)
    if GITHUB_TOKEN and GITHUB_REPO:
        _save_json_api('performance.json', perf, 'state: atualiza performance [skip ci]')
    print(f"[PERFORMANCE] Salvo localmente: {sum((v.get('total', 0) for v in perf.values()))} registros")

def registrar_performance(mercado, resultado):
    """Registra resultado de um mercado específico no performance.json."""
    perf = _load_performance_github()
    if mercado not in perf:
        perf[mercado] = {'green': 0, 'red': 0, 'refund': 0, 'total': 0}
    if resultado == 'refund':
        perf[mercado]['refund'] = perf[mercado].get('refund', 0) + 1
        perf[mercado]['total'] += 1
    else:
        perf[mercado]['total'] += 1
        if resultado == 'green':
            perf[mercado]['green'] += 1
        else:
            perf[mercado]['red'] += 1
    _save_performance_github(perf)
    total = perf[mercado]['total']
    greens = perf[mercado]['green']
    pct = greens / total * 100 if total > 0 else 0
    print(f'[PERFORMANCE] {MAPA_MERCADO.get(mercado, mercado)}: {resultado} ({greens}/{total} = {pct:.1f}%)')

def get_performance():
    """Retorna a performance acumulada geral usando todas as entradas reais."""
    registros = _load_entradas()
    resultado = {cod: {'nome': nome, 'green': 0, 'red': 0, 'refund': 0, 'total': 0} for cod, nome in MAPA_MERCADO.items()}
    for registro in registros:
        mercado = str(registro.get('mercado', ''))
        if mercado not in resultado:
            # Registros de mercados antigos/removidos não entram no relatório atual.
            # Assim, aliases e IDs custom antigos não duplicam o total geral.
            continue
        status = str(registro.get('resultado', '')).lower()
        if status == 'green':
            resultado[mercado]['green'] += 1
        elif status == 'red':
            resultado[mercado]['red'] += 1
        elif status in ('refund', 'reembolso'):
            resultado[mercado]['refund'] += 1
    for info in resultado.values():
        greens = info['green']
        reds = info['red']
        refunds = info['refund']
        info['total'] = greens + reds + refunds
        avaliados = greens + reds
        info['pct'] = greens / avaliados * 100 if avaliados > 0 else 0
        info['valido'] = avaliados >= 1000 and info['pct'] >= 70
    return resultado

def gerar_layout_performance():
    """Gera layout do relatório de performance por mercado."""
    dados = get_performance()
    sep = '━' * 22
    blocos = []
    for cod, info in dados.items():
        nome = info['nome']
        g = info['green']
        r = info['red']
        f = info['refund']
        t = info['total']
        pct = info['pct']
        blocos.append(f'<b>{nome}</b>\n   ⏳ Total: {t} | 🟢 {g} | 🔴 {r} | 🔵 {f}\n   🎯 Acerto: {pct:.1f}%')
    total_g = sum((d['green'] for d in dados.values()))
    total_r = sum((d['red'] for d in dados.values()))
    total_f = sum((d['refund'] for d in dados.values()))
    total_t = total_g + total_r + total_f
    total_avaliados = total_g + total_r
    total_pct = total_g / total_avaliados * 100 if total_avaliados > 0 else 0
    msg = f"{sep}\n📊<b>RELATÓRIO DE PERFORMANCE</b>📊\n{sep}\n{f'{chr(10)}{sep}{chr(10)}'.join(blocos)}{chr(10)}{sep}\n📌 <b>TOTAL GERAL: {total_t} Sinais</b>\n      | 🟢 {total_g} | 🔴 {total_r} | 🔵 {total_f} | {total_pct:.1f}%|\n{sep}\nRegras de Validação:\n✅ Mínimo 1000 entradas + ≥70%\n{sep}"
    return msg

def enviar_relatorio_performance():
    """Gera o relatório de performance. Retorna o texto da mensagem (sem enviar)."""
    return gerar_layout_performance()

def gerar_layout_relatorio_geral():
    """Gera o acumulado geral no mesmo formato resumido do relatório mensal."""
    dados, dias_ativos = _agregar_resultados_gerais()
    sep = '━━━━━━━━━━━━━━━━━━━━━━'
    total_g = sum(info['green'] for info in dados.values())
    total_r = sum(info['red'] for info in dados.values())
    total_f = sum(info['refund'] for info in dados.values())
    total_t = total_g + total_r + total_f
    avaliados = total_g + total_r
    total_pct = total_g / avaliados * 100 if avaliados > 0 else 0.0
    return (
        f"{sep}\n📊<b>RELATÓRIO GERAL</b>📊\n{sep}\n"
        f"🟢 GREEN: {total_g}\n"
        f"🔴 RED: {total_r}\n"
        f"🔵 REEMBOLSO: {total_f}\n"
        f"📈 TOTAL GERAL DE ENTRADAS: {total_t}\n"
        f"🎯 ASSERTIVIDADE: {total_pct:.1f}%\n"
        f"{sep}\n📅 Dias com entradas: {len(dias_ativos)}\n{sep}"
    )

def enviar_relatorio_geral():
    """Gera o relatório geral acumulado sem enviá-lo diretamente."""
    return gerar_layout_relatorio_geral()

def get_performance_hoje():
    """Retorna performance por mercado somente dos resultados do dia no fuso BRT."""
    hoje = datetime.now(BRT).strftime('%Y-%m-%d')
    registros = _load_resultados_github()
    perf = {}
    for cod, nome in MAPA_MERCADO.items():
        perf[cod] = {'nome': nome, 'green': 0, 'red': 0, 'refund': 0, 'total': 0}
    for r in registros:
        if r.get('data') != hoje:
            continue
        mercado = r.get('mercado', '')
        resultado = r.get('resultado', '')
        if mercado not in perf or not resultado:
            continue
        perf[mercado]['total'] += 1
        if resultado == 'green':
            perf[mercado]['green'] += 1
        elif resultado == 'refund':
            perf[mercado]['refund'] += 1
        else:
            perf[mercado]['red'] += 1
    for cod, info in perf.items():
        g = info['green']
        r = info['red']
        f = info['refund']
        info['total'] = g + r + f
        info['pct'] = g / (g + r) * 100 if (g + r) > 0 else 0
    return perf

def gerar_layout_mercados_hoje():
    """Gera desempenho por mercado somente para o dia atual."""
    dados = get_performance_hoje()
    sep = '━' * 22
    blocos = []
    for cod, info in dados.items():
        blocos.append(f"<b>{info['nome']}</b>\n   Total: {info['total']} | 🟢 {info['green']} | 🔴 {info['red']} | 🔵 {info['refund']}\n   🎯 Acerto: {info['pct']:.1f}%")
    total_g = sum(d['green'] for d in dados.values())
    total_r = sum(d['red'] for d in dados.values())
    total_f = sum(d['refund'] for d in dados.values())
    total_t = total_g + total_r + total_f
    avaliados = total_g + total_r
    total_pct = total_g / avaliados * 100 if avaliados > 0 else 0
    corpo = (f"{chr(10)}{sep}{chr(10)}".join(blocos) if blocos else 'Nenhum resultado registrado hoje.')
    data_hoje = datetime.now(BRT).strftime('%d/%m/%Y')
    return f"{sep}\n📊<b>MERCADOS — {data_hoje}</b>📊\n{sep}\n{corpo}\n{sep}\n📌 <b>TOTAL DO DIA: {total_t} Sinais</b>\n      | 🟢 {total_g} | 🔴 {total_r} | 🔵 {total_f} | {total_pct:.1f}%|\n{sep}"

def get_performance_mensal():
    """Retorna performance por mercado no mesmo recorte do relatório mensal."""
    mes_atual = datetime.now(BRT).strftime('%Y-%m')
    dados, _ = _agregar_resultados_mensais(mes_atual)
    return dados

def get_performance_24h():
    """Retorna performance por mercado nas últimas 24h a partir dos resultados salvos."""
    registros = _load_resultados_github()
    agora = datetime.now(BRT)
    corte = agora - timedelta(hours=24)
    perf = {}
    for cod, nome in MAPA_MERCADO.items():
        perf[cod] = {'nome': nome, 'green': 0, 'red': 0, 'refund': 0, 'total': 0}
    for r in registros:
        ts_str = r.get('timestamp', '')
        mercado = r.get('mercado', '')
        resultado = r.get('resultado', '')
        if not ts_str or not mercado or (not resultado):
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
        perf[mercado]['total'] += 1
        if resultado == 'green':
            perf[mercado]['green'] += 1
        elif resultado == 'refund':
            perf[mercado]['refund'] += 1
        else:
            perf[mercado]['red'] += 1
    for cod, info in perf.items():
        g = info['green']
        r = info['red']
        f = info['refund']
        info['total'] = g + r + f
        info['pct'] = g / (g + r) * 100 if (g + r) > 0 else 0
    return perf

def gerar_layout_mercados24h():
    """Gera layout do relatório de performance por mercado nas últimas 24h."""
    dados = get_performance_24h()
    sep = '━' * 22
    blocos = []
    for cod, info in dados.items():
        nome = info['nome']
        g = info['green']
        r = info['red']
        f = info['refund']
        t = info['total']
        pct = info['pct']
        blocos.append(f'<b>{nome}</b>\n   Total: {t} | 🟢 {g} | 🔴 {r} | 🔵 {f}\n   🎯 Acerto: {pct:.1f}%')
    total_g = sum((d['green'] for d in dados.values()))
    total_r = sum((d['red'] for d in dados.values()))
    total_f = sum((d['refund'] for d in dados.values()))
    total_t = total_g + total_r + total_f
    total_avaliados = total_g + total_r
    total_pct = total_g / total_avaliados * 100 if total_avaliados > 0 else 0
    msg = f"{sep}\n📊<b>MERCADOS — ÚLTIMAS 24H</b>📊\n{sep}\n{f'{chr(10)}{sep}{chr(10)}'.join(blocos)}{chr(10)}{sep}\n📌 <b>TOTAL GERAL: {total_t} Sinais</b>\n      | 🟢 {total_g} | 🔴 {total_r} | 🔵 {total_f} | {total_pct:.1f}%|\n{sep}"
    return msg

def enviar_relatorio_mercados24h():
    """Gera o relatório de mercados 24h. Retorna o texto da mensagem (sem enviar)."""
    return gerar_layout_mercados24h()
_CACHED_DATA = None
DATA_UNAVAILABLE = False

def _get_data():
    """Busca dados do SokkerPro com cache e três tentativas."""
    global _CACHED_DATA, DATA_UNAVAILABLE
    if _CACHED_DATA is not None:
        DATA_UNAVAILABLE = False
        return _CACHED_DATA
    DATA_UNAVAILABLE = False
    ultimo_erro = None
    for tentativa in range(1, 4):
        try:
            r = requests.get(SOKKERPRO_URL, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}, timeout=30)
            r.raise_for_status()
            texto = r.text
            inicio_json = texto.find('{')
            if inicio_json < 0:
                raise ValueError('resposta sem JSON')
            dados = json.loads(texto[inicio_json:])
            # O proxy pode devolver um envelope JSON com o conteúdo original em data.content.
            if isinstance(dados.get('data'), dict) and isinstance(dados['data'].get('content'), str):
                conteudo = dados['data']['content']
                conteudo_inicio = conteudo.find('{')
                if conteudo_inicio >= 0:
                    dados = json.loads(conteudo[conteudo_inicio:])
            fixtures = dados.get('data', {}).get('sortedCategorizedFixtures') if isinstance(dados, dict) else None
            if not isinstance(fixtures, list):
                raise ValueError('resposta sem lista de partidas')
            _CACHED_DATA = dados
            return _CACHED_DATA
        except Exception as e:
            ultimo_erro = e
            print(f'[SKP] Tentativa {tentativa}/3 falhou: {e}')
            if tentativa < 3:
                time.sleep(2)
    DATA_UNAVAILABLE = True
    print(f'[SKP] Fonte indisponível após 3 tentativas: {ultimo_erro}')
    return None

def _get_float(val, default=0.0):
    if not val or str(val).strip() in ('', 'None'):
        return default
    try:
        return float(str(val).split('#')[0].strip())
    except:
        return default

def _get_int(val, default=0):
    if not val or str(val).strip() in ('', 'None'):
        return default
    try:
        return int(float(str(val)))
    except:
        return default

def _get_corner_total(fixture):
    """Retorna total de escanteios; None quando a fonte não informou um dos lados."""
    raw_h = fixture.get('localCorners')
    raw_a = fixture.get('visitorCorners')
    if raw_h is None or raw_a is None or str(raw_h).strip() in ('', 'x', 'X', 'None') or str(raw_a).strip() in ('', 'x', 'X', 'None'):
        return None
    c_h = _get_int(raw_h, default=-1)
    c_a = _get_int(raw_a, default=-1)
    if c_h < 0 or c_a < 0:
        return None
    return c_h + c_a

def _extrair_stats_sokkerpro(fix):
    """Extrai TODOS os stats disponíveis de uma fixture SokkerPro."""

    def g(k, d=0):
        return _get_int(fix.get(k, d))

    def gf(k, d=0.0):
        return _get_float(fix.get(k, d))
    btts_prob = 0.0
    prob_mercados = {}
    media_gols_ht_h = 0.0
    media_gols_ht_a = 0.0
    media_gols_ft_h = 0.0
    media_gols_ft_a = 0.0
    try:
        prog_raw = fix.get('prognosticos', '')
        if prog_raw and isinstance(prog_raw, str) and prog_raw.strip() and (prog_raw != '""'):
            prog = json.loads(prog_raw)
            if 'mercado_ambos_marcam' in prog and 'ambos_sim' in prog['mercado_ambos_marcam']:
                btts_prob = gf(prog['mercado_ambos_marcam']['ambos_sim'].get('probabilidade', 0))
            if 'mercado_gols_primeiro_tempo' in prog:
                det = prog['mercado_gols_primeiro_tempo'].get('over_0_5', {}).get('detalhes', {})
                media_gols_ht_h = gf(det.get('media_casa_pt', 0))
                media_gols_ht_a = gf(det.get('media_fora_pt', 0))
            if 'mercado_gols' in prog:
                det = prog['mercado_gols'].get('over_0_5', {}).get('detalhes', {})
                media_gols_ft_h = gf(det.get('media_casa', 0))
                media_gols_ft_a = gf(det.get('media_fora', 0))
    except Exception:
        pass
    try:
        prog = json.loads(fix.get('prognosticos', '{}') or '{}')
        for key, item in prog.get('mercado_gols_primeiro_tempo', {}).items():
            if isinstance(item, dict) and item.get('res') is not None:
                prob_mercados['ht_' + key] = item.get('res')
        for key, item in prog.get('mercado_gols', {}).items():
            if isinstance(item, dict) and item.get('res') is not None:
                prob_mercados['ft_' + key] = item.get('res')
        for chave_mercado, prefixo in [('mercado_1x2','1x2_'),('mercado_1x2_1t','1x2_1t_')]:
            for key, item in prog.get(chave_mercado, {}).items():
                if isinstance(item, dict) and item.get('probabilidade') is not None:
                    prob_mercados[prefixo + key] = item.get('probabilidade')
                if isinstance(item, dict) and item.get('probabilidade_original') is not None:
                    prob_mercados[prefixo + key + '_original'] = item.get('probabilidade_original')
        item = prog.get('mercado_ambos_marcam', {}).get('ambos_sim', {})
        if isinstance(item, dict) and item.get('probabilidade') is not None:
            prob_mercados['btts'] = item.get('probabilidade')
        item = prog.get('mercado_ambos_marcam', {}).get('ambos_nao', {})
        if isinstance(item, dict) and item.get('probabilidade') is not None:
            prob_mercados['btts_nao'] = item.get('probabilidade')
        for key, item in prog.get('mercado_escanteios', {}).items():
            if isinstance(item, dict) and item.get('probabilidade') is not None:
                prob_mercados['corner_' + key] = item.get('probabilidade')
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
        try:
            return int(float(str(raw)))
        except:
            return -1
    odds_mercados = {}
    for chave, bruto in fix.items():
        if str(chave).startswith('BET365_'):
            valor = _get_float(bruto, None)
            if valor is not None and valor > 1:
                odds_mercados[str(chave)] = valor
    return {'chutes_tot_h': g('localShotsTotal'), 'chutes_tot_a': g('visitorShotsTotal'), 'chutes_gol_h': g('localShotsOnGoal'), 'chutes_gol_a': g('visitorShotsOnGoal'), 'escanteios_h': _corners('localCorners'), 'escanteios_a': _corners('visitorCorners'), 'escanteios_5m': g('corners5m'), 'escanteios_5m_h': g('localCorners5m'), 'escanteios_5m_a': g('visitorCorners5m'), 'escanteios_10m': g('corners10m'), 'escanteios_10m_h': g('localCorners10m'), 'escanteios_10m_a': g('visitorCorners10m'), 'escanteios_15m': g('corners15m'), 'escanteios_15m_h': g('localCorners15m'), 'escanteios_15m_a': g('visitorCorners15m'), 'odd_gols_ht_over_0_5': gf('BET365_GOLS1T_OVER_0_5'), 'odd_gols_ht_over_1_5': gf('BET365_GOLS1T_OVER_1_5'), 'odd_gols_ht_over_2_5': gf('BET365_GOLS1T_OVER_2_5'), 'odd_gols_ht_over_3_5': gf('BET365_GOLS1T_OVER_3_5'), 'odd_gols_ft_over_0_5': gf('BET365_GOLS_OVER_0_5'), 'odd_gols_ft_over_1_5': gf('BET365_GOLS_OVER_1_5'), 'odd_gols_ft_over_2_5': gf('BET365_GOLS_OVER_2_5'), 'odd_gols_ft_over_3_5': gf('BET365_GOLS_OVER_3_5'), 'odd_cantos_ht_over_4': gf('BET365_CANTO1T_OVER_4'), 'odd_cantos_ft_over_7': gf('BET365_CANTO_OVER_7'), 'odd_cantos_ft_over_10': gf('BET365_CANTO_OVER_10'), 'odd_btts_ht_sim': gf('BET365_AMBAS1T_YES'), 'odd_btts_ht_nao': gf('BET365_AMBAS1T_NO'), 'odd_vencedor_ht_casa': gf('BET365_VENCEDOR1T_HOME'), 'odd_vencedor_ht_empate': gf('BET365_VENCEDOR1T_DRAW'), 'odd_vencedor_ht_fora': gf('BET365_VENCEDOR1T_AWAY'), 'odd_vencedor_ft_casa': gf('BET365_VENCEDOR_HOME'), 'odd_vencedor_ft_empate': gf('BET365_VENCEDOR_DRAW'), 'odd_vencedor_ft_fora': gf('BET365_VENCEDOR_AWAY'), 'ataques_perigosos_h': g('localAttacksDangerousAttacks'), 'ataques_perigosos_a': g('visitorAttacksDangerousAttacks'), 'red_cards_h': g('localRedCards'), 'red_cards_a': g('visitorRedCards'), 'dapm5_h': gf('localDapm5'), 'dapm5_a': gf('visitorDapm5'), 'dapm10_h': gf('localDapm10'), 'dapm10_a': gf('visitorDapm10'), 'dapm_total_h': gf('localDapmTotal'), 'dapm_total_a': gf('visitorDapmTotal'), 'medias_home_goal': gf('medias_home_goal'), 'medias_away_goal': gf('medias_away_goal'), 'medias_goal_h': gf('medias_home_goal'), 'medias_goal_a': gf('medias_away_goal'), 'medias_home_corners': gf('medias_home_corners'), 'medias_away_corners': gf('medias_away_corners'), 'medias_corners_h': gf('medias_home_corners'), 'medias_corners_a': gf('medias_away_corners'), 'chutes_inside_h': g('localShotsInsideBox'), 'chutes_inside_a': g('visitorShotsInsideBox'), 'chutes_outside_h': g('localShotsOutsideBox'), 'chutes_outside_a': g('visitorShotsOutsideBox'), 'chutes_bloq_h': g('localShotsBlocked'), 'chutes_bloq_a': g('visitorShotsBlocked'), 'goal_attempts_h': g('localGoalAttempts'), 'goal_attempts_a': g('visitorGoalAttempts'), 'big_chances_h': g('localBigChancesCreated'), 'big_chances_a': g('visitorBigChancesCreated'), 'faltas_h': g('localFouls'), 'faltas_a': g('visitorFouls'), 'yellow_cards_h': g('localYellowCards'), 'yellow_cards_a': g('visitorYellowCards'), 'impedimentos_h': g('localOffsides'), 'impedimentos_a': g('visitorOffsides'), 'defesas_h': g('localSaves'), 'defesas_a': g('visitorSaves'), 'pressure_bar_h': g('localPressureBar'), 'pressure_bar_a': g('visitorPressureBar'), 'ball_safe_h': g('localBallSafe'), 'ball_safe_a': g('visitorBallSafe'), 'xg_h': gf('localXg'), 'xg_a': gf('visitorXg'), 'posse_h': gf('localBallPossession'), 'posse_a': gf('visitorBallPossession'), 'ataques_h': g('localAttacksAttacks'), 'ataques_a': g('visitorAttacksAttacks'), 'btts_probabilidade': btts_prob, 'media_gols_ht_h': media_gols_ht_h, 'media_gols_ht_a': media_gols_ht_a, 'media_gols_ft_h': media_gols_ft_h, 'media_gols_ft_a': media_gols_ft_a, 'dapm_max_h': dapm_max, 'dapm_max_a': dapm_max, 'prob_mercados': prob_mercados, 'odds_mercados': odds_mercados}

def get_jogos_sokkerpro(fids_existentes):
    """Busca jogos, stats E odds em UMA unica chamada HTTP."""
    data = _get_data()
    if not data:
        return []
    jogos = []
    try:
        for cat in data['data']['sortedCategorizedFixtures']:
            for fix in cat['fixtures']:
                fid = str(fix.get('fixtureId', ''))
                if not fid or fid in fids_existentes:
                    continue
                status = fix.get('status', '')
                liga_api = str(fix.get('leagueName', ''))
                if re.search(r"\bwomen(?:'s)?\b|\bfemin(?:ine|ino)?\b|\bfemale\b", liga_api, re.IGNORECASE):
                    continue
                minuto = _get_int(fix.get('minute', 0))
                if status in ('FT', 'PEN'):
                    continue
                if status == '2nd':
                    period = 2
                elif status == '1st':
                    period = 1
                elif status == 'HT':
                    period = 1
                elif status == 'NS':
                    period = 0
                else:
                    period = 0
                if status == 'NS' and (not minuto):
                    continue
                stats = _extrair_stats_sokkerpro(fix)
                oh = _get_float(fix.get('XBET_VENCEDOR_HOME'))
                oa = _get_float(fix.get('XBET_VENCEDOR_AWAY'))
                if not (oh > 1 and oa > 1):
                    oh = _get_float(fix.get('BET365_VENCEDOR_1_LIVE'))
                    oa = _get_float(fix.get('BET365_VENCEDOR_2_LIVE'))
                pais_fix = fix.get('countryName') or cat.get('countryName', '')
                if isinstance(pais_fix, dict):
                    pais_fix = pais_fix.get('name') or pais_fix.get('countryName') or pais_fix.get('code') or ''
                if not pais_fix:
                    for chave_pais in ('countryCode', 'country_code', 'countryShortCode', 'countryIso'):
                        valor_pais = fix.get(chave_pais)
                        if valor_pais:
                            pais_fix = '__ISO__:' + str(valor_pais).lower()
                            break
                if not pais_fix:
                    iso_paises = {
                        'ar':'Argentina','bo':'Bolivia','br':'Brazil','cl':'Chile','co':'Colombia','cr':'Costa Rica','ec':'Ecuador','sv':'El Salvador','gt':'Guatemala','hn':'Honduras','mx':'Mexico','ni':'Nicaragua','pa':'Panama','py':'Paraguay','pe':'Peru','pr':'Puerto Rico','us':'United States','uy':'Uruguay','ve':'Venezuela','ca':'Canada','gb':'England','es':'Spain','pt':'Portugal','it':'Italy','fr':'France','de':'Germany','nl':'Netherlands','be':'Belgium','tr':'Turkey','gr':'Greece','au':'Australia','jp':'Japan','kr':'South Korea','cn':'China','za':'South Africa','ae':'United Arab Emirates','sa':'Saudi Arabia','qa':'Qatar','in':'India','ru':'Russia','ch':'Switzerland','at':'Austria','pl':'Poland','cz':'Czech Republic','dk':'Denmark','se':'Sweden','no':'Norway','fi':'Finland','ua':'Ukraine','il':'Israel','eg':'Egypt','ma':'Morocco','tn':'Tunisia','ng':'Nigeria','gh':'Ghana','az':'Azerbaijan','lt':'Lithuania','bg':'Bulgaria','ee':'Estonia','ro':'Romania','rs':'Serbia','hr':'Croatia','sk':'Slovakia','hu':'Hungary','si':'Slovenia','is':'Iceland','ie':'Ireland','sc':'Scotland','wales':'Wales','al':'Albania','ba':'Bosnia and Herzegovina','me':'Montenegro','mk':'North Macedonia','ge':'Georgia','am':'Armenia','kz':'Kazakhstan','uz':'Uzbekistan','th':'Thailand','my':'Malaysia','id':'Indonesia','vn':'Vietnam','nz':'New Zealand','zw':'Zimbabwe','ke':'Kenya','tz':'Tanzania','ug':'Uganda','dz':'Algeria','cm':'Cameroon','ci':'Ivory Coast','sn':'Senegal','br':'Brazil'
                    }
                    caminho_pais = str(fix.get('countryImagePath', ''))
                    m_pais = re.search(r'/short/([a-z]{2})\.png', caminho_pais.lower())
                    if m_pais:
                        pais_fix = '__ISO__:' + m_pais.group(1)
                if not pais_fix and fix.get('leagueName') == 'Premier League' and ({fix.get('localTeamName'), fix.get('visitorTeamName')} & {'Qarabağ', 'Şamaxı FK'}):
                    pais_fix = 'Azerbaijan'
                if not pais_fix and fix.get('leagueName') == 'Super Liga' and ({fix.get('localTeamName'), fix.get('visitorTeamName')} & {'Sheriff', 'FC Sheriff', 'Sheriff Tiraspol', 'FC Politehnica', 'Politehnica UTM'}):
                    pais_fix = 'Moldova, Republic of'
                if not pais_fix and fix.get('leagueName') == 'A Lyga':
                    pais_fix = 'Lithuania'
                if not pais_fix and fix.get('leagueName') == 'Premiership Development Liga':
                    pais_fix = 'Northern Ireland'
                jogos.append({'fid': fid, 'home': fix.get('localTeamName', 'Home'), 'away': fix.get('visitorTeamName', 'Away'), 'minuto': minuto or _get_int(fix.get('minutePrimeiroTempo', 0)) or _get_int(fix.get('minuteSegundoTempo', 0)), 'period': period, 'sh': _get_int(fix.get('scoresLocalTeam', 0)), 'sa': _get_int(fix.get('scoresVisitorTeam', 0)), 'liga': fix.get('leagueName', 'Liga'), 'pais': pais_fix, 'source': 'sokkerpro', '_stats': stats, '_odd_h': oh if oh and oh > 1 else None, '_odd_a': oa if oa and oa > 1 else None})
    except:
        pass
    return jogos

def get_stats_sokkerpro(fid_raw, home='', away=''):
    data = _get_data()
    if not data:
        return {}
    try:
        for cat in data['data']['sortedCategorizedFixtures']:
            for fix in cat['fixtures']:
                if str(fix.get('fixtureId', '')) == str(fid_raw):
                    stats = _extrair_stats_sokkerpro(fix)
                    # O endpoint geral traz estatísticas, mas as odds por mercado
                    # ficam no endpoint individual da partida.
                    try:
                        detalhe_resp = requests.get(f'https://r.jina.ai/http://m2.sokkerpro.com/fixture/{fid_raw}', headers={'User-Agent': 'Mozilla/5.0'}, timeout=30)
                        detalhe_texto = detalhe_resp.text
                        detalhe_inicio = detalhe_texto.find('{')
                        detalhe = json.loads(detalhe_texto[detalhe_inicio:]) if detalhe_inicio >= 0 else {}
                        if isinstance(detalhe.get('data'), dict) and isinstance(detalhe['data'].get('content'), str):
                            detalhe_conteudo = detalhe['data']['content']
                            detalhe_conteudo_inicio = detalhe_conteudo.find('{')
                            if detalhe_conteudo_inicio >= 0:
                                detalhe = json.loads(detalhe_conteudo[detalhe_conteudo_inicio:])
                        if detalhe.get('success') and isinstance(detalhe.get('data'), dict):
                            detalhe_stats = _extrair_stats_sokkerpro(detalhe['data'])
                            stats['odds_mercados'] = detalhe_stats.get('odds_mercados', {})
                            for campo in ('escanteios_5m','escanteios_5m_h','escanteios_5m_a','escanteios_10m','escanteios_10m_h','escanteios_10m_a','escanteios_15m','escanteios_15m_h','escanteios_15m_a','big_chances_h','big_chances_a'):
                                if campo in detalhe_stats:
                                    stats[campo] = detalhe_stats[campo]
                    except Exception as e:
                        print(f'[SKP] Odds individuais indisponíveis para {fid_raw}: {e}')
                    return stats
    except:
        pass
    return {}

def get_odds_sokkerpro(fid_raw):
    data = _get_data()
    if not data:
        return (None, None)
    try:
        for cat in data['data']['sortedCategorizedFixtures']:
            for fix in cat['fixtures']:
                if str(fix.get('fixtureId', '')) != str(fid_raw):
                    continue
                oh = _get_float(fix.get('XBET_VENCEDOR_HOME'))
                oa = _get_float(fix.get('XBET_VENCEDOR_AWAY'))
                if oh > 1 and oa > 1:
                    return (oh, oa)
                oh = _get_float(fix.get('BET365_VENCEDOR_1_LIVE'))
                oa = _get_float(fix.get('BET365_VENCEDOR_2_LIVE'))
                if oh > 1 and oa > 1:
                    return (oh, oa)
                return (None, None)
    except Exception:
        return (None, None)
    return (None, None)

def get_stats_sokkerpro_by_name(home, away):
    """Fallback: busca stats no SokkerPro pelo nome dos times."""
    try:
        data = _get_data()
        if not data:
            return {}
        for cat in data['data']['sortedCategorizedFixtures']:
            for fix in cat['fixtures']:
                if fix.get('localTeamName', '').lower() == home.lower() and fix.get('visitorTeamName', '').lower() == away.lower():
                    return _extrair_stats_sokkerpro(fix)
    except:
        pass
    return {}

def calcular_prob_gols_ht(chutes_tot, chutes_gol, minuto):
    """Estima prob de gols usando taxa de chutes como proxy de xG."""
    import math as _math
    taxa_conversao = 0.1
    xg = chutes_gol * taxa_conversao + chutes_tot * 0.04
    min_restantes_ht = max(45 - minuto, 1)
    min_restantes_ft = max(90 - minuto, 1)
    taxa_por_min = xg / max(minuto, 1)
    xg_rest_ht = taxa_por_min * min_restantes_ht
    xg_rest_ft = taxa_por_min * min_restantes_ft
    xg_total_ft = xg + xg_rest_ft
    prob_05_ht = round((1 - _math.exp(-max(xg_rest_ht, 0.05))) * 100, 1)
    prob_15_ft = round((1 - _math.exp(-max(xg_total_ft - 1, 0.1))) * 100, 1)
    return (prob_15_ft, prob_05_ht)

def filtrar_janelas(jogos):
    resultado = []
    for j in jogos:
        m = j['minuto']
        p_raw = j['period']
        if isinstance(p_raw, str):
            p = 2 if '2' in p_raw else 1
        else:
            p = p_raw
        em_janela = p == 1 and 15 <= m <= 27 or (p == 1 and 28 <= m <= 38) or (p == 2 and 55 <= m <= 77) or (p == 2 and 78 <= m <= 88)
        if em_janela:
            resultado.append(j)
    return resultado

def _probabilidade_para_sinal(stats, tipo, sh, sa, cantos_atual):
    mapa = stats.get('prob_mercados', {}) if stats else {}
    if tipo == 'gol_intervalo':
        return mapa.get('ht_over_0_5')
    if tipo == 'over_15':
        return mapa.get('ft_over_1_5')
    if tipo in ('over_gol', 'over', 'gol_partida'):
        return mapa.get('ft_over_' + str(sh + sa + 1) + '_5')
    if tipo == 'ambas_marcam':
        return mapa.get('btts')
    if tipo in ('escanteio', 'corner', 'escanteio_ht', 'escanteio_ft'):
        alvo = cantos_atual + 0.5
        for chave, valor in mapa.items():
            if not chave.startswith('corner_over_'):
                continue
            try:
                linha = float(chave.replace('corner_over_', '').replace('_', '.'))
            except Exception:
                continue
            if abs(linha - alvo) < 0.01:
                return valor
    return None

def nome_liga_exibicao(liga, pais):
    PAIS_NOME = {
        'Aruba': ('🇦🇼', 'Aruba'),
        'Afghanistan': ('🇦🇫', 'Afeganistão'),
        'Angola': ('🇦🇴', 'Angola'),
        'Anguilla': ('🇦🇮', 'Anguila'),
        'Åland Islands': ('🇦🇽', 'Ilhas Aland'),
        'Albania': ('🇦🇱', 'Albânia'),
        'Andorra': ('🇦🇩', 'Andorra'),
        'United Arab Emirates': ('🇦🇪', 'Emirados Árabes Unidos'),
        'Argentina': ('🇦🇷', 'Argentina'),
        'Armenia': ('🇦🇲', 'Armênia'),
        'American Samoa': ('🇦🇸', 'Samoa Americana'),
        'Antarctica': ('🇦🇶', 'Antártida'),
        'French Southern Territories': ('🇹🇫', 'Territórios Franceses do Sul'),
        'Antigua and Barbuda': ('🇦🇬', 'Antígua e Barbuda'),
        'Australia': ('🇦🇺', 'Austrália'),
        'Austria': ('🇦🇹', 'Áustria'),
        'Azerbaijan': ('🇦🇿', 'Azerbaijão'),
        'Burundi': ('🇧🇮', 'Burundi'),
        'Belgium': ('🇧🇪', 'Bélgica'),
        'Benin': ('🇧🇯', 'Benin'),
        'Bonaire, Sint Eustatius and Saba': ('🇧🇶', 'Países Baixos Caribenhos'),
        'Burkina Faso': ('🇧🇫', 'Burquina Faso'),
        'Bangladesh': ('🇧🇩', 'Bangladesh'),
        'Bulgaria': ('🇧🇬', 'Bulgária'),
        'Bahrain': ('🇧🇭', 'Barein'),
        'Bahamas': ('🇧🇸', 'Bahamas'),
        'Bosnia and Herzegovina': ('🇧🇦', 'Bósnia e Herzegovina'),
        'Saint Barthélemy': ('🇧🇱', 'São Bartolomeu'),
        'Belarus': ('🇧🇾', 'Bielorrússia'),
        'Belize': ('🇧🇿', 'Belize'),
        'Bermuda': ('🇧🇲', 'Bermudas'),
        'Bolivia, Plurinational State of': ('🇧🇴', 'Bolívia'),
        'Brazil': ('🇧🇷', 'Brasil'),
        'Barbados': ('🇧🇧', 'Barbados'),
        'Brunei Darussalam': ('🇧🇳', 'Brunei'),
        'Bhutan': ('🇧🇹', 'Butão'),
        'Bouvet Island': ('🇧🇻', 'Ilha Bouvet'),
        'Botswana': ('🇧🇼', 'Botsuana'),
        'Central African Republic': ('🇨🇫', 'República Centro-Africana'),
        'Canada': ('🇨🇦', 'Canadá'),
        'Cocos (Keeling) Islands': ('🇨🇨', 'Ilhas Cocos (Keeling)'),
        'Switzerland': ('🇨🇭', 'Suíça'),
        'Chile': ('🇨🇱', 'Chile'),
        'China': ('🇨🇳', 'China'),
        "Côte d'Ivoire": ('🇨🇮', 'Costa do Marfim'),
        'Cameroon': ('🇨🇲', 'Camarões'),
        'Congo, The Democratic Republic of the': ('🇨🇩', 'Congo - Kinshasa'),
        'Congo': ('🇨🇬', 'República do Congo'),
        'Cook Islands': ('🇨🇰', 'Ilhas Cook'),
        'Colombia': ('🇨🇴', 'Colômbia'),
        'Comoros': ('🇰🇲', 'Comores'),
        'Cabo Verde': ('🇨🇻', 'Cabo Verde'),
        'Costa Rica': ('🇨🇷', 'Costa Rica'),
        'Cuba': ('🇨🇺', 'Cuba'),
        'Curaçao': ('🇨🇼', 'Curaçao'),
        'Christmas Island': ('🇨🇽', 'Ilha Christmas'),
        'Cayman Islands': ('🇰🇾', 'Ilhas Cayman'),
        'Cyprus': ('🇨🇾', 'Chipre'),
        'Czechia': ('🇨🇿', 'Tchéquia'),
        'Germany': ('🇩🇪', 'Alemanha'),
        'Djibouti': ('🇩🇯', 'Djibuti'),
        'Dominica': ('🇩🇲', 'Dominica'),
        'Denmark': ('🇩🇰', 'Dinamarca'),
        'Dominican Republic': ('🇩🇴', 'República Dominicana'),
        'Algeria': ('🇩🇿', 'Argélia'),
        'Ecuador': ('🇪🇨', 'Equador'),
        'Egypt': ('🇪🇬', 'Egito'),
        'Eritrea': ('🇪🇷', 'Eritreia'),
        'Western Sahara': ('🇪🇭', 'Saara Ocidental'),
        'Spain': ('🇪🇸', 'Espanha'),
        'Estonia': ('🇪🇪', 'Estônia'),
        'Ethiopia': ('🇪🇹', 'Etiópia'),
        'Finland': ('🇫🇮', 'Finlândia'),
        'Fiji': ('🇫🇯', 'Fiji'),
        'Falkland Islands (Malvinas)': ('🇫🇰', 'Ilhas Malvinas'),
        'France': ('🇫🇷', 'França'),
        'Faroe Islands': ('🇫🇴', 'Ilhas Faroé'),
        'Micronesia, Federated States of': ('🇫🇲', 'Micronésia'),
        'Gabon': ('🇬🇦', 'Gabão'),
        'United Kingdom': ('🇬🇧', 'Reino Unido'),
        'Georgia': ('🇬🇪', 'Geórgia'),
        'Guernsey': ('🇬🇬', 'Guernsey'),
        'Ghana': ('🇬🇭', 'Gana'),
        'Gibraltar': ('🇬🇮', 'Gibraltar'),
        'Guinea': ('🇬🇳', 'Guiné'),
        'Guadeloupe': ('🇬🇵', 'Guadalupe'),
        'Gambia': ('🇬🇲', 'Gâmbia'),
        'Guinea-Bissau': ('🇬🇼', 'Guiné-Bissau'),
        'Equatorial Guinea': ('🇬🇶', 'Guiné Equatorial'),
        'Greece': ('🇬🇷', 'Grécia'),
        'Grenada': ('🇬🇩', 'Granada'),
        'Greenland': ('🇬🇱', 'Groenlândia'),
        'Guatemala': ('🇬🇹', 'Guatemala'),
        'French Guiana': ('🇬🇫', 'Guiana Francesa'),
        'Guam': ('🇬🇺', 'Guam'),
        'Guyana': ('🇬🇾', 'Guiana'),
        'Hong Kong': ('🇭🇰', 'Hong Kong, RAE da China'),
        'Heard Island and McDonald Islands': ('🇭🇲', 'Ilhas Heard e McDonald'),
        'Honduras': ('🇭🇳', 'Honduras'),
        'Croatia': ('🇭🇷', 'Croácia'),
        'Haiti': ('🇭🇹', 'Haiti'),
        'Hungary': ('🇭🇺', 'Hungria'),
        'Indonesia': ('🇮🇩', 'Indonésia'),
        'Isle of Man': ('🇮🇲', 'Ilha de Man'),
        'India': ('🇮🇳', 'Índia'),
        'British Indian Ocean Territory': ('🇮🇴', 'Território Britânico do Oceano Índico'),
        'Ireland': ('🇮🇪', 'Irlanda'),
        'Iran, Islamic Republic of': ('🇮🇷', 'Irã'),
        'Iraq': ('🇮🇶', 'Iraque'),
        'Iceland': ('🇮🇸', 'Islândia'),
        'Israel': ('🇮🇱', 'Israel'),
        'Italy': ('🇮🇹', 'Itália'),
        'Jamaica': ('🇯🇲', 'Jamaica'),
        'Jersey': ('🇯🇪', 'Jersey'),
        'Jordan': ('🇯🇴', 'Jordânia'),
        'Japan': ('🇯🇵', 'Japão'),
        'Kazakhstan': ('🇰🇿', 'Cazaquistão'),
        'Kenya': ('🇰🇪', 'Quênia'),
        'Kyrgyzstan': ('🇰🇬', 'Quirguistão'),
        'Cambodia': ('🇰🇭', 'Camboja'),
        'Kiribati': ('🇰🇮', 'Quiribati'),
        'Saint Kitts and Nevis': ('🇰🇳', 'São Cristóvão e Névis'),
        'Korea, Republic of': ('🇰🇷', 'Coreia do Sul'),
        'Kuwait': ('🇰🇼', 'Kuwait'),
        "Lao People's Democratic Republic": ('🇱🇦', 'Laos'),
        'Lebanon': ('🇱🇧', 'Líbano'),
        'Liberia': ('🇱🇷', 'Libéria'),
        'Libya': ('🇱🇾', 'Líbia'),
        'Saint Lucia': ('🇱🇨', 'Santa Lúcia'),
        'Liechtenstein': ('🇱🇮', 'Liechtenstein'),
        'Sri Lanka': ('🇱🇰', 'Sri Lanka'),
        'Lesotho': ('🇱🇸', 'Lesoto'),
        'Lithuania': ('🇱🇹', 'Lituânia'),
        'Luxembourg': ('🇱🇺', 'Luxemburgo'),
        'Latvia': ('🇱🇻', 'Letônia'),
        'Macao': ('🇲🇴', 'Macau, RAE da China'),
        'Saint Martin (French part)': ('🇲🇫', 'São Martinho'),
        'Morocco': ('🇲🇦', 'Marrocos'),
        'Monaco': ('🇲🇨', 'Mônaco'),
        'Moldova, Republic of': ('🇲🇩', 'Moldávia'),
        'Madagascar': ('🇲🇬', 'Madagascar'),
        'Maldives': ('🇲🇻', 'Maldivas'),
        'Mexico': ('🇲🇽', 'México'),
        'Marshall Islands': ('🇲🇭', 'Ilhas Marshall'),
        'North Macedonia': ('🇲🇰', 'Macedônia do Norte'),
        'Mali': ('🇲🇱', 'Mali'),
        'Malta': ('🇲🇹', 'Malta'),
        'Myanmar': ('🇲🇲', 'Mianmar (Birmânia)'),
        'Montenegro': ('🇲🇪', 'Montenegro'),
        'Mongolia': ('🇲🇳', 'Mongólia'),
        'Northern Mariana Islands': ('🇲🇵', 'Ilhas Marianas do Norte'),
        'Mozambique': ('🇲🇿', 'Moçambique'),
        'Mauritania': ('🇲🇷', 'Mauritânia'),
        'Montserrat': ('🇲🇸', 'Montserrat'),
        'Martinique': ('🇲🇶', 'Martinica'),
        'Mauritius': ('🇲🇺', 'Maurício'),
        'Malawi': ('🇲🇼', 'Malaui'),
        'Malaysia': ('🇲🇾', 'Malásia'),
        'Mayotte': ('🇾🇹', 'Mayotte'),
        'Namibia': ('🇳🇦', 'Namíbia'),
        'New Caledonia': ('🇳🇨', 'Nova Caledônia'),
        'Niger': ('🇳🇪', 'Níger'),
        'Norfolk Island': ('🇳🇫', 'Ilha Norfolk'),
        'Nigeria': ('🇳🇬', 'Nigéria'),
        'Nicaragua': ('🇳🇮', 'Nicarágua'),
        'Niue': ('🇳🇺', 'Niue'),
        'Netherlands': ('🇳🇱', 'Países Baixos'),
        'Norway': ('🇳🇴', 'Noruega'),
        'Nepal': ('🇳🇵', 'Nepal'),
        'Nauru': ('🇳🇷', 'Nauru'),
        'New Zealand': ('🇳🇿', 'Nova Zelândia'),
        'Oman': ('🇴🇲', 'Omã'),
        'Pakistan': ('🇵🇰', 'Paquistão'),
        'Panama': ('🇵🇦', 'Panamá'),
        'Pitcairn': ('🇵🇳', 'Ilhas Pitcairn'),
        'Peru': ('🇵🇪', 'Peru'),
        'Philippines': ('🇵🇭', 'Filipinas'),
        'Palau': ('🇵🇼', 'Palau'),
        'Papua New Guinea': ('🇵🇬', 'Papua-Nova Guiné'),
        'Poland': ('🇵🇱', 'Polônia'),
        'Puerto Rico': ('🇵🇷', 'Porto Rico'),
        "Korea, Democratic People's Republic of": ('🇰🇵', 'Coreia do Norte'),
        'Portugal': ('🇵🇹', 'Portugal'),
        'Paraguay': ('🇵🇾', 'Paraguai'),
        'Palestine, State of': ('🇵🇸', 'Territórios palestinos'),
        'French Polynesia': ('🇵🇫', 'Polinésia Francesa'),
        'Qatar': ('🇶🇦', 'Catar'),
        'Réunion': ('🇷🇪', 'Reunião'),
        'Romania': ('🇷🇴', 'Romênia'),
        'Russian Federation': ('🇷🇺', 'Rússia'),
        'Rwanda': ('🇷🇼', 'Ruanda'),
        'Saudi Arabia': ('🇸🇦', 'Arábia Saudita'),
        'Sudan': ('🇸🇩', 'Sudão'),
        'Senegal': ('🇸🇳', 'Senegal'),
        'Singapore': ('🇸🇬', 'Singapura'),
        'South Georgia and the South Sandwich Islands': ('🇬🇸', 'Ilhas Geórgia do Sul e Sandwich do Sul'),
        'Saint Helena, Ascension and Tristan da Cunha': ('🇸🇭', 'Santa Helena'),
        'Svalbard and Jan Mayen': ('🇸🇯', 'Svalbard e Jan Mayen'),
        'Solomon Islands': ('🇸🇧', 'Ilhas Salomão'),
        'Sierra Leone': ('🇸🇱', 'Serra Leoa'),
        'El Salvador': ('🇸🇻', 'El Salvador'),
        'San Marino': ('🇸🇲', 'San Marino'),
        'Somalia': ('🇸🇴', 'Somália'),
        'Saint Pierre and Miquelon': ('🇵🇲', 'São Pedro e Miquelão'),
        'Serbia': ('🇷🇸', 'Sérvia'),
        'South Sudan': ('🇸🇸', 'Sudão do Sul'),
        'Sao Tome and Principe': ('🇸🇹', 'São Tomé e Príncipe'),
        'Suriname': ('🇸🇷', 'Suriname'),
        'Slovakia': ('🇸🇰', 'Eslováquia'),
        'Slovenia': ('🇸🇮', 'Eslovênia'),
        'Sweden': ('🇸🇪', 'Suécia'),
        'Eswatini': ('🇸🇿', 'Essuatíni'),
        'Sint Maarten (Dutch part)': ('🇸🇽', 'Sint Maarten'),
        'Seychelles': ('🇸🇨', 'Seicheles'),
        'Syrian Arab Republic': ('🇸🇾', 'Síria'),
        'Turks and Caicos Islands': ('🇹🇨', 'Ilhas Turcas e Caicos'),
        'Chad': ('🇹🇩', 'Chade'),
        'Togo': ('🇹🇬', 'Togo'),
        'Thailand': ('🇹🇭', 'Tailândia'),
        'Tajikistan': ('🇹🇯', 'Tadjiquistão'),
        'Tokelau': ('🇹🇰', 'Tokelau'),
        'Turkmenistan': ('🇹🇲', 'Turcomenistão'),
        'Timor-Leste': ('🇹🇱', 'Timor-Leste'),
        'Tonga': ('🇹🇴', 'Tonga'),
        'Trinidad and Tobago': ('🇹🇹', 'Trinidad e Tobago'),
        'Tunisia': ('🇹🇳', 'Tunísia'),
        'Türkiye': ('🇹🇷', 'Turquia'),
        'Tuvalu': ('🇹🇻', 'Tuvalu'),
        'Taiwan, Province of China': ('🇹🇼', 'Taiwan'),
        'Tanzania, United Republic of': ('🇹🇿', 'Tanzânia'),
        'Uganda': ('🇺🇬', 'Uganda'),
        'Ukraine': ('🇺🇦', 'Ucrânia'),
        'United States Minor Outlying Islands': ('🇺🇲', 'Ilhas Menores Distantes dos EUA'),
        'Uruguay': ('🇺🇾', 'Uruguai'),
        'United States': ('🇺🇸', 'Estados Unidos'),
        'Uzbekistan': ('🇺🇿', 'Uzbequistão'),
        'Holy See (Vatican City State)': ('🇻🇦', 'Cidade do Vaticano'),
        'Saint Vincent and the Grenadines': ('🇻🇨', 'São Vicente e Granadinas'),
        'Venezuela, Bolivarian Republic of': ('🇻🇪', 'Venezuela'),
        'Virgin Islands, British': ('🇻🇬', 'Ilhas Virgens Britânicas'),
        'Virgin Islands, U.S.': ('🇻🇮', 'Ilhas Virgens Americanas'),
        'Viet Nam': ('🇻🇳', 'Vietnã'),
        'Vanuatu': ('🇻🇺', 'Vanuatu'),
        'Wallis and Futuna': ('🇼🇫', 'Wallis e Futuna'),
        'Samoa': ('🇼🇸', 'Samoa'),
        'Yemen': ('🇾🇪', 'Iêmen'),
        'South Africa': ('🇿🇦', 'África do Sul'),
        'Zambia': ('🇿🇲', 'Zâmbia'),
        'Zimbabwe': ('🇿🇼', 'Zimbábue'),
        'England': ('🏴󠁧󠁢󠁥󠁮󠁧󠁿', 'Inglaterra'),
        'Northern Ireland': ('🏴', 'Irlanda do Norte'),
        'Scotland': ('🏴', 'Escócia'),
        'Wales': ('🏴', 'País de Gales'),
        'Faroe Islands': ('🇫🇴', 'Ilhas Faroé'),
    }
    PAIS_CODIGO = {
        'aw': ('🇦🇼', 'Aruba'),
        'af': ('🇦🇫', 'Afeganistão'),
        'ao': ('🇦🇴', 'Angola'),
        'ai': ('🇦🇮', 'Anguila'),
        'ax': ('🇦🇽', 'Ilhas Aland'),
        'al': ('🇦🇱', 'Albânia'),
        'ad': ('🇦🇩', 'Andorra'),
        'ae': ('🇦🇪', 'Emirados Árabes Unidos'),
        'ar': ('🇦🇷', 'Argentina'),
        'am': ('🇦🇲', 'Armênia'),
        'as': ('🇦🇸', 'Samoa Americana'),
        'aq': ('🇦🇶', 'Antártida'),
        'tf': ('🇹🇫', 'Territórios Franceses do Sul'),
        'ag': ('🇦🇬', 'Antígua e Barbuda'),
        'au': ('🇦🇺', 'Austrália'),
        'at': ('🇦🇹', 'Áustria'),
        'az': ('🇦🇿', 'Azerbaijão'),
        'bi': ('🇧🇮', 'Burundi'),
        'be': ('🇧🇪', 'Bélgica'),
        'bj': ('🇧🇯', 'Benin'),
        'bq': ('🇧🇶', 'Países Baixos Caribenhos'),
        'bf': ('🇧🇫', 'Burquina Faso'),
        'bd': ('🇧🇩', 'Bangladesh'),
        'bg': ('🇧🇬', 'Bulgária'),
        'bh': ('🇧🇭', 'Barein'),
        'bs': ('🇧🇸', 'Bahamas'),
        'ba': ('🇧🇦', 'Bósnia e Herzegovina'),
        'bl': ('🇧🇱', 'São Bartolomeu'),
        'by': ('🇧🇾', 'Bielorrússia'),
        'bz': ('🇧🇿', 'Belize'),
        'bm': ('🇧🇲', 'Bermudas'),
        'bo': ('🇧🇴', 'Bolívia'),
        'br': ('🇧🇷', 'Brasil'),
        'bb': ('🇧🇧', 'Barbados'),
        'bn': ('🇧🇳', 'Brunei'),
        'bt': ('🇧🇹', 'Butão'),
        'bv': ('🇧🇻', 'Ilha Bouvet'),
        'bw': ('🇧🇼', 'Botsuana'),
        'cf': ('🇨🇫', 'República Centro-Africana'),
        'ca': ('🇨🇦', 'Canadá'),
        'cc': ('🇨🇨', 'Ilhas Cocos (Keeling)'),
        'ch': ('🇨🇭', 'Suíça'),
        'cl': ('🇨🇱', 'Chile'),
        'cn': ('🇨🇳', 'China'),
        'ci': ('🇨🇮', 'Costa do Marfim'),
        'cm': ('🇨🇲', 'Camarões'),
        'cd': ('🇨🇩', 'Congo - Kinshasa'),
        'cg': ('🇨🇬', 'República do Congo'),
        'ck': ('🇨🇰', 'Ilhas Cook'),
        'co': ('🇨🇴', 'Colômbia'),
        'km': ('🇰🇲', 'Comores'),
        'cv': ('🇨🇻', 'Cabo Verde'),
        'cr': ('🇨🇷', 'Costa Rica'),
        'cu': ('🇨🇺', 'Cuba'),
        'cw': ('🇨🇼', 'Curaçao'),
        'cx': ('🇨🇽', 'Ilha Christmas'),
        'ky': ('🇰🇾', 'Ilhas Cayman'),
        'cy': ('🇨🇾', 'Chipre'),
        'cz': ('🇨🇿', 'Tchéquia'),
        'de': ('🇩🇪', 'Alemanha'),
        'dj': ('🇩🇯', 'Djibuti'),
        'dm': ('🇩🇲', 'Dominica'),
        'dk': ('🇩🇰', 'Dinamarca'),
        'do': ('🇩🇴', 'República Dominicana'),
        'dz': ('🇩🇿', 'Argélia'),
        'ec': ('🇪🇨', 'Equador'),
        'eg': ('🇪🇬', 'Egito'),
        'er': ('🇪🇷', 'Eritreia'),
        'eh': ('🇪🇭', 'Saara Ocidental'),
        'es': ('🇪🇸', 'Espanha'),
        'ee': ('🇪🇪', 'Estônia'),
        'et': ('🇪🇹', 'Etiópia'),
        'fi': ('🇫🇮', 'Finlândia'),
        'fj': ('🇫🇯', 'Fiji'),
        'fk': ('🇫🇰', 'Ilhas Malvinas'),
        'fr': ('🇫🇷', 'França'),
        'fo': ('🇫🇴', 'Ilhas Faroé'),
        'fm': ('🇫🇲', 'Micronésia'),
        'ga': ('🇬🇦', 'Gabão'),
        'gb': ('🇬🇧', 'Reino Unido'),
        'ge': ('🇬🇪', 'Geórgia'),
        'gg': ('🇬🇬', 'Guernsey'),
        'gh': ('🇬🇭', 'Gana'),
        'gi': ('🇬🇮', 'Gibraltar'),
        'gn': ('🇬🇳', 'Guiné'),
        'gp': ('🇬🇵', 'Guadalupe'),
        'gm': ('🇬🇲', 'Gâmbia'),
        'gw': ('🇬🇼', 'Guiné-Bissau'),
        'gq': ('🇬🇶', 'Guiné Equatorial'),
        'gr': ('🇬🇷', 'Grécia'),
        'gd': ('🇬🇩', 'Granada'),
        'gl': ('🇬🇱', 'Groenlândia'),
        'gt': ('🇬🇹', 'Guatemala'),
        'gf': ('🇬🇫', 'Guiana Francesa'),
        'gu': ('🇬🇺', 'Guam'),
        'gy': ('🇬🇾', 'Guiana'),
        'hk': ('🇭🇰', 'Hong Kong, RAE da China'),
        'hm': ('🇭🇲', 'Ilhas Heard e McDonald'),
        'hn': ('🇭🇳', 'Honduras'),
        'hr': ('🇭🇷', 'Croácia'),
        'ht': ('🇭🇹', 'Haiti'),
        'hu': ('🇭🇺', 'Hungria'),
        'id': ('🇮🇩', 'Indonésia'),
        'im': ('🇮🇲', 'Ilha de Man'),
        'in': ('🇮🇳', 'Índia'),
        'io': ('🇮🇴', 'Território Britânico do Oceano Índico'),
        'ie': ('🇮🇪', 'Irlanda'),
        'ir': ('🇮🇷', 'Irã'),
        'iq': ('🇮🇶', 'Iraque'),
        'is': ('🇮🇸', 'Islândia'),
        'il': ('🇮🇱', 'Israel'),
        'it': ('🇮🇹', 'Itália'),
        'jm': ('🇯🇲', 'Jamaica'),
        'je': ('🇯🇪', 'Jersey'),
        'jo': ('🇯🇴', 'Jordânia'),
        'jp': ('🇯🇵', 'Japão'),
        'kz': ('🇰🇿', 'Cazaquistão'),
        'ke': ('🇰🇪', 'Quênia'),
        'kg': ('🇰🇬', 'Quirguistão'),
        'kh': ('🇰🇭', 'Camboja'),
        'ki': ('🇰🇮', 'Quiribati'),
        'kn': ('🇰🇳', 'São Cristóvão e Névis'),
        'kr': ('🇰🇷', 'Coreia do Sul'),
        'kw': ('🇰🇼', 'Kuwait'),
        'la': ('🇱🇦', 'Laos'),
        'lb': ('🇱🇧', 'Líbano'),
        'lr': ('🇱🇷', 'Libéria'),
        'ly': ('🇱🇾', 'Líbia'),
        'lc': ('🇱🇨', 'Santa Lúcia'),
        'li': ('🇱🇮', 'Liechtenstein'),
        'lk': ('🇱🇰', 'Sri Lanka'),
        'ls': ('🇱🇸', 'Lesoto'),
        'lt': ('🇱🇹', 'Lituânia'),
        'lu': ('🇱🇺', 'Luxemburgo'),
        'lv': ('🇱🇻', 'Letônia'),
        'mo': ('🇲🇴', 'Macau, RAE da China'),
        'mf': ('🇲🇫', 'São Martinho'),
        'ma': ('🇲🇦', 'Marrocos'),
        'mc': ('🇲🇨', 'Mônaco'),
        'md': ('🇲🇩', 'Moldávia'),
        'mg': ('🇲🇬', 'Madagascar'),
        'mv': ('🇲🇻', 'Maldivas'),
        'mx': ('🇲🇽', 'México'),
        'mh': ('🇲🇭', 'Ilhas Marshall'),
        'mk': ('🇲🇰', 'Macedônia do Norte'),
        'ml': ('🇲🇱', 'Mali'),
        'mt': ('🇲🇹', 'Malta'),
        'mm': ('🇲🇲', 'Mianmar (Birmânia)'),
        'me': ('🇲🇪', 'Montenegro'),
        'mn': ('🇲🇳', 'Mongólia'),
        'mp': ('🇲🇵', 'Ilhas Marianas do Norte'),
        'mz': ('🇲🇿', 'Moçambique'),
        'mr': ('🇲🇷', 'Mauritânia'),
        'ms': ('🇲🇸', 'Montserrat'),
        'mq': ('🇲🇶', 'Martinica'),
        'mu': ('🇲🇺', 'Maurício'),
        'mw': ('🇲🇼', 'Malaui'),
        'my': ('🇲🇾', 'Malásia'),
        'yt': ('🇾🇹', 'Mayotte'),
        'na': ('🇳🇦', 'Namíbia'),
        'nc': ('🇳🇨', 'Nova Caledônia'),
        'ne': ('🇳🇪', 'Níger'),
        'nf': ('🇳🇫', 'Ilha Norfolk'),
        'ng': ('🇳🇬', 'Nigéria'),
        'ni': ('🇳🇮', 'Nicarágua'),
        'nu': ('🇳🇺', 'Niue'),
        'nl': ('🇳🇱', 'Países Baixos'),
        'no': ('🇳🇴', 'Noruega'),
        'np': ('🇳🇵', 'Nepal'),
        'nr': ('🇳🇷', 'Nauru'),
        'nz': ('🇳🇿', 'Nova Zelândia'),
        'om': ('🇴🇲', 'Omã'),
        'pk': ('🇵🇰', 'Paquistão'),
        'pa': ('🇵🇦', 'Panamá'),
        'pn': ('🇵🇳', 'Ilhas Pitcairn'),
        'pe': ('🇵🇪', 'Peru'),
        'ph': ('🇵🇭', 'Filipinas'),
        'pw': ('🇵🇼', 'Palau'),
        'pg': ('🇵🇬', 'Papua-Nova Guiné'),
        'pl': ('🇵🇱', 'Polônia'),
        'pr': ('🇵🇷', 'Porto Rico'),
        'kp': ('🇰🇵', 'Coreia do Norte'),
        'pt': ('🇵🇹', 'Portugal'),
        'py': ('🇵🇾', 'Paraguai'),
        'ps': ('🇵🇸', 'Territórios palestinos'),
        'pf': ('🇵🇫', 'Polinésia Francesa'),
        'qa': ('🇶🇦', 'Catar'),
        're': ('🇷🇪', 'Reunião'),
        'ro': ('🇷🇴', 'Romênia'),
        'ru': ('🇷🇺', 'Rússia'),
        'rw': ('🇷🇼', 'Ruanda'),
        'sa': ('🇸🇦', 'Arábia Saudita'),
        'sd': ('🇸🇩', 'Sudão'),
        'sn': ('🇸🇳', 'Senegal'),
        'sg': ('🇸🇬', 'Singapura'),
        'gs': ('🇬🇸', 'Ilhas Geórgia do Sul e Sandwich do Sul'),
        'sh': ('🇸🇭', 'Santa Helena'),
        'sj': ('🇸🇯', 'Svalbard e Jan Mayen'),
        'sb': ('🇸🇧', 'Ilhas Salomão'),
        'sl': ('🇸🇱', 'Serra Leoa'),
        'sv': ('🇸🇻', 'El Salvador'),
        'sm': ('🇸🇲', 'San Marino'),
        'so': ('🇸🇴', 'Somália'),
        'pm': ('🇵🇲', 'São Pedro e Miquelão'),
        'rs': ('🇷🇸', 'Sérvia'),
        'ss': ('🇸🇸', 'Sudão do Sul'),
        'st': ('🇸🇹', 'São Tomé e Príncipe'),
        'sr': ('🇸🇷', 'Suriname'),
        'sk': ('🇸🇰', 'Eslováquia'),
        'si': ('🇸🇮', 'Eslovênia'),
        'se': ('🇸🇪', 'Suécia'),
        'sz': ('🇸🇿', 'Essuatíni'),
        'sx': ('🇸🇽', 'Sint Maarten'),
        'sc': ('🇸🇨', 'Seicheles'),
        'sy': ('🇸🇾', 'Síria'),
        'tc': ('🇹🇨', 'Ilhas Turcas e Caicos'),
        'td': ('🇹🇩', 'Chade'),
        'tg': ('🇹🇬', 'Togo'),
        'th': ('🇹🇭', 'Tailândia'),
        'tj': ('🇹🇯', 'Tadjiquistão'),
        'tk': ('🇹🇰', 'Tokelau'),
        'tm': ('🇹🇲', 'Turcomenistão'),
        'tl': ('🇹🇱', 'Timor-Leste'),
        'to': ('🇹🇴', 'Tonga'),
        'tt': ('🇹🇹', 'Trinidad e Tobago'),
        'tn': ('🇹🇳', 'Tunísia'),
        'tr': ('🇹🇷', 'Turquia'),
        'tv': ('🇹🇻', 'Tuvalu'),
        'tw': ('🇹🇼', 'Taiwan'),
        'tz': ('🇹🇿', 'Tanzânia'),
        'ug': ('🇺🇬', 'Uganda'),
        'ua': ('🇺🇦', 'Ucrânia'),
        'um': ('🇺🇲', 'Ilhas Menores Distantes dos EUA'),
        'uy': ('🇺🇾', 'Uruguai'),
        'us': ('🇺🇸', 'Estados Unidos'),
        'uz': ('🇺🇿', 'Uzbequistão'),
        'va': ('🇻🇦', 'Cidade do Vaticano'),
        'vc': ('🇻🇨', 'São Vicente e Granadinas'),
        've': ('🇻🇪', 'Venezuela'),
        'vg': ('🇻🇬', 'Ilhas Virgens Britânicas'),
        'vi': ('🇻🇮', 'Ilhas Virgens Americanas'),
        'vn': ('🇻🇳', 'Vietnã'),
        'vu': ('🇻🇺', 'Vanuatu'),
        'wf': ('🇼🇫', 'Wallis e Futuna'),
        'ws': ('🇼🇸', 'Samoa'),
        'ye': ('🇾🇪', 'Iêmen'),
        'za': ('🇿🇦', 'África do Sul'),
        'zm': ('🇿🇲', 'Zâmbia'),
        'zw': ('🇿🇼', 'Zimbábue'),
    }
    if isinstance(pais, str):
        if pais.startswith('__ISO__:'):
            pais = pais.split(':', 1)[1].lower()
        import re
        m_codigo = re.match(r'^([a-z]{2})\s+', pais.lower())
        if m_codigo:
            pais = m_codigo.group(1)
    info = PAIS_NOME.get(pais) or PAIS_CODIGO.get(pais.lower()) if isinstance(pais, str) else None
    if info:
        return liga + ' (' + info[0] + ' ' + info[1] + ')'
    return liga

def _odds_do_mercado(stats, tipo, extra_val=None):
    odds = (stats or {}).get('odds_mercados', {})
    if tipo in ('gol_intervalo','over_gol','over_15'):
        try:
            limite_linha=float(extra_val)
        except (TypeError, ValueError):
            return 'indisponível', 'indisponível'
        prefixo='BET365_GOLS1T_' if tipo=='gol_intervalo' else 'BET365_GOLS_'
        asiatico_linha=str(int(limite_linha+0.5)).replace('.','_')
        limite_txt=str(limite_linha).replace('.','_')
        asiaticos=[prefixo+'OVER_'+asiatico_linha+'_LIVE']
        limites=[prefixo+'OVER_'+limite_txt+'_LIVE']
        def achar(lista):
            for nome in lista:
                if nome in odds and odds[nome] > 1:
                    return f'{odds[nome]:.2f}'
            return 'indisponível'
        return achar(asiaticos), achar(limites)
    if tipo == 'ambas_marcam':
        for nome in ('BET365_AMBAS_YES_LIVE',):
            if nome in odds and odds[nome] > 1:
                return f'{odds[nome]:.2f}', None
        return 'indisponível', None
    if extra_val is None:
        return 'indisponível', None
    try:
        linha=float(extra_val)
    except (TypeError, ValueError):
        return 'indisponível','indisponível'
    prefixo='BET365_CANTO1T_OVER_' if tipo=='escanteio_ht' else 'BET365_CANTO_OVER_'
    sufixo=str(linha).replace('.','_')
    asiaticos=[prefixo+sufixo+'_LIVE',prefixo+sufixo.replace('_0','')+'_LIVE']
    limite=[]
    if linha.is_integer():
        # A linha limite fica meio ponto abaixo da linha asiática:
        # asiático 4.0 -> limite 3.5; asiático 10.0 -> limite 9.5.
        meio=str(int(linha)-1)+'_5'
        limite=[prefixo+meio+'_LIVE']
    else:
        limite=[]
    def achar(lista):
        for nome in lista:
            if nome in odds and odds[nome] > 1:
                return f'{odds[nome]:.2f}'
        return 'indisponível'
    return achar(asiaticos), achar(limite)


def _odd_real_disponivel(stats, tipo, extra_val):
    """Retorna a odd do mercado encontrada pela API; None se a linha não existir."""
    odds = (stats or {}).get('odds_mercados', {})
    if not isinstance(odds, dict):
        return None
    try:
        extra = float(extra_val)
    except (TypeError, ValueError):
        return None
    if tipo == 'escanteio_ht':
        prefix = 'BET365_CANTO1T_OVER_'
        alvo = extra + 1.0
        partes = [str(int(alvo)) if alvo.is_integer() else str(alvo).replace('.', '_')]
    elif tipo == 'escanteio_ft':
        prefix = 'BET365_CANTO_OVER_'
        alvo = extra + 1.0
        partes = [str(int(alvo)) if alvo.is_integer() else str(alvo).replace('.', '_')]
    elif tipo == 'gol_intervalo':
        prefix = 'BET365_GOLS1T_OVER_'
        partes = ['0_5']
    elif tipo in ('gol_partida', 'over_gol'):
        prefix = 'BET365_GOLS_OVER_'
        alvo = extra + 0.5
        partes = [str(alvo).replace('.', '_')]
    elif tipo == 'over_15':
        prefix = 'BET365_GOLS_OVER_'
        partes = ['1_5']
    elif tipo == 'ambas_marcam':
        partes = []
        prefix = 'BET365_AMBAS_YES'
    else:
        return None
    candidatos = []
    if tipo == 'ambas_marcam':
        candidatos = [k for k in odds if k.startswith(prefix) and k.endswith('_LIVE')]
    else:
        for parte in partes:
            candidatos.extend((prefix + parte + '_LIVE', prefix + parte, prefix + parte.replace('_0', '') + '_LIVE'))
    for chave in candidatos:
        valor = odds.get(chave)
        try:
            if float(valor) > 1:
                return float(valor)
        except (TypeError, ValueError):
            continue
    return None


def msg_universal(home, away, minuto, liga, pais, n, mercado, entrada, placar, extra_val=None, cantos_atual=0, stats=None, sh=0, sa=0, fav_final='h', odd_h=None, odd_a=None, odd_b365=None, odd_bano=None, nome=None, tipo='', probabilidade=None):
    NL = chr(10)
    chutes_h = stats.get('chutes_tot_h', 0) if stats else 0
    chutes_a = stats.get('chutes_tot_a', 0) if stats else 0
    alvo_h = stats.get('chutes_gol_h', 0) if stats else 0
    alvo_a = stats.get('chutes_gol_a', 0) if stats else 0
    tentativas_h = stats.get('goal_attempts_h', 0) if stats else 0
    tentativas_a = stats.get('goal_attempts_a', 0) if stats else 0
    grandes_h = stats.get('big_chances_h', 0) if stats else 0
    grandes_a = stats.get('big_chances_a', 0) if stats else 0
    dentro_h = stats.get('chutes_inside_h', 0) if stats else 0
    dentro_a = stats.get('chutes_inside_a', 0) if stats else 0
    cant_h = max(0, stats.get('escanteios_h', 0) if stats else 0)
    cant_a = max(0, stats.get('escanteios_a', 0) if stats else 0)
    atq_per_h = stats.get('ataques_perigosos_h', 0) if stats else 0
    atq_per_a = stats.get('ataques_perigosos_a', 0) if stats else 0
    pressao_h = stats.get('pressure_bar_h', 0) if stats else 0
    pressao_a = stats.get('pressure_bar_a', 0) if stats else 0
    dapm10_h = _get_float(stats.get('dapm10_h', 0)) if stats else 0
    dapm10_a = _get_float(stats.get('dapm10_a', 0)) if stats else 0
    dapm5_h = _get_float(stats.get('dapm5_h', 0)) if stats else 0
    dapm5_a = _get_float(stats.get('dapm5_a', 0)) if stats else 0
    atq_max = max(atq_per_h, atq_per_a)
    appm_val = round(atq_max / minuto, 2) if minuto > 0 else 0
    if atq_per_h > atq_per_a:
        quem = 'do Mandante'
        dominante = home
    elif atq_per_a > atq_per_h:
        quem = 'do Visitante'
        dominante = away
    else:
        quem = 'de ambas equipes'
        dominante = 'Ambos'
    if appm_val >= 2.0:
        alerta = 'Pressão Constante.'
    elif appm_val >= 1.5:
        alerta = 'Pegando Fogo.'
    elif appm_val >= 1.0:
        alerta = 'Ritmo Intenso.'
    elif appm_val >= 0.8:
        alerta = 'Pressão ' + quem + '.'
    elif appm_val >= 0.7:
        alerta = 'Ritmo Moderado.'
    elif appm_val >= 0.5:
        alerta = 'Ritmo Médio.'
    elif appm_val >= 0.3:
        alerta = 'Ritmo Fraco.'
    else:
        alerta = 'Ritmo Muito Baixo.'
    appm = appm_val
    dapm10 = max(dapm10_h, dapm10_a)
    dapm5 = max(dapm5_h, dapm5_a)
    title = nome if nome else mercado
    atencao_over = ''
    if tipo == 'gol_intervalo':
        atencao_over = (NL + '<b>          ⚠️ATENÇÃO⚠️</b>' + NL +
                        '<b>👉Não Saiu o Gol até os 35 minutos, fazer a Proteção em Canto Asiático e Limite HT⛳️</b>')
    elif tipo in ('over_gol', 'gol_partida'):
        atencao_over = (NL + '<b>          ⚠️ATENÇÃO⚠️</b>' + NL +
                        '<b>👉Não Saiu o Gol até os 85 minutos, fazer a Proteção em Canto Asiático e Limite FT⛳️</b>')
    if tipo in ('escanteio', 'corner', 'escanteio_ht', 'escanteio_ft'):
        linha = cantos_atual + 1.0
        entrada = 'Mais de ' + f'{linha:.1f}' + ' Asiático⛳️'
    elif tipo in ('gol_intervalo', 'over_gol', 'over_15', 'ambas_marcam', 'over', 'gol_partida'):
        if 'Over' not in str(entrada) and 'Ambas' not in str(entrada):
            if tipo == 'over_15':
                entrada = 'Over 1.5'
            elif tipo == 'ambas_marcam':
                entrada = 'Ambas Marcam'
            elif tipo == 'gol_intervalo':
                entrada = 'Over 0.5'
            elif tipo in ('over_gol', 'over', 'gol_partida'):
                linha = sh + sa + 0.5
                entrada = f'Mais de {linha}'
        entrada = entrada + '⚽️'
    elif 'CORNER' in mercado or 'ESCANTEIO' in mercado or (nome and 'CANTO' in nome.upper()):
        linha = cantos_atual + 1.0
        entrada = 'Mais de ' + f'{linha:.1f}' + ' Asiático⛳️'
    elif 'Over' not in str(entrada) and 'Ambas' not in str(entrada):
        entrada = entrada + '⚽️'
    if fav_final == 'h':
        fav_nome = home
    elif fav_final == 'a':
        fav_nome = away
    else:
        fav_nome = '—'
    # Valores fixos apenas como recomendação, sem representar a odd ao vivo capturada.
    odd_texto = '<b>💰Odd Asiático Mínima: 1.90</b>' + NL + '<b>💰Odd Limite Mínima: 1.70</b>'
    prob_texto = (NL + f'<b>📊 Probabilidade: {probabilidade}%</b>') if probabilidade is not None else ''
    sep = '━' * 22
    liga_formatada=nome_liga_exibicao(liga, pais)
    import re
    m_liga_pais=re.match(r'^(.*) \(([^)]+)\)$', liga_formatada)
    if m_liga_pais:
        liga=m_liga_pais.group(1)
        pais_com_flag=m_liga_pais.group(2)
        partes_pais=pais_com_flag.split(' ', 1)
        pais_texto=(partes_pais[1]+partes_pais[0]) if len(partes_pais)==2 else pais_com_flag
    else:
        liga=liga_formatada
        pais_texto=''
    liga_texto = '<b>🌍 Liga: ' + liga + '</b>'
    pais_texto_linha = '<b>🗺️País: ' + pais_texto + '</b>' if pais_texto else ''
    msg = f'{sep}' + NL + f'<b>{title}</b>' + NL + f'{sep}' + NL + f'<b>⚽️ Placar: {placar}</b>' + NL + f'{liga_texto}' + (NL + pais_texto_linha if pais_texto_linha else '') + NL + f'<b>📡 {home} x {away}</b>' + NL + f'<b>👀 ODDs: Casa {(odd_h if odd_h else chr(8212))} / Fora {(odd_a if odd_a else chr(8212))}</b>' + NL + '<b>⏰️ Minuto: ' + str(minuto) + "'</b>" + NL + f'{sep}' + NL + '<b>📊 Estatísticas ao Vivo da Partida:</b>' + NL + f'<b>🚀 Chutes totais: {chutes_h} | {chutes_a}</b>' + NL + f'<b>🎯 Chutes no alvo: {alvo_h} | {alvo_a}</b>' + NL + f'<b>⚡️ Tentativas de gol: {tentativas_h} | {tentativas_a}</b>' + NL + f'<b>💥 Grandes chances criadas: {grandes_h} | {grandes_a}</b>' + NL + f'<b>🥅 Chutes na área: {dentro_h} | {dentro_a}</b>' + NL + f'<b>⛳️ Escanteios: {cant_h} | {cant_a}</b>' + NL + f'<b>⚔️ Ataques perigosos: {atq_per_h} | {atq_per_a}</b>' + NL + f'<b>🌋 Pressão da partida: {pressao_h} | {pressao_a}</b>' + NL + f'<b>🔥 APPM da partida: {appm}</b>' + NL + f'<b>🔥 APPM últimos 10 min: {dapm10}</b>' + NL + f'<b>🔥 APPM últimos 5 min: {dapm5}</b>' + NL + f'{sep}' + NL + '<b>💡 Análise Técnica da Partida:</b>' + NL + f'<b>🎯 Favorito: {fav_nome}</b>' + NL + f'<b>🚨 Alerta: {alerta}</b>' + NL + f'{sep}' + NL + f'<b>📌 Entrada: {entrada}</b>' + prob_texto + NL + odd_texto + NL + f'{sep}' + atencao_over
    keyboard = {'inline_keyboard': [[{'text': '🟣BET365🟣', 'url': 'https://www.bet365.bet.br/#/AZ/'}, {'text': '🟠BETANO🟠', 'url': 'https://www.betano.bet.br/live/'}]]}
    return (msg, keyboard)

def checar_resultado(sinal):
    """Verifica se um sinal já enviado deu green ou red usando SokkerPro."""
    try:
        fid_raw = str(sinal.get('fixture_id', '')).replace('skp_', '')
        mercado = sinal.get('mercado')
        data = _get_data()
        if not data:
            return None
        fixture = None
        for cat in data['data']['sortedCategorizedFixtures']:
            for fix in cat['fixtures']:
                if str(fix.get('fixtureId', '')) == str(fid_raw):
                    fixture = fix
                    break
            if fixture:
                break
        if not fixture:
            # O jogo pode já ter saído de /livescores. Busca o resultado
            # definitivo diretamente pelo fixtureId na própria SokkerPro.
            try:
                detalhe = requests.get(
                    f'https://m2.sokkerpro.com/fixture/{fid_raw}',
                    headers={'User-Agent': 'Mozilla/5.0'}, timeout=10
                ).json()
                fixture = detalhe.get('data') if detalhe.get('success') else None
                if fixture:
                    eh_corner_ht = mercado in ('CORNER_HT', 'escanteio_ht') or sinal.get('tipo') == 'escanteio_ht'
                    if eh_corner_ht and fixture.get('localCornersHT') is not None:
                        fixture = dict(fixture)
                        fixture['localCorners'] = fixture.get('localCornersHT')
                        fixture['visitorCorners'] = fixture.get('visitorCornersHT')
            except Exception as e:
                print(f'[AUDITORIA] Fixture {fid_raw} indisponível: {e}')
                return None
        if not fixture:
            return None
        # Auditoria de escanteio HT deve usar exclusivamente os campos
        # confirmados do primeiro tempo. Nunca aceitar os campos totais
        # como substitutos, pois eles podem voltar zerados/inconsistentes
        # enquanto a partida ainda está no segundo tempo.
        eh_corner_ht_sinal = (
            mercado in ('CORNER_HT', 'escanteio_ht')
            or (mercado and mercado.startswith('custom_') and sinal.get('tipo') == 'escanteio_ht')
            or sinal.get('tipo') == 'escanteio_ht'
        )
        if eh_corner_ht_sinal:
            raw_ht_h = fixture.get('localCornersHT')
            raw_ht_a = fixture.get('visitorCornersHT')
            invalid_ht = (
                raw_ht_h is None or raw_ht_a is None
                or str(raw_ht_h).strip() in ('', 'x', 'X', 'None')
                or str(raw_ht_a).strip() in ('', 'x', 'X', 'None')
            )
            if invalid_ht:
                print(f'[AUDITORIA] {fid_raw}: escanteios HT ainda indisponíveis; aguardando nova leitura')
                return None
            total_ht_corners = _get_int(raw_ht_h, default=-1) + _get_int(raw_ht_a, default=-1)
            if total_ht_corners < 0:
                return None
            # Escanteios não podem diminuir. Se a API devolver HT menor que
            # o total já registrado no momento da entrada, é leitura inválida
            # e não pode gerar RED.
            entrada_cantos = sinal.get('extra_val')
            if entrada_cantos is not None and total_ht_corners < int(entrada_cantos):
                print(f'[AUDITORIA] {fid_raw}: leitura HT inconsistente ({total_ht_corners} < entrada {entrada_cantos}); aguardando nova leitura')
                return None
            fixture = dict(fixture)
            fixture['localCorners'] = raw_ht_h
            fixture['visitorCorners'] = raw_ht_a
        # Mercados de escanteio HT sempre usam os escanteios do primeiro tempo.
        # O /livescores pode trazer o jogo ainda presente com os campos totais;
        # nesse caso, priorizar explicitamente os campos HT para não classificar
        # um reembolso como red (ou um green como red).
        if sinal.get('tipo') == 'escanteio_ht' and fixture.get('localCornersHT') is not None:
            fixture = dict(fixture)
            fixture['localCorners'] = fixture.get('localCornersHT')
            fixture['visitorCorners'] = fixture.get('visitorCornersHT')
        # O status oficial da SokkerPro é a fonte da verdade para o fim do período.
        # Não usar o minuto numérico: em 45+X/90+X ele pode antecipar a auditoria
        # enquanto ainda há acréscimos para jogar.
        status = str(fixture.get('status', '')).strip().upper()
        is_final = status in ('FT', 'PEN', 'AET')
        is_2h = status in ('2ND', 'HT')
        mercados_ht = ['HT', 'CORNER_HT', 'BTTS', 'escanteio_ht']
        eh_mercado_ht = mercado in mercados_ht or (mercado and mercado.startswith('custom_') and (sinal.get('tipo') in ('escanteio_ht', 'gol_intervalo')))
        if not (is_final or (eh_mercado_ht and is_2h)):
            return None
        gh = int(fixture.get('scoresLocalTeam', 0) or 0)
        ga = int(fixture.get('scoresVisitorTeam', 0) or 0)
        total_final = gh + ga
        total_ht = int(fixture.get('scoresHT', 0) or 0)
        entry_total = sinal.get('entry_total')
        if mercado in ('HT', 'over_05_ht', 'gol_intervalo'):
            return 'green' if entry_total is not None and total_ht > entry_total else 'red' if entry_total is not None and (is_2h or is_final) else None
        elif mercado == 'BTTS':
            return 'green' if gh >= 1 and ga >= 1 else 'red' if is_final else None
        elif mercado == 'OFT':
            return 'green' if entry_total is not None and total_final > entry_total else 'red' if entry_total is not None and is_final else None
        elif mercado == 'OVERGOAL':
            gols_entrada = sinal.get('extra_val', 0)
            return 'green' if total_final > gols_entrada else 'red' if is_final else None
        elif mercado in ['CORNER_HT']:
            if status not in ('HT', 'FT') and (not is_final):
                return None
            c_final = _get_corner_total(fixture)
            if c_final is None:
                return None
            c_entrada = sinal.get('extra_val', 0)
            linha_asian = c_entrada + 1
            if c_final > linha_asian:
                return 'green'
            if c_final == linha_asian:
                return 'refund'
            return 'red'
        elif mercado == 'CORNER_FT':
            c_final = _get_corner_total(fixture)
            if c_final is None:
                return None
            c_entrada = sinal.get('extra_val', 0)
            linha_asian = c_entrada + 1
            if c_final > linha_asian:
                return 'green'
            if c_final == linha_asian:
                return 'refund'
            return 'red' if is_final else None
        elif mercado and mercado.startswith('custom_'):
            extra = sinal.get('extra_val')
            tipo_mkt = sinal.get('tipo', '')
            if tipo_mkt == 'gol_intervalo':
                return 'green' if entry_total is not None and total_ht > entry_total else 'red' if entry_total is not None and (is_2h or is_final) else None
            elif tipo_mkt == 'gol_partida':
                return 'green' if total_final > extra else 'red' if is_final else None
            elif tipo_mkt == 'over_15':
                return 'green' if entry_total is not None and total_final > entry_total else 'red' if entry_total is not None and is_final else None
            elif tipo_mkt == 'ambas_marcam':
                return 'green' if gh >= 1 and ga >= 1 else 'red' if is_final else None
            elif tipo_mkt == 'escanteio_ht':
                if status not in ('HT', 'FT') and (not is_final):
                    return None
                c_final = _get_corner_total(fixture)
                if c_final is None:
                    return None
                c_entrada = extra if extra is not None else 0
                linha_asian = c_entrada + 1
                if c_final > linha_asian:
                    return 'green'
                if c_final == linha_asian:
                    return 'refund'
                return 'red'
            elif tipo_mkt == 'escanteio_ft':
                c_final = _get_corner_total(fixture)
                if c_final is None:
                    return None
                c_entrada = extra if extra is not None else 0
                linha_asian = c_entrada + 1
                if c_final > linha_asian:
                    return 'green'
                if c_final == linha_asian:
                    return 'refund'
                return 'red' if is_final else None
            if extra is not None:
                if total_final > extra:
                    return 'green'
                return 'red' if is_final else None
            return None
        extra = sinal.get('extra_val')
        tipo_mkt = sinal.get('tipo', '')
        if tipo_mkt == 'gol_intervalo':
            return 'green' if entry_total is not None and total_ht > entry_total else 'red' if entry_total is not None and (is_2h or is_final) else None
        elif tipo_mkt == 'over_15':
            return 'green' if entry_total is not None and total_final > entry_total else 'red' if entry_total is not None and is_final else None
        elif tipo_mkt in ('over_gol', 'over'):
            return 'green' if total_final > extra else 'red' if is_final else None
        elif tipo_mkt == 'ambas_marcam':
            return 'green' if gh >= 1 and ga >= 1 else 'red' if is_final else None
        elif tipo_mkt == 'escanteio_ht':
            if status not in ('HT', 'FT') and (not is_final):
                return None
            c_final = _get_corner_total(fixture)
            if c_final is None:
                return None
            c_entrada = extra if extra is not None else 0
            linha_asian = c_entrada + 1
            if c_final > linha_asian:
                return 'green'
            if c_final == linha_asian:
                return 'refund'
            return 'red'
        elif tipo_mkt == 'escanteio_ft':
            if not is_final:
                return None
            c_final = _get_corner_total(fixture)
            if c_final is None:
                return None
            c_entrada = extra if extra is not None else 0
            linha_asian = c_entrada + 1
            if c_final > linha_asian:
                return 'green'
            if c_final == linha_asian:
                return 'refund'
            return 'red'
        return None
    except:
        return None

# ========== VIP PIX (ASAAS) — polling phase 1 ==========
VIP_CHAT_ID = int(os.environ.get('VIP_GROUP_CHAT_ID', '-1003843430798'))
VIP_PRICE, VIP_DAYS, VIP_GRACE_HOURS = 50.0, 30, 24
VIP_STATE_FILE = os.path.join(BASE_DIR, 'vip_state.json')
VIP_ASAAS_BASE = 'https://api.asaas.com/v3'

def _vip_admin_ids():
    return {int(x.strip()) for x in os.environ.get('VIP_ADMIN_IDS', '').split(',') if x.strip()}

def _vip_state_load():
    state = {'payments': {}, 'members': {}}
    if GITHUB_TOKEN and GITHUB_REPO:
        try:
            r = requests.get(f'https://api.github.com/repos/{GITHUB_REPO}/contents/vip_state.json', headers={'Authorization': f'Bearer {GITHUB_TOKEN}', 'Accept': 'application/vnd.github+json'}, timeout=10)
            if r.status_code == 200: state = json.loads(base64.b64decode(r.json()['content']).decode())
        except Exception as e: print(f'[VIP] Estado remoto indisponível: {e}')
    elif os.path.exists(VIP_STATE_FILE):
        try:
            with open(VIP_STATE_FILE) as f: state = json.load(f)
        except Exception as e: print(f'[VIP] Estado local inválido: {e}')
    state.setdefault('payments', {}); state.setdefault('members', {}); state.setdefault('awaiting_cpf', {})
    return state

def _vip_state_save(state):
    with open(VIP_STATE_FILE, 'w') as f: json.dump(state, f, ensure_ascii=False, indent=2)
    return _save_json_api('vip_state.json', state, 'state: atualiza VIP Pix [skip ci]') if GITHUB_TOKEN and GITHUB_REPO else True

def _vip_headers():
    key = os.environ.get('ASAAS_API_KEY') or os.environ.get('ASAAS_TOKEN')
    return {'access_token': key, 'Content-Type': 'application/json', 'User-Agent': 'sokkerpro-vip/1'} if key else None

def _vip_send(chat_id, text):
    return requests.post(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage', json={'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML', 'disable_web_page_preview': True}, timeout=15)

def _vip_sales_message():
    phone = os.environ.get('VIP_SUPPORT_WHATSAPP', '').strip()
    support = f'📱 Suporte WhatsApp: {phone}\n' if phone else ''
    return ('━━━━━━━━━━━━━━━━━━━━\n<b>🚀 MÁQUINA DE GREENS VIP</b>\n━━━━━━━━━━━━━━━━━━━━\n\n🔥 <b>SINAIS AO VIVO COM ALTA ASSERTIVIDADE</b>\n\n📊 <b>6 MERCADOS:</b>\n⚽️ Over Gol Intervalo\n⚽️ Over Gol Partida\n⚽️ Over 1.5 Gols Partida\n⚽️ Ambas Marcam\n🚩 Escanteio Limite HT\n🚩 Escanteio Limite FT\n\n💰 <b>Investimento: R$ 50,00</b>\n📅 <b>Acesso: 30 dias + 24h de tolerância</b>\n💳 Pagamento via <b>PIX</b> com aprovação automática\n\n⚠️ Clique aqui👉<b>/vip</b> para gerar seu PIX.\n👤 Telegram: <b>@maquinadegreensvip</b>\n' + support + 'ℹ️ Comandos: /vip — gerar PIX | /vipstatus — consultar status\n🛟 Em caso de dúvida, procure o suporte.')

def _vip_create_payment(chat_id, user, cpf_cnpj):
    headers = _vip_headers()
    if not headers: return None, 'Pagamento temporariamente indisponível. Tente novamente mais tarde.'
    try:
        c = requests.post(f'{VIP_ASAAS_BASE}/customers', headers=headers, json={'name': (user.get('first_name') or 'Cliente VIP')[:80], 'cpfCnpj': cpf_cnpj, 'externalReference': f'telegram:{chat_id}'}, timeout=15)
        if c.status_code not in (200, 201): return None, 'Não foi possível iniciar o pagamento.'
        cid = c.json()['id']
        p = requests.post(f'{VIP_ASAAS_BASE}/payments', headers=headers, json={'customer': cid, 'billingType': 'PIX', 'value': VIP_PRICE, 'dueDate': datetime.now(BRT).strftime('%Y-%m-%d'), 'description': 'Acesso Máquina de Greens VIP - 30 dias', 'externalReference': f'telegram:{chat_id}'}, timeout=15)
        if p.status_code not in (200, 201): return None, 'Não foi possível gerar o PIX.'
        pid = p.json()['id']; q = requests.get(f'{VIP_ASAAS_BASE}/payments/{pid}/pixQrCode', headers=headers, timeout=15)
        if q.status_code != 200: return None, 'PIX indisponível no momento. Tente novamente.'
        return {'id': pid, 'customer_id': cid, 'payload': q.json().get('payload', '')}, None
    except requests.RequestException as e:
        print(f'[VIP] Asaas indisponível: {e}'); return None, 'Serviço de pagamento indisponível. Tente mais tarde.'

VIP_POLL_ENABLED = os.environ.get('VIP_POLL_ENABLED', '').strip().lower() in ('1', 'true', 'yes')

def run_vip_maintenance():
    """Run VIP payment/member maintenance only when explicitly enabled."""
    state = _vip_state_load()
    if _vip_poll_and_expire(state):
        _vip_state_save(state)

def _vip_poll_and_expire(state):
    headers = _vip_headers(); changed = False
    if headers:
        for pid, item in state['payments'].items():
            if item.get('status') in ('RECEIVED', 'CONFIRMED', 'EXPIRED'): continue
            try:
                r = requests.get(f'{VIP_ASAAS_BASE}/payments/{pid}', headers=headers, timeout=15)
                if r.status_code != 200: continue
                status = r.json().get('status', ''); item['status'] = status; changed = True
                if status in ('RECEIVED', 'CONFIRMED') and not item.get('activated_at'):
                    now = datetime.now(timezone.utc); exp = now + timedelta(days=VIP_DAYS); uid = str(item['chat_id'])
                    link = requests.post(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/createChatInviteLink', json={'chat_id': VIP_CHAT_ID, 'name': f'VIP {uid}', 'creates_join_request': True}, timeout=15)
                    invite = link.json().get('result', {}).get('invite_link') if link.ok and link.json().get('ok') else None
                    item.update({'activated_at': now.isoformat(), 'expires_at': exp.isoformat()}); state['members'][uid] = {'chat_id': item['chat_id'], 'expires_at': exp.isoformat(), 'payment_id': pid}
                    _vip_send(item['chat_id'], f'✅ <b>Pagamento confirmado!</b>\n\nSeu acesso VIP é válido por 30 dias.\n' + (f'\n🔗 Entre pelo convite: {invite}' if invite else '\nConvite pendente; contate o suporte.'))
            except requests.RequestException as e: print(f'[VIP] Poll {pid}: {e}')
    # Approve only paid users' pending join requests; never approve unknown users.
    try:
        pending = requests.get(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/getChatJoinRequests', params={'chat_id': VIP_CHAT_ID, 'limit': 100}, timeout=15)
        if pending.ok and pending.json().get('ok'):
            for join in pending.json().get('result', []):
                uid = str(join.get('from', {}).get('id', ''))
                if uid in state['members'] and not state['members'][uid].get('removed_at'):
                    ar = requests.post(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/approveChatJoinRequest', json={'chat_id': VIP_CHAT_ID, 'user_id': int(uid)}, timeout=15)
                    if ar.ok and ar.json().get('ok'): changed = True
    except requests.RequestException as e: print(f'[VIP] Join requests indisponíveis: {e}')
    now = datetime.now(timezone.utc)
    for uid, m in state['members'].items():
        if m.get('removed_at'): continue
        try: deadline = datetime.fromisoformat(m['expires_at']) + timedelta(hours=VIP_GRACE_HOURS)
        except (KeyError, ValueError): continue
        if now >= deadline:
            r = requests.post(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/banChatMember', json={'chat_id': VIP_CHAT_ID, 'user_id': int(uid), 'until_date': int(now.timestamp()) + 60}, timeout=15)
            if r.ok and r.json().get('ok'):
                requests.post(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/unbanChatMember', json={'chat_id': VIP_CHAT_ID, 'user_id': int(uid), 'only_if_banned': True}, timeout=15); m['removed_at'] = now.isoformat(); changed = True
    return changed

def _vip_handle(chat_id, msg):
    if chat_id <= 0: return
    state = _vip_state_load()
    text = (msg.get('text') or '').strip()
    uid = str(chat_id)
    if uid in state.get('awaiting_cpf', {}) and not text.startswith('/'):
        cpf_cnpj = ''.join(ch for ch in text if ch.isdigit())
        if len(cpf_cnpj) not in (11, 14):
            _vip_send(chat_id, 'Envie um CPF com 11 dígitos ou CNPJ com 14 dígitos para gerar o PIX.')
            return
        data, err = _vip_create_payment(chat_id, msg.get('from', {}), cpf_cnpj)
        if err:
            _vip_send(chat_id, err)
            return
        state['awaiting_cpf'].pop(uid, None)
        state['payments'][data['id']] = {'chat_id': chat_id, 'status': 'PENDING', 'created_at': datetime.now(timezone.utc).isoformat(), 'customer_id': data['customer_id']}
        _vip_state_save(state)
        _vip_send(chat_id, _vip_sales_message() + f'\n\n<b>PIX COPIA E COLA:</b>\n<code>{data["payload"]}</code>\n\nApós o pagamento, a confirmação e o convite serão enviados automaticamente.')
        return
    if text.partition(' ')[0].partition('@')[0].lower() != '/vip':
        return
    state['awaiting_cpf'][uid] = datetime.now(timezone.utc).isoformat()
    _vip_state_save(state)
    _vip_send(chat_id, _vip_sales_message() + '\n\nPara gerar sua cobrança Pix, envie agora seu CPF ou CNPJ apenas nesta conversa privada.')

def check_status_command(total_jogos_live=0, jogos_live=None, jogos_na_janela=None):
    last_id = 0
    last_id = 0
    try:
        req = request.Request(f'https://api.github.com/repos/{GITHUB_REPO}/contents/last_update.json', headers={'Authorization': f'Bearer {GITHUB_TOKEN}', 'Accept': 'application/vnd.github+json'})
        resp = request.urlopen(req, timeout=10)
        gh_data = json.loads(resp.read())
        gh_content = base64.b64decode(gh_data['content']).decode()
        last_id = json.loads(gh_content).get('last_id', 0)
        print(f'[CMD] last_id lido do GitHub: {last_id}')
    except Exception:
        pass
    sep = '━━━━━━━━━━━━━━━━━━━━━━'
    try:
        r = requests.get(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates', params={'offset': last_id + 1, 'timeout': 5}, timeout=10).json()
        if not r.get('ok'):
            return
    except Exception as e:
        print(f'[CMD] Erro ao consultar Telegram: {e}')
        return
    new_last_id = last_id
    radar_respondido = False
    relatorio_respondido = False
    agora_ts = datetime.now(timezone.utc).timestamp()
    for update in r.get('result', []):
        new_last_id = update['update_id']
        msg = update.get('message', {})
        text = msg.get('text', '')
        comando = text.partition(' ')[0].partition('@')[0].lower()
        chat_orig = msg.get('chat', {}).get('id', 0)
        msg_ts = msg.get('date', 0)
        if agora_ts - msg_ts > 600:
            continue
        if comando == '/start' and chat_orig > 0:
            _vip_send(chat_orig, _vip_sales_message())
        elif comando == '/vip':
            _vip_handle(chat_orig, msg)
        elif chat_orig > 0 and text and not text.startswith('/'):
            _vip_handle(chat_orig, msg)
        elif comando == '/vipstatus' and chat_orig in _vip_admin_ids():
            st = _vip_state_load(); _vip_send(chat_orig, f'VIP: {len(st["payments"])} pagamentos, {len(st["members"])} membros registrados.')
        if comando == '/relatoriomensal' and (not relatorio_respondido):
            msg = enviar_relatorio_mensal()
            requests.post(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage', json={'chat_id': chat_orig, 'text': msg, 'parse_mode': 'HTML'})
            relatorio_respondido = True
        if comando == '/relatoriogeral' and (not relatorio_respondido):
            msg = enviar_relatorio_geral()
            requests.post(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage', json={'chat_id': chat_orig, 'text': msg, 'parse_mode': 'HTML'})
            relatorio_respondido = True
        if comando == '/relatoriodiario' and (not relatorio_respondido):
            enviar_relatorio_diario()
            relatorio_respondido = True
        elif comando in ('/mercados', '/mercadosmensal', '/mercados24h'):
            try:
                if comando == '/mercadosmensal':
                    msg = gerar_layout_mercados_mensal()
                elif comando == '/mercados24h':
                    msg = gerar_layout_mercados_hoje()
                else:
                    msg = enviar_relatorio_performance()
                if msg:
                    requests.post(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage', json={'chat_id': chat_orig, 'text': msg, 'parse_mode': 'HTML'})
                else:
                    requests.post(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage', json={'chat_id': chat_orig, 'text': 'Ainda sem dados de performance registrados.', 'parse_mode': 'HTML'})
            except Exception as e:
                print(f'[PERFORMANCE] Erro: {e}')
        elif comando == '/radar' and (not radar_respondido):
            if DATA_UNAVAILABLE:
                msg_radar = f'{sep}\n📡👉<b>RADAR DE JOGOS AO VIVO</b>👈📡\n{sep}\n⚠️ <b>Fonte SokkerPro indisponível neste ciclo.</b>\n🔄 <b>O bot tentou consultar novamente e não recebeu uma resposta válida.</b>\n{sep}'
                requests.post(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage', json={'chat_id': chat_orig, 'text': msg_radar, 'parse_mode': 'HTML'}, timeout=10)
                radar_respondido = True
                continue
            jogos_live = jogos_live or []
            jogos_na_janela = jogos_na_janela or []
            if jogos_na_janela:
                linhas_janela = ''
                for j in jogos_na_janela:
                    h = j.get('home', '')
                    a = j.get('away', '')
                    m = j.get('minuto', 0)
                    sh = j.get('sh', 0)
                    sa = j.get('sa', 0)
                    liga = j.get('liga', '')
                    linhas_janela += f"🎯 <b>{h} x {a}</b> | {m}' | {sh}x{sa} | {liga}\n"
            else:
                linhas_janela = 'Nenhum jogo na janela no momento.'
            fora_janela = [j for j in jogos_live if j not in jogos_na_janela]
            if fora_janela:
                linhas_fora = ''
                for j in fora_janela[:10]:
                    h = j.get('home', '')
                    a = j.get('away', '')
                    m = j.get('minuto', 0)
                    sh = j.get('sh', 0)
                    sa = j.get('sa', 0)
                    linhas_fora += f"⏳ {h} x {a} | {m}' | {sh}x{sa}\n"
                if len(fora_janela) > 10:
                    linhas_fora += f'... e mais {len(fora_janela) - 10} jogos'
            else:
                linhas_fora = '—'
            msg_radar = f'{sep}\n📡👉<b>RADAR DE JOGOS AO VIVO</b>👈📡\n{sep}\n🔴 <b>{total_jogos_live} jogos ao vivo</b>\n🎯 <b>{len(jogos_na_janela)} na janela alvo</b>\n{sep}\n🚨<b>JOGOS NO ALVO:</b>\n{linhas_janela}{sep}\n<b>⏳ FORA DA JANELA:</b>\n{linhas_fora}{sep}'
            requests.post(f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage', json={'chat_id': chat_orig, 'text': msg_radar, 'parse_mode': 'HTML'}, timeout=10)
            radar_respondido = True
    if new_last_id > last_id:
        with open(LAST_UPDATE_FILE, 'w') as f:
            json.dump({'last_id': new_last_id}, f)
        if GITHUB_TOKEN and GITHUB_REPO:
            _save_json_api('last_update.json', {'last_id': new_last_id}, 'state: last_update [skip ci]')
        print(f'[CMD] last_id salvo: {new_last_id}')
_HIST_CACHE = {}

def get_media_gols_historica_skp(home, away, stats):
    """Retorna a média de gols por partida usando os campos medias da SokkerPro.
    As médias da SokkerPro já consideram no mínimo 10 jogos.
    Bloqueia mercados de gol se média < 2.30. Sem dados = bloqueia (retorna -1)."""
    chave = f'{home}_{away}'
    if chave in _HIST_CACHE:
        return _HIST_CACHE[chave]
    if not stats:
        _HIST_CACHE[chave] = -1.0
        return -1.0
    try:
        media_h = stats.get('medias_home_goal', 0)
        media_a = stats.get('medias_away_goal', 0)
        if media_h <= 0 and media_a <= 0:
            _HIST_CACHE[chave] = -1.0
            return -1.0
        media_total = media_h + media_a
        _HIST_CACHE[chave] = media_total
        return media_total
    except:
        _HIST_CACHE[chave] = -1.0
        return -1.0

def run_ciclo(sent, total_env, confirmed_ids=None):
    global CONFIG_MERCADOS
    CONFIG_MERCADOS = carregar_config_github()
    global MAPA_MERCADO
    MAPA_MERCADO = _gerar_mapa_mercados()
    'Executa um ciclo completo de coleta, análise e envio.'
    global _CACHED_DATA, DATA_UNAVAILABLE
    _CACHED_DATA = None
    DATA_UNAVAILABLE = False
    # Lê os comandos antes da coleta pesada, usando os dados do ciclo anterior.
    # Assim /radar não fica bloqueado esperando as consultas detalhadas.
    global _LAST_RADAR_DATA
    try:
        _radar_total, _radar_live, _radar_janela = _LAST_RADAR_DATA
    except NameError:
        _radar_total, _radar_live, _radar_janela = 0, [], []
    # No primeiro ciclo ainda não há cache: não consumir /radar respondendo 0.
    # O processamento normal, depois da coleta, responderá com os dados atuais.
    if _radar_total > 0:
        check_status_command(total_jogos_live=_radar_total, jogos_live=_radar_live, jogos_na_janela=_radar_janela)
    _repo_atual = os.environ.get('GITHUB_REPOSITORY', '').lower()
    if 'sokkerpro' in _repo_atual:
        BOT_SOURCE = 'sokkerpro'
    else:
        BOT_SOURCE = 'sokkerpro'
    print(f'[Ciclo] Fonte: {BOT_SOURCE.upper()} | Repo: {_repo_atual}')
    jogos_live = []
    if BOT_SOURCE == 'sokkerpro':
        jogos_live = get_jogos_sokkerpro(set())
        print(f'[SokkerPro] {len(jogos_live)} jogos ao vivo')
    jogos_na_janela = filtrar_janelas(jogos_live)
    print(f'[Janela] {len(jogos_na_janela)} jogos nas janelas alvo')
    _LAST_RADAR_DATA = (len(jogos_live), jogos_live, jogos_na_janela)
    check_status_command(total_jogos_live=len(jogos_live), jogos_live=jogos_live, jogos_na_janela=jogos_na_janela)
    if VIP_POLL_ENABLED:
        run_vip_maintenance()
    try:
        sinais_p = _load_sinais_github()
        if confirmed_ids is None:
            confirmed_ids = set()
        rest = []
        for s in sinais_p:
            # Cada mercado configurado possui sua própria confirmação.
            # Mercados diferentes no mesmo jogo devem confirmar separadamente.
            uid = f"{s.get('fixture_id', '?')}_{s.get('mercado', '?')}"
            if uid in confirmed_ids:
                print(f'[SINAIS] Pulando duplicata: {uid}')
                continue
            res = checar_resultado(s)
            if res:
                if not _claim_auditoria_slot(uid):
                    print(f'[SINAIS] Auditoria já reservada por outra execução: {uid}')
                    continue
                confirmed_ids.add(uid)
                emoji = '🟢GREEN CONFIRMADO🟢' if res == 'green' else ('🔵REEMBOLSO CONFIRMADO🔵' if res == 'refund' else '🔴RED CONFIRMADO🔴')
                if s.get('message_id'):
                    send_telegram(emoji, reply_to=s.get('message_id'))
                salvar_resultado(res, mercado=s.get('mercado'), fixture_id=s.get('fixture_id'))
                atualizar_entrada_historico(s, res)
                registrar_performance(s.get('mercado'), res)
            else:
                rest.append(s)
        _save_sinais_github(rest)
        print(f'[SINAIS] {len(sinais_p) - len(rest)} resultados confirmados, {len(rest)} ainda pendentes')
    except Exception as e:
        print(f'[SINAIS] Erro validação: {e}')
    if not jogos_na_janela:
        print('[OK] Nenhum jogo na janela — aguardando próximo ciclo')
        save_sent(sent)
        print('Finalizado. Enviados: 0')
        return (sent, total_env)
    jogos_dedup = []
    vistos_chaves = set()
    for j in jogos_na_janela:
        hn_j = norm_nome_time(j['home'])
        an_j = norm_nome_time(j['away'])
        chave = hashlib.md5(f'{hn_j}-{an_j}'.encode()).hexdigest()[:16]
        if chave not in vistos_chaves:
            vistos_chaves.add(chave)
            jogos_dedup.append(j)
    print(f'[Dedup] {len(jogos_na_janela)} -> {len(jogos_dedup)} jogos unicos')
    for j in jogos_dedup:
        fid = j['fid']
        h, a = (j['home'], j['away'])
        hn = norm_nome_time(h)
        an = norm_nome_time(a)
        dedup_id = hashlib.md5(f'{hn}-{an}'.encode()).hexdigest()[:12]
        m = j['minuto']
        p_raw = j['period']
        if isinstance(p_raw, str):
            p = 2 if '2' in p_raw else 1 if '1' in p_raw else p_raw
        else:
            p = p_raw
        sh, sa = (j['sh'], j['sa'])
        liga = str(j['liga'])
        pais = j.get('pais', '')
        stot = sh + sa
        placar = f'{sh}x{sa}'
        print(f'[Analisando] {h} x {a} | {placar} | {m}min')
        fid_raw = j.get('fid_raw', fid)
        stats = {}
        if BOT_SOURCE == 'sokkerpro':
            try:
                sb = get_stats_sokkerpro(fid_raw, h, a)
                if isinstance(sb, dict) and sb:
                    stats = sb
            except:
                pass
            if not stats or not (stats.get('chutes_tot_h', 0) > 0 or stats.get('chutes_tot_a', 0) > 0 or stats.get('escanteios_h', -1) >= 0 or (stats.get('escanteios_a', -1) >= 0) or (stats.get('ataques_perigosos_h', 0) > 0) or (stats.get('ataques_perigosos_a', 0) > 0)):
                try:
                    sb_name = get_stats_sokkerpro_by_name(h, a)
                    if isinstance(sb_name, dict):
                        if 'Club Friendlies' in liga:
                            stats = sb_name
                            print(f"[SKP-NAME] Friendlies aceito: esc {sb_name.get('escanteios_h')}x{sb_name.get('escanteios_a')}")
                        elif sb_name.get('chutes_tot_h', 0) > 0 or sb_name.get('chutes_tot_a', 0) > 0 or sb_name.get('ataques_perigosos_h', 0) > 0 or (sb_name.get('ataques_perigosos_a', 0) > 0) or (sb_name.get('chutes_gol_h', 0) > 0) or (sb_name.get('chutes_gol_a', 0) > 0):
                            stats = sb_name
                            print(f"[SKP-NAME] Stats via nome OK: esc {sb_name.get('escanteios_h')}x{sb_name.get('escanteios_a')} | chutes {sb_name.get('chutes_tot_h')}x{sb_name.get('chutes_tot_a')}")
                except:
                    pass
        for k in ['chutes_tot_h', 'chutes_tot_a', 'chutes_gol_h', 'chutes_gol_a']:
            stats.setdefault(k, 0)
        for k in ['escanteios_h', 'escanteios_a']:
            stats.setdefault(k, -1)
        for k in ['red_cards_h', 'red_cards_a']:
            stats.setdefault(k, 0)
        for k in ['medias_home_goal', 'medias_away_goal']:
            stats.setdefault(k, 0)
        if stats:
            print(f"[STATS-{BOT_SOURCE.upper()}] {h} x {a} | chutes: {stats.get('chutes_tot_h', 0)}/{stats.get('chutes_tot_a', 0)} | cantos: {stats.get('escanteios_h', -1)}/{stats.get('escanteios_a', -1)} | atq_perig: {stats.get('ataques_perigosos_h', 0)}/{stats.get('ataques_perigosos_a', 0)}")
        tem_stats = stats and (stats.get('chutes_tot_h', 0) > 0 or stats.get('chutes_tot_a', 0) > 0 or stats.get('escanteios_h', -1) > 0 or (stats.get('escanteios_a', -1) > 0) or (stats.get('ataques_perigosos_h', 0) > 0) or (stats.get('ataques_perigosos_a', 0) > 0))
        if not tem_stats:
            print(f'[SKIP] {h} x {a} — sem stats reais (chutes, cantos ou ataques perigosos) em nenhuma API, pulando jogo')
            continue
        odd_h = j.get('odd_h')
        odd_a = j.get('odd_a')
        fav_por_odds = False
        if BOT_SOURCE == 'sokkerpro':
            try:
                oh, oa = get_odds_sokkerpro(fid_raw)
                if oh and oa and (oh > 1) and (oa > 1):
                    odd_h, odd_a = (oh, oa)
                    fav_final = 'h' if odd_h <= odd_a else 'a'
                    fav_por_odds = True
                    print(f'[ODDS-SKP] {h} x {a} — odd Casa:{odd_h:.2f} Fora:{odd_a:.2f}')
            except:
                pass
        if not fav_por_odds:
            if stats and stats.get('fav_side') in ('h', 'a'):
                fav_final = stats['fav_side']
                print(f'[FAV-STATS] {h} x {a} — sem odds, favorito pelo chutes: {fav_final}')
            elif stats and (stats.get('chutes_tot_h', 0) > 0 or stats.get('chutes_tot_a', 0) > 0):
                fav_final = 'h' if stats.get('chutes_tot_h', 0) >= stats.get('chutes_tot_a', 0) else 'a'
                print(f'[FAV-STATS] {h} x {a} — sem odds, favorito pelo chutes: {fav_final}')
            else:
                fav_final = 'h'
                print(f'[FAV-HOME] {h} x {a} — sem odds e sem stats, assumindo mandante como favorito')
        if not (odd_h and odd_h > 1 and odd_a and (odd_a > 1)):
            print(f'[SKIP-SEM-ODDS] {h} x {a} — nenhuma odd válida (Casa:{odd_h} Fora:{odd_a}), pulando sinal')
            continue
        red_fav = stats.get(f'red_cards_{fav_final}', 0) if stats else 0

        def _cfg(mkt, campo, default):
            m = CONFIG_MERCADOS.get(mkt, {})
            return m.get('criterios', {}).get(campo, default)

        def _situacao_fav_ok(mercado, fav_gols, adv_gols):
            """Verifica se a situação do favorito é válida conforme config.
            Opções: perdendo | empatando | perdendo_ou_empatando | zebra"""
            situacao = mercado.get('criterios', {}).get('situacao_favorito', '')
            if not situacao:
                return True
            if situacao == 'ganhando':
                return fav_gols > adv_gols
            if situacao == 'empatando':
                return fav_gols == adv_gols
            if situacao == 'perdendo':
                return fav_gols < adv_gols
            if situacao == 'perdendo_ou_empatando':
                return fav_gols <= adv_gols
            if situacao == 'zebra_ganhando':
                return fav_gols < adv_gols
            return True

        def _validar_criterios_gerais(mkt_nome, stats, fav_final):
            """Valida todos os critérios do config.json para um mercado.
            Retorna (ok: bool, motivos: list)."""
            mkt_cfg = CONFIG_MERCADOS.get(mkt_nome, {})
            crit = mkt_cfg.get('criterios', {})
            motivos = []
            fav_prefix = 'h' if fav_final == 'h' else 'a'
            mapa = {'chutes_alvo_min': ('chutes_gol', 'sum', 'min'), 'chutes_totais_min': ('chutes_tot', 'sum', 'min'), 'escanteios_minimos': ('escanteios', 'sum', 'min'), 'chutes_inside_min': ('chutes_inside', 'fav', 'min'), 'chutes_inside_total_min': ('chutes_inside', 'sum', 'min'), 'chutes_outside_min': ('chutes_outside', 'fav', 'min'), 'goal_attempts_min': ('goal_attempts', 'fav', 'min'), 'big_chances_created_min': ('big_chances', 'fav', 'min'), 'chutes_bloq_max': ('chutes_bloq', 'fav', 'max'), 'defesas_min': ('defesas', 'fav', 'min'), 'faltas_min': ('faltas', 'fav', 'min'), 'yellow_max': ('yellow_cards', 'fav', 'max'), 'impedimentos_min': ('impedimentos', 'fav', 'min'), 'pressure_bar_min': ('pressure_bar', 'fav', 'min'), 'ball_safe_min': ('ball_safe', 'fav', 'min'), 'dapm_5_min': ('dapm5', 'fav', 'min'), 'dapm_total_orig_min': ('dapm_total', 'fav', 'min'), 'xg_total_min': ('xg', 'sum', 'min'), 'xg_casa_min': ('xg', 'h', 'min'), 'xg_fora_min': ('xg', 'a', 'min'), 'posse_bola_min': ('posse', 'fav', 'min'), 'ataques_perigosos_min': ('ataques_perigosos', 'fav', 'min'), 'media_gols_partida_min': ('medias_goal', 'sum', 'min'), 'media_corners_total_min': ('medias_corners', 'sum', 'min'), 'media_corners_casa_min': ('medias_corners', 'h', 'min'), 'media_corners_fora_min': ('medias_corners', 'a', 'min'), 'appm_min_por_time': ('dapm_total', 'max', 'min'), 'appm_total_min': ('dapm_total', 'max', 'min'), 'media_gols_ht_min': ('media_gols_ht', 'sum', 'min'), 'media_gols_ft_min': ('media_gols_ft', 'sum', 'min')}
            btts_prob_val = crit.get('btts_probabilidade_min')
            if btts_prob_val is not None and btts_prob_val != '':
                try:
                    bp = float(btts_prob_val)
                    v = stats.get('btts_probabilidade', 0)
                    if isinstance(v, str) or v is None:
                        v = 0
                    if float(v) < bp:
                        motivos.append(f'btts_probabilidade_min={float(v):.0f}% < min {bp:.0f}%')
                except:
                    pass
            for campo, (base, lado, oper) in mapa.items():
                valor_cfg = crit.get(campo)
                if valor_cfg is None or valor_cfg == '':
                    continue
                valor_cfg = float(valor_cfg)
                if lado == 'sum':
                    v_h = stats.get(f'{base}_h', 0)
                    v_a = stats.get(f'{base}_a', 0)
                    if isinstance(v_h, str) or v_h is None:
                        v_h = 0
                    if isinstance(v_a, str) or v_a is None:
                        v_a = 0
                    valor_stats = float(v_h) + float(v_a)
                elif lado == 'fav':
                    v = stats.get(f'{base}_{fav_prefix}', 0)
                    if isinstance(v, str) or v is None:
                        v = 0
                    valor_stats = float(v)
                elif lado == 'h':
                    v = stats.get(f'{base}_h', 0)
                    if isinstance(v, str) or v is None:
                        v = 0
                    valor_stats = float(v)
                elif lado == 'a':
                    v = stats.get(f'{base}_a', 0)
                    if isinstance(v, str) or v is None:
                        v = 0
                    valor_stats = float(v)
                elif lado == 'max':
                    v_h = stats.get(f'{base}_h', 0)
                    v_a = stats.get(f'{base}_a', 0)
                    if isinstance(v_h, str) or v_h is None:
                        v_h = 0
                    if isinstance(v_a, str) or v_a is None:
                        v_a = 0
                    valor_stats = float(max(float(v_h), float(v_a)))
                elif lado == 'total':
                    v = stats.get(base, 0)
                    if isinstance(v, str) or v is None:
                        v = 0
                    valor_stats = float(v)
                elif lado == 'diff':
                    v_h = stats.get(f'{base}_h', 0)
                    v_a = stats.get(f'{base}_a', 0)
                    if isinstance(v_h, str) or v_h is None:
                        v_h = 0
                    if isinstance(v_a, str) or v_a is None:
                        v_a = 0
                    valor_stats = abs(float(v_h) - float(v_a))
                if oper == 'min':
                    if valor_stats < valor_cfg:
                        motivos.append(f'{campo}={valor_stats:.1f} < min {valor_cfg:.1f}')
                elif oper == 'max':
                    if valor_stats > valor_cfg:
                        motivos.append(f'{campo}={valor_stats:.1f} > max {valor_cfg:.1f}')
            # Critérios brutos da API SokkerPro configurados pelo painel.
            # Cada chave é avaliada uma única vez; valores ausentes não passam automaticamente.
            api_criterios = mkt_cfg.get('criterios_api', [])
            vistos_api = set()
            for item in api_criterios:
                campo = item.get('campo')
                if not campo or campo in vistos_api:
                    continue
                vistos_api.add(campo)
                api_map = {'chutes_alvo_min':('chutes_gol_h','chutes_gol_a','sum'),'chutes_totais_min':('chutes_tot_h','chutes_tot_a','sum'),'ataques_perigosos_min':('ataques_perigosos_h','ataques_perigosos_a','fav'),'escanteios_minimos':('escanteios_h','escanteios_a','sum'),'chutes_inside_min':('chutes_inside_h','chutes_inside_a','fav'),'chutes_inside_total_min':('chutes_inside_h','chutes_inside_a','sum'),'chutes_outside_min':('chutes_outside_h','chutes_outside_a','fav'),'goal_attempts_min':('goal_attempts_h','goal_attempts_a','fav'),'big_chances_created_min':('big_chances_h','big_chances_a','fav'),'chutes_bloq_max':('chutes_bloq_h','chutes_bloq_a','fav'),'defesas_min':('defesas_h','defesas_a','fav'),'faltas_min':('faltas_h','faltas_a','fav'),'yellow_max':('yellow_cards_h','yellow_cards_a','fav'),'impedimentos_min':('impedimentos_h','impedimentos_a','fav'),'pressure_bar_min':('pressure_bar_h','pressure_bar_a','fav'),'ball_safe_min':('ball_safe_h','ball_safe_a','fav'),'posse_bola_min':('posse_h','posse_a','fav'),'xg_total_min':('xg_h','xg_a','sum'),'media_gols_partida_min':('medias_goal_h','medias_goal_a','sum'),'media_corners_total_min':('medias_corners_h','medias_corners_a','sum'),'media_corners_casa_min':('medias_corners_h','medias_corners_a','h'),'media_corners_fora_min':('medias_corners_h','medias_corners_a','a'),'appm_min_por_time':('dapm_total_h','dapm_total_a','max'),'appm_total_min':('dapm_total_h','dapm_total_a','max'),'media_gols_ht_min':('media_gols_ht_h','media_gols_ht_a','sum'),'media_gols_ft_min':('media_gols_ft_h','media_gols_ft_a','sum'),'dapm_5_min':('dapm5_h','dapm5_a','fav'),'dapm_total_orig_min':('dapm_total_h','dapm_total_a','fav')}
                if campo == 'chutes_bloq_fav':
                    atual_raw = stats.get('chutes_bloq_h' if fav_final == 'h' else 'chutes_bloq_a')
                elif campo == 'diferenca_gols_fav_max':
                    atual_raw = (sa - sh) if fav_final == 'h' else (sh - sa)
                elif campo == 'max_red_card_fav':
                    atual_raw = red_fav
                elif campo in api_map:
                    h,a,lado=api_map[campo]; vh,va=stats.get(h),stats.get(a)
                    if lado=='sum': atual_raw=float(vh or 0)+float(va or 0)
                    elif lado=='max': atual_raw=max(float(vh or 0),float(va or 0))
                    elif lado=='h': atual_raw=vh
                    elif lado=='a': atual_raw=va
                    else: atual_raw=vh if fav_final=='h' else va
                elif campo == 'appm_partida_calc':
                    if not m or float(m) <= 0:
                        motivos.append(f'{campo}=minuto inválido')
                        continue
                    atual_raw = (float(stats.get('ataques_perigosos_h', 0)) + float(stats.get('ataques_perigosos_a', 0))) / float(m)
                elif str(campo).startswith('prob_'):
                    atual_raw = stats.get('prob_mercados', {}).get(str(campo)[5:])
                else:
                    atual_raw = stats.get(campo)
                if atual_raw is None or atual_raw == '':
                    motivos.append(f'{campo}=ausente')
                    continue
                try:
                    atual = float(atual_raw)
                    alvo = float(item.get('valor'))
                    op = item.get('operador', 'gte')
                    if op == 'gte': ok_api = atual >= alvo
                    elif op == 'lte': ok_api = atual <= alvo
                    elif op == 'gt': ok_api = atual > alvo
                    elif op == 'lt': ok_api = atual < alvo
                    elif op == 'eq': ok_api = atual == alvo
                    elif op == 'between': ok_api = atual >= alvo and atual <= float(item.get('valor2'))
                    else: ok_api = False
                    if not ok_api:
                        motivos.append(f'{campo}={atual:g} não atende {op} {alvo:g}')
                except (TypeError, ValueError):
                    motivos.append(f'{campo}=inválido')
            return (len(motivos) == 0, motivos)
        fav_gols = sh if fav_final == 'h' else sa
        adv_gols = sa if fav_final == 'h' else sh
        print(f"[DIAG] {h} x {a} | placar={placar} | min={m} | periodo={p} | fav={fav_final} | gols_fav={fav_gols} gols_adv={adv_gols} | odds_casa={odd_h} odds_fora={odd_a} | chutes_totais={stats.get('chutes_tot_h', 0)}x{stats.get('chutes_tot_a', 0)} | chutes_gol={stats.get('chutes_gol_h', 0)}x{stats.get('chutes_gol_a', 0)} | atq_perig={stats.get('ataques_perigosos_h', 0)}x{stats.get('ataques_perigosos_a', 0)} | escanteios={stats.get('escanteios_h', '?')}x{stats.get('escanteios_a', '?')} | red_fav={red_fav}")
        diff_max_ht = _cfg('over_05_ht', 'diferenca_gols_fav_max', 0)
        diff_max_btts = _cfg('ambas_marcam', 'diferenca_gols_fav_max', 1)
        diff_max_oft = _cfg('over_15_ft', 'diferenca_gols_fav_max', 1)
        diff_max_overgoal = _cfg('over_gol_partida', 'diferenca_gols_fav_max', 1)
        diff_max_corner_ht = _cfg('escanteio_ht', 'diferenca_gols_fav_max', 1)
        diff_max_corner_ft = _cfg('escanteio_ft', 'diferenca_gols_fav_max', 1)
        red_max_ht = _cfg('over_05_ht', 'max_red_card_fav', 0)
        red_max_btts = _cfg('ambas_marcam', 'max_red_card_fav', 0)
        red_max_oft = _cfg('over_15_ft', 'max_red_card_fav', 0)
        red_max_overgoal = _cfg('over_gol_partida', 'max_red_card_fav', 0)
        red_max_corner_ht = _cfg('escanteio_ht', 'max_red_card_fav', 0)
        red_max_corner_ft = _cfg('escanteio_ft', 'max_red_card_fav', 0)
        fav_empatando = sh == sa
        diff_gols = adv_gols - fav_gols
        for mk, mc in CONFIG_MERCADOS.items():
            if not mc.get('ativo', True):
                continue
            cper = int(mc.get('periodo', 0))
            if cper > 0 and p != cper:
                continue
            cini = int(mc.get('minuto_inicio', 0))
            cfim = int(mc.get('minuto_fim', 99))
            if not cini <= m <= cfim:
                continue
            cplacar = mc.get('placar_valido', '')
            if cplacar:
                pv = [x.strip().replace('_', 'x') for x in cplacar.split(',')]
                if placar not in pv:
                    print(f'[DIAG-{mk}-BARRA] {h} x {a} — placar {placar} não atende ({cplacar}), pulando')
                    continue
            if not _situacao_fav_ok(mc, fav_gols, adv_gols):
                print(f'[DIAG-{mk}-BARRA] {h} x {a} — situação do favorito não atende, pulando')
                continue
            diff_max = mc.get('criterios', {}).get('diferenca_gols_fav_max', 99)
            if diff_max < 99 and diff_gols > diff_max:
                print(f'[DIAG-{mk}-BARRA] {h} x {a} — diferença de gols ({diff_gols}) > max ({diff_max}), pulando')
                continue
            red_max = mc.get('criterios', {}).get('max_red_card_fav', 99)
            if red_max < 99 and red_fav > red_max:
                print(f'[DIAG-{mk}-BARRA] {h} x {a} — favorito com cartão vermelho ({red_fav} > {red_max}), pulando')
                continue
            ok, motivos = _validar_criterios_gerais(mk, stats, fav_final)
            if not ok:
                for motivo in motivos:
                    print(f'[DIAG-{mk}-BARRA] {h} x {a} — {motivo}')
                continue
            hoje = datetime.now(BRT).strftime('%Y%m%d')
            key = f'{dedup_id}_{mk}_{hoje}'
            if key in sent:
                print(f'[DIAG-{mk}-DUP] {h} x {a} — já enviado hoje ({key}), pulando')
                continue
            cnome = mc.get('nome', mk)
            c_tipo = mc.get('tipo', '')
            notificar = mc.get('notificar', True)
            extra_val = 0
            linha_str = ''
            if c_tipo in ('escanteio_ht', 'escanteio_ft', 'corner', 'escanteio'):
                _eh = stats.get('escanteios_h', -1) if stats else -1
                _ea = stats.get('escanteios_a', -1) if stats else -1
                if _eh < 0 or _ea < 0:
                    print(f'[DIAG-{mk}-ESC] {h} x {a} — sem dados de escanteio (disponível), pulando')
                    continue
                cantos_h = max(0, _eh)
                cantos_a = max(0, _ea)
                extra_val = cantos_h + cantos_a
                linha_str = f'o+{extra_val + 0.5}'
            elif c_tipo in ('gol_partida', 'over_gol'):
                extra_val = sh + sa
                linha_str = f'o+{extra_val + 0.5}'
            elif c_tipo == 'gol_intervalo':
                extra_val = 0
                linha_str = 'o+0.5'
            elif c_tipo == 'over_15':
                extra_val = sh + sa
                linha_str = 'o+1.5'
            elif c_tipo == 'ambas_marcam':
                linha_str = 'bts_yes'
            odd_real = _odd_real_disponivel(stats, c_tipo, extra_val)
            if odd_real is None:
                print(f'[DIAG-{mk}-ODD] {h} x {a} — mercado/linha não encontrada na API, não enviando')
                continue
            ob365 = odd_real
            obano = None
            if notificar:
                mid = send_telegram(msg_universal(h, a, m, liga, pais, 5, mk, cnome, placar, cantos_atual=extra_val if 'escanteio' in c_tipo else 0, stats=stats, sh=sh, sa=sa, fav_final=fav_final, odd_h=odd_h, odd_a=odd_a, odd_b365=ob365, odd_bano=obano, nome=cnome, tipo=c_tipo, probabilidade=_probabilidade_para_sinal(stats, c_tipo, sh, sa, extra_val if 'escanteio' in c_tipo else 0)), marca=key, home=h, away=a, odd_b365_val=ob365, odd_bano_val=obano)
            else:
                print(f'[DIAG-{mk}-SILENT] {h} x {a} — notificar=False, registrando sem enviar')
                mid = 0
            sent.add(key)
            total_env += 1
            save_sent(sent)
            registrar_sinal(fid, mk, h, a, mid, extra_val=extra_val, tipo=c_tipo, entry_sh=sh, entry_sa=sa, odd_b365=ob365, odd_bano=obano)
    try:
        agora_hora = datetime.now(BRT)
        if agora_hora.hour == 23 and agora_hora.minute >= 55:
            data_rel = agora_hora.strftime('%Y-%m-%d')
            print(f'[AUTO] janela 23:55 — verificando relatórios de {data_rel}')
            if _claim_report_slot(f'diario_{data_rel}'):
                enviar_relatorio_diario()
            else:
                print(f'[AUTO] relatório diário já reservado: {data_rel}')
            if _claim_report_slot(f'mercados_dia_{data_rel}'):
                msg_mercados = gerar_layout_mercados_hoje()
                if msg_mercados:
                    send_telegram(msg_mercados)
            else:
                print(f'[AUTO] relatório de mercados do dia já reservado: {data_rel}')
    except Exception as e:
        print(f'[AUTO] Erro auto-dispatch: {e}')
    print(f'[Ciclo] Finalizado. Enviados neste ciclo: {total_env}')
    return (sent, total_env)

def configurar_comandos_telegram():
    """Publica o menu de comandos visível nos grupos do bot."""
    comandos = [
        {'command': 'mercados', 'description': 'Performance acumulada geral'},
        {'command': 'mercadosmensal', 'description': 'Performance do mês atual'},
        {'command': 'mercados24h', 'description': 'Performance do dia atual'},
        {'command': 'relatoriodiario', 'description': 'Relatório do dia'},
        {'command': 'relatoriomensal', 'description': 'Relatório do mês'},
        {'command': 'relatoriogeral', 'description': 'Relatório geral acumulado'},
        {'command': 'radar', 'description': 'Jogos ao vivo e oportunidades'},
        {'command': 'vip', 'description': 'Assinar acesso VIP via PIX'},
    ]
    try:
        r = requests.post(
            f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/setMyCommands',
            json={'commands': comandos, 'scope': {'type': 'all_group_chats'}},
            timeout=10
        )
        if r.ok:
            print('[CMD] Menu de comandos publicado para grupos')
        else:
            print(f'[CMD] Menu de comandos não publicado: HTTP {r.status_code}')
    except Exception as e:
        print(f'[CMD] Erro ao publicar menu de comandos: {e}')

def run():
    """Executa 3 ciclos de 1 minuto cada para contornar limite de 5 min do cron."""
    configurar_comandos_telegram()
    confirmed_ids = set()
    sent = load_sent()
    total_env = 0
    print(f'[Iniciando] Monitoramento com 3 ciclos de 1 minuto cada')
    for ciclo in range(3):
        print(f"\n{'=' * 50}")
        print(f'=== CICLO {ciclo + 1}/3 ===')
        print(f"{'=' * 50}")
        sent, total_env = run_ciclo(sent, total_env, confirmed_ids)
        if ciclo < 2:
            print(f'[Aguardando 60s para próximo ciclo...]')
            time.sleep(60)
    print(f"\n{'=' * 50}")
    print(f'=== EXECUÇÃO COMPLETA ===')
    print(f'Total de sinais enviados: {total_env}')
    print(f"{'=' * 50}")
if __name__ == '__main__':
    run()

def get_favorito_odds(home, away, fid=None, league=None):
    if not fid:
        return ('h', None, None)
    odds = get_odds_sokkerpro(str(fid))
    if odds and odds[0] is not None:
        return (odds[0], odds[1], odds[3])
    return ('h', None, None)

def get_odd_favorito_num(home, away, fid=None, league=None, fid_raw=None):
    ident = fid_raw or fid
    if not ident:
        return 99
    odds = get_odds_sokkerpro(str(ident))
    if odds and odds[0] is not None:
        return min(odds[1], odds[3])
    return 99
