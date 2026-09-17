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
        self.accent = False

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

    def image(self, text, fixed_lines=None):
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
        if fixed_lines and len(lines) > fixed_lines:
            lines = lines[:fixed_lines]
            ellipsis = '…'
            while lines[-1] and self.paths(lines[-1] + ellipsis)[0] > self.max_width:
                lines[-1] = lines[-1][:-1].rstrip()
            lines[-1] += ellipsis
        rendered = [self.paths(line) for line in lines]
        width = self.max_width if fixed_lines else round(max(item[0] for item in rendered)) + 4
        height = 24 * (fixed_lines or len(lines))
        key_source = f"{self.max_width}:{text}" + (":accent" if self.accent else "")
        if fixed_lines:
            key_source += f":lines={fixed_lines}"
        key = sha256(key_source.encode()).hexdigest()[:20]
        rel = f'assets/text/{key}.svg'
        self.used.add(rel)
        groups = ''.join(f'<g transform="translate(2 {16+24*i}) scale({scale} {-scale})">{paths}</g>'
                         for i, (_, paths, scale) in enumerate(rendered))
        light, dark = ('#285e28', '#b6e89b') if self.accent else ('#24292f', '#c9d1d9')
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">'
               f'<title>{escape(text)}</title>'
               f'<style>g{{fill:{light}}}@media(prefers-color-scheme:dark){{g{{fill:{dark}}}}}</style>'
               + groups + '</svg>\n')
        path = self.root / rel
        path.parent.mkdir(exist_ok=True)
        path.write_text(svg)
        return f'<img src="{rel}" width="{width}" alt="{escape(text, quote=True)}">'

    def inline(self, text, fixed_lines=None):
        # HTML attributes (including alt text and URLs) are kept verbatim.
        tokens = re.split(r'(<[^>]+>|\[[^\]]*\]\([^)]*\))', text)
        out = []
        for token in tokens:
            if token.startswith('<'):
                out.append(token)
            elif token.startswith('[') and re.fullmatch(r'\[[^\]]*\]\([^)]*\)', token):
                match = re.fullmatch(r'\[([^\]]*)\]\(([^)]*)\)', token)
                out.append(f'[{self.inline(match[1], fixed_lines=fixed_lines)}]({match[2]})')
            elif token.strip():
                out.append((' ' if token.startswith(' ') else '') + self.image(token, fixed_lines=fixed_lines) + (' ' if token.endswith(' ') else ''))
            else:
                out.append(token)
        return ''.join(out)

    def render(self, source):
        lines = []
        for line in source.splitlines():
            self.accent = '<h3>' in line
            if '<td ' in line: self.max_width = 200
            if '</td>' in line: self.max_width = 480
            description = re.fullmatch(r'(\s*)<p data-repo-description>(.*)</p>', line)
            if description:
                lines.append(f'{description.group(1)}<p>{self.inline(description.group(2), fixed_lines=2)}</p>')
                continue
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
