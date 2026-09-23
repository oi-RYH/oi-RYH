"""Render the featured projects as a clickable Minecraft masterwork hall."""
from pathlib import Path
import random

from PIL import Image, ImageDraw, ImageFont, ImageFilter

from pixel_readme import ROOT


PROJECTS = (
    {
        "name": "Dawn",
        "eyebrow": "RELEASED  ·  v1.0.3",
        "lines": ("MacBook을 여닫는 순간을", "더 매끄럽게 만드는 경험"),
        "tech": "JavaScript  ·  Three.js  ·  macOS",
        "kind": "dawn",
        "accent": "#78d8ff",
    },
    {
        "name": "캐리캐리체인지",
        "eyebrow": "CAPSTONE  ·  TEAM LEAD",
        "lines": ("캐리어 세척과 외관 검사를", "한 흐름으로 묶은 자동 장치"),
        "tech": "OpenCV  ·  Embedded  ·  Vision",
        "kind": "carrier",
        "accent": "#ffd66b",
    },
    {
        "name": "Saydays",
        "eyebrow": "IN DEVELOPMENT",
        "lines": ("자연어 일정과 Todo를", "여러 기기에서 이어 쓰는 캘린더"),
        "tech": "Swift  ·  Kotlin  ·  React",
        "kind": "saydays",
        "accent": "#80f0c8",
    },
)


def _pixel_laptop(draw, ox, oy):
    draw.rectangle((ox + 20, oy + 7, ox + 88, oy + 51), fill="#182942", outline="#d9e7ef", width=5)
    draw.rectangle((ox + 29, oy + 16, ox + 79, oy + 42), fill="#60c9ed")
    draw.rectangle((ox + 22, oy + 47, ox + 100, oy + 63), fill="#aab7c2", outline="#e9f0f2", width=4)
    draw.polygon(((ox + 22, oy + 63), (ox + 100, oy + 63), (ox + 88, oy + 72), (ox + 8, oy + 72)), fill="#626f7d")
    draw.rectangle((ox + 54, oy + 55, ox + 67, oy + 59), fill="#d8e1e6")


def _pixel_carrier(draw, ox, oy):
    draw.rectangle((ox + 30, oy + 5, ox + 77, oy + 18), fill="#82715e")
    draw.rectangle((ox + 20, oy + 15, ox + 90, oy + 74), fill="#c39145", outline="#f2d08a", width=5)
    draw.line((ox + 55, oy + 17, ox + 55, oy + 72), fill="#765329", width=4)
    draw.rectangle((ox + 28, oy + 28, ox + 48, oy + 48), fill="#273c48", outline="#72e4ed", width=4)
    draw.rectangle((ox + 34, oy + 34, ox + 42, oy + 42), fill="#bffaff")
    for x in (31, 77):
        draw.rectangle((ox + x, oy + 74, ox + x + 9, oy + 84), fill="#31343c")
    for y in (29, 50):
        draw.rectangle((ox + 96, oy + y, ox + 105, oy + y + 9), fill="#66d6d0")


def _pixel_calendar(draw, ox, oy):
    draw.rectangle((ox + 14, oy + 14, ox + 94, oy + 78), fill="#e5dfcb", outline="#fff7dd", width=5)
    draw.rectangle((ox + 14, oy + 14, ox + 94, oy + 32), fill="#2f8b7a")
    for x in (29, 77):
        draw.rectangle((ox + x, oy + 7, ox + x + 7, oy + 23), fill="#b8d2ce")
    for yy in (42, 56, 70):
        for xx in (28, 45, 62, 79):
            draw.rectangle((ox + xx, oy + yy, ox + xx + 7, oy + yy + 7), fill="#748d91")
    # A small sprout emerging from the calendar.
    draw.rectangle((ox + 53, oy - 5, ox + 59, oy + 16), fill="#6ca64a")
    draw.rectangle((ox + 34, oy - 11, ox + 55, oy + 2), fill="#7bd45d")
    draw.rectangle((ox + 58, oy - 17, ox + 82, oy - 3), fill="#94df66")


