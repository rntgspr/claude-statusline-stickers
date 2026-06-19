"""Codepoint layout: the single source of truth for sprite→codepoint mapping.

A sprite owns a CP_STRIDE-wide block: the icon at the block base, the
full-sprite glyph at SPRITE_CP_OFF. The blank filler sits in its own block past
the last sprite; probe glyphs follow it.
"""
from .config import CP_BASE, CP_STRIDE, SPRITE_CP_OFF


def find_free_base(font, count):
    """Return a base codepoint with `count` consecutive unmapped codepoints."""
    used = set()
    for sub in font["cmap"].tables:
        used.update(sub.cmap.keys())

    cp = CP_BASE
    while any(c in used for c in range(cp, cp + count)):
        cp += CP_STRIDE
    return cp


class CodepointLayout:
    """Maps (sprite index, slot) pairs to concrete codepoints."""

    def __init__(self, base, n_sprites):
        """Anchor the layout at `base`, reserving one block per sprite + blank."""
        self.base = base
        self.n_sprites = n_sprites

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
        """The transparent filler codepoint (past the last sprite block)."""
        return self.base + self.n_sprites * CP_STRIDE
