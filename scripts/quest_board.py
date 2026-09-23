"""Render the dynamic Minecraft quest board as a Pillow pixel scene."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import json
import random

from pixel_readme import ROOT


def write_quest_board(repos, root=ROOT):
    random.seed(27)
    W, H = 960, 400
    img = Image.new('RGB', (W, H), '#171923')
    d = ImageDraw.Draw(img)

    # Continue the dark oak workshop below the enchanting GUI.
    for y in range(0, H, 34):
        offset = -32 if (y // 34) % 2 else 0
        for x in range(offset, W, 64):
            base = random.choice(['#312216', '#38271a', '#402b1a', '#2e2016'])
            d.rectangle((x+1, y+1, x+62, y+32), fill=base, outline='#20170f', width=2)
            d.line((x+5, y+5, x+54, y+5), fill='#503721', width=2)
            for _ in range(4):
                px, py = x+random.randint(7,56), y+random.randint(9,28)
                d.rectangle((px, py, px+random.randint(8,18), py+1), fill='#261a10')
    for x, y in [(128,150),(110,184),(842,167),(864,206),(88,220),(884,236)]:
        d.rectangle((x,y,x+5,y+12), fill='#50613a'); d.rectangle((x+5,y+7,x+11,y+12), fill='#687944')

    # Side banners.
    def banner(x):
        d.polygon([(x,0),(x+56,0),(x+56,126),(x+28,154),(x,126)], fill='#142a50')
        d.line((x+5,0,x+5,122,x+28,144,x+51,122,x+51,0), fill='#b27b31', width=4)
    # Small muted banners retain the familiar quest board silhouette.
    banner(52); banner(852)

    # Shelving, crates and plants.
    d.rectangle((0,42,48,306), fill='#3a2115', outline='#1b120d', width=5)
    for yy in range(60,286,50):
        d.rectangle((4,yy,44,yy+42), fill='#241713'); d.rectangle((0,yy+40,48,yy+47), fill='#69401f')
        for xx in range(8,42,8): d.rectangle((xx,yy+8,xx+5,yy+36), fill=random.choice(['#4a5640','#76472b','#394b61','#67502b']))
    d.rectangle((12,322,103,397), fill='#5b331b', outline='#2b1a11', width=5)
    d.line((16,327,98,392), fill='#84502a', width=6); d.line((98,327,16,392), fill='#84502a', width=6)
    d.rectangle((852,319,950,398), fill='#5b331b', outline='#2b1a11', width=5)
    for xx in [862,902,940]: d.rectangle((xx,322,xx+7,394), fill='#7e4a25')
    # pots and leaves
    for bx in [70,878]:
        d.rectangle((bx-14,293,bx+14,325), fill='#743a1f', outline='#351b11', width=3)
        for _ in range(16):
            lx, ly = bx+random.randint(-22,22), 285-random.randint(0,35)
            d.rectangle((lx-5,ly-4,lx+5,ly+4), fill=random.choice(['#637329','#7e8b32','#455f2b','#a2a943']))

    # Board shadow and posts.
    d.rectangle((126,50,834,362), fill='#120b08')
    for x in (140, 786):
        d.rectangle((x,48,x+38,376), fill='#4b2917', outline='#24150e', width=5)
        d.rectangle((x+7,54,x+15,369), fill='#72401f')
    # Main wood field and beams.
    d.rectangle((164,63,810,348), fill='#3b2014', outline='#1b100b', width=6)
    for y in (62, 334):
        d.rectangle((122,y,840,y+30), fill='#542c18', outline='#25140d', width=5)
        d.line((132,y+8,830,y+8), fill='#75401f', width=3)
    for _ in range(45):
        x=random.randint(170,802); y=random.randint(98,330); ln=random.randint(8,40)
        d.line((x,y,min(x+ln,806),y), fill=random.choice(['#4c2818','#6a371d','#2d1a12']), width=random.choice([1,2]))

    # The section heading is a nameplate inside the board, not a separate gap.
    for box in [(310,34,650,64),(350,20,610,52),(405,7,555,38)]:
        d.rectangle(box, fill='#54301b', outline='#28160e', width=4)
    d.rectangle((348,24,612,70), fill='#1f160e', outline='#784b29', width=4)
    d.line((354,29,606,29), fill='#ad7941', width=2)
    for nx in (358,600):
        d.rectangle((nx,43,nx+4,47), fill='#bb9154')
    plate_font = ImageFont.truetype(str(root / 'assets/fonts/neodgm.ttf'), 24)
    d.fontmode = '1'
    label = 'Recently Updated'
    label_width = d.textlength(label, font=plate_font)
    d.text(((W-label_width)/2,36), label, font=plate_font, fill='#e8c483')

    # Metal braces.
    for x in (132, 794):
        for y in (56, 328):
            d.rectangle((x,y,x+54,y+42), fill='#3c383c', outline='#19181c', width=4)
            d.rectangle((x+9,y+8,x+44,y+32), fill='#575157', outline='#262329', width=3)
            d.rectangle((x+21,y+15,x+33,y+26), fill='#29262a')

    # Warm lantern glow layers.
    glow = Image.new('RGBA', (W,H), (0,0,0,0)); gd = ImageDraw.Draw(glow)
    for cx in (135,825):
        for radius, alpha in [(58,18),(42,28),(28,45)]: gd.ellipse((cx-radius,116-radius,cx+radius,116+radius), fill=(255,145,36,alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(18)); img = Image.alpha_composite(img.convert('RGBA'), glow).convert('RGB'); d = ImageDraw.Draw(img)
    for cx in (135,825):
        d.line((cx,0,cx,76), fill='#1c1717', width=5)
        for yy in range(8,72,14): d.rectangle((cx-5,yy,cx+5,yy+6), fill='#292226')
        d.rectangle((cx-22,76,cx+22,145), fill='#3b291e', outline='#171313', width=4)
        d.rectangle((cx-15,88,cx+15,132), fill='#e88b22')
        d.rectangle((cx-10,94,cx+10,126), fill='#ffd65a')
        d.rectangle((cx-5,98,cx+5,122), fill='#fff2a3')
        d.line((cx,80,cx,140), fill='#6f4527', width=3)

    # Fonts and wrapping.
    font_path = str(root / 'assets/fonts/neodgm.ttf')
    font_name = ImageFont.truetype(font_path, 17)
    font_body = ImageFont.truetype(font_path, 12)
    font_label = ImageFont.truetype(font_path, 14)
    font_meta = ImageFont.truetype(font_path, 12)
    # NeoDGM is a pixel font. Disabling grayscale antialiasing keeps its
    # one-pixel stems crisp after GitHub scales the three image slices.
    text_draw = ImageDraw.Draw(img)
    text_draw.fontmode = '1'

    def wrap_text(text, font, max_width, max_lines=2):
        words = text.split(); lines=[]; line=''
        for word in words:
            cand=(line+' '+word).strip()
            if line and text_draw.textbbox((0,0), cand, font=font)[2] > max_width:
                lines.append(line); line=word
            else: line=cand
        if line: lines.append(line)
        if len(lines)>max_lines:
            lines=lines[:max_lines]
            while text_draw.textbbox((0,0), lines[-1]+'…', font=font)[2] > max_width and lines[-1]: lines[-1]=lines[-1][:-1]
            lines[-1]+='…'
        return lines

    # Three pinned parchment cards, with pixel-notched edges and light texture.
    card_xs = [202,399,596]
    for i,(x,repo) in enumerate(zip(card_xs,repos[:3])):
        y,w,h = 92,162,236
        d.rectangle((x+6,y+7,x+w+7,y+h+8), fill='#1d110b')
        d.rectangle((x,y,x+w,y+h), fill='#d8ad6b', outline='#7d4725', width=3)
        d.rectangle((x+5,y+5,x+w-5,y+h-5), fill='#e8c483')
        # irregular paper edge notches
        for yy in range(y+12,y+h-10,28):
            side = -1 if (yy//28)%2 else 1
            if side<0: d.rectangle((x,yy,x+5,yy+7), fill='#3b2014')
            else: d.rectangle((x+w-5,yy,x+w,yy+7), fill='#3b2014')
        for _ in range(30):
            px=random.randint(x+8,x+w-8); py=random.randint(y+8,y+h-8)
            d.rectangle((px,py,px+random.randint(1,3),py+random.randint(1,2)), fill=random.choice(['#dfb875','#efcc8a','#d4aa69']))
        # corner rivets
        for rx,ry in [(x+8,y+8),(x+w-17,y+8),(x+8,y+h-17),(x+w-17,y+h-17)]:
            d.rectangle((rx+2,ry+3,rx+13,ry+14), fill='#2c2525')
            d.rectangle((rx,ry,rx+11,ry+11), fill='#51454a', outline='#211b1e', width=2)
            d.rectangle((rx+2,ry+2,rx+5,ry+5), fill='#75666b')
        tx=x+12
        name_font = font_name
        for size in range(17, 14, -1):
            candidate = ImageFont.truetype(font_path, size)
            if text_draw.textbbox((0, 0), repo['name'], font=candidate)[2] <= w-24:
                name_font = candidate
                break
        text_draw.text((tx,y+31), repo['name'], font=name_font, fill='#2b190f')
        desc=repo.get('description') or '저장소에서 자세한 내용을 확인하세요.'
        for row,line in enumerate(wrap_text(desc,font_body,w-24)):
            text_draw.text((tx,y+67+row*20),line,font=font_body,fill='#432b1b')
        lang=repo.get('language') or '언어 정보 없음'
        text_draw.text((tx,y+154),f'◆ {lang}',font=font_label,fill='#214d25')
        text_draw.text((tx,y+188),f'업데이트 · {repo["pushed_at"][:10]}',font=font_meta,fill='#513923')

    # Floor tiles and carpet edge.
    d.rectangle((0,376,W,H), fill='#474047')
    for x in range(0,W,48):
        d.line((x,376,x-10,H),fill='#292a31',width=2)
    d.line((0,376,W,376),fill='#887151',width=4)
    d.polygon([(250,400),(710,400),(670,383),(290,383)], fill='#162a50', outline='#a6752b')

    # Mild vignette while preserving crisp geometry.
    vig = Image.new('RGBA',(W,H),(0,0,0,0)); vd=ImageDraw.Draw(vig)
    for k,a in [(0,80),(10,55),(20,35)]: vd.rectangle((k,k,W-k-1,H-k-1),outline=(0,0,0,a),width=10)
    img=Image.alpha_composite(img.convert('RGBA'),vig).convert('RGB')
    # Meet the exact color of the shelf at the bottom of the enchanting image.
    # This lies inside the existing 400px canvas and adds no scroll height.
    d = ImageDraw.Draw(img)
    d.rectangle((0,0,W,5), fill='#24190f')
    d.rectangle((0,6,W,8), fill='#644425')
    d.rectangle((0,9,W,12), fill='#17110b')
    output = root / 'assets/scenes'
    output.mkdir(parents=True, exist_ok=True)
    img.save(output / 'quest-board-python-body12.png', optimize=True)
    for index, (left, right) in enumerate(((0, 384), (384, 576), (576, 960)), 1):
        img.crop((left, 0, right, H)).save(output / f'quest-board-python-body12-{index}.png', optimize=True)


def main():
    repos = json.loads((ROOT / 'data/recent-repos.json').read_text())
    write_quest_board(repos, ROOT)


if __name__ == '__main__':
    main()
