#!/usr/bin/env python3
"""캔버스(결제수단별 혜택 와이어프레임) 보드 → UT 화면 동기화.

사용:  python3 sync.py <canvas_project_dir> <in_config.json> <out_config.json>
- canvas_project_dir: 캔버스에서 읽어온 project/*.dc.html 이 있는 폴더
- map.json(같은 폴더)의 규칙대로 보드를 UT 화면 html로 바꿔 넣어요.
- 누르는 영역(data-hs), 모션, 결제 금액 표시는 UT 것을 유지해요.
"""
import json, re, sys, os, subprocess, copy
from bs4 import BeautifulSoup, NavigableString

HERE = os.path.dirname(os.path.abspath(__file__))
M = json.load(open(os.path.join(HERE, 'map.json')))
BLOB = M['blobs']  # 캔버스 blob id → UT blob id

def norm(s): return re.sub(r'\s+', ' ', s or '').strip()

def board_parts(path):
    h = open(path).read()
    style = ''
    hm = re.search(r'<helmet>\s*<style>(.*?)</style>', h, re.S)
    if hm:
        style = hm.group(1)
        style = re.sub(r'@font-face\{[^}]*\}', '', style)
        style = re.sub(r'(^|\n)\s*body\{[^}]*\}', r'\1', style)
        style = re.sub(r'(^|\n)\s*a\{[^}]*\}a:hover\{[^}]*\}', r'\1', style)
        style = style.strip()
    body = re.search(r'<x-dc>(.*)</x-dc>', h, re.S).group(1)
    body = re.sub(r'<helmet>.*?</helmet>', '', body, flags=re.S).strip()
    sm = re.search(r'<script type="text/x-dc"[^>]*>(.*?)</script>', h, re.S)
    return style, body, (sm.group(1) if sm else '')

def render_vals(script):
    js = ("class DCLogic{constructor(){this.props={};this.state={}}}\n" + script +
          "\nconst c=new Component();let v={};try{v=c.renderVals()||{}}catch(e){}\n"
          "for(const k in v){if(typeof v[k]==='function')delete v[k]}\nprocess.stdout.write(JSON.stringify(v));")
    r = subprocess.run(['node', '-e', js], capture_output=True, text=True, timeout=20)
    try: return json.loads(r.stdout or '{}')
    except Exception: return {}

def get(vals, path):
    cur = vals
    for p in path.split('.'):
        if isinstance(cur, dict) and p in cur: cur = cur[p]
        else: return None
    return cur

def expand(body, vals):
    def sub_holes(s, scope):
        return re.sub(r'\{\{\s*([\w.]+)\s*\}\}', lambda m: str(get(scope, m.group(1))) if get(scope, m.group(1)) is not None else m.group(0), s)
    def do_for(s, scope):
        pat = re.compile(r'<sc-for\s+list="\{\{\s*([\w.]+)\s*\}\}"\s+as="(\w+)"[^>]*>(.*?)</sc-for>', re.S)
        def rep(m):
            lst = get(scope, m.group(1)) or []
            out = []
            for it in lst:
                sc = dict(scope); sc[m.group(2)] = it
                out.append(sub_holes(do_for(m.group(3), sc), sc))
            return ''.join(out)
        return pat.sub(rep, s)
    return sub_holes(do_for(body, vals), vals)

def find_text_el(soup, text, within=None):
    root = within or soup
    cands = [e for e in root.find_all(True) if norm(e.get_text()) == text]
    if not cands:
        cands = [e for e in root.find_all(True) if text in norm(e.get_text())]
        cands.sort(key=lambda e: len(norm(e.get_text())))
    else:
        # 가장 안쪽 요소
        cands = [e for e in cands if not any(norm(c.get_text()) == text for c in e.find_all(True))] or cands
    return cands[0] if cands else None

def climb(el, up):
    if up == 'a':
        a = el if el.name == 'a' else el.find_parent('a')
        return a or el
    for _ in range(int(up)):
        if el.parent: el = el.parent
    return el

