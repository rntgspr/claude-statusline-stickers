"""Codepoint layout: the single source of truth for sprite→codepoint mapping.

A theme owns a THEME_SPAN-wide slot, anchored by the `codepointSlot` its
theme.json declares — so a theme's codepoints are the same in every build that
ships it, whatever else the build contains. Inside that slot a sprite owns a
CP_STRIDE-wide block: the icon at the block base, the full-sprite glyph at
SPRITE_CP_OFF. The blank filler owns the slot's last block, so appending a
sprite never lands on it; probe glyphs follow it inside that block.

Slot 0 is the probes'. Themes start at 1.
"""
from .config import CP_BASE, CP_STRIDE, SPRITE_CP_OFF, THEME_SPAN


def theme_base(slot):
    """First codepoint of a theme slot — the anchor its whole block hangs off."""
    return CP_BASE + slot * THEME_SPAN


def slot_capacity():
    """How many sprites a slot holds, once the trailing blank is accounted for."""
    return THEME_SPAN // CP_STRIDE - 1


def collides_with_skeleton(font, slot):
    """True when a slot's range overlaps a codepoint the skeleton font maps.

    The skeleton supplies the cell metrics, not glyphs, so an overlap would let
    its cmap win for one of our sprites. Plane 15 is empty in practice; this is
    the assertion that keeps it that way.
    """
    used = set()
    for sub in font["cmap"].tables:
        used.update(sub.cmap.keys())

    base = theme_base(slot)
    return any(c in used for c in range(base, base + THEME_SPAN))


class CodepointLayout:
    """Maps a sprite index to the concrete codepoints of its block."""

    def __init__(self, base):
        """Anchor the layout at `base`, the first codepoint of its slot."""
        self.base = base

    def block(self, i):
        """First codepoint of sprite i's block."""
        return self.base + i * CP_STRIDE

    def icon(self, i):
        """Single-cell icon glyph of sprite i."""
        return self.block(i)

    def sprite_full(self, i):
        """Whole-sprite single glyph of sprite i."""
        return self.block(i) + SPRITE_CP_OFF

    @property
    def blank(self):
        """The transparent filler codepoint, fixed at the slot's last block."""
        return self.base + slot_capacity() * CP_STRIDE
