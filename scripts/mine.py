"""Community mine: validated inputs, persistent receipts, no shell interpolation."""
import argparse
import base64
from datetime import datetime, timezone
from html import escape
import json
import os
from pathlib import Path
import random
import re
import subprocess
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 6, 3
ORES = {
    'stone': ('돌', '🪨', 1, 46),
    'coal_ore': ('석탄', '⬛', 2, 20),
    'iron_ore': ('철', '⚪', 4, 13),
    'redstone_ore': ('레드스톤', '🔴', 6, 8),
    'lapis_ore': ('청금석', '🔵', 8, 6),
    'gold_ore': ('금', '🟡', 12, 4),
    'diamond_ore': ('다이아몬드', '💎', 50, 2),
    'emerald_ore': ('에메랄드', '🟢', 80, 1),
}

MINE_SLOT_DIR = ROOT / 'assets' / 'mine-grid'


def _pixel_group(font, text, center_x, baseline, size=16, fill='#d8e2e8'):
    """Convert one label to font outlines so GitHub never substitutes the font."""
    width, paths, scale = font.paths(text, size=size)
    return (f'<g fill="{fill}" transform="translate({center_x - width / 2:.2f} {baseline}) '
            f'scale({scale:.6f} {-scale:.6f})">{paths}</g>')


def _slot_svg(x, y, cell):
    """Write one self-contained lacquer-and-nacre mine slot."""
    from pixel_readme import PixelText

    ore = cell['ore'] if cell else 'stone'
    source = ROOT / 'assets' / 'blocks' / ('mined' if cell else '') / f'{ore}.svg'
    block_uri = 'data:image/svg+xml;base64,' + base64.b64encode(source.read_bytes()).decode('ascii')
    font = PixelText(ROOT)
    label = '' if cell is None else '채굴 완료'
    reward = '' if cell is None else f'{ORES[ore][0]} 획득'
    coord = _pixel_group(font, str(x + 1), 80, 22, size=16, fill='#e7eef2')
    labels = '' if cell is None else (
        _pixel_group(font, label, 80, 137, size=14)
        + _pixel_group(font, reward, 80, 160, size=14, fill='#b9eba6'))
    # The rectilinear corners borrow the proportions of Joseon key-fret inlay.
    corner = ('M6 31V6h25 M11 27V11h16v8h-8v-4h4 '
              'M154 31V6h-25 M149 27V11h-16v8h8v-4h-4 '
              'M6 145v25h25 M11 149v16h16v-8h-8v4h4 '
              'M154 145v25h-25 M149 149v16h-16v-8h8v4h-4')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="160" height="176" viewBox="0 0 160 176" role="img">
<title>{escape(str(x + 1) + '열 ' + str(y + 1) + '행' + (': 돌' if cell is None else ': 채굴 완료, ' + ORES[ore][0] + ' 획득'))}</title>
<defs>
  <linearGradient id="lacquer" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#111820"/><stop offset=".52" stop-color="#05090d"/><stop offset="1" stop-color="#10151b"/></linearGradient>
  <linearGradient id="nacre" x1="0%" y1="0%" x2="100%" y2="100%"><stop stop-color="#91edf0"/><stop offset="28%" stop-color="#f3d5ea"/><stop offset="55%" stop-color="#e8cf86"/><stop offset="78%" stop-color="#91c9f5"/><stop offset="100%" stop-color="#c7f4db"/></linearGradient>