def build(entry, board_dir, cur_html, log):
    style, body, script = board_parts(os.path.join(board_dir, entry['board'] + '.dc.html'))
    if '<sc-' in body or '{{' in body:
        body = expand(body, render_vals(script))
    # blob 바꾸기
    missing = set()
    def blob_rep(m):
        bid = m.group(1)
        if bid in BLOB: return '/_blob/' + BLOB[bid]
        missing.add(bid); return m.group(0)
    if entry.get('lottie'):
        body = re.sub(r'(ref="\{\{ ?setBox ?\}\}"[^>]*?)url\(/_blob/[0-9a-f]{32}\)', r'\1', body)
    body = re.sub(r'/_blob/([0-9a-f]{32})', blob_rep, body)
    for a, b in M.get('replace_all', []) + entry.get('replace', []):
        body = body.replace(a, b)
    soup = BeautifulSoup(body, 'html.parser')
    cur = BeautifulSoup(cur_html, 'html.parser')
    root = soup.find(True)
    if entry.get('overlay') and root is not None:
        root['style'] = re.sub(r'background:\s*#666666', 'background: rgba(0, 0, 0, 0.6)', root.get('style', ''))
    # 행 지우기
    for r in entry.get('remove', []):
        r = r if isinstance(r, dict) else {'text': r}
        el = find_text_el(soup, r['text'])
        if el is not None:
            climb(el, r.get('up', 'a')).decompose()
        else: log.append(f"  지울 행 '{r['text']}' 를 보드에서 못 찾음")
    # 순서 바꾸기: move 행을 before 행 앞으로
    for o in entry.get('order', []):
        a = find_text_el(soup, o['move']); b = find_text_el(soup, o['before'])
        if a is None or b is None:
            log.append(f"  순서 바꿀 행을 못 찾음 ({o['move']} → {o['before']})"); continue
        a = climb(a, o.get('up', 'a')); b = climb(b, o.get('up', 'a'))
        a.extract(); b.insert_before(a)
    # 누르는 영역
    for sp in entry.get('spots', []):
        within = None
        if sp.get('within'):
            w = find_text_el(soup, sp['within'])
            within = climb(w, 'a') if w is not None else None
        el = find_text_el(soup, sp['text'], within)
        if el is None:
            log.append(f"  누르는 영역 {sp['id']} ('{sp['text']}') 못 찾음"); continue
        if sp.get('wrap'):
            w = soup.new_tag('span'); w['data-hs'] = sp['id']; w['style'] = sp['wrap']
            el.wrap(w)
            st = el.get('style', '')
            el['style'] = re.sub(r'\s*margin-left:\s*4px;?', '', re.sub(r'\s*vertical-align:\s*middle;?', '', st)).strip()
            continue
        t = climb(el, sp.get('up', 'a'))
        t['data-hs'] = sp['id']
        for k, v in sp.get('attrs', {}).items(): t[k] = v
    # 남은 링크는 일반 요소로
    for a in soup.find_all('a'):
        a.name = 'div'
        if 'href' in a.attrs: del a['href']
    # 모션: UT 쪽 모션 요소를 그대로 옮겨요
    if entry.get('lottie'):
        src = cur.find(attrs={'data-lottie': True})
        dst = soup.find(attrs={'ref': True})
        if src is not None and dst is not None:
            dst.replace_with(copy.copy(src))
        else: log.append('  모션 자리를 못 찾음')
    for e in soup.find_all(attrs={'ref': True}): del e['ref']
    # 결제 금액(할인 반영 표시)
    if entry.get('amount'):
        el = find_text_el(soup, entry['amount'])
        if el is not None: el['data-amount'] = re.sub(r'\D', '', entry['amount'])
        else: log.append('  결제 금액 자리를 못 찾음')
    html = str(soup)
    for pat, rep in entry.get('regex', []):
        html = re.sub(pat, rep, html, flags=re.S)
    if style: html = '<style>' + style + '</style>' + html
    missing = {b for b in missing if b in html}
    for bid in missing: log.append(f'  UT에 없는 이미지 {bid} (복사 필요)')
    return html, missing

def main():
    board_dir, inp, outp = sys.argv[1:4]
    raw = json.load(open(inp)); st = raw.get('data', raw)
    S = {s['id']: s for v in st['variants'] for s in v['screens']}
    log, changed, allmissing = [], [], set()
    for entry in M['screens']:
        ids = [i for i in entry['ut'] if i in S]
        need = {sp['id'] for s in ids for sp in S[s].get('spots', []) if sp['act'] not in ('radio',)}
        sub = []
        html, miss = build(entry, board_dir, S[ids[0]]['html'], sub)
        allmissing |= miss
        got = set(re.findall(r'data-hs="([^"]+)"', html))
        lack = need - got
        if lack: sub.append('  빠진 누르는 영역: ' + ', '.join(sorted(lack)))
        bad = bool(lack) or bool(miss)
        tag = '그대로 둠' if bad else ('바뀜' if html != S[ids[0]]['html'] else '변화 없음')
        log.append(f"[{entry['board']}] → {', '.join(ids)}: {tag}")
        log += sub
        if not bad:
            for i in ids:
                if S[i]['html'] != html: S[i]['html'] = html; changed.append(i)
    import time
    if changed: st['updatedAt'] = time.time() * 1000
    json.dump(st, open(outp, 'w'), ensure_ascii=False)
    print('\n'.join(log)); print('바뀐 화면:', changed)
    if allmissing: print('복사할 이미지:', sorted(allmissing))

if __name__ == '__main__': main()
