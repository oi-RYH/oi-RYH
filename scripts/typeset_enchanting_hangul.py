"""Compose real NeoDunggeunmo glyph outlines over generated GUI artwork.

The artwork is image-generated; this script typesets the four Korean runs
and adds a shallow oak shelf to meet the recent-project board below it.
Outlines embed the exact font independently of viewer fonts.
"""
from base64 import b64encode
from html import escape
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets/featured-projects'
FONT = ROOT / 'assets/fonts/neodgm.ttf'
# Positions are baselines in the original 1536 x 1024 generated composition.
RUNS = (
    (596, 336, 32, 'MacBook 덮개 움직임을 부드러운 화면 전환으로'),
    (596, 534, 48, '캐리캐리체인지'),
    (596, 574, 32, '캐리어 세척과 외관 손상 검사를 하나의 장치로'),
    (596, 810, 32, '자연어 일정과 Todo를 여러 기기에서 이어서'),
)


def build():
    font = TTFont(FONT)
    cmap, glyphs = font.getBestCmap(), font.getGlyphSet()
    groups = []
    for x, y, size, value in RUNS:
        scale = size / font['head'].unitsPerEm
        # Tighten by one source bitmap pixel; never distort the glyph shapes.
        tracking = -2 / scale if size == 32 else 0
        advance, paths = 0, []
        for char in value:
            assert ord(char) in cmap, f'Missing font glyph: {char}'
            glyph = glyphs[cmap[ord(char)]]
            pen = SVGPathPen(glyphs)
            glyph.draw(pen)
            paths.append(f'<path transform="translate({advance} 0)" d="{pen.getCommands()}"/>')
            advance += glyph.width + tracking
        assert x + advance * scale <= 1275, f'Text overlaps XP: {value}'
        groups.append(f'<g aria-label="{escape(value)}" fill="#151510" '
                      f'transform="translate({x} {y}) scale({scale} {-scale})">'
                      + ''.join(paths) + '</g>')
        print(f'{value}: {advance * scale:g}px, NeoDunggeunmo {size}px')
    # A shallow shelf finishes the existing floor area and meets the quest
    # board's dark oak edge without adding height or covering the GUI.
    shelf = ('<defs><linearGradient id="workshop-fade" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#24190f" stop-opacity="0"/>'
             '<stop offset="1" stop-color="#24190f"/></linearGradient></defs>'
             '<rect x="0" y="922" width="1536" height="78" fill="url(#workshop-fade)"/>'
             '<rect x="0" y="1000" width="1536" height="24" fill="#24190f"/>'
             '<rect x="0" y="1000" width="1536" height="4" fill="#89603a"/>'
             '<rect x="0" y="1004" width="1536" height="5" fill="#533820"/>')
    # Each crop is embedded, so GitHub SVG images have no external dependencies.
    for name, top, height, background in (
        ('enchanting-typeset', 0, 1024, 'enchanting-clean-background.png'),
        ('typeset-option-1', 180, 234, 'typeset-background-1.png'),
        ('typeset-option-2', 414, 239, 'typeset-background-2.png'),
        ('typeset-option-3', 653, 371, 'typeset-background-3.png'),
    ):
        data = b64encode((ASSETS / background).read_bytes()).decode()
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" '
               f'xmlns:xlink="http://www.w3.org/1999/xlink" width="1536" height="{height}" '
               f'viewBox="0 {top} 1536 {height}" role="img">'
               '<title>Featured Projects — NeoDunggeunmo 한글 폰트</title>'
               f'<image x="0" y="{top}" width="1536" height="{height}" '
               f'xlink:href="data:image/png;base64,{data}"/>'
               + ''.join(groups) + shelf + '</svg>\n')
        (ASSETS / f'{name}.svg').write_text(svg)


if __name__ == '__main__':
    build()
