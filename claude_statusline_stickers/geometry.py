"""CellMetrics: the px<->units<->cells ruler derived from font metrics + dials.

One place that knows how the terminal's cell geometry (the primary font at the
configured size and line height) maps to font units and bitmap pixels. Pure
arithmetic — no fontTools, no PIL — so it is trivially testable.
"""
from dataclasses import dataclass

from .config import CELL_SCALE_Y, SPLIT, STRIKE_PX


@dataclass(frozen=True)
class CellMetrics:
    """Resolved cell geometry for one base font."""

    upem: int
    ascent: int
    descent: int
    advance: int
    cell_h: int
    below: int
    ppem: int
    units_per_px: float

    @classmethod
    def from_font(cls, font):
        """Derive every cell measure from a font's metrics and the dials."""
        upem = font["head"].unitsPerEm
        ascent, descent = font["hhea"].ascent, font["hhea"].descent
        advance = font["hmtx"]["space"][0]

        # effective cell: font metrics scaled by the terminal's line height;
        # the extra vertical space is split around the glyph box per SPLIT
        cell_h = round((ascent - descent) * CELL_SCALE_Y)
        below = round((cell_h - (ascent - descent)) * SPLIT)

        # sbix strike resolution → font units per bitmap pixel
        ppem = round(upem * STRIKE_PX / cell_h)
        units_per_px = upem / ppem

        return cls(upem, ascent, descent, advance, cell_h, below, ppem, units_per_px)
