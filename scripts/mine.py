"""Community mine: validated inputs, persistent receipts, no shell interpolation."""
import argparse
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

def new_grid():
    # Draw ore on mining, so the public state file cannot reveal hidden ores.
    return [[None for _ in range(WIDTH)] for _ in range(HEIGHT)]

def initial_state():
    return dict(layer=1, grid=new_grid(), miners={}, totals={}, receipts={}, log=[])

def play(state, title, user, issue_id, rng=random):
    key = str(issue_id)
    if key in state['receipts']:
        return state['receipts'][key]
    match = re.fullmatch(r'mine\|([1-9][0-9]{0,5})\|([0-5])\|([0-2])', title)
    if not match or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]{0,38}', user):
        return None
    layer, x, y = map(int, match.groups())
    if layer != state['layer']:
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
    notice = ('돌을 클릭하고 열린 이슈를 제출하면 채굴됩니다. 처리 후 이 페이지를 새로고침하세요. '
              'GitHub 로그인이 필요하며 결과 반영에는 시간이 걸릴 수 있습니다.' if live else
              '**미리보기 모드** · 광산 자동화는 기본 브랜치에 반영한 뒤 활성화됩니다. 지금은 이슈가 생성되지 않습니다.')
    rows = ['| ' + ' | '.join(str(x + 1) for x in range(WIDTH)) + ' |', '|' + ':---:|' * WIDTH]
    for y, row in enumerate(state['grid']):
        cells = []
        for x, cell in enumerate(row):
            ore = cell['ore'] if cell else 'stone'
            img = f'<img src="assets/blocks/{ore}.svg" width="44" alt="{x+1}열 {y+1}행: {ORES[ore][0]}">'
            if cell is None:
                query = urlencode(dict(title=f'mine|{state["layer"]}|{x}|{y}', body='제목을 그대로 두고 이슈를 제출하면 이 블록을 채굴합니다.'))
                link = f'https://github.com/{repo}/issues/new?{query}' if live else '#mine-help'
                img = f'[{img}]({link})'
            else:
                img = (f'<img src="assets/blocks/mined/{ore}.svg" width="44" '
                       f'alt="{x+1}열 {y+1}행: 채굴 완료, {ORES[ore][0]} 획득">'
                       f'<br><sub>채굴 완료<br>{ORES[ore][0]} 획득</sub>')
            cells.append(img)
        rows.append('| ' + ' | '.join(cells) + ' |')
    count = sum(cell is not None for row in state['grid'] for cell in row)
    stats = [f'**지하 {state["layer"]}층** · 이번 층 {count}/{WIDTH*HEIGHT}블록 · 누적 {sum(state["totals"].values())}블록']
    if state['miners']:
        stats += ['', '| 광부 | 블록 | 점수 |', '| :--- | ---: | ---: |']
        for user, rec in sorted(state['miners'].items(), key=lambda item: (-item[1]['score'], item[0]))[:5]:
            stats.append(f'| [@{user}](https://github.com/{user}) | {rec["blocks"]} | {rec["score"]} |')
        stats += ['', '**최근 발견**', '']
        for entry in reversed(state['log']):
            for ore, (name, emoji, _, _) in ORES.items():
                entry = entry.replace(emoji, f'<img src="assets/blocks/{ore}.svg" width="20" alt="{name}">')
            stats.append('- ' + entry)
    else:
        stats += ['', '아직 첫 광부가 없습니다. 오리는 곡괭이를 들 수 없거든요.']
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
                result = play(state, issue['title'], issue['user']['login'], issue['number'])
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
        git('add', 'README.md', 'data/mine.json', 'assets/text', 'data/recent-repos.json')
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
