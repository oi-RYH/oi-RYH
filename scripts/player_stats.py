"""Generate a self-contained Minecraft inventory from public GitHub stats."""
import argparse
import base64
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
    # A Minecraft-style diamond pickaxe: stepped cyan head, dark outline and
    # a diagonal wooden handle. Keeping every edge on the pixel grid makes the
    # silhouette stay readable at the inventory card's native size.
    return (f'<g data-icon="diamond-pickaxe" aria-label="diamond pickaxe">'
            f'<path d="M{x+1} {y+2}h17v3h4v4h-5V{y+7}h-4v4H{x+9}V{y+7}H{x+5}v3H{x+1}z" fill="#173f43"/>'
            f'<path d="M{x+2} {y+1}h16v3h4v4h-5V{y+6}h-5v4H{x+9}V{y+6}H{x+5}v3H{x+2}z" fill="#50d7d0"/>'
            f'<path d="M{x+14} {y+8}h5v5h-3v4h-4v4H{x+8}v4H{x+3}v-5h4v-4h4v-4h3z" fill="#4b2d1d"/>'
            f'<path d="M{x+15} {y+8}h3v5h-3v4h-4v4H{x+7}v3H{x+4}v-3h4v-4h4v-4h3z" fill="#9a6338"/>'
            f'</g>')


