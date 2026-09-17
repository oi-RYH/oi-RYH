"""Generate a self-contained Minecraft inventory from public GitHub stats."""
import argparse
from html import escape
import json
import os
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from activity_map import fetch_calendar, outlined
from pixel_readme import PixelText, ROOT

WIDTH, HEIGHT = 960, 330

LANGUAGE_COLORS = {
    'C++': '#5d8fc9', 'C#': '#a179dc', 'Python': '#f2c94c',
    'TypeScript': '#4f9ad7', 'JavaScript': '#f1d84b', 'Swift': '#f17a4b',
    'Java': '#e38c44', 'C': '#8da4bd', 'Rust': '#ce8252', 'Go': '#42b7ca',
    'HTML': '#e3653f', 'CSS': '#7e62c4', 'Kotlin': '#a578ef',
    'Dart': '#4bb7da', 'Shell': '#74b866', 'Jupyter Notebook': '#e88945',
}


def api(path, token):
    request = Request(
        f'https://api.github.com/{path}',
        headers={'Authorization': f'Bearer {token}',
                 'Accept': 'application/vnd.github+json',
                 'User-Agent': 'minecraft-player-inventory'})
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def fetch_stats(login, token):
    user = api(f'users/{quote(login, safe="")}', token)
    repos = []
    for page in range(1, 11):
        batch = api(f'users/{quote(login, safe="")}/repos?type=owner&sort=pushed&per_page=100&page={page}', token)
        repos.extend(batch)
        if len(batch) < 100:
            break
    owned = [repo for repo in repos if not repo.get('fork') and not repo.get('archived')]
    projects = [repo for repo in owned if repo['name'].lower() != login.lower()]
    languages = {}
    for repo in projects:
        result = api(f'repos/{quote(login, safe="")}/{quote(repo["name"], safe="")}/languages', token)
        for language, byte_count in result.items():
            languages[language] = languages.get(language, 0) + int(byte_count)
    calendar = fetch_calendar(login, token)
    active_days = [day for week in calendar.get('weeks', [])
                   for day in week.get('contributionDays', [])
                   if int(day.get('contributionCount', 0)) > 0]
    current = max(projects, key=lambda repo: repo.get('pushed_at') or '', default=None)
    return {
        'login': login,
        'public_repos': len(owned),
        'stars': sum(int(repo.get('stargazers_count', 0)) for repo in projects),
        'followers': int(user.get('followers', 0)),
        'year_contributions': int(calendar.get('totalContributions', 0)),
        'last_active': max((day['date'] for day in active_days), default='기록 없음'),
        'current_repo': current['name'] if current else '퀘스트 없음',
        'languages': languages,
    }


def slot(x, y, width, height):
    return (f'<rect class="slot" x="{x}" y="{y}" width="{width}" height="{height}"/>'
            f'<path class="slot-shadow" d="M{x} {y+height}V{y}H{x+width}"/>'
            f'<path class="slot-light" d="M{x} {y+height}H{x+width}V{y}"/>')


def stat_icon(kind, x, y):
    if kind == 'chest':
        return (f'<rect x="{x}" y="{y+5}" width="26" height="19" fill="#8a552d"/>'
                f'<rect x="{x}" y="{y+3}" width="26" height="6" fill="#b5773d"/>'
                f'<rect x="{x+11}" y="{y+8}" width="5" height="7" fill="#d9bc64"/>')
    if kind == 'star':
        return f'<path d="M{x+13} {y}l4 9 9 1-7 6 2 9-8-5-8 5 2-9-7-6 9-1z" fill="#f2c94c"/>'
    if kind == 'heads':
        return (f'<rect x="{x+2}" y="{y+2}" width="9" height="9" fill="#d39a72"/>'
                f'<rect x="{x}" y="{y+13}" width="13" height="10" fill="#4f91b8"/>'
                f'<rect x="{x+16}" y="{y+5}" width="8" height="8" fill="#bd835f"/>'
                f'<rect x="{x+14}" y="{y+15}" width="12" height="8" fill="#5c76a7"/>')
    return (f'<path d="M{x+2} {y+1}h8l5 5-4 4-3-3-6 17-4-2 7-17z" fill="#54c9c1"/>'
            f'<path d="M{x+11} {y+7}l11 11-4 4-11-11z" fill="#8a5b35"/>')


def avatar():
    # Steve with low-set rimless glasses, pickaxe and a silver laptop.
    return '''<g aria-label="안경을 쓰고 곡괭이와 맥북을 든 스티브">
  <rect x="75" y="69" width="72" height="72" fill="#9b633f"/>
  <rect x="75" y="69" width="72" height="17" fill="#352318"/>
  <rect x="75" y="83" width="12" height="20" fill="#352318"/>
  <rect x="135" y="83" width="12" height="20" fill="#352318"/>
  <rect x="87" y="102" width="23" height="15" fill="#d7e5ef" fill-opacity=".45" stroke="#e8eef2" stroke-width="2"/>
  <rect x="116" y="102" width="23" height="15" fill="#d7e5ef" fill-opacity=".45" stroke="#e8eef2" stroke-width="2"/>
  <rect x="110" y="107" width="6" height="2" fill="#e8eef2"/>
  <rect x="95" y="106" width="6" height="6" fill="#2c2144"/><rect x="124" y="106" width="6" height="6" fill="#2c2144"/>
  <rect x="75" y="141" width="72" height="46" fill="#3aada6"/>
  <rect x="88" y="187" width="22" height="27" fill="#443b89"/><rect x="112" y="187" width="22" height="27" fill="#443b89"/>
  <g transform="translate(42 128) rotate(-23)"><rect width="7" height="82" fill="#704729"/><path d="M-18 2h42v8H-18z" fill="#55cfc5"/></g>
  <g class="laptop"><rect x="139" y="145" width="42" height="31" rx="2" fill="#b9bec3" stroke="#e6e9eb" stroke-width="3"/><rect x="154" y="156" width="10" height="10" fill="#6f7479"/><path d="M135 177h51v6h-51z" fill="#868b90"/></g>
</g>'''


