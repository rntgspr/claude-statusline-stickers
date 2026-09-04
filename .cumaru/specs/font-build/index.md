---
human_revised: false
name: font-build
summary: Turn a theme's sprite PNGs into one sbix colour-glyph font for the statusline
depends-on: [themes]
relates: [install]
apps: [engine]
---

# Font build

## Overview

The build engine turns a theme's sprite PNGs into a single TrueType font whose glyphs are full-colour Apple `sbix` bitmaps mapped to Private-Use-Area codepoints. This is the core trick of the project: the Claude Code statusline accepts only text + ANSI colour, and every real terminal image protocol (iTerm2 OSC 1337, kitty, sixel, DECDHL) is stripped by its escape filter — but a font glyph *is* text, so it passes. Each glyph also carries a traced vector outline so engines without `sbix` get an ANSI-tintable monochrome fallback.

`stickers build` (module `build.py`) orchestrates the build — by default every theme into one font, or a single theme via `--theme`/`STICKERS_THEME` — writing everything locally under `$STICKERS_HOME/build/` and touching nothing on the live system (that is [install](../install/)'s job). The heavy lifting is split into single-concern modules in the package: the cell-geometry ruler, the codepoint layout, the image helpers, the font canvas, and the glyph renderers.

## Requirements (EARS)

### Cell geometry

- WHEN a build starts THE SYSTEM SHALL derive cell metrics (advance, cell height, ppem, units-per-pixel) from the skeleton font's metrics scaled by the terminal spacing dials (`CELL_SCALE_Y`, `SPLIT`).

### Codepoint layout

- WHEN allocating glyphs THE SYSTEM SHALL give each theme its own contiguous region from one free Supplementary-PUA base — a `CP_STRIDE`-wide block per sprite, the icon at the block base and the full-sprite glyph at `SPRITE_CP_OFF`.
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
- 2026-06-16: Ink anchored at column 0 and extends right only — ink left of the anchor cell is clipped by Warp.
- 2026-06-16: Vector outline clamped to ±32767 (TrueType coordinate cap); the `sbix` bitmap has no such cap and draws in full.
- 2026-06-16: `VER` baked into the family name for cache-busting — a renderer can never serve stale glyphs for a family it has never seen.
- 2026-06-16: Monolithic `build()` (~240 lines) split into single-concern modules; proven byte-identical, then functionally-identical (same codepoint→bitmap map) after renaming glyphs `poke.*` → `sprite.*`.
- 2026-06-17: Packaged into `claude_statusline_stickers/` driven by a `stickers` CLI; the build is `stickers build` → `build.run()`, and local output moved under `STICKERS_HOME` (default `~/.cache/claude-statusline-stickers`); env `COMICS_VER` → `STICKERS_VER` (plan `maintenance-cli-and-brew`).

## Files

- `claude_statusline_stickers/config.py` — dials, paths, codepoint constants, `VER`.
- `claude_statusline_stickers/geometry.py` — `CellMetrics`: the px↔units↔cells ruler.
- `claude_statusline_stickers/codepoints.py` — `CodepointLayout` + `find_free_base`.
- `claude_statusline_stickers/imaging.py` — `trace_outline`, `png_bytes`, `normalize`.
- `claude_statusline_stickers/fontcanvas.py` — `FontCanvas`: the TTFont under construction (`add_glyph`/`map_cp`/`finalize`).
- `claude_statusline_stickers/renderers.py` — icon / sprite / probe glyph emitters.
- `claude_statusline_stickers/build.py` — `run()` orchestrates the build for the active theme(s).