</defs>
<rect x="1.5" y="1.5" width="157" height="173" rx="2" fill="url(#lacquer)" stroke="#18242c" stroke-width="3"/>
<path d="M5 5h150v2H7v164H5zm150 0v166H5v-2h148V5z" fill="#bceef0"/>
<rect x="10" y="10" width="140" height="156" fill="none" stroke="#c5a764" stroke-opacity=".78"/>
<path d="{corner}" fill="none" stroke="#8de6ec" stroke-width="3" stroke-linecap="square" stroke-linejoin="miter"/>
<g fill="#72d4da"><path d="M5 5h27v4H9v23H5zM11 11h16v4H15v12h-4z"/><path d="M155 5h-27v4h23v23h4zM149 11h-16v4h12v12h4z"/><path d="M5 171h27v-4H9v-23H5zM11 165h16v-4H15v-12h-4z"/><path d="M155 171h-27v-4h23v-23h4zM149 165h-16v-4h12v-12h4z"/></g>
<g fill="#efc7e5" stroke="#dfbd72" stroke-width=".7"><path d="M8 4l4 4-4 4-4-4z"/><path d="M152 4l4 4-4 4-4-4z"/><path d="M8 164l4 4-4 4-4-4z"/><path d="M152 164l4 4-4 4-4-4z"/></g>
<g fill="#eed7a0"><path d="M56 6l6 4 6-4 6 4 6-4 6 4 6-4 6 4 6-4v3l-6 4-6-4-6 4-6-4-6 4-6-4-6 4-6-4z"/><path d="M56 170l6-4 6 4 6-4 6 4 6-4 6 4 6-4 6 4v-3l-6-4-6 4-6-4-6 4-6-4-6 4-6-4-6 4z"/></g>
{coord}
<image x="50" y="48" width="60" height="60" preserveAspectRatio="xMidYMid meet" href="{block_uri}"/>
{labels}
</svg>
'''
    MINE_SLOT_DIR.mkdir(parents=True, exist_ok=True)
    path = MINE_SLOT_DIR / f'cell-{y + 1}-{x + 1}.svg'
    path.write_text(svg)
    return path.relative_to(ROOT).as_posix()

def new_grid():
    # Draw ore on mining, so the public state file cannot reveal hidden ores.
    return [[None for _ in range(WIDTH)] for _ in range(HEIGHT)]

def initial_state():
    return dict(layer=1, grid=new_grid(), miners={}, totals={}, receipts={}, daily_claims={}, log=[])

def play(state, title, user, issue_id, rng=random, played_on=None):
    key = str(issue_id)
    if key in state['receipts']:
        return state['receipts'][key]
    match = re.fullmatch(r'mine\|([1-9][0-9]{0,5})\|([0-5])\|([0-2])', title)
    if not match or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]{0,38}', user):
        return None
    played_on = played_on or datetime.now(timezone.utc).date().isoformat()
    daily_claims = state.setdefault('daily_claims', {})
    layer, x, y = map(int, match.groups())
    if user in daily_claims.get(played_on, []):
        result = '오늘은 이미 채굴했습니다. UTC 자정 이후 다시 도전해주세요.'
    elif layer != state['layer']:
        result = '이미 지나간 층입니다. 최신 README에서 블록을 다시 골라주세요.'
    elif state['grid'][y][x] is not None:
        result = '이미 누군가 캔 블록입니다. 다른 블록을 골라주세요.'
    else:
        ore = rng.choices(list(ORES), weights=[v[3] for v in ORES.values()])[0]
        name, emoji, points, _ = ORES[ore]
        state['grid'][y][x] = dict(ore=ore, user=user)
        miner = state['miners'].setdefault(user, dict(blocks=0, score=0))
        miner['blocks'] += 1
        miner['score'] += points
        state['totals'][ore] = state['totals'].get(ore, 0) + 1
        daily_claims.setdefault(played_on, []).append(user)
        result = f'{emoji} @{user}: {name} 획득! +{points}점'
        state['log'] = (state['log'] + [result])[-5:]
        if all(cell is not None for row in state['grid'] for cell in row):
            state['layer'] += 1
            state['grid'] = new_grid()
            result += ' 이 층을 전부 캤습니다. 다음 층이 열렸어요!'
    state['receipts'][key] = result
    return result

def replace(text, name, content):
    pattern = rf'<!-- {name}:START -->.*?<!-- {name}:END -->'
    if len(re.findall(pattern, text, re.S)) != 1:
        raise ValueError(f'Missing or duplicate README marker: {name}')
    return re.sub(pattern, lambda _: f'<!-- {name}:START -->\n{content}\n<!-- {name}:END -->', text, flags=re.S)

def render(text, state, live=False, repo='oi-RYH/oi-RYH'):
    notice_text = ('돌을 클릭하고 열린 이슈를 제출하면 채굴됩니다. GitHub 계정당 UTC 기준 하루 1회 채굴할 수 있습니다.' if live else
                   '**미리보기 모드** · 광산 자동화는 기본 브랜치에 반영한 뒤 활성화됩니다. 지금은 이슈가 생성되지 않습니다.')
    notice = f'<p align="center">{notice_text}</p>'
    rows = ['<p align="center">']
    for y, row in enumerate(state['grid']):
        cells = []
        for x, cell in enumerate(row):
            ore = cell['ore'] if cell else 'stone'
            slot = _slot_svg(x, y, cell)
            alt = (f'{x+1}열 {y+1}행: {ORES[ore][0]}' if cell is None
                   else f'{x+1}열 {y+1}행: 채굴 완료, {ORES[ore][0]} 획득')
            img = f'<img src="{slot}" width="16%" alt="{alt}">'
            if cell is None:
                query = urlencode(dict(title=f'mine|{state["layer"]}|{x}|{y}', body='제목을 그대로 두고 이슈를 제출하면 이 블록을 채굴합니다.'))
                link = f'https://github.com/{repo}/issues/new?{query}' if live else '#mine-help'
                img = f'<a href="{link}">{img}</a>'
            cells.append(img)
        rows.append(''.join(cells) + ('<br>' if y < HEIGHT - 1 else ''))
    rows.append('</p>')
    count = sum(cell is not None for row in state['grid'] for cell in row)
    stats = [f'<p align="center"><strong>지하 {state["layer"]}층</strong> · 이번 층 {count}/{WIDTH*HEIGHT}블록 · 누적 {sum(state["totals"].values())}블록</p>']
    if state['miners']:
        stats += ['', '<table align="center">',
                  '<thead><tr><th align="center">광부</th><th align="center">블록</th><th align="center">점수</th></tr></thead>',
                  '<tbody>']
        for user, rec in sorted(state['miners'].items(), key=lambda item: (-item[1]['score'], item[0]))[:5]:
            stats.append(f'<tr><td align="center"><a href="https://github.com/{user}">@{user}</a></td>'
                         f'<td align="center">{rec["blocks"]}</td><td align="center">{rec["score"]}</td></tr>')
        stats += ['</tbody>', '</table>', '', '<p align="center"><strong>최근 발견</strong><br>']
        for entry in reversed(state['log']):
            for ore, (name, emoji, _, _) in ORES.items():
                entry = entry.replace(emoji, f'<img src="assets/blocks/{ore}.svg" width="20" alt="{name}">')
            stats.append(entry + '<br>')
        stats.append('</p>')
    else:
        stats += ['', '<p align="center">아직 첫 광부가 없습니다. 오리는 곡괭이를 들 수 없거든요.</p>']
    for name, content in [('MINE_MODE', notice), ('MINE_GRID', '\n'.join(rows)), ('MINE_STATS', '\n'.join(stats))]:
        text = replace(text, name, content)
    return text

def api(repo, path, payload=None, method=None):
    data = None if payload is None else json.dumps(payload).encode()
    request = Request(f'https://api.github.com/repos/{repo}/{path}', data=data, method=method,
                      headers={'Authorization': 'Bearer ' + os.environ['GH_TOKEN'],
                               'Accept': 'application/vnd.github+json', 'Content-Type': 'application/json'})
    with urlopen(request, timeout=30) as response:
        return json.load(response)

def git(*args):
    return subprocess.run(['git', *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--queue', action='store_true')
    args = parser.parse_args()
    path = ROOT / 'data/mine.json'
    state = json.loads(path.read_text()) if path.exists() else initial_state()
    repo = os.environ.get('GITHUB_REPOSITORY', 'oi-RYH/oi-RYH')
    pending = []
    if args.queue:
        branch = os.environ['DEFAULT_BRANCH']
        if git('branch', '--show-current') != branch:
            raise RuntimeError('Only process live games on the default branch')
        # Scan open issues: workflow concurrency can replace pending runs.
        for page in range(1, 11):
            issues = api(repo, f'issues?state=open&sort=created&direction=asc&per_page=100&page={page}')
            for issue in issues:
                if 'pull_request' in issue or issue['user']['type'] != 'User':
                    continue
                played_on = str(issue.get('created_at', ''))[:10] or None
                result = play(state, issue['title'], issue['user']['login'], issue['number'], played_on=played_on)
                if result is not None:
                    pending.append((issue['number'], result))
                if len(pending) >= 50:
                    break
            if len(issues) < 100 or len(pending) >= 50:
                break
    if args.queue:
        from recent_repos import refresh
        try:
            refresh(repo.split('/')[0], ROOT)
        except Exception as error:
            # A temporary API failure must not block mining or clear the cards.
            if not (ROOT / 'data/recent-repos.json').exists():
                raise
            print(f'Recent repositories refresh failed; keeping last snapshot: {type(error).__name__}')
    from pixel_readme import build
    source = ROOT / 'README.source.md'
    rendered = render(source.read_text(), state, live=args.queue, repo=repo)
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')
    build(rendered, ROOT)
    if args.queue:
        git('add', 'README.md', 'data/mine.json', 'assets/text', 'assets/mine-grid', 'data/recent-repos.json',
            'assets/scenes/quest-board-python-body12.png', 'assets/scenes/quest-board-python-body12-1.png',
            'assets/scenes/quest-board-python-body12-2.png', 'assets/scenes/quest-board-python-body12-3.png')
        if git('diff', '--cached', '--name-only'):
            git('commit', '-m', 'chore: update community mine')
            # Do not announce success until the state is durably pushed.
            git('push', 'origin', f'HEAD:{branch}')
        for number, result in pending:
            marker = f'<!-- mine-receipt:{number} -->'
            comments = api(repo, f'issues/{number}/comments?per_page=100')
            if not any(marker in comment['body'] and comment['user']['login'] == 'github-actions[bot]' for comment in comments):
                api(repo, f'issues/{number}/comments', {'body': f'{marker}\n{result}\n\nhttps://github.com/{repo.split("/")[0]}'})
            api(repo, f'issues/{number}', {'state': 'closed'}, method='PATCH')

if __name__ == '__main__':
    main()
