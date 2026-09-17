"""Render editable README.source.md text as self-contained pixel SVGs.

Links, tables, details and image alt text stay in HTML/Markdown. Only visible
text runs become images. Never interpret user input as SVG or shell code.
"""
from functools import lru_cache
from hashlib import sha256
from html import escape, unescape
from pathlib import Path
import re
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen

ROOT = Path(__file__).resolve().parents[1]

class PixelText:
    def __init__(self, root=ROOT):
        self.root = root
        self.font = TTFont(root / 'assets/fonts/neodgm.ttf')
        self.glyphs = self.font.getGlyphSet()
        self.cmap = self.font.getBestCmap()
        self.used = set()
        self.max_width = 480

    @lru_cache(maxsize=2048)
    def glyph(self, char):
        # Unknown characters in public usernames/logs get a visible fallback.
        glyph = self.glyphs[self.cmap.get(ord(char), self.cmap[ord('?')])]
        pen = SVGPathPen(self.glyphs)
        glyph.draw(pen)
        return glyph.width, pen.getCommands()

    def paths(self, text, size=16):
        scale = size / self.font['head'].unitsPerEm
        x, paths = 0, []
        for char in text:
            advance, path = self.glyph(char)
            paths.append(f'<path transform="translate({x} 0)" d="{path}"/>')
            x += advance
        return x * scale, ''.join(paths), scale

    def image(self, text):
        text = unescape(text).replace('**', '').strip()
        if not text:
            return ''
        # Limit line length without splitting glyph outlines or shrinking text.
        lines, line = [], ''
        for word in re.findall(r'\S+\s*', text):
            for char in word:
                if self.paths(line + char)[0] > self.max_width:
                    split = line.rfind(' ')
                    if split > 0:
                        lines.append(line[:split])
                        line = line[split+1:]
                    else:
                        lines.append(line)
                        line = ''
                line += char
        if line.strip(): lines.append(line.rstrip())
        rendered = [self.paths(line) for line in lines]
        width = round(max(item[0] for item in rendered)) + 4
        height = 24 * len(lines)
        key = sha256(f"{self.max_width}:{text}".encode()).hexdigest()[:20]
        rel = f'assets/text/{key}.svg'
        self.used.add(rel)
        groups = ''.join(f'<g transform="translate(2 {16+24*i}) scale({scale} {-scale})">{paths}</g>'
                         for i, (_, paths, scale) in enumerate(rendered))
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">'
               f'<title>{escape(text)}</title>'
               '<style>g{fill:#24292f}@media(prefers-color-scheme:dark){g{fill:#c9d1d9}}</style>'
               + groups + '</svg>\n')
        path = self.root / rel
        path.parent.mkdir(exist_ok=True)
        path.write_text(svg)
        return f'<img src="{rel}" width="{width}" alt="{escape(text, quote=True)}">'

    def inline(self, text):
        # HTML attributes (including alt text and URLs) are kept verbatim.
        tokens = re.split(r'(<[^>]+>|\[[^\]]*\]\([^)]*\))', text)
        out = []
        for token in tokens:
            if token.startswith('<'):
                if 'https://img.shields.io/' in token:
                    label = re.search(r'alt="([^"]+)"', token)
                    out.append(self.image(label.group(1)) if label else token)
                else:
                    out.append(token)
            elif token.startswith('[') and re.fullmatch(r'\[[^\]]*\]\([^)]*\)', token):
                match = re.fullmatch(r'\[([^\]]*)\]\(([^)]*)\)', token)
                out.append(f'[{self.inline(match[1])}]({match[2]})')
            elif token.strip():
                out.append((' ' if token.startswith(' ') else '') + self.image(token) + (' ' if token.endswith(' ') else ''))
            else:
                out.append(token)
        return ''.join(out)

    def render(self, source):
        lines = []
        native = False
        for line in source.splitlines():
            if line == '<!-- RECENT_REPOS:START -->': native = True
            if native:
                lines.append(line)
                if line == '<!-- RECENT_REPOS:END -->': native = False
                continue
            if '<td ' in line: self.max_width = 200
            if '</td>' in line: self.max_width = 480
            if not line.strip() or line.lstrip().startswith('<!--'):
                lines.append(line)
            elif re.fullmatch(r'[|:\-\s]+', line):
                lines.append(line)
            elif line.startswith('|'):
                lines.append('|'.join(self.inline(cell) for cell in line.split('|')))
            else:
                prefix = re.match(r'^(#{1,6} |[-*] )', line)
                n = prefix.end() if prefix else 0
                lines.append(line[:n] + self.inline(line[n:]))
        return '\n'.join(lines) + '\n'

    def clean(self):
        # Delete only obsolete generated text, after the new README is written.
        for path in (self.root / 'assets/text').glob('*.svg'):
            if str(path.relative_to(self.root)) not in self.used:
                path.unlink()


def build(source, root=ROOT):
    from recent_repos import populate
    if '<!-- RECENT_REPOS:START -->' in source:
        source = populate(source, root)
    renderer = PixelText(root)
    result = renderer.render(source)
    (root / 'README.md').write_text(result)
    renderer.clean()
    return result

if __name__ == '__main__':
    import json
    from mine import render
    state = json.loads((ROOT / 'data/mine.json').read_text())
    build(render((ROOT / 'README.source.md').read_text(), state, live=True))