def build(root=ROOT):
    """One GUI, sliced horizontally so each enchantment remains a real link."""
    width, height = 960, 664
    img = Image.new('RGB', (width, height), '#080808')
    d = ImageDraw.Draw(img)
    d.fontmode = '1'
    fp = str(root / 'assets/fonts/neodgm.ttf')
    def text(x, y, value, size=20, color='#343434'):
        d.text((x,y), value, font=ImageFont.truetype(fp,size), fill=color)
    def bevel(box, fill, raised=True, thickness=5):
        x,y,r,b=box
        d.rectangle(box,fill=fill)
        light,dark=('#ffffff','#555555') if raised else ('#373737','#eeeeee')
        d.line((x,b,x,y,r,y),fill=light,width=thickness)
        d.line((r,y,r,b,x,b),fill=dark,width=thickness)
    bevel((7,7,952,656),'#c6c6c6',thickness=7)
    text(34,25,'Enchanting',28)
    text(670,32,'PROJECT SELECTION',18,'#626262')
    # Open book, brown leather cover, cream pages and central binding.
    d.polygon([(342,110),(427,79),(478,101),(522,79),(614,110),(604,165),(524,149),(478,177),(426,149),(354,167)],fill='#643b22')
    d.polygon([(351,104),(426,75),(474,98),(474,164),(426,140),(359,156)],fill='#f2e6bd')
    d.polygon([(482,98),(524,75),(606,104),(599,156),(523,140),(482,164)],fill='#ded0a6')
    d.line((478,99,478,166),fill='#977448',width=5)
    for i in range(4):
        y=103+i*10
        d.line((371,y+10,424,y-9,453,y+3),fill='#a69778',width=3)
        d.line((501,y+3,525,y-9,583,y+10),fill='#a69778',width=3)
    # Item and lapis input slots, as in the enchanting interface.
    bevel((111,95,178,162),'#8b8b8b',False)
    bevel((194,95,261,162),'#8b8b8b',False)
    d.polygon([(126,112),(146,104),(165,116),(159,143),(138,150),(124,137)],fill='#594581')
    d.line((128,112,147,117,163,116),fill='#b492e9',width=4)
    def lapis(x,y,s=1):
        points=[(0,12),(10,0),(23,3),(29,14),(22,28),(5,27)]
        d.polygon([(x+a*s,y+b*s) for a,b in points],fill='#1745a2')
        d.polygon([(x+4*s,y+12*s),(x+11*s,y+3*s),(x+20*s,y+5*s),(x+14*s,y+16*s)],fill='#528be3')
        d.line((x+6*s,y+24*s,x+18*s,y+25*s,x+25*s,y+15*s),fill='#10275e',width=max(2,int(3*s)))
    lapis(208,109,1.3)
    text(700,111,'3 PROJECTS',20,'#4b4b4b')
    text(700,144,'선택해서 저장소 열기',16,'#646464')
    # Decorative glyphs only; project descriptions remain plain readable text.
    def glyphs(x,y,index):
        rng=random.Random(84+index)
        for k in range(15):
            gx=x+k*14
            d.line((gx,y,gx,y+10,gx+7,y+10),fill='#88744f',width=2)
            if rng.randrange(2): d.line((gx,y+4,gx+8,y+4,gx+8,y),fill='#88744f',width=2)
            else: d.rectangle((gx+5,y,gx+8,y+2),fill='#88744f')
    desc=[('MacBook 덮개 움직임을 부드러운 화면 전환으로','JavaScript · Three.js · macOS  /  Released v1.0.3'),
          ('캐리어 세척과 외관 손상 검사를 하나의 장치로','OpenCV · Embedded · Vision  /  Team Lead'),
          ('자연어 일정과 Todo를 여러 기기에서 이어서','Swift · Kotlin · React  /  In Development')]
    for i,p in enumerate(PROJECTS):
        y=202+i*146
        bevel((32,y,927,y+132),'#796343',False,4)
        d.rectangle((39,y+7,920,y+125),fill='#c5b58d')
        d.line((42,y+9,916,y+9),fill='#e9dcb6',width=3)
        bevel((49,y+20,144,y+111),'#3e3b32',False,3)
        icon=Image.new('RGBA',(115,105),(0,0,0,0))
        painter=ImageDraw.Draw(icon)
        {'dawn':_pixel_laptop,'carrier':_pixel_carrier,'saydays':_pixel_calendar}[p['kind']](painter,0,19 if i==2 else 5)
        icon=icon.resize((86,79),Image.Resampling.NEAREST)
        img.paste(icon,(54,y+26),icon)
        glyphs(167,y+13,i)
        text(167,y+32,p['name'],26,'#29251f')
        text(167,y+68,desc[i][0],20,'#3a3329')
        text(167,y+100,desc[i][1],16,'#5d513b')
        lapis(832,y+47,1.1)
        text(877,y+49,str((5,15,30)[i]),26,'#244b16')
    out=root/'assets/featured-projects'
    out.mkdir(exist_ok=True,parents=True)
    img.save(out/'enchanting-preview.png',optimize=True)
    img.crop((0,0,width,196)).save(out/'enchanting-header.png',optimize=True)
    for i,(a,b) in enumerate(((196,342),(342,488),(488,664)),1):
        img.crop((0,a,width,b)).save(out/f'enchanting-option-{i}.png',optimize=True)


if __name__ == '__main__':
    build()
