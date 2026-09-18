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
    """Build a side-view abandoned mineshaft with chunky profile sprites."""
    output = root / 'assets/scenes'
    output.mkdir(parents=True, exist_ok=True)
    shades = ['#5a5d5e', '#626667', '#4e5253', '#686b6c']
    stone = ''.join(
        f'<g><rect x="{col*32}" y="{row*32}" width="31" height="31" fill="{shades[(row*3+col)%4]}"/>'
        f'<path d="M{col*32+3} {row*32+5}h9v4h-5v6h-4zm{col*32+17} {row*32+20}h9v4h-9z" fill="#777a7a" opacity=".45"/></g>'
        for row in range(10) for col in range(30)
    )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="300" viewBox="0 0 960 300" role="img" aria-labelledby="title desc" shape-rendering="crispEdges">
  <title id="title">스티브의 작업 교대</title><desc id="desc">단순한 스티브가 세 채굴 지점으로 빠르게 이동해 곡괭이질하고 닭은 광산을 돌아다닙니다.</desc>
  <rect width="960" height="300" fill="#303536"/>
  <g>{stone}</g>
  <path d="M0 105h64V72h64V88h96V55h96v28h96V66h128v25h96V58h96v31h96v-17h64v151H0z" fill="#10161b"/>
  <path d="M0 223h960v77H0z" fill="#4f5354"/>
  <path d="M0 223h960v8H0z" fill="#737778"/>

  <g fill="#684728"><rect x="70" y="80" width="18" height="143"/><rect x="872" y="80" width="18" height="143"/><rect x="70" y="80" width="820" height="18"/></g>
  <g fill="#8a6035"><rect x="76" y="80" width="6" height="143"/><rect x="878" y="80" width="6" height="143"/><rect x="70" y="85" width="820" height="6"/></g>
  <g fill="#684728"><rect x="337" y="98" width="14" height="125"/><rect x="609" y="98" width="14" height="125"/></g>
  <g fill="#8a6035"><rect x="341" y="98" width="5" height="125"/><rect x="613" y="98" width="5" height="125"/></g>

  <g><rect x="278" y="101" width="7" height="28" fill="#684728"/><rect x="270" y="124" width="23" height="10" fill="#f4b942"/><rect x="275" y="127" width="13" height="12" fill="#ffdd67"/></g>
  <g><rect x="675" y="101" width="7" height="28" fill="#684728"/><rect x="667" y="124" width="23" height="10" fill="#f4b942"/><rect x="672" y="127" width="13" height="12" fill="#ffdd67"/></g>

  <g fill="#555a5b" stroke="#74797a" stroke-width="3"><rect x="225" y="176" width="47" height="47"/><rect x="495" y="176" width="47" height="47"/><rect x="765" y="176" width="47" height="47"/></g>
  <g fill="#d7a82e"><rect x="232" y="183" width="10" height="10"/><rect x="255" y="201" width="9" height="9"/></g>
  <g fill="#4bc7c3"><rect x="502" y="197" width="11" height="11"/><rect x="525" y="181" width="9" height="9"/></g>
  <g fill="#56bd67"><rect x="772" y="185" width="10" height="10"/><rect x="794" y="204" width="9" height="9"/></g>
  <g stroke="#9fa5a5" stroke-width="5"><path d="M0 254h960"/><path d="M0 276h960"/></g>
  <path d="M20 248v34m55-34v34m55-34v34m55-34v34m55-34v34m55-34v34m55-34v34m55-34v34m55-34v34m55-34v34m55-34v34m55-34v34m55-34v34m55-34v34m55-34v34m55-34v34m55-34v34m55-34v34m55-34v34" stroke="#6d4729" stroke-width="9"/>

  <g class="steve" transform="translate(155 128)">
    <animateTransform attributeName="transform" type="translate" dur="12s" repeatCount="indefinite" calcMode="linear" keyTimes="0;.20;.235;.47;.505;.74;.775;1" values="155 128;155 128;425 128;425 128;695 128;695 128;155 128;155 128"/>
    <g class="right-profile">
      <animate attributeName="opacity" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0;.74;.775;1" values="1;0;1;1"/>
      <rect width="36" height="38" fill="#79533b"/><rect x="36" y="17" width="7" height="9" fill="#a97a58"/>
      <rect x="27" y="14" width="7" height="6" fill="#d7c3ad"/><rect x="31" y="15" width="3" height="3" fill="#30251f"/>
      <path d="M24 12h13v11H24" fill="none" stroke="#cbd0d6" stroke-width="2"/>
      <rect x="5" y="38" width="31" height="36" fill="#36a7aa"/><rect x="5" y="74" width="31" height="34" fill="#5142a5"/><rect x="18" y="91" width="5" height="17" fill="#10161b"/>
      <g transform="translate(34 57)"><g class="pickaxe" transform="rotate(-38)">
        <animateTransform attributeName="transform" type="rotate" dur=".9s" repeatCount="indefinite" values="-38;18;-38"/>
        <path d="M1 4L34-34" stroke="#8d5d32" stroke-width="7"/>
        <path d="M6-46h56v9H6zM6-37h9v9H6zm47 0h9v9h-9z" fill="#4dc9cd"/>
      </g></g>
    </g>
    <g class="left-profile" transform="translate(43 0) scale(-1 1)" opacity="0">
      <animate attributeName="opacity" dur="12s" repeatCount="indefinite" calcMode="discrete" keyTimes="0;.74;.775;1" values="0;1;0;0"/>
      <rect width="36" height="38" fill="#79533b"/><rect x="36" y="17" width="7" height="9" fill="#a97a58"/>
      <rect x="27" y="14" width="7" height="6" fill="#d7c3ad"/><rect x="31" y="15" width="3" height="3" fill="#30251f"/>
      <path d="M24 12h13v11H24" fill="none" stroke="#cbd0d6" stroke-width="2"/>
      <rect x="5" y="38" width="31" height="36" fill="#36a7aa"/><rect x="5" y="74" width="31" height="34" fill="#5142a5"/><rect x="18" y="91" width="5" height="17" fill="#10161b"/>
      <g transform="translate(34 57)"><g class="pickaxe" transform="rotate(-38)">
        <animateTransform attributeName="transform" type="rotate" dur=".9s" repeatCount="indefinite" values="-38;18;-38"/>
        <path d="M1 4L34-34" stroke="#8d5d32" stroke-width="7"/>
        <path d="M6-46h56v9H6zM6-37h9v9H6zm47 0h9v9h-9z" fill="#4dc9cd"/>
      </g>
    </g>
    </g>
  </g>

  <g class="chicken" transform="translate(690 191)">
    <animateTransform attributeName="transform" type="translate" dur="15s" repeatCount="indefinite" values="690 191;560 188;825 191;350 188;690 191"/>
    <rect width="38" height="29" fill="#e9e4d7"/><rect x="21" y="-18" width="24" height="25" fill="#f4f0e5"/>
    <rect x="45" y="-9" width="9" height="7" fill="#e5ae28"/><rect x="28" y="-11" width="4" height="4" fill="#1b2025"/>
    <rect x="25" y="7" width="7" height="8" fill="#c84b3f"/><path d="M9 29v13m20-13v13" stroke="#d99c2b" stroke-width="5"/>
  </g>
  <style>@media(prefers-reduced-motion:reduce){{animateTransform{{display:none}}}}</style>
