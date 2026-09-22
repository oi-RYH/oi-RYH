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
    random.seed(42)
    width, height = 960, 410
    image = Image.new("RGB", (width, height), "#0c0a12")
    draw = ImageDraw.Draw(image)

    # A continuous deepslate hall makes the three independently linked slices
    # read as one scene on GitHub.
    for y in range(0, height, 36):
        offset = -42 if (y // 36) % 2 else 0
        for x in range(offset, width, 84):
            shade = random.choice(("#211c2a", "#292132", "#30253a", "#1c1925"))
            draw.rectangle((x + 1, y + 1, x + 81, y + 33), fill=shade, outline="#100e17", width=3)
            draw.line((x + 8, y + 7, x + 69, y + 7), fill="#44344e", width=2)

    # An enchanting-table canopy: obsidian, red lacquer and a restrained
    # dancheong rhythm keep it connected to the Korean Minecraft setting.
    draw.rectangle((0, 0, width, 39), fill="#160f1d")
    draw.rectangle((0, 7, width, 16), fill="#65253d")
    draw.rectangle((0, 23, width, 32), fill="#174f4d")
    for x in range(13, width, 48):
        draw.rectangle((x, 20, x + 22, 35), fill="#1e6962")
        draw.rectangle((x + 5, 22, x + 17, 31), fill="#74304f")
        draw.rectangle((x + 9, 24, x + 13, 29), fill="#d6b35c")
    draw.line((0, 39, width, 39), fill="#9f79d0", width=3)

    font_path = str(root / "assets/fonts/neodgm.ttf")
    font_name = ImageFont.truetype(font_path, 24)
    font_name_ko = ImageFont.truetype(font_path, 21)
    font_eye = ImageFont.truetype(font_path, 12)
    font_body = ImageFont.truetype(font_path, 14)
    font_tech = ImageFont.truetype(font_path, 12)
    font_action = ImageFont.truetype(font_path, 13)
    draw.fontmode = "1"

    # A faint cyber scan line is the only futuristic accent.
    glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for x, project in enumerate(PROJECTS):
        cx = x * 320 + 160
        color = project["accent"]
        rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
        gd.ellipse((cx - 105, 55, cx + 105, 252), fill=(*rgb, 35))
        gd.ellipse((cx - 62, 80, cx + 62, 222), outline=(169, 91, 255, 75), width=12)
    glow = glow.filter(ImageFilter.GaussianBlur(22))
    image = Image.alpha_composite(image.convert("RGBA"), glow).convert("RGB")
    draw = ImageDraw.Draw(image)
    draw.fontmode = "1"

    for index, project in enumerate(PROJECTS):
        left = index * 320
        accent = project["accent"]

        # Obsidian alcove, lacquer corners and an enchanted advancement path.
        draw.rectangle((left + 17, 52, left + 303, 389), fill="#121019", outline="#09070d", width=7)
        draw.rectangle((left + 22, 57, left + 298, 384), outline="#392348", width=8)
        draw.rectangle((left + 30, 65, left + 290, 376), outline="#b08add", width=2)
        for px, py in ((28, 63), (275, 63), (28, 351), (275, 351)):
            draw.rectangle((left + px, py, left + px + 18, py + 18), fill="#21152c", outline="#c5a3e7", width=3)
            draw.rectangle((left + px + 6, py + 6, left + px + 12, py + 12), fill=accent)

        # Geometric glyphs circle the item like enchanting-table letters.
        for gx, gy, flip in ((66, 98, 0), (242, 98, 1), (61, 176, 1), (247, 176, 0)):
            x = left + gx
            draw.line((x, gy, x + (-10 if flip else 10), gy + 8, x, gy + 16), fill="#8558b8", width=3)
            draw.rectangle((x - 2, gy + 20, x + 3, gy + 25), fill=accent)

        # Obsidian item frame, floating project artifact and spell ring.
        draw.ellipse((left + 91, 78, left + 229, 216), outline="#51316e", width=5)
        draw.rectangle((left + 95, 83, left + 225, 211), fill="#20142c", outline="#08060c", width=7)
        draw.rectangle((left + 106, 94, left + 214, 200), fill="#17151f", outline="#a66ce2", width=5)
        draw.rectangle((left + 116, 104, left + 204, 190), outline=accent, width=2)
        if project["kind"] == "dawn":
            _pixel_laptop(draw, left + 105, 112)
        elif project["kind"] == "carrier":
            _pixel_carrier(draw, left + 105, 105)
        else:
            _pixel_calendar(draw, left + 106, 111)
        # Open spellbook pedestal under every artifact.
        draw.polygon(((left + 116, 191), (left + 154, 184), (left + 160, 194), (left + 166, 184),
                      (left + 204, 191), (left + 194, 207), (left + 166, 202), (left + 160, 211),
                      (left + 154, 202), (left + 126, 207)), fill="#d9c797", outline="#6e4e55")
        draw.line((left + 160, 194, left + 160, 207), fill="#8f4e72", width=3)
        draw.rectangle((left + 151, 210, left + 169, 215), fill="#8b5fc0")
        if index < 2:
            draw.line((left + 294, 147, left + 326, 147), fill="#6e4b91", width=5)
            draw.rectangle((left + 301, 141, left + 311, 152), fill=accent)
            draw.rectangle((left + 313, 143, left + 320, 150), fill="#d49cff")

        def centered(text, y, font, fill):
            box = draw.textbbox((0, 0), text, font=font)
            draw.text((left + 160 - (box[2] - box[0]) / 2, y), text, font=font, fill=fill)

        name_font = font_name_ko if index == 1 else font_name
        centered(project["name"], 221, name_font, "#f1e6c8")
        centered(project["eyebrow"], 257, font_eye, accent)
        centered(project["lines"][0], 282, font_body, "#d8d9dc")
        centered(project["lines"][1], 304, font_body, "#d8d9dc")
        draw.line((left + 66, 335, left + 254, 335), fill="#59406d", width=2)
        centered(project["tech"], 345, font_tech, "#aeb7be")
        centered("[ 저장소 열기 ]", 369, font_action, accent)

    output = root / "assets/featured-projects"
    output.mkdir(parents=True, exist_ok=True)
    image.save(output / "masterwork-hall.png", optimize=True)
    for index, (left, right) in enumerate(((0, 320), (320, 640), (640, 960)), 1):
        image.crop((left, 0, right, height)).save(output / f"masterwork-hall-{index}.png", optimize=True)


if __name__ == "__main__":
    build()
