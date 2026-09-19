"""Build the centered animated workbench intro and clickable hotbar cards."""
from pathlib import Path
import re

from pixel_readme import PixelText, ROOT


def text_group(renderer, text, size, y, color, *, center=None, x=None, cls=''):
    width, paths, scale = renderer.paths(text, size)
    if x is None:
        x = round(center - width / 2)
    class_attr = f' class="{cls}"' if cls else ''
    return f'<g{class_attr} fill="{color}" transform="translate({x} {y}) scale({scale} {-scale})">{paths}</g>'


def icon(name, x, y, size, root=ROOT):
    raw = (root / f'assets/blocks/{name}.svg').read_text()
    inner = re.sub(r'^.*?<svg[^>]*>', '', raw, count=1, flags=re.S)
    inner = re.sub(r'</svg>\s*$', '', inner, flags=re.S)
    return f'<g transform="translate({x} {y}) scale({size / 32})">{inner}</g>'


def build(root=ROOT):
    renderer = PixelText(root)
    intro = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="280" viewBox="0 0 960 280" role="img" aria-labelledby="title desc" shape-rendering="crispEdges">',
        '<title id="title">RYH’s Workbench</title>',
        '<desc id="desc">마인크래프트 서버 화면처럼 접속 상태가 움직이는 작업대 소개</desc>',
        '''<style>
.cursor{animation:blink 1s steps(2,end) infinite}.splash{animation:pulse 1.8s steps(2,end) infinite}
.line{opacity:0;animation:chat 12s steps(1,end) infinite}.b{animation-delay:3s}.c{animation-delay:6s}.d{animation-delay:9s}
@keyframes chat{0%,24%{opacity:1}25%,100%{opacity:0}}@keyframes blink{50%{opacity:0}}@keyframes pulse{50%{opacity:.68}}
@media(prefers-reduced-motion:reduce){.line,.cursor,.splash{animation:none}.line{opacity:0}.a{opacity:1}}
</style>''',
        '<rect width="960" height="280" fill="#0d1117"/>',
        '<path fill="#26362b" d="M74 91h812v3H74z"/><path fill="#6f4a2b" d="M74 91h112v3H74zm700 0h112v3H774z"/>',
        text_group(renderer, "RYH's WORKBENCH", 32, 48, '#b6e89b', center=480),
        text_group(renderer, '곡괭이로는 디버깅이 안 돼서 맥북을 샀습니다.', 15, 78, '#c9d1d9', center=480),
        '<rect x="74" y="110" width="812" height="146" fill="#10161c" stroke="#435746" stroke-width="4"/>',
        '<path fill="#6d4a2a" d="M74 110h18v5H79v13h-5zm812 0v18h-5v-13h-13v-5zM74 256v-18h5v13h13v5zm812 0h-18v-5h13v-13h5z"/>',
        '<rect x="96" y="134" width="768" height="2" fill="#2f4135"/><circle cx="108" cy="123" r="4" fill="#72d687"/><circle cx="122" cy="123" r="4" fill="#ffd75e"/><circle cx="136" cy="123" r="4" fill="#d55c52"/>',
        text_group(renderer, 'RYH / WORKBENCH', 17, 164, '#85d391', x=106),
        text_group(renderer, 'ALSO TRY DEBUGGING!', 15, 164, '#ffe16b', x=650, cls='splash'),
    ]
    messages = [
        ('a', '> RYH joined the server.'),
        ('b', '> Pickaxe equipped.'),
        ('c', '> Error: debugger failed.'),
        ('d', '> MacBook equipped.'),
    ]
    for cls, message in messages:
        intro.append(text_group(renderer, message, 21, 216, '#e6edf3', x=106, cls=f'line {cls}'))
    intro.extend([
        '<rect class="cursor" x="838" y="197" width="10" height="20" fill="#85d391"/>',
        '</svg>\n',
    ])
    (root / 'assets/workbench-intro.svg').write_text(''.join(intro))

    nav_dir = root / 'assets/workbench-nav'
    nav_dir.mkdir(parents=True, exist_ok=True)
    cards = [
        ('crafting', 'crafting_table', '제작 중'),
        ('inventory', 'chest', '상자 열기'),
        ('mine', 'pickaxe', '돌 캐기'),
        ('notes', 'book_and_quill', '작업 일지'),
    ]
    for index, (filename, icon_name, label) in enumerate(cards, 1):
        svg = [
            '<svg xmlns="http://www.w3.org/2000/svg" width="224" height="118" viewBox="0 0 224 118" role="img" aria-labelledby="title" shape-rendering="crispEdges">',
            f'<title id="title">{label}</title>',
            '<rect width="224" height="118" fill="#0d1117"/>',
            '<rect x="4" y="4" width="216" height="110" fill="#11171d" stroke="#3b4650" stroke-width="2"/>',
            '<path fill="#263038" d="M14 14h196v4H14zM14 100h196v4H14z"/>',
            text_group(renderer, str(index), 10, 30, '#74808b', x=18),
            icon(icon_name, 90, 20, 44, root),
            text_group(renderer, label, 16, 88, '#c9d1d9', center=112),
            '<path fill="#405344" d="M4 4h16v3H7v13H4zm216 0v16h-3V7h-13V4z"/>',
            '</svg>\n',
        ]
        (nav_dir / f'{filename}.svg').write_text(''.join(svg))


if __name__ == '__main__':
    build()