def stat_panel(font, x, y, label, value, icon):
    return (slot(x, y, 284, 58) + stat_icon(icon, x + 15, y + 16)
            + outlined(font, label, x + 54, y + 22, 11, 'slot-muted')
            + outlined(font, str(value), x + 54, y + 47, 21, 'bright'))


def language_slots(font, languages):
    total = sum(languages.values())
    ranked = sorted(languages.items(), key=lambda item: (-item[1], item[0]))[:5]
    output = []
    for index in range(5):
        x, y = 40 + index * 178, 264
        output.append(slot(x, y, 164, 56))
        if index >= len(ranked):
            output.append(outlined(font, 'EMPTY', x + 49, y + 34, 12, 'muted'))
            continue
        language, byte_count = ranked[index]
        percent = round(byte_count * 100 / total) if total else 0
        color = LANGUAGE_COLORS.get(language, '#8f9aa3')
        output.append(f'<rect class="item" x="{x+12}" y="{y+12}" width="30" height="30" fill="{color}"/>')
        output.append(f'<rect class="glint" x="{x+17}" y="{y+16}" width="8" height="5" fill="#ffffff" fill-opacity=".55"/>')
        display = language if len(language) <= 16 else language[:15] + '…'
        output.append(outlined(font, display, x + 50, y + 24, 11, 'slot-muted'))
        output.append(outlined(font, f'{percent}%', x + 50, y + 44, 13, 'bright'))
    return ''.join(output)


def render(stats):
    font = PixelText(ROOT)
    login = str(stats.get('login', 'player'))
    current = str(stats.get('current_repo', '퀘스트 없음'))
    current_display = current if len(current) <= 28 else current[:27] + '…'
    title = escape(f'{login} Minecraft player inventory')
    description = escape(
        f"{stats.get('public_repos', 0)} public repositories, {stats.get('stars', 0)} stars, "
        f"{stats.get('followers', 0)} followers, {stats.get('year_contributions', 0)} contributions in the last year.")
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc" shape-rendering="crispEdges">
<title id="title">{title}</title><desc id="desc">{description}</desc>
<style>
  .panel{{fill:#c6c6c6;stroke:#1f1f1f;stroke-width:5}} .panel-light{{fill:none;stroke:#ffffff;stroke-width:4}} .panel-shadow{{fill:none;stroke:#555555;stroke-width:4}}
  .slot{{fill:#252a2e}} .slot-shadow{{fill:none;stroke:#555b60;stroke-width:4}} .slot-light{{fill:none;stroke:#e5e5e5;stroke-width:3}}
  .ink{{fill:#242424}} .bright{{fill:#b6e89b}} .muted{{fill:#687078}} .slot-muted{{fill:#b8c0c5}}
  .item{{stroke:#15191c;stroke-width:3}} .glint{{animation:glint 2.8s steps(2,end) infinite}} .laptop{{animation:laptop 3s steps(2,end) infinite}}
  @keyframes glint{{50%{{opacity:.15}}}} @keyframes laptop{{50%{{filter:brightness(1.18)}}}}
  @media(prefers-reduced-motion:reduce){{.glint,.laptop{{animation:none}}}}
</style>
<rect class="panel" x="2" y="2" width="956" height="326"/>
<path class="panel-light" d="M8 322V8H952"/><path class="panel-shadow" d="M8 322H952V8"/>
{outlined(font, 'PLAYER INVENTORY', 38, 37, 22, 'ink')}
{outlined(font, f'CURRENT QUEST · {current_display}', 560, 33, 12, 'muted')}
{avatar()}
{outlined(font, f'PLAYER · {login}', 64, 236, 13, 'ink')}
{outlined(font, 'MAIN: PICKAXE · OFF: MACBOOK', 286, 236, 12, 'muted')}
{stat_panel(font, 286, 58, 'PUBLIC REPOS', stats.get('public_repos', 0), 'chest')}
{stat_panel(font, 588, 58, 'STARS EARNED', stats.get('stars', 0), 'star')}
{stat_panel(font, 286, 128, 'FOLLOWERS', stats.get('followers', 0), 'heads')}
{stat_panel(font, 588, 128, 'YEAR BLOCKS', stats.get('year_contributions', 0), 'pickaxe')}
{outlined(font, f'LAST LOGIN · {stats.get("last_active", "기록 없음")}', 588, 215, 12, 'muted')}
{outlined(font, 'LANGUAGE HOTBAR', 40, 256, 12, 'ink')}
{language_slots(font, stats.get('languages', {}))}
</svg>'''
    ET.fromstring(svg)
    return svg + '\n'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='dist/player-inventory.svg')
    parser.add_argument('--fixture')
    args = parser.parse_args()
    if args.fixture:
        stats = json.loads(Path(args.fixture).read_text())
    else:
        token = os.environ.get('GH_TOKEN')
        if not token:
            raise RuntimeError('GH_TOKEN is required without --fixture')
        login = os.environ.get('GITHUB_REPOSITORY_OWNER', 'oi-RYH')
        stats = fetch_stats(login, token)
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render(stats))


if __name__ == '__main__':
    main()
