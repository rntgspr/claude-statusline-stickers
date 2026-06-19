"""FontCanvas: the patched TTFont under construction.

Wraps a loaded skeleton font and exposes the two mutating primitives the
renderers need — add_glyph (vector outline + sbix colour bitmap) and map_cp
(point a codepoint at a glyph) — plus finalize (assemble the sbix table, rename
the family, purge old versions, save). All fontTools-specific knowledge lives
here; renderers speak only in images, boxes and codepoints.
"""
from fontTools.ttLib import newTable
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
from fontTools.ttLib.tables.sbixGlyph import Glyph as SbixGlyph
from fontTools.ttLib.tables.sbixStrike import Strike

from .imaging import png_bytes, trace_outline


def ensure_cmap12(font):
    """Return the font's format-12 cmap subtables, creating one if absent."""
    subs = [s for s in font["cmap"].tables if s.format == 12]
    if subs:
        return subs

    bmp = font.getBestCmap()
    sub = CmapSubtable.getSubtableClass(12)(12)
    sub.format = 12
    sub.reserved = 0
    sub.length = 0
    sub.nGroups = 0
    sub.platformID = 3
    sub.platEncID = 10
    sub.language = 0
    sub.cmap = dict(bmp)
    font["cmap"].tables.append(sub)
    return [sub]


def rename_font(font, renames):
    """Rewrite name-table records so the patched font installs as a new family."""
    for rec in font["name"].names:
        s = rec.toUnicode()
        for old, new in renames:
            s = s.replace(old, new)
        rec.string = s


class FontCanvas:
    """A skeleton font being patched with sprite glyphs."""

    def __init__(self, font, metrics):
        """Capture the font + cell metrics and open an sbix strike for the build."""
        self.font = font
        self.m = metrics
        self.glyph_order = font.getGlyphOrder()
        self.cmap12 = ensure_cmap12(font)
        self.strike = Strike(ppem=metrics.ppem, resolution=72)

    def add_glyph(self, name, image, w_units, h_units, y0, x0=0):
        """Add one glyph: a traced vector outline plus an sbix colour bitmap.

        The outline box is clamped to the ±32767 TrueType coordinate cap (the
        sbix bitmap has no such limit and draws in full). No inset — if tinted
        outline edges ever peek out from behind the bitmap again (white picket
        stripes), restore the 3%-per-side inset that used to live here.
        """
        m = self.m
        self.font["glyf"].glyphs[name] = trace_outline(
            image,
            min(round(w_units), 32700 - x0),
            min(round(h_units), 32700 - y0),
            y0,
            x0,
        )
        self.font["hmtx"].metrics[name] = (m.advance, 0)
        self.glyph_order.append(name)
        self.strike.glyphs[name] = SbixGlyph(
            glyphName=name,
            graphicType="png ",
            imageData=png_bytes(image),
            originOffsetX=round(x0 / m.units_per_px),
            originOffsetY=round(y0 / m.units_per_px),
        )

    def map_cp(self, cp, name):
        """Point a codepoint at a glyph in every format-12 cmap subtable."""
        for sub in self.cmap12:
            sub.cmap[cp] = name

    def finalize(self, out_dir, out_name, renames, purge=None):
        """Assemble the sbix table, rename the family, purge old builds, save."""
        self.font.setGlyphOrder(self.glyph_order)
        if "post" in self.font and self.font["post"].formatType == 2.0:
            self.font["post"].extraNames = []
            self.font["post"].mapping = {}

        sbix = newTable("sbix")
        sbix.version = 1
        sbix.flags = 1
        sbix.strikes = {self.m.ppem: self.strike}
        self.font["sbix"] = sbix

        rename_font(self.font, renames)
        out_dir.mkdir(parents=True, exist_ok=True)
        if purge:
            for old in out_dir.glob(purge):
                old.unlink()
        self.font.save(out_dir / out_name)
