"""Build the deliberately low-fi interactive scenes used by the README."""
import json
import math

from PIL import Image, ImageDraw

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
    """Composite generated artwork into a GitHub-safe animated GIF."""
    output = root / 'assets/scenes'
    output.mkdir(parents=True, exist_ok=True)
    size = (960, 349)
    background = Image.open(output / 'concepts/cave-background.png').convert('RGB').resize(
        size, Image.Resampling.NEAREST
    )
    sprite = Image.open(output / 'characters/steve-three-quarter.png').convert('RGBA')
    sprite = sprite.crop(sprite.getbbox()).resize((84, 88), Image.Resampling.NEAREST)
    sprite_left = sprite.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    stops = ((132, 180), (360, 180), (556, 166))

    def lerp(start, end, amount):
        return tuple(round(a + (b - a) * amount) for a, b in zip(start, end))

    def pose(frame):
        if frame < 18:
            return stops[0], True, True
        if frame < 22:
            return lerp(stops[0], stops[1], (frame - 18) / 3), True, False
        if frame < 40:
            return stops[1], True, True
        if frame < 44:
            return lerp(stops[1], stops[2], (frame - 40) / 3), True, False
        if frame < 62:
            return stops[2], True, True
        if frame < 67:
            return lerp(stops[2], stops[0], (frame - 62) / 4), False, False
        return stops[0], True, True

    def draw_pickaxe(draw, x, y, facing_right, frame):
        swing = (math.sin(frame * math.pi / 4) + 1) / 2
        angle = math.radians(-58 + swing * 62)
        if not facing_right:
            angle = math.pi - angle
        pivot = (x + (76 if facing_right else 8), y + 59)
        tip = (pivot[0] + math.cos(angle) * 49, pivot[1] + math.sin(angle) * 49)
        draw.line((pivot, tip), fill='#7d4d29', width=7)
        perpendicular = angle + math.pi / 2
        head_a = (tip[0] + math.cos(perpendicular) * 25, tip[1] + math.sin(perpendicular) * 25)
        head_b = (tip[0] - math.cos(perpendicular) * 25, tip[1] - math.sin(perpendicular) * 25)
        draw.line((head_a, head_b), fill='#4fc8cb', width=9)
        for hx, hy in (head_a, head_b):
            draw.rectangle((hx - 4, hy - 4, hx + 4, hy + 4), fill='#4fc8cb')
        if swing > .82:
            direction = 1 if facing_right else -1
            for dx, dy, side in ((8, 4, 0), (15, 12, 1), (7, 19, 2)):
                cx = pivot[0] + direction * (48 + dx)
                cy = pivot[1] + dy
                draw.rectangle((cx, cy, cx + 4 - side, cy + 4 - side), fill='#a9d957')

    def draw_chicken(draw, frame):
        travel = frame if frame < 40 else 80 - frame
        x = 708 + round(travel * 3.5)
        y = 236 - (3 if frame % 8 in (2, 3) else 0)
        facing_right = frame < 40
        if facing_right:
            draw.rectangle((x, y, x + 25, y + 17), fill='#eee9dc')
            draw.rectangle((x + 15, y - 12, x + 31, y + 4), fill='#f7f2e7')
            draw.rectangle((x + 31, y - 5, x + 37, y), fill='#e8b334')
            draw.rectangle((x + 21, y - 7, x + 24, y - 4), fill='#232a28')
            draw.rectangle((x + 18, y + 4, x + 23, y + 10), fill='#c94b43')
        else:
            draw.rectangle((x, y, x + 25, y + 17), fill='#eee9dc')
            draw.rectangle((x - 6, y - 12, x + 10, y + 4), fill='#f7f2e7')
            draw.rectangle((x - 12, y - 5, x - 6, y), fill='#e8b334')
            draw.rectangle((x + 1, y - 7, x + 4, y - 4), fill='#232a28')
            draw.rectangle((x + 2, y + 4, x + 7, y + 10), fill='#c94b43')
        draw.line((x + 7, y + 17, x + 7, y + 25), fill='#d9a02f', width=3)
        draw.line((x + 19, y + 17, x + 19, y + 25), fill='#d9a02f', width=3)

    frames = []
    for frame_number in range(80):
        frame = background.convert('RGBA')
        draw = ImageDraw.Draw(frame)
        (x, y), facing_right, mining = pose(frame_number)
        if not mining:
            direction = -1 if facing_right else 1
            for offset, alpha in ((18, 100), (31, 70), (44, 40)):
                streak_x = x + direction * offset
                draw.line((streak_x, y + 35, streak_x + direction * 28, y + 35), fill=(130, 209, 194, alpha), width=3)
        draw.ellipse((x + 12, y + 80, x + 77, y + 91), fill=(0, 0, 0, 105))
        frame.alpha_composite(sprite if facing_right else sprite_left, (x, y))
        if mining:
            draw_pickaxe(draw, x, y, facing_right, frame_number)
        draw_chicken(draw, frame_number)
        frames.append(frame.convert('RGB'))

    palette = frames[0].quantize(colors=224, method=Image.Quantize.MEDIANCUT)
    indexed = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
    indexed[0].save(
        output / 'mine-shift.gif',
        save_all=True,
        append_images=indexed[1:],
        duration=110,
        loop=0,
        optimize=True,
        disposal=1,
    )


def build():
    repos = json.loads((ROOT / 'data/recent-repos.json').read_text())
    write_quest_board(repos)
    write_reference_mine()


if __name__ == '__main__':
    build()
