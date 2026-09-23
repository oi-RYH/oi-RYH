"""Generated enchanting artwork with real-font, data-driven inventory slots."""
from base64 import b64encode
from html import escape
from io import BytesIO
from pathlib import Path
from urllib.parse import quote
import json
import xml.etree.ElementTree as ET

from PIL import Image
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

from pixel_readme import ROOT
from typeset_enchanting_hangul import RUNS

REL = 'assets/featured-inventory'


class Type:
    def __init__(self, root):
        self.font = TTFont(root / 'assets/fonts/neodgm.ttf')
        self.cmap = self.font.getBestCmap()
        self.glyphs = self.font.getGlyphSet()

    def width(self, value, size):
        return sum(self.glyphs[self.cmap.get(ord(c), self.cmap[ord('?')])].width
                   for c in value) * size / self.font['head'].unitsPerEm

    def text(self, value, x, y, size, color='#252525', tracking=0):
        scale = size / self.font['head'].unitsPerEm
        parts, advance = [], 0
        for c in value:
            glyph = self.glyphs[self.cmap.get(ord(c), self.cmap[ord('?')])]
            pen = SVGPathPen(self.glyphs)
            glyph.draw(pen)
            parts.append(f'<path transform="translate({advance} 0)" d="{pen.getCommands()}"/>')
            advance += glyph.width + tracking/scale
        return (f'<g aria-label="{escape(value, quote=True)}" fill="{color}" '
                f'transform="translate({x} {y}) scale({scale} {-scale})">'
                + ''.join(parts) + '</g>')

    def fit(self, value, size, width):
        if self.width(value, size) <= width:
            return value
        while value and self.width(value + '…', size) > width:
            value = value[:-1]
        return value + '…'

    def wrap(self, value, size, width, limit=2):
        lines, line = [], ''
        for word in value.split():
            candidate = (line+' '+word).strip()
            if line and self.width(candidate, size) > width:
                lines.append(line); line = ''
            # Split unusually long tokens only when a whole word cannot fit.
            for c in ((' ' if line else '')+word):
                if self.width(line+c, size) > width:
                    lines.append(line.rstrip()); line = ''
                line += c
        if line.strip(): lines.append(line.strip())
        if len(lines) > limit:
            lines = lines[:limit]
            lines[-1] = self.fit(lines[-1]+'…', size, width)
        return lines


def write_inventory(repos, root=ROOT):
    out = root / REL
    out.mkdir(parents=True, exist_ok=True)
    # Copying the source into temporary test roots is unnecessary: it is static
    # artwork, whereas all generated outputs and font inputs use the given root.
    source = out / 'generated-background.png'
    if not source.exists(): source = ROOT / REL / 'generated-background.png'
    background = Image.open(source).convert('RGB')
    assert background.size == (1536, 1408)
    typ = Type(root)
    featured = ''.join(typ.text(value, x, y, size, '#151510', -2 if size == 32 else 0)
                       for x, y, size, value in RUNS)
    inventory = []
    for i in range(3):
        x, y = 148 + 420*i, 978
        if i >= len(repos):
            inventory.append(typ.text('Empty slot', x+24, y+62, 28, '#505050'))
            continue
        repo = repos[i]
        icon = ET.fromstring((ROOT/'assets/blocks/chest.svg').read_text())
        icon.set('x', str(x+20)); icon.set('y', str(y+18))
        icon.set('width','56'); icon.set('height','56')
        inventory.append(ET.tostring(icon, encoding='unicode'))
        inventory.append(typ.text(typ.fit(repo['name'],32,296),x+88,y+56,32,'#171717'))
        desc = repo.get('description') or '저장소에서 자세히 보기'
        for row, line in enumerate(typ.wrap(desc,24,352)):
            inventory.append(typ.text(line,x+24,y+116+32*row,24,'#242424'))
        inventory.append(typ.text(typ.fit(repo.get('language') or '언어 정보 없음',24,352),x+24,y+206,24,'#174523'))
        inventory.append(typ.text('PUSH '+repo.get('pushed_at','')[:10]+' UTC',x+24,y+246,20,'#383838'))

    def save(name, box, paths):
        left, top, right, bottom = box
        buf = BytesIO()
        background.crop(box).save(buf, format='PNG')
        data = b64encode(buf.getvalue()).decode()
        w, h = right-left, bottom-top
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
               f'width="{w}" height="{h}" viewBox="{left} {top} {w} {h}" role="img">'
               '<title>Featured Projects and Recent Work inventory</title>'
               f'<image x="{left}" y="{top}" width="{w}" height="{h}" '
               f'xlink:href="data:image/png;base64,{data}"/>'+paths+'</svg>\n')
        (out/f'{name}.svg').write_text(svg)

    for name, top, bottom in [('header',0,180),('featured-1',180,414),
                              ('featured-2',414,653),('featured-3',653,950)]:
        save(name,(0,top,1536,bottom),featured)
    for i,(left,right) in enumerate(((0,558),(558,978),(978,1536)),1):
        save(f'recent-{i}',(left,950,right,1408),''.join(inventory))
    save('preview',(0,0,1536,1408),featured+''.join(inventory))


def cards(repos, owner):
    widths = (36.328125, 27.34375, 36.328125)
    panels = []
    for i in range(3):
        name = repos[i]['name'] if i < len(repos) else 'Empty slot'
        img = (f'<img src="{REL}/recent-{i+1}.svg" width="{widths[i]}%" align="top" '
               f'alt="{escape(name, quote=True)} 최근 저장소 인벤토리 슬롯">')
        if i < len(repos):
            url = f'https://github.com/{quote(owner,safe="")}/{quote(name,safe="")}'
            img = f'<a href="{url}">{img}</a>'
        else:
            img = '<picture>'+img+'</picture>'
        panels.append(img)
    return '<div align="center">'+''.join(panels)+'</div>'


if __name__ == '__main__':
    write_inventory(json.loads((ROOT/'data/recent-repos.json').read_text()))
