---
human_revised: false
generated: false
name: themes
summary: Theme model (theme.json + sprites) and sprite fetching/normalization, selected by --theme/STICKERS_THEME
depends-on: []
relates: [font-build]
apps: [themes, engine]
deltas: [maintenance-all-themes-one-font, maintenance-cli-and-brew]
---

# Themes

## Overview

A *theme* is a self-contained folder `themes/<name>/` holding a `theme.json` (the sprite list — each with a display name, a cache key, and a source URL — plus an optional emoji probe) and the sprite PNGs themselves. The `theme.json` ships in the package (read-only); the PNGs are fetched into the work dir. The active theme is chosen by `--theme` / the `STICKERS_THEME` environment variable (default `pokemon`), which makes the whole pipeline theme-agnostic: pokémon is just one theme among many. Current themes: `pokemon`, `southpark`, `amongus`, `memes`.

`stickers fetch` (module `fetch.py`) populates a theme's work folder by downloading each sprite from its URL and normalizing it to a uniform size. Adding a new theme is pure data — a `theme.json` (bundled, or dropped in the work dir), no code — and the font family name is fixed across themes (see [install](../install/)), so themes never touch font naming.

## Requirements (EARS)

### Theme selection & definition

- WHEN `--theme`/`STICKERS_THEME` is set THE SYSTEM SHALL load that theme's `theme.json`; WHEN unset THE SYSTEM SHALL default to `pokemon`.
- WHERE a `theme.json` of the same name exists in the work dir THE SYSTEM SHALL prefer it over the bundled one.
- THE SYSTEM SHALL keep sprite content (names, keys, URLs, agentNames) only in `theme.json`, never hardcoded in `config.py`.
- WHERE a sprite declares `agentNames` THE SYSTEM SHALL let those agent names resolve to it in the statusline manifest.
- WHERE a sprite has no `url` THE SYSTEM SHALL treat its PNG as user-supplied and leave the local file in place.

### Fetching & normalization

- WHEN fetching THE SYSTEM SHALL download each sprite into the work dir (`$STICKERS_HOME/themes/<name>/<key>.png`), skipping files that already exist unless `--force` is given.
- WHEN saving a fetched sprite THE SYSTEM SHALL normalize it to `IMAGE_SIZE`×`IMAGE_SIZE` (256²) by contain-fit on a transparent canvas, preserving aspect ratio (no distortion).
- WHERE a sprite source rejects the default agent THE SYSTEM SHALL send a browser-like User-Agent.

## Decisions

- 2026-06-16: Image sources are per-sprite URLs in `theme.json`; the catalogue of known-good CDNs (PokéHOME, OpenMoji, StickPNG, flagcdn, api-sports, cryptocurrency-icons) lives in agent memory.
- 2026-06-17: Each theme is a self-contained folder (`theme.json` + PNGs) — superseded the earlier split of `themes/<name>.json` + a separate `images/<name>/`.
- 2026-06-17: Sprites normalized to 256² on fetch — uniform inputs regardless of source resolution (PokéHOME 128, OpenMoji 618, StickPNG wildly varied).
- 2026-06-16: Star Wars was dropped — OpenMoji emoji proxies didn't hold the theme; StickPNG (cartoon characters) is the better source for character themes.
- 2026-06-17: `theme.json` bundled in the package (read-only); PNGs fetched into the work dir under `STICKERS_HOME`; selection env `COMICS_THEME` → `STICKERS_THEME`, with a `--theme` CLI flag (plan `maintenance-cli-and-brew`).

## Files

- `claude_statusline_stickers/theme.py` — `Theme`/`Sprite`, `load()` via `--theme`/`STICKERS_THEME`, bundled-vs-work paths.
- `claude_statusline_stickers/fetch.py` — `run()` downloads + normalizes sprites into the work dir.
- `claude_statusline_stickers/themes/<name>/theme.json` — sprite list + source URLs (+ optional `emoji_probe`).
- `claude_statusline_stickers/config.py` — `IMAGE_SIZE`, `BUNDLED_THEMES`, `WORK_THEMES`.