def language_icon(font, language, x, y):
    """Return a compact, recognizable pixel rendition of a language logo."""
    color = LANGUAGE_COLORS.get(language, '#8f9aa3')
    start = f'<g data-language-icon="{escape(language)}" aria-label="{escape(language)} logo">'
    end = '</g>'
    if language in ('JavaScript', 'TypeScript'):
        initials = 'JS' if language == 'JavaScript' else 'TS'
        ink = '#242424' if language == 'JavaScript' else '#ffffff'
        return (start + f'<rect x="{x}" y="{y}" width="30" height="30" rx="2" fill="{color}"/>'
                + outlined(font, initials, x + 8, y + 23, 10, ink) + end)
    if language == 'Swift':
        return (start + f'<rect x="{x}" y="{y}" width="30" height="30" rx="3" fill="#f47746"/>'
                f'<path d="M{x+5} {y+7}c5 4 8 5 12 7-3-3-5-6-6-8 5 4 9 6 12 7-2-4-5-7-8-9 7 3 11 8 10 14 0 3-2 5-5 6 1-3 0-5-3-7-5 2-11-2-12-6 3 2 6 3 10 3-5-2-9-6-12-11z" fill="#fff"/>'
                f'<path d="M{x+20} {y+18}c3 0 5 2 5 5-2-2-4-2-7-1z" fill="#fff"/>' + end)
    if language == 'CSS':
        return (start + f'<path d="M{x+3} {y+2}h24l-2 23-10 3-10-3z" fill="#6b56c9"/>'
                f'<path d="M{x+15} {y+5}h9l-2 17-7 2z" fill="#8d76e5"/>'
                f'<path d="M{x+8} {y+7}h14l-1 4h-8v3h8l-1 8-5 2-6-2-1-5h4l1 2 3 1 1-3H{x+9}z" fill="#fff"/>' + end)
    if language == 'Kotlin':
        return (start + f'<rect x="{x}" y="{y}" width="30" height="30" rx="2" fill="#7f52ff"/>'
                f'<path d="M{x} {y}h30L{x} {y+30}z" fill="#f18b55"/>'
                f'<path d="M{x} {y+30}l15-15 15 15z" fill="#b657d4"/>'
                f'<path d="M{x+7} {y+6}h5v7l7-7h6l-9 9 9 9h-7l-6-7v7H{x+7}z" fill="#fff" fill-opacity=".92"/>' + end)
    if language == 'Python':
        return (start + f'<path d="M{x+7} {y+3}h10c4 0 6 2 6 6v5H{x+12}v3H{x+5}V{y+9}c0-3 2-6 2-6z" fill="#4381a8"/>'
                f'<rect x="{x+10}" y="{y+6}" width="3" height="3" fill="#fff"/>'
                f'<path d="M{x+23} {y+27}H{x+13}c-4 0-6-2-6-6v-5h11v-3h7v8c0 3-2 6-2 6z" fill="#f0c94a"/>'
                f'<rect x="{x+17}" y="{y+21}" width="3" height="3" fill="#fff"/>' + end)
    if language in ('C', 'C++', 'C#'):
        suffix = {'C': 'C', 'C++': 'C++', 'C#': 'C#'}[language]
        size = 8 if language != 'C' else 12
        return (start + f'<path d="M{x+15} {y+1}l13 7v14l-13 7-13-7V{y+8}z" fill="{color}"/>'
                f'<path d="M{x+15} {y+5}l9 5v10l-9 5-9-5V{y+10}z" fill="#263747" fill-opacity=".35"/>'
                + outlined(font, suffix, x + (8 if language != 'C' else 10), y + 20, size, '#ffffff') + end)
    if language == 'Java':
        return (start + f'<path d="M{x+9} {y+20}h13v3c0 4-3 5-7 5s-6-1-6-5z" fill="#4e85a6"/>'
                f'<path d="M{x+22} {y+21}h4v4h-4" fill="none" stroke="#4e85a6" stroke-width="2"/>'
                f'<path d="M{x+13} {y+18}c7-4-4-5 4-10M{x+18} {y+17}c7-5-3-6 4-12" fill="none" stroke="#e47743" stroke-width="2"/>' + end)
    if language == 'HTML':
        return (start + f'<path d="M{x+3} {y+2}h24l-2 23-10 3-10-3z" fill="#e3653f"/>'
                + outlined(font, '5', x + 11, y + 21, 13, '#ffffff') + end)
    if language == 'Dart':
        return (start + f'<path d="M{x+5} {y+4}l13-2 8 8-2 14-8 4L{x+4} {y+16}z" fill="#49b9d5"/>'
                f'<path d="M{x+5} {y+4}l11 12h10M{x+4} {y+16}h12l8 8" fill="none" stroke="#e7fbff" stroke-width="2"/>' + end)
    if language == 'Shell':
        return (start + f'<rect x="{x+1}" y="{y+3}" width="28" height="24" rx="3" fill="#29343a" stroke="#74b866" stroke-width="2"/>'
                f'<path d="M{x+6} {y+10}l5 5-5 5M{x+14} {y+20}h9" fill="none" stroke="#e9f6e8" stroke-width="2"/>' + end)
    if language == 'Go':
        return start + f'<ellipse cx="{x+15}" cy="{y+15}" rx="14" ry="10" fill="#42b7ca"/>' + outlined(font, 'GO', x + 6, y + 19, 9, '#ffffff') + end
    if language == 'Rust':
        return (start + f'<circle cx="{x+15}" cy="{y+15}" r="13" fill="#352f2c"/>'
                f'<path d="M{x+15} {y}v5M{x+15} {y+25}v5M{x} {y+15}h5M{x+25} {y+15}h5" stroke="#ce8252" stroke-width="3"/>'
                + outlined(font, 'R', x + 10, y + 20, 11, '#ffffff') + end)
    if language == 'Jupyter Notebook':
        return (start + f'<circle cx="{x+15}" cy="{y+15}" r="10" fill="none" stroke="#e88945" stroke-width="4"/>'
                f'<circle cx="{x+8}" cy="{y+3}" r="2" fill="#777"/><circle cx="{x+23}" cy="{y+27}" r="2" fill="#777"/>' + end)
    return (start + f'<rect x="{x}" y="{y}" width="30" height="30" rx="3" fill="{color}"/>'
            f'<path d="M{x+7} {y+8}h16v3H{x+11}v8h12v3H{x+7}z" fill="#fff" fill-opacity=".9"/>' + end)


AVATAR_IMAGE = ROOT / 'assets' / 'player-avatar.jpg'


def avatar():
    # Cropped screenshot of Steve (glasses, pickaxe, silver laptop) framed like an inventory slot.
    data = base64.b64encode(AVATAR_IMAGE.read_bytes()).decode('ascii')
    return f'''<g aria-label="안경을 쓰고 곡괭이와 맥북을 든 스티브">
  {slot(20, 60, 170, 160)}
  <clipPath id="avatar-clip"><rect x="24" y="64" width="162" height="152"/></clipPath>
  <image x="24" y="64" width="162" height="152" clip-path="url(#avatar-clip)"
    preserveAspectRatio="xMidYMid slice" href="data:image/jpeg;base64,{data}"/>
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
        output.append(language_icon(font, language, x + 12, y + 12))
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
