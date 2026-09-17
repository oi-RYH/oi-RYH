"""Generate a self-contained Minecraft activity map from GitHub contributions."""
import argparse
from datetime import date
from html import escape
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from pixel_readme import PixelText, ROOT

WIDTH, HEIGHT = 960, 252
GRID_X, GRID_Y, STEP, BLOCK = 43, 55, 16, 12

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays { contributionCount date weekday }
        }
      }
    }
  }
}
"""


def fetch_calendar(login, token):
    payload = json.dumps({'query': QUERY, 'variables': {'login': login}}).encode()
    request = Request(
        'https://api.github.com/graphql', data=payload,
        headers={'Authorization': f'Bearer {token}',
                 'Accept': 'application/vnd.github+json',
                 'Content-Type': 'application/json',
                 'User-Agent': 'minecraft-activity-map'})
    with urlopen(request, timeout=30) as response:
        result = json.load(response)
    if result.get('errors'):
        raise RuntimeError(result['errors'][0].get('message', 'GitHub GraphQL error'))
    user = result.get('data', {}).get('user')
    if not user:
        raise RuntimeError(f'GitHub user not found: {login}')
    return user['contributionsCollection']['contributionCalendar']


def contribution_level(count, maximum):
    if count <= 0:
        return 0
    return min(4, 1 + ((count - 1) * 4 // max(1, maximum)))


def outlined(font, text, x, y, size, css_class):
    _, paths, scale = font.paths(text, size)
    return (f'<g class="{css_class}" transform="translate({x} {y}) '
            f'scale({scale} {-scale})">{paths}</g>')


def block(day, week_index, maximum, sparkle=False):
    count = int(day.get('contributionCount', 0))
    level = contribution_level(count, maximum)
    x = GRID_X + week_index * STEP
    y = GRID_Y + int(day.get('weekday', 0)) * STEP
    ore = {
        1: '#343a40',  # coal
        2: '#d89b65',  # iron
        3: '#f2c94c',  # gold
        4: '#56d8c4',  # diamond
    }.get(level)
    parts = [f'<g class="day level-{level}" data-date="{escape(str(day.get("date", "")))}" '
             f'data-count="{count}">',
             f'<rect x="{x}" y="{y}" width="{BLOCK}" height="{BLOCK}" rx="1"/>',
             f'<path class="edge" d="M{x} {y+BLOCK}V{y}H{x+BLOCK}"/>']
    if ore:
        parts += [f'<rect class="ore" x="{x+3}" y="{y+3}" width="3" height="3" fill="{ore}"/>',
                  f'<rect class="ore" x="{x+8}" y="{y+7}" width="2" height="3" fill="{ore}"/>']
        if level >= 3:
            parts.append(f'<rect class="ore" x="{x+4}" y="{y+9}" width="2" height="2" fill="{ore}"/>')
    if sparkle:
        parts.append(f'<rect class="spark" x="{x+8}" y="{y+1}" width="2" height="2" fill="#fff7b2"/>')
    parts.append('</g>')
    return ''.join(parts)


def chicken_cart(identifier, resting=False):
    css_class = 'cart-rest' if resting else 'cart'
    # Pixel chicken in a minecart. All coordinates are relative to the cart.
    return f'''<g id="{identifier}" class="{css_class}">
  <rect x="8" y="-13" width="12" height="10" fill="#f4f0df"/>
  <rect x="11" y="-16" width="9" height="5" fill="#f4f0df"/>
  <rect x="18" y="-14" width="5" height="4" fill="#e0a11b"/>
  <rect x="13" y="-14" width="2" height="2" fill="#17191c"/>
  <rect x="9" y="-4" width="3" height="4" fill="#cf3e35"/>
  <path d="M2 0h25l-3 10H6z" fill="#737b82" stroke="#b2bac2" stroke-width="2"/>
  <rect x="6" y="2" width="17" height="3" fill="#40464c"/>
  <rect x="7" y="10" width="5" height="3" fill="#16191d"/>
  <rect x="19" y="10" width="5" height="3" fill="#16191d"/>
</g>'''


def render(calendar, login='oi-RYH'):
    weeks = calendar.get('weeks', [])[-53:]
    days = [day for week in weeks for day in week.get('contributionDays', [])]
    maximum = max((int(day.get('contributionCount', 0)) for day in days), default=0)
    total = int(calendar.get('totalContributions', sum(int(d.get('contributionCount', 0)) for d in days)))
    active = [day for day in days if int(day.get('contributionCount', 0)) > 0]
    sparkling_dates = {day.get('date') for day in active[-7:]}
    cells = ''.join(block(day, week_index, maximum, day.get('date') in sparkling_dates)
                    for week_index, week in enumerate(weeks)
                    for day in week.get('contributionDays', []))
    font = PixelText(ROOT)
    today = date.today().isoformat()
    xp_segments = max(1, (total % 100 + 9) // 10) if total else 0
    xp = ''.join(f'<rect x="{310+i*24}" y="224" width="20" height="8" '
                 f'fill="{"#55d36a" if i < xp_segments else "#183126"}"/>' for i in range(10))
    sleepers = ''.join(f'<rect x="{36+i*32}" y="187" width="5" height="14" class="sleeper"/>'
                       for i in range(28))

    title = escape(f"{login}'s Minecraft contribution mine: {total} contributions")
    description = escape('A 53 by 7 block activity map. A chicken rides a minecart below recent contribution ore blocks.')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc" shape-rendering="crispEdges">
<title id="title">{title}</title><desc id="desc">{description}</desc>
<style>
  .frame{{fill:#0d1117;stroke:#405344;stroke-width:4}} .corner{{fill:#6b4c2e}}
  .label{{fill:#b6e89b}} .muted{{fill:#96a29c}}
  .day rect:first-child{{fill:#18212b}} .day .edge{{fill:none;stroke:#283440;stroke-width:2}}
  .level-1 rect:first-child{{fill:#343a40}} .level-1 .edge{{stroke:#525a61}}
  .level-2 rect:first-child{{fill:#4b4a46}} .level-2 .edge{{stroke:#68665f}}
  .level-3 rect:first-child{{fill:#51482f}} .level-3 .edge{{stroke:#75683e}}
  .level-4 rect:first-child{{fill:#294d49}} .level-4 .edge{{stroke:#3d716a}}
  .rail{{fill:#8f969d}} .sleeper{{fill:#6e4628}} .xp-frame{{fill:#08110d;stroke:#3a7d44;stroke-width:2}}
  .spark{{animation:twinkle 1.8s steps(2,end) infinite}} .spark:nth-of-type(2n){{animation-delay:.7s}}
  @keyframes twinkle{{50%{{opacity:.15}}}}
  #cart{{animation:ride 16s ease-in-out infinite}} @keyframes ride{{0%,100%{{transform:translate(35px,184px)}}50%{{transform:translate(895px,184px)}}}}
  #cart-rest{{display:none}}
  @media(prefers-reduced-motion:reduce){{#cart{{display:none}}#cart-rest{{display:block}}.spark{{animation:none}}}}
</style>
<rect class="frame" x="2" y="2" width="956" height="248" rx="4"/>
<path class="corner" d="M2 22V2h20v5H7v15zm956 0V2h-20v5h15v15zM2 230v20h20v-5H7v-15zm956 0v20h-20v-5h15v-15z"/>
{outlined(font, 'CODE CAVERNS', 42, 35, 20, 'label')}
{outlined(font, f'LAST SAVE {today}', 746, 32, 12, 'muted')}
<g id="contribution-blocks">{cells}</g>
<rect class="rail" x="32" y="188" width="896" height="3"/><rect class="rail" x="32" y="197" width="896" height="3"/>{sleepers}
{chicken_cart('cart')}{chicken_cart('cart-rest', resting=True).replace('class="cart-rest"', 'class="cart-rest" transform="translate(820 184)"')}
{outlined(font, f'지난 1년 · {total}블록', 42, 236, 15, 'label')}
<rect class="xp-frame" x="306" y="220" width="248" height="16"/>
{xp}
{outlined(font, '승객: 닭 · 기관사: 아직 없음', 565, 236, 13, 'muted')}
</svg>'''
    ET.fromstring(svg)
    return svg + '\n'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='dist/minecraft-activity.svg')
    parser.add_argument('--fixture')
    args = parser.parse_args()
    login = os.environ.get('GITHUB_REPOSITORY_OWNER', 'oi-RYH')
    if args.fixture:
        calendar = json.loads(Path(args.fixture).read_text())
    else:
        token = os.environ.get('GH_TOKEN')
        if not token:
            raise RuntimeError('GH_TOKEN is required without --fixture')
        calendar = fetch_calendar(login, token)
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render(calendar, login))


if __name__ == '__main__':
    main()
