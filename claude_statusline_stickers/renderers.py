"""Sprite renderers: turn a sprite image into glyphs on a FontCanvas.

Each renderer adds glyphs to the canvas and returns what the caller needs (the
statusline text lines, or the icon glyph name). They share nothing but the
canvas, the cell metrics (canvas.m) and the codepoint layout. Glyph names are
theme-neutral (sprite.<name>...); the sprite's identity lives in its codepoint.
"""
from PIL import Image

from .config import SPRITE_ANCHOR_CELLS, SPRITE_BOX_PX


def add_blank(canvas, layout, glyph="sprite.blank"):
    """Add a transparent filler glyph at this layout's blank codepoint.

    The glyph name is parameterized so each theme's blank is a distinct glyph
    (no name collision) when many themes share one font.
    """
    m = canvas.m
    canvas.add_glyph(glyph, Image.new("RGBA", (4, 4), (0, 0, 0, 0)),
                     m.advance, m.cell_h, m.descent - m.below)
    canvas.map_cp(layout.blank, glyph)


def render_probes(canvas, layout, cache_dir=None):
    """Add the overflow-probe bars + gray sheet; write probe files if cache_dir.

    H bars (red) extend N cells right of the anchor; V bars (green) extend up;
    the gray sheet covers exactly 32 cols x 8 rows drawn raw. Used to measure
    where the renderer starts clipping ink and the px-per-cell ruler.
    """
    m = canvas.m
    cell_w_px = round(m.advance / m.units_per_px)
    cell_h_px = round(m.cell_h / m.units_per_px)
    probe_lines = []
    pcp = layout.blank + 1

    for n in (1, 2, 4, 8, 16, 28):
        bar = Image.new("RGBA", (cell_w_px * n, cell_h_px), (220, 50, 50, 255))
        canvas.add_glyph(f"probe.h{n}", bar, n * m.advance, m.cell_h, m.descent - m.below)
        canvas.map_cp(pcp, f"probe.h{n}")
        probe_lines.append(f"h{n:02d} {chr(pcp)}")
        pcp += 1

    for n in (1, 2, 4, 7):
        bar = Image.new("RGBA", (cell_w_px, cell_h_px * n), (50, 200, 80, 255))
        canvas.add_glyph(f"probe.v{n}", bar, m.advance, n * m.cell_h, m.descent - m.below)
        canvas.map_cp(pcp, f"probe.v{n}")
        probe_lines.append(f"v{n} {chr(pcp)}")
        pcp += 1

    gray_w_px = round(32 * m.advance / m.units_per_px)
    gray_h_px = round(8 * m.cell_h / m.units_per_px)
    gray = Image.new("RGBA", (gray_w_px, gray_h_px), (128, 128, 128, 255))
    canvas.add_glyph("probe.gray", gray, 32 * m.advance, 8 * m.cell_h, m.descent - m.below)
    canvas.map_cp(pcp, "probe.gray")
    probe_lines.append(f"gray {chr(pcp)}")
    if cache_dir is not None:
        gray.save(cache_dir / "probe_gray.png")
        print(f"  probe gray at U+{pcp:05X}: {gray_w_px}x{gray_h_px}px "
              f"= 32 cols x 8 rows  (1 col = {m.advance / m.units_per_px:.1f}px, "
              f"1 row = {m.cell_h / m.units_per_px:.1f}px)")
    pcp += 1

    if cache_dir is not None:
        (cache_dir / "probe.txt").write_text("\n".join(probe_lines) + "\n")


def render_icon(canvas, layout, i, name, sprite):
    """Add the single-cell icon glyph; return its name (for emoji-probe mapping)."""
    m = canvas.m
    glyph = f"sprite.{name}"
    canvas.add_glyph(glyph, sprite, m.cell_h, m.cell_h, m.descent - m.below)
    canvas.map_cp(layout.icon(i), glyph)
    return glyph


def render_sprite_full(canvas, layout, i, name, sprite):
    """The whole sprite as ONE glyph; return the blank-padded anchor lines.

    Alpha-trim the art, contain-fit it into SPRITE_BOX_PX (no distortion),
    anchor it at the bottom-left of the anchor cell, and reserve blank lines for
    the actual ink height so the block hugs the sprite (no empty ceiling).
    """
    m = canvas.m
    bbox = sprite.split()[3].getbbox()
    trimmed = sprite.crop(bbox)
    box_w, box_h = SPRITE_BOX_PX
    fit = min(box_w / trimmed.width, box_h / trimmed.height)
    scaled = trimmed.resize(
        (round(trimmed.width * fit), round(trimmed.height * fit)), Image.LANCZOS,
    )

    x0 = 0
    y0 = m.descent  # image bottom at the descender — the spacing region below
                    # the cell gets clipped, so no ink hangs under the glyph
    w_units = round(scaled.width * m.units_per_px)
    h_units = round(scaled.height * m.units_per_px)
    glyph = f"sprite.{name}.full"
    canvas.add_glyph(glyph, scaled, w_units, h_units, y0, x0)
    canvas.map_cp(layout.sprite_full(i), glyph)

    ink_h_units = round(scaled.height * m.units_per_px)
    rows_above = -(-(y0 + ink_h_units) // m.cell_h)  # ceil division
    lines = [chr(layout.blank)] * rows_above
    lines.append(chr(layout.blank) * SPRITE_ANCHOR_CELLS + chr(layout.sprite_full(i)))
    return lines
