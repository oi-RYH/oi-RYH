# Inventory comparison preview

This variant leaves the board preview on `codex/portfolio-info-preview`
unchanged. `codex/portfolio-inventory-preview` uses a generated extension of
the same Enchant GUI, with three live recent-repository slots in its lower
inventory area. Main is unchanged.

The background was edited with the built-in image generation tool. It was
normalized to 1536 × 1408 and the original upper 884 rows were preserved
to retain the approved enchanting runes and artwork. Actual NeoDunggeunmo
glyph paths supply Korean text and live repository names/descriptions.

`scripts/inventory_projects.py` reads the existing recent-repository snapshot
through the README update pipeline. Images are sliced without layout gaps so
all six project links remain independent. Missing repository slots stay empty.
Edit data or layout in the renderer, not in the generated images.

## Image editing prompt

Edit the supplied Minecraft Enchant GUI into one integrated Enchant + Inventory menu for a portfolio. Output EXACTLY 1536x1408 pixels, extending the original canvas DOWNWARD. Preserve original upper content position and scale: x coordinates unchanged; top grey frame starts y100, book, MacBook input, lapis ingredient, right XP orbs, English names and tech rows remain in same positions. Keep the four blank Korean text areas blank for real-font typesetting later.
Critical: remove the lower frame edge at y890 and extend the SAME grey GUI down to y1320, sides staying x108 and x1424. No shelf, no wood beam, no second panel or dividing scene. One uninterrupted grey Minecraft GUI. Continue dark blurred bookshelf background outside the window to bottom of canvas.
Below existing third enchantment button ending y880:
At x150 y925 write 'Inventory' in classic dark Minecraft pixel font. At x1040 y925 write 'RECENT WORK' smaller.
Below that, exactly 3 WIDE EMPTY recessed inventory slots in a horizontal row:
left bounds x148..548 y978..1256;
middle bounds x568..968 y978..1256;
right bounds x988..1388 y978..1256.
Use authentic Minecraft inventory-slot bevels: medium grey interiors, dark top/left inset border and white lower/right edges. Interiors EMPTY without any words, icons, glyphs or decoration. These slots will receive live repository descriptions and icons later. No tiny inventory grid. Bottom frame at y1310..1330. Keep overall authentic pixel GUI aesthetic, flat front view, existing warm background, not ornate or photorealistic. Don't add Korean text anywhere.
