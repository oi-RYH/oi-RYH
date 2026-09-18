"""Build the deliberately low-fi interactive scenes used by the README."""
import json

from pixel_readme import PixelText, ROOT


def wrap(text, font, width, size, lines=2):
    words = text.split()
    out, line = [], ''
    for word in words:
        candidate = f'{line} {word}'.strip()
        if line and font.paths(candidate, size)[0] > width:
            out.append(line)
            line = word
        else:
            line = candidate
    if line:
        out.append(line)
    if not out:
        out = ['저장소에서 자세한 내용을', '확인하세요.']
    if len(out) > lines:
        out = out[:lines]
        while out[-1] and font.paths(out[-1] + '…', size)[0] > width:
            out[-1] = out[-1][:-1].rstrip()
        out[-1] += '…'
    return out


def paths(font, text, x, y, size, fill):
    _, glyphs, scale = font.paths(text, size)
    return f'<g transform="translate({x} {y}) scale({scale} {-scale})" fill="{fill}">{glyphs}</g>'


def write_quest_board(repos, root=ROOT):
    """Put the live repository data onto a small, flat pixel notice board."""
    output = root / 'assets/scenes'
    output.mkdir(parents=True, exist_ok=True)
    font = PixelText(root)
    cards = []
    for index, repo in enumerate(repos[:3]):
        x = 40 + index * 305
        name = repo['name']
        while name and font.paths(name, 17)[0] > 245:
            name = name[:-1]
        if name != repo['name']:
            name += '…'
        cards.append(f'<g><rect x="{x}" y="34" width="270" height="192" class="paper"/><rect x="{x+126}" y="27" width="18" height="18" class="pin"/></g>')
        cards.append(paths(font, name, x + 18, 72, 17, '#302113'))
        description = repo.get('description') or '저장소에서 자세한 내용을 확인하세요.'
        for row, line in enumerate(wrap(description, font, 232, 13)):
            cards.append(paths(font, line, x + 18, 116 + row * 23, 13, '#5a452d'))
        language = repo.get('language') or '언어 정보 없음'
        cards.append(paths(font, f'◆ {language}', x + 18, 178, 12, '#285e28'))
        cards.append(paths(font, f'업데이트 · {repo["pushed_at"][:10]}', x + 18, 208, 10, '#7a6142'))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="258" viewBox="0 0 960 258" role="img" aria-labelledby="title desc" shape-rendering="crispEdges">
  <title id="title">현재 퀘스트 게시판</title><desc id="desc">최근 푸시한 공개 저장소 세 개가 픽셀 의뢰서로 붙어 있습니다.</desc>
  <style>.paper{{fill:#d9c79b;stroke:#76502e;stroke-width:5}}.pin{{fill:#d9a441;animation:pin 2.4s steps(2,end) infinite}}@keyframes pin{{50%{{transform:translateY(2px)}}}}@media(prefers-reduced-motion:reduce){{.pin{{animation:none}}}}</style>
  <rect width="960" height="258" rx="5" fill="#111820"/>
  <path d="M0 218h960v40H0z" fill="#0a0f14"/>
  <rect x="14" y="12" width="932" height="230" fill="#4f321f" stroke="#76502e" stroke-width="7"/>
  <path d="M24 23h912M24 232h912" stroke="#2e1c13" stroke-width="7" stroke-dasharray="55 9"/>
  {''.join(cards)}
</svg>\n'''
    (output / 'quest-board.svg').write_text(svg)


def write_mine_shift(root=ROOT):
    """Build a short side-view mining loop with intentionally chunky sprites."""
    output = root / 'assets/scenes'
    output.mkdir(parents=True, exist_ok=True)
    shades = ['#343a40', '#3d4349', '#2c3238']
    tiles = ''.join(
        f'<rect x="{col*40}" y="{row*34}" width="38" height="32" fill="{shades[(row+col)%3]}"/>'
        for row in range(4) for col in range(24)
    )
    floor = ''.join(
        f'<rect x="{col*40}" y="220" width="38" height="38" fill="{shades[(col+1)%3]}"/>'
        for col in range(24)
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="258" viewBox="0 0 960 258" role="img" aria-labelledby="title desc" shape-rendering="crispEdges">
  <title id="title">스티브의 작업 교대</title><desc id="desc">단순한 스티브가 세 채굴 지점으로 빠르게 이동해 곡괭이질하고 닭은 광산을 돌아다닙니다.</desc>
  <rect width="960" height="258" fill="#10161d"/>
  <g opacity=".72">{tiles}</g>
  <path d="M0 118h960v102H0z" fill="#151c23"/>
  <path d="M0 196h960v24H0z" fill="#202831"/>
  {floor}
  <g fill="#4a5158"><rect x="208" y="150" width="42" height="46"/><rect x="508" y="150" width="42" height="46"/><rect x="808" y="150" width="42" height="46"/></g>
  <g fill="#6b737b"><rect x="215" y="157" width="10" height="10"/><rect x="233" y="174" width="9" height="9"/><rect x="516" y="171" width="11" height="11"/><rect x="532" y="155" width="9" height="9"/><rect x="817" y="160" width="10" height="10"/><rect x="833" y="179" width="8" height="8"/></g>
  <g fill="#d8a62a"><rect x="218" y="160" width="6" height="6"/><rect x="535" y="158" width="6" height="6"/></g>
  <g fill="#49c5c1"><rect x="520" y="175" width="7" height="7"/><rect x="820" y="163" width="7" height="7"/></g>

  <g class="steve" transform="translate(118 102)">
    <animateTransform attributeName="transform" type="translate" dur="12s" repeatCount="indefinite" calcMode="linear" keyTimes="0;.20;.235;.47;.505;.74;.775;1" values="118 102;118 102;418 102;418 102;718 102;718 102;118 102;118 102"/>
    <rect width="48" height="42" fill="#79533b"/>
    <rect x="7" y="17" width="12" height="7" fill="#d7c3ad"/><rect x="29" y="17" width="12" height="7" fill="#d7c3ad"/>
    <path d="M5 15h17v11H5zm21 0h17v11H26zM22 19h4" fill="none" stroke="#cbd0d6" stroke-width="2"/>
    <rect y="42" width="48" height="42" fill="#36a7aa"/>
    <rect y="84" width="48" height="38" fill="#5142a5"/><rect x="21" y="99" width="6" height="23" fill="#151c23"/>
    <g transform="translate(43 55)">
      <g class="pickaxe" transform="rotate(-38)">
        <animateTransform attributeName="transform" type="rotate" dur=".9s" repeatCount="indefinite" values="-38;18;-38"/>
        <path d="M2 4L34-34" stroke="#8d5d32" stroke-width="7"/>
        <path d="M20-43h40v9H20zM51-34h9v10h-9z" fill="#4dc9cd"/>
      </g>
    </g>
  </g>

  <g class="chicken" transform="translate(690 172)">
    <animateTransform attributeName="transform" type="translate" dur="15s" repeatCount="indefinite" values="690 172;510 169;790 172;330 168;690 172"/>
    <rect width="38" height="29" fill="#e9e4d7"/><rect x="21" y="-18" width="24" height="25" fill="#f4f0e5"/>
    <rect x="45" y="-9" width="9" height="7" fill="#e5ae28"/><rect x="28" y="-11" width="4" height="4" fill="#1b2025"/>
    <rect x="25" y="7" width="7" height="8" fill="#c84b3f"/><path d="M9 29v13m20-13v13" stroke="#d99c2b" stroke-width="5"/>
  </g>
  <style>@media(prefers-reduced-motion:reduce){{animateTransform{{display:none}}}}</style>
</svg>\n'''
    (output / 'mine-shift.svg').write_text(svg)


def build():
    repos = json.loads((ROOT / 'data/recent-repos.json').read_text())
    write_quest_board(repos)
    write_mine_shift()


if __name__ == '__main__':
    build()
