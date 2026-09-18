"""Compose generated raster artwork into self-contained animated README SVGs.

The artwork is generated separately. This script only layers, labels and
animates those assets so GitHub can display each scene as a single image.
"""
from base64 import b64encode
from html import escape
import json
from pathlib import Path

from pixel_readme import PixelText, ROOT


RASTER = ROOT / 'assets/scenes/raster'
SCENES = ROOT / 'assets/scenes'


def data_uri(path):
    mime = 'image/png' if path.suffix == '.png' else 'image/jpeg'
    return f'data:{mime};base64,' + b64encode(path.read_bytes()).decode()


def write_story_scene(name, background, steve, chicken, title):
    bg = data_uri(RASTER / background)
    hero = data_uri(RASTER / 'steve.png')
    bird = data_uri(RASTER / 'chicken.png')
    sx, sy, sw = steve
    cx, cy, cw = chicken
    sh = round(sw * 440 / 293)
    ch = round(cw * 278 / 240)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="512" viewBox="0 0 1280 512" role="img">
  <title>{escape(title)}</title>
  <defs>
    <linearGradient id="shade" x1="0" y1="0" x2="0" y2="1"><stop offset="58%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#000" stop-opacity=".30"/></linearGradient>
  </defs>
  <image href="{bg}" width="1280" height="512" preserveAspectRatio="xMidYMid slice"/>
  <g class="steve">
    <animateTransform attributeName="transform" type="translate" values="0 0;12 -3;25 0;12 -2;0 0" dur="7.2s" repeatCount="indefinite"/>
    <image href="{hero}" x="{sx}" y="{sy}" width="{sw}" height="{sh}"/>
  </g>
  <g class="chicken">
    <animateTransform attributeName="transform" type="translate" values="0 0;8 -10;16 0;8 -4;0 0" dur="2.8s" repeatCount="indefinite"/>
    <image href="{bird}" x="{cx}" y="{cy}" width="{cw}" height="{ch}"/>
  </g>
  <rect width="1280" height="512" fill="url(#shade)" pointer-events="none"/>
  <style>@media(prefers-reduced-motion:reduce){{animateTransform{{display:none}}}}</style>
</svg>\n'''
    (SCENES / f'{name}.svg').write_text(svg)


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
    raster = root / 'assets/scenes/raster'
    if not raster.exists():
        raster = RASTER
    output = root / 'assets/scenes'
    output.mkdir(parents=True, exist_ok=True)
    bg = data_uri(raster / 'quest-board-bg.jpg')
    font = PixelText(root)
    columns = [280, 535, 790]
    layers = []
    for index, repo in enumerate(repos[:3]):
        x = columns[index]
        name = repo['name']
        if font.paths(name, 18)[0] > 205:
            while name and font.paths(name + '…', 18)[0] > 205:
                name = name[:-1]
            name += '…'
        layers.append(paths(font, name, x, 162, 18, '#352011'))
        description = repo.get('description') or '저장소에서 자세한 내용을 확인하세요.'
        for row, line in enumerate(wrap(description, font, 205, 13)):
            layers.append(paths(font, line, x, 226 + row * 24, 13, '#50331d'))
        language = repo.get('language') or '언어 정보 없음'
        layers.append(paths(font, f'◆ {language}', x, 321, 13, '#285e28'))
        layers.append(paths(font, f'업데이트 · {repo["pushed_at"][:10]}', x, 359, 11, '#765331'))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="532" viewBox="0 0 1280 532" role="img">
  <title>최근 푸시한 공개 저장소 3개가 붙은 퀘스트 게시판</title>
  <image href="{bg}" width="1280" height="532"/>
  {''.join(layers)}
</svg>\n'''
    (output / 'quest-board.svg').write_text(svg)


def build():
    write_story_scene('storage-room', 'storage-room-bg.jpg', (155, 158, 170), (410, 315, 78), '스티브와 닭이 보관실을 지나가는 장면')
    write_story_scene('mine-descent', 'mine-descent-bg.jpg', (855, 180, 150), (1060, 325, 72), '스티브와 닭이 깊은 광산으로 내려가는 장면')
    write_story_scene('records-room', 'records-room-bg.jpg', (885, 170, 150), (1090, 330, 72), '스티브와 닭이 지하 기록실을 지나가는 장면')
    repos = json.loads((ROOT / 'data/recent-repos.json').read_text())
    write_quest_board(repos)


if __name__ == '__main__':
    build()
