---
human_revised: false
plan: maintenance-stable-codepoint-layout
date: 2026-09-04
apps: [engine, themes]
summary: What changed in font-build and themes when the codepoint layout stopped being positional and became slot-anchored
---

# Delta — stable, identity-anchored codepoint layout

## font-build

**Codepoint layout.** A theme's base no longer comes from a cursor walk over the
build's theme list. It comes from `theme_base(slot)` = `CP_BASE + slot *
THEME_SPAN`, where `slot` is the `codepointSlot` the theme's own `theme.json`
declares. Slot 0 is reserved for the probe glyphs; themes start at 1. The
consequence is the whole point of the change: a theme's codepoints are identical
in every build that ships it, whatever else that build contains.

**Dials.** `CP_STRIDE` `0x140` → `0x10` and `SPRITE_CP_OFF` `0x110` → `0x8`. Only
two codepoints per sprite were ever mapped; the rest was headroom left over from
the per-cell mosaic dropped in `maintenance-drop-mosaic`. New `THEME_SPAN =
0x400` — 63 sprites per slot, 56 slots in Plane 15.

**Validation.** New `build.check_slots()` runs before any glyph is rendered and
raises `SystemExit` on a missing slot, slot 0, a duplicate slot, a theme with
more sprites than a slot holds, or a slot overlapping the skeleton font's cmap.
Each error names the theme (and, for a collision, both themes).

**Removed.** `codepoints.find_free_base()` — the layout is no longer discovered
by scanning. Its guard survives as `codepoints.collides_with_skeleton()`, now an
assertion rather than an allocator. New `codepoints.slot_capacity()`.

**Build output.** The summary line reports `slots [name=n, …]` instead of a
single discovered base.

## themes

**`theme.json` gains a required `codepointSlot`.** Bundled allocation, in the
order the themes were added to the project — deliberately not alphabetical, so
the number never tracks a sort order: `pokemon` 1, `southpark` 2, `amongus` 3,
`memes` 4, `powerrangers` 5, `cars` 6.

`Theme` carries `codepoint_slot`, defaulting to `None` when the file omits it,
so the build raises a named error instead of guessing — a guessed slot would be
the positional layout all over again.

## Verification

- Full set vs. each of three subsets (`cars`, `pokemon`, `amongus` withheld) and
  vs. the full set plus a new slot-7 theme: **0** shared glyphs changed
  codepoint. The same check against the old positional layout moves 64, 32, and
  86 glyphs respectively.
- All four guards fail with their named error; the real six-theme set passes.
- sbix content unchanged: 116 glyphs, identical names, **0** differing bitmaps
  against the previously installed font. Only the cmap and the `font_*.txt`
  codepoints moved.
- Built and installed (`ClaudeStatusLineStickers110757`); the statusline resolves
  `/tmp/mcqueen` → `sprite.cars.mcqueen.full` and `/tmp/pikachu` →
  `sprite.pokemon.pikachu.full`.

## Known one-time cost

This build moves every codepoint once. A terminal still holding an older font
shows tofu until it is restarted — which is the honest failure, and the last
time it happens: from here, adding a theme leaves every existing theme where it
is.
