---
human_revised: false
name: font-build
summary: Turn a theme's sprite PNGs into one sbix colour-glyph font for the statusline
depends-on: [themes]
relates: [install]
targets: [engine]
---

# Font build

## Overview

The build engine turns a theme's sprite PNGs into a single TrueType font whose glyphs are full-colour Apple `sbix` bitmaps mapped to Private-Use-Area codepoints. This is the core trick of the project: the Claude Code statusline accepts only text + ANSI colour, and every real terminal image protocol (iTerm2 OSC 1337, kitty, sixel, DECDHL) is stripped by its escape filter — but a font glyph *is* text, so it passes. Each glyph also carries a traced vector outline so engines without `sbix` get an ANSI-tintable monochrome fallback.

`stickers build` (module `build.py`) orchestrates the build — by default every theme into one font, or a single theme via `--theme`/`STICKERS_THEME` — writing everything locally under `$STICKERS_HOME/build/` and touching nothing on the live system (that is [install](../install/)'s job). The heavy lifting is split into single-concern modules in the package: the cell-geometry ruler, the codepoint layout, the image helpers, the font canvas, and the glyph renderers.

Codepoints are **anchored to theme identity**, not to build order. Each theme declares a permanent `codepointSlot` and always occupies `CP_BASE + slot * THEME_SPAN`. This is load-bearing because the font is fallback-only: a terminal resolves a codepoint against whatever build it still holds cached, so a layout that shifted when a theme was added made it draw a *different theme's* sprite — a silent, plausible wrong answer rather than a visible failure.

## Requirements (EARS)

### Cell geometry

- WHEN a build starts THE SYSTEM SHALL derive cell metrics (advance, cell height, ppem, units-per-pixel) from the skeleton font's metrics scaled by the terminal spacing dials (`CELL_SCALE_Y`, `SPLIT`).

### Codepoint layout

- WHEN allocating glyphs THE SYSTEM SHALL anchor each theme at `CP_BASE + codepointSlot * THEME_SPAN`, taking the slot from the theme's own `theme.json` — never from the theme's position in the build's theme list.
- WHEN a theme is added or removed THE SYSTEM SHALL keep every other theme's sprites at the codepoints they already had.
- WITHIN a theme's slot THE SYSTEM SHALL give each sprite a `CP_STRIDE`-wide block, the icon at the block base and the full-sprite glyph at `SPRITE_CP_OFF`, with the blank filler fixed at the slot's last block so that appending a sprite never reuses the codepoint an older build used as filler.
- WHEN a theme declares no slot, claims the reserved probe slot 0, collides with another theme's slot, holds more sprites than a slot fits, or overlaps the skeleton font's cmap THE SYSTEM SHALL fail the build naming the theme, before rendering any glyph.
- WHERE a theme declares an emoji probe THE SYSTEM SHALL additionally map that emoji codepoint to the named sprite's icon glyph.

### Glyph encoding

- WHEN adding a glyph THE SYSTEM SHALL store both a traced vector outline (clamped to ±32767 units) and an `sbix` PNG bitmap, so engines without `sbix` fall back to a tintable outline.
- WHEN emitting the sprite glyph THE SYSTEM SHALL alpha-trim and contain-fit the art, anchor it bottom-left at the descender, and reserve only as many blank lines as the ink height needs.

### Output

- WHEN a build completes THE SYSTEM SHALL write the font, one `font_<theme>_<key>.txt` per sprite, and a `manifest.json` (agentNames → glyph/txt) under `$STICKERS_HOME/build/` (all themes → `build/all/`), without writing to `~/`.
- WHERE `STICKERS_VER` is set THE SYSTEM SHALL use it as the version baked into the family name and filename, making the build reproducible.

## Decisions

- 2026-06-16: Whole sprite as ONE glyph, not a per-cell mosaic — Warp renders ink ~28 cells right and 7 up of the anchor without clipping, so one glyph gives zero seams.
- 2026-06-17: Dead mosaic path removed (plan `maintenance-drop-mosaic`) — `render_mosaic*`, `tile_color`, `CellMetrics.tile_w/tile_cols`, `CodepointLayout.allocate`, and the orphaned dials (`BLEED_*`, `ROW_*`, `TILE_ROWS`, `SPRITE_MODE`, plus the always-1.0 `CELL_SCALE_X`/`DRAW_SCALE`); `TILE_H`→`STRIKE_PX`. Output byte-equivalent.
- 2026-06-17: All themes build into one font at distinct codepoint ranges + a `manifest.json` (plan `maintenance-all-themes-one-font`); the per-cell mosaic is no longer emitted, keeping the combined font small (~7 MB for 4 themes).
- 2026-09-04: Codepoints anchored to a declared `codepointSlot` per theme instead of a positional cursor walk (plan `maintenance-stable-codepoint-layout`) — adding or removing a theme no longer moves any other theme's sprites. `CP_STRIDE` `0x140`→`0x10` and `SPRITE_CP_OFF` `0x110`→`0x8` (only two codepoints per sprite were ever mapped; the rest was mosaic-era headroom), new `THEME_SPAN` `0x400`. Rejected hash-anchored bases: at 49 sprites over the ~3600 slots that fit in Plane 15 the birthday collision probability is ~28% and grows, and probing to resolve it reintroduces the order-dependence being removed. Moved every codepoint once; glyph content byte-identical.
- 2026-06-16: Ink anchored at column 0 and extends right only — ink left of the anchor cell is clipped by Warp.
- 2026-06-16: Vector outline clamped to ±32767 (TrueType coordinate cap); the `sbix` bitmap has no such cap and draws in full.
- 2026-06-16: `VER` baked into the family name for cache-busting — a renderer can never serve stale glyphs for a family it has never seen.
- 2026-06-16: Monolithic `build()` (~240 lines) split into single-concern modules; proven byte-identical, then functionally-identical (same codepoint→bitmap map) after renaming glyphs `poke.*` → `sprite.*`.
- 2026-06-17: Packaged into `claude_statusline_stickers/` driven by a `stickers` CLI; the build is `stickers build` → `build.run()`, and local output moved under `STICKERS_HOME` (default `~/.cache/claude-statusline-stickers`); env `COMICS_VER` → `STICKERS_VER` (plan `maintenance-cli-and-brew`).

## Files

- `claude_statusline_stickers/config.py` — dials, paths, codepoint constants, `VER`.
- `claude_statusline_stickers/geometry.py` — `CellMetrics`: the px↔units↔cells ruler.
- `claude_statusline_stickers/codepoints.py` — `CodepointLayout`, `theme_base`, `slot_capacity`, `collides_with_skeleton`.
- `claude_statusline_stickers/imaging.py` — `trace_outline`, `png_bytes`, `normalize`.
- `claude_statusline_stickers/fontcanvas.py` — `FontCanvas`: the TTFont under construction (`add_glyph`/`map_cp`/`finalize`).
- `claude_statusline_stickers/renderers.py` — icon / sprite / probe glyph emitters.
- `claude_statusline_stickers/build.py` — `run()` orchestrates the build for the active theme(s).
