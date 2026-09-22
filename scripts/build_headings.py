"""Build outlined pixel headings; requires fonttools (pip install fonttools)."""
from pathlib import Path
from html import escape
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

ROOT = Path(__file__).resolve().parents[1]
HEADINGS = {
    'workbench': ('RYH’s Workbench', 32),
    'crafting': ('Currently crafting', 24),
    'selected-builds': ('Selected builds', 24),
    'technical-loadout': ('Technical loadout', 24),
    'inventory': ('Inventory', 24),
    'community-mine': ('공용 광산', 24),
    'field-notes': ('작업 일지', 24),
    'say-days': ('Say Days', 20),
    'bonsai': ('bonsai', 20),
    'stereo-camera': ('Stereo camera', 20),
}

def build():
    font = TTFont(ROOT / 'assets/fonts/neodgm.ttf')
    glyphs, cmap = font.getGlyphSet(), font.getBestCmap()
    target = ROOT / 'assets/headings'
    target.mkdir(exist_ok=True)
    sizes = {}
    for name, (text, size) in HEADINGS.items():
        scale = size / font['head'].unitsPerEm
        x, paths = 0, []
        for char in text:
            glyph = glyphs[cmap[ord(char)]]
            pen = SVGPathPen(glyphs)
            glyph.draw(pen)
            paths.append(f'<path transform="translate({x} 0)" d="{pen.getCommands()}"/>')
            x += glyph.width
        width, height = round(x * scale) + 4, size + 8
        # Outline paths avoid external font loading in GitHub image rendering.
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(text)}">'
               f'<title>{escape(text)}</title><style>g{{fill:#285e28}}@media(prefers-color-scheme:dark){{g{{fill:#b6e89b}}}}</style>'
               f'<g transform="translate(2 {size * 0.75 + 4}) scale({scale} {-scale})">' + ''.join(paths) + '</g></svg>\n')
        (target / f'{name}.svg').write_text(svg)
        sizes[name] = width
    return sizes

if __name__ == '__main__':
    print(build())
