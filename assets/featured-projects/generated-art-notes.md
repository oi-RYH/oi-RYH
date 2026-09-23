# Enchanting project selector

## Current typography implementation

The README now uses `typeset-header.png` and three `typeset-option-*.svg` images. The Korean title and three descriptions are real NeoDunggeunmo v1.601 glyph outlines from `assets/fonts/neodgm.ttf`, not image-generated approximations. This is the same Korean pixel font as the rest of the README, not Mojang's proprietary font. Font shapes are embedded as SVG paths, so the viewer does not need the font installed. The AI-generated background, MacBook and XP orbs are retained as embedded raster artwork.

Edit the Korean strings in `scripts/typeset_enchanting_hangul.py` and run that script to regenerate. Description font size is 32px, title 48px, both integer multiples of its 16px bitmap grid. Rendered inspection image: `enchanting-typeset-preview.png`.

The older generation notes below describe the previous, fully raster version.

### Background cleanup prompt (built-in image generation)

Precise local text removal edit for later deterministic typesetting. Use attached 1536x1024 Minecraft GUI as edit target. Erase ONLY these four text regions, filling seamlessly with the same underlying beige or lavender smooth parchment background:
1. Row 1 description, entire line "MacBook 덮개 움직임을 부드러운 화면 전환으로", rectangle approximately x589..1260 y305..347.
2. Row 2 Korean title "캐리캐리체인지", rectangle x590..938 y493..545.
3. Row 2 description "캐리어 세척과 외관 손상 검사를 하나의 장치로", rectangle x590..1233 y550..585.
4. Row 3 description "자연어 일정과 Todo를 여러 기기에서 이어서", rectangle x590..1206 y783..819.
These regions must now be EMPTY clean parchment ready for real font overlays. DO NOT add or redraw text there. Preserve all other pixels/layout as closely as possible. Keep Dawn and Saydays English titles, all English technology lines, runes, MacBook input, lapis ingredient, green experience orb icons, 5/15/30 level numbers, bookshelves, book and GUI borders. Same 1536x1024 canvas and positions. Do not shift anything.

Created with the built-in image generation tool using the user's Minecraft enchanting GUI reference. The generated PNG is the source artwork; horizontal crops preserve its pixels and allow each project to link separately in GitHub README. Text is part of this preview image and must be regenerated if project summaries change.

Crop boundaries: y = 0, 180, 414, 653, 1024. Canvas: 1536 × 1024.

## Latest edit prompt (built-in image generation)

Use case: precise-object-edit.
Edit target: attached existing Minecraft enchanting portfolio GUI. Make ONLY these changes, preserve 1536x1024 composition, all panel boundaries, background, book, three row sizes and content.
1. Replace the diamond sword in the small square INPUT slot under the book at left (around x200 y410) with a clearly recognizable open silver MacBook laptop pixel sprite, dark screen, silver keyboard, small subtle purple enchanted glint. Fits within exactly the same slot. Keep the adjacent blue lapis ingredient slot unchanged.
2. Replace the three large blue lapis icons at the FAR RIGHT of each option with Minecraft EXPERIENCE ORBS: chunky small round yellow-green luminous pixel balls, pale lime/yellow bright centers, green stepped pixel edges, no blue or gems. Retain green level numbers 5, 15, 30 in existing positions.
3. Redraw ALL Korean text using authentic Minecraft Korean bitmap-style glyphs: NeoDunggeunmo / DungGeunMo inspired 16x16 Hangul bitmap type, square pixels, crisp stair-step strokes, monospaced block construction. Absolutely no smooth vector sans-serif Hangul. Existing title 캐리캐리체인지 and all three description lines need matching pixel Korean font. Exact Korean text:
Row 1: "MacBook 덮개 움직임을 부드러운 화면 전환으로"
Row 2 project title: "캐리캐리체인지"
Row 2 description: "캐리어 세척과 외관 손상 검사를 하나의 장치로"
Row 3: "자연어 일정과 Todo를 여러 기기에서 이어서"
Keep all other text identical including Dawn, Saydays, technologies, Enchant, Featured Projects, glyph accents. Keep current type sizes and alignment, descriptions must fit and be readable. Keep the existing parchment beige rows and third lavender row. Preserve original warm blurred library and grey GUI. No new UI elements or inventory grid.

## Original generation prompt

Use case: ui-mockup. Create a finished landscape Minecraft Java enchanting GUI graphic for a GitHub portfolio README, using the attached image as visual reference, not as a literal screenshot to copy. Faithful vanilla Minecraft chunky pixel GUI aesthetic: light grey beveled window, tiny low resolution textures, warm parchment enchantment buttons, vivid green level numbers, blue lapis icon, open pixel book, diamond sword input slot. Behind the window is a dark out-of-focus Minecraft bookshelf room. NOT fantasy RPG cards, no ornate purple frames, no photoreal objects. No people.
Composition: wide 3:2 canvas. Large front-facing grey GUI fills 90% width. Upper compact header contains the title "Enchant" at left, open book and diamond sword/lapis slots below, and "Featured Projects" at right. Under header are exactly THREE full-width horizontal selection buttons stacked vertically, separated by clear horizontal grey gutters. Buttons large and legible; no inventory grid as this is a project selector. Left miniature pixel project icon, name and readable Korean description centrally, short technologies line beneath, lapis and green level at right. Tiny enchanting glyph accents only above the names. Third row subtle vanilla lavender hover fill, first two parchment taupe.
Exact readable text:
Row 1: "Dawn" / "MacBook 덮개 움직임을 부드러운 화면 전환으로" / "macOS · JavaScript · Three.js" / green "5". Icon a tiny laptop.
Row 2: "캐리캐리체인지" / "캐리어 세척과 외관 손상 검사를 하나의 장치로" / "OpenCV · Embedded · Vision" / green "15". Icon a small suitcase.
Row 3: "Saydays" / "자연어 일정과 Todo를 여러 기기에서 이어서" / "Swift · Kotlin · React" / green "30". Icon a tiny calendar.
Prioritize big readable pixel typography and exact names, consistent alignment. No tooltip obscuring descriptions. GUI entire frame in canvas. Keep all three horizontal rows distinct so they can be sliced into independent linked images without changing artwork.