</svg>\n'''
    (output / 'mine-shift.svg').write_text(svg)


def write_reference_mine(root=ROOT):
    """Build the lush side-view pixel cave from the approved visual reference."""
    output = root / 'assets/scenes'
    output.mkdir(parents=True, exist_ok=True)

    def tile(x, y, kind='stone'):
        colors = {
            'stone': ('#4d5054', '#62656a', '#393c40'),
            'moss': ('#52672d', '#718c36', '#34451f'),
            'deep': ('#34363b', '#45484d', '#25272b'),
        }
        base, light, dark = colors[kind]
        return (f'<g><rect x="{x}" y="{y}" width="31" height="31" fill="{base}"/>'
                f'<path d="M{x+3} {y+4}h11v4H{x+7}v5H{x+3}zm{x+17} {y+19}h10v5H{x+22}v4H{x+17}z" fill="{light}" opacity=".62"/>'
                f'<path d="M{x+1} {y+27}h18v3H{x+1}zm{x+25} {y+8}h5v14h-5z" fill="{dark}"/></g>')

    ceiling = []
    for row in range(3):
        for col in range(7, 30):
            kind = 'moss' if (col + row) % 6 in (0, 1) else ('deep' if col > 15 else 'stone')
            ceiling.append(tile(col * 32, row * 32, kind))
    ground_heights = [8,8,8,7,7,8,7,6,7,7,8,8,7,7,7,7,7,7,6,6,7,7]
    ground = []
    for col, top in enumerate(ground_heights):
        for row in range(top, 11):
            kind = 'moss' if row == top and col < 12 else ('deep' if col > 13 else 'stone')
            ground.append(tile(col * 32, row * 32, kind))

    def vine(x, y, blocks, berries=False):
        parts = [f'<path d="M{x} {y}v{blocks*25}" stroke="#37551f" stroke-width="6"/>']
        for index in range(blocks):
            yy = y + index * 25
            side = -1 if index % 2 else 1
            parts.append(f'<path d="M{x} {yy+5}l{side*13} 9-9 8-8-7 11-12z" fill="#6e9734"/>')
            if berries and index % 2:
                parts.append(f'<rect x="{x+side*12-3}" y="{yy+12}" width="7" height="7" fill="#f2a735"/><rect x="{x+side*10-1}" y="{yy+13}" width="3" height="3" fill="#ffd75e"/>')
        return ''.join(parts)

    vines = ''.join([
        vine(275, 52, 5, True), vine(355, 73, 4), vine(505, 82, 5, True),
        vine(647, 64, 5), vine(758, 76, 4, True), vine(865, 50, 6, True),
    ])
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="352" viewBox="0 0 960 352" role="img" aria-labelledby="title desc" shape-rendering="crispEdges">
  <title id="title">초록 동굴 채굴 교대</title><desc id="desc">측면 모습의 작은 스티브가 이끼 낀 동굴의 작업 지점을 오가며 곡괭이질하고 닭은 물가를 돌아다닙니다.</desc>
  <defs><pattern id="dither" width="8" height="8" patternUnits="userSpaceOnUse"><rect width="2" height="2" fill="#d9edc7" opacity=".55"/></pattern></defs>
  <rect width="960" height="352" fill="#19221c"/>
  <path d="M0 0h230v48h46v68h-42v42H118v40H0z" fill="#8fc5e8"/>
  <path d="M0 35h92v18h55v22h82v39h-65v29H80v38H0z" fill="#dce9ca"/>
  <path d="M0 88h255v135H0z" fill="url(#dither)"/>
  <path d="M198 0h34l230 248H342z" fill="#d9e7b0" opacity=".18"/>
  <path d="M255 38h32l240 268h-72z" fill="#c9db8a" opacity=".16"/>
  <g>{''.join(ceiling)}</g>
  <path d="M242 0v40h-34v28h50v36h33V72h38V42h34V0z" fill="#52672d"/>
  {vines}

  <g>{''.join(ground)}</g>
  <g><rect x="176" y="194" width="31" height="31" fill="#52672d"/><path d="M182 214h20v6h-20z" fill="#718c36"/></g>
  <g><rect x="239" y="161" width="31" height="63" fill="#4d5054"/><path d="M245 168h17v6h-8v9h-9z" fill="#62656a"/></g>
  <path d="M126 222v-35h7v35m-17-24h27" stroke="#638e31" stroke-width="6"/>
  <path d="M226 161v-34h7v34m-17-23h27" stroke="#6e9734" stroke-width="6"/>
  <path d="M620 225v-38h7v38m-18-25h29" stroke="#6e9734" stroke-width="6"/>
  <g fill="#e06a9e"><rect x="266" y="226" width="19" height="19"/><rect x="254" y="214" width="19" height="19"/><rect x="278" y="214" width="19" height="19"/><rect x="266" y="202" width="19" height="19"/><rect x="271" y="219" width="9" height="9" fill="#ffd36a"/></g>

  <path d="M704 244h256v108H704z" fill="#455f72"/>
  <path d="M704 244h256v7H704z" fill="#87b7c6"/>
  <path d="M704 267h256v7H704zM704 301h256v6H704z" fill="#5b7888" opacity=".55"/>
  <g fill="#b07783"><rect x="777" y="287" width="28" height="12"/><rect x="769" y="280" width="12" height="10"/><rect x="804" y="284" width="8" height="7"/><rect x="785" y="281" width="4" height="4" fill="#20272d"/></g>
  <g fill="#c58c52"><rect x="862" y="318" width="30" height="10"/><path d="M852 323l11-8v16zM891 318l10-7v20l-10-6z"/><rect x="870" y="315" width="4" height="4" fill="#20272d"/></g>

  <g fill="#555a5d" stroke="#777c80" stroke-width="3"><rect x="337" y="231" width="42" height="42"/><rect x="505" y="231" width="42" height="42"/><rect x="650" y="209" width="42" height="42"/></g>
  <g fill="#d9aa32"><rect x="344" y="238" width="9" height="9"/><rect x="363" y="256" width="8" height="8"/></g>
  <g fill="#4dc8c4"><rect x="512" y="252" width="10" height="10"/><rect x="530" y="236" width="8" height="8"/></g>
  <g fill="#57bd68"><rect x="657" y="216" width="9" height="9"/><rect x="676" y="234" width="8" height="8"/></g>

  <g class="steve" transform="translate(278 188)">
    <animateTransform attributeName="transform" type="translate" dur="13s" repeatCount="indefinite" calcMode="linear" keyTimes="0;.22;.25;.48;.51;.74;.78;1" values="278 188;278 188;446 188;446 188;591 166;591 166;278 188;278 188"/>
    <g class="right-profile">
      <animate attributeName="opacity" dur="13s" repeatCount="indefinite" calcMode="discrete" keyTimes="0;.74;.78;1" values="1;0;1;1"/>
      <rect x="4" width="44" height="39" fill="#8b5a36"/><rect x="42" y="9" width="9" height="25" fill="#a96f45"/>
      <rect x="12" y="13" width="31" height="26" fill="#d69a70"/><rect x="43" y="22" width="8" height="8" fill="#d69a70"/>
      <rect x="35" y="18" width="7" height="6" fill="#eef2df"/><rect x="39" y="20" width="3" height="3" fill="#26312e"/>
      <path d="M32 15h13v12H32" fill="none" stroke="#cdd5d1" stroke-width="2"/>
      <rect x="8" y="39" width="40" height="27" fill="#35aeb0"/><rect x="12" y="66" width="32" height="22" fill="#4e419f"/><rect x="26" y="76" width="5" height="12" fill="#18211d"/>
      <g transform="translate(44 53)"><g class="pickaxe" transform="rotate(-38)">
        <animateTransform attributeName="transform" type="rotate" dur=".92s" repeatCount="indefinite" values="-38;20;-38"/>
        <path d="M1 4L31-31" stroke="#8d5d32" stroke-width="6"/>
        <path d="M5-43h52v8H5zM5-35h8v8H5zm44 0h8v8h-8z" fill="#52ced0"/>
      </g></g>
    </g>
    <g class="left-profile" transform="translate(51 0) scale(-1 1)" opacity="0">
      <animate attributeName="opacity" dur="13s" repeatCount="indefinite" calcMode="discrete" keyTimes="0;.74;.78;1" values="0;1;0;0"/>
      <rect x="4" width="44" height="39" fill="#8b5a36"/><rect x="42" y="9" width="9" height="25" fill="#a96f45"/>
      <rect x="12" y="13" width="31" height="26" fill="#d69a70"/><rect x="43" y="22" width="8" height="8" fill="#d69a70"/>
      <rect x="35" y="18" width="7" height="6" fill="#eef2df"/><rect x="39" y="20" width="3" height="3" fill="#26312e"/>
      <path d="M32 15h13v12H32" fill="none" stroke="#cdd5d1" stroke-width="2"/>
      <rect x="8" y="39" width="40" height="27" fill="#35aeb0"/><rect x="12" y="66" width="32" height="22" fill="#4e419f"/><rect x="26" y="76" width="5" height="12" fill="#18211d"/>
      <g transform="translate(44 53)"><g class="pickaxe" transform="rotate(-38)">
        <animateTransform attributeName="transform" type="rotate" dur=".92s" repeatCount="indefinite" values="-38;20;-38"/>
        <path d="M1 4L31-31" stroke="#8d5d32" stroke-width="6"/>
        <path d="M5-43h52v8H5zM5-35h8v8H5zm44 0h8v8h-8z" fill="#52ced0"/>
      </g></g>
    </g>
  </g>

  <g class="chicken" transform="translate(570 229)">
    <animateTransform attributeName="transform" type="translate" dur="16s" repeatCount="indefinite" values="570 229;665 207;530 229;690 207;570 229"/>
    <rect width="34" height="25" fill="#eee9dc"/><rect x="19" y="-15" width="22" height="22" fill="#f7f2e7"/><rect x="41" y="-7" width="8" height="6" fill="#e8b334"/>
    <rect x="25" y="-9" width="4" height="4" fill="#232a28"/><rect x="23" y="7" width="7" height="8" fill="#c94b43"/><path d="M8 25v11m18-11v11" stroke="#d9a02f" stroke-width="4"/>
  </g>
  <style>@media(prefers-reduced-motion:reduce){{animateTransform{{display:none}}}}</style>
</svg>\n'''
    (output / 'mine-shift.svg').write_text(svg)


def build():
    repos = json.loads((ROOT / 'data/recent-repos.json').read_text())
    write_quest_board(repos)
    write_reference_mine()


if __name__ == '__main__':
    build()
