---
human_revised: false
name: themes
summary: Theme model (theme.json + sprites) and sprite fetching/normalization, selected by --theme/STICKERS_THEME
depends-on: []
relates: [font-build]
apps: [themes, engine]
---

# Themes

## Overview

A *theme* is a self-contained folder `themes/<name>/` holding a `theme.json` (a permanent `codepointSlot`; the sprite list — each with a display name, a cache key, and a source URL — plus an optional emoji probe) and the sprite PNGs themselves. The `theme.json` ships in the package (read-only); the PNGs are fetched into the work dir. The active theme is chosen by `--theme` / the `STICKERS_THEME` environment variable (default `pokemon`), which makes the whole pipeline theme-agnostic: pokémon is just one theme among many. Current themes: `pokemon`, `southpark`, `amongus`, `memes`, `powerrangers`, `cars`, `smurfs`, `zootopia`.

`stickers fetch` (module `fetch.py`) populates a theme's work folder by downloading each sprite from its URL and normalizing it to a uniform size. Adding a new theme is pure data — a `theme.json` (bundled, or dropped in the work dir), no code — and the font family name is fixed across themes (see [install](../install/)), so themes never touch font naming.

Every theme owns a **permanent `codepointSlot`**, which is what keeps its sprites at the same codepoints across builds (see [font-build](../font-build/)). Slots are allocated in the order themes are added, never alphabetically, precisely so the number does not track a sort order. Bundled: `pokemon` 1, `southpark` 2, `amongus` 3, `memes` 4, `powerrangers` 5, `cars` 6, `smurfs` 7, `zootopia` 8. Slot 0 belongs to the probe glyphs.

`agentNames` are globally unique across every theme — the manifest is one flat agent→sprite map, and a duplicate fails the build. That is why `powerrangers` prefixes its colours (`megared`, not `red`, which is Among Us) and `cars` ships `carslogo` rather than `logo`.

## Requirements (EARS)

### Theme selection & definition

- WHEN `--theme`/`STICKERS_THEME` is set THE SYSTEM SHALL load that theme's `theme.json`; WHEN unset THE SYSTEM SHALL default to `pokemon`.
- WHERE a `theme.json` of the same name exists in the work dir THE SYSTEM SHALL prefer it over the bundled one.
- THE SYSTEM SHALL keep sprite content (names, keys, URLs, agentNames) only in `theme.json`, never hardcoded in `config.py`.
- THE SYSTEM SHALL require every theme to declare a `codepointSlot` in its `theme.json`, unique across themes and never 0.
- WHEN new sprites are added to an existing theme THE SYSTEM SHALL have them appended to the sprite list, since a sprite's offset is its index within the theme's slot.
- THE SYSTEM SHALL keep `agentNames` unique across all themes; a duplicate fails the build.
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
- 2026-09-04: `theme.json` gained a required `codepointSlot` (plan `maintenance-stable-codepoint-layout`) — a theme's codepoints follow its identity, not its position in the build's theme list. Adding a theme no longer moves any other theme's sprites.
- 2026-09-04: `zootopia` added from StickPNG (slot 8, 15 sprites) — one per character out of 27 images. Pose selection was driven by measured ink: `normalize()` contain-fits the padded source, so an image with wide transparent margins loses resolution, and the pick per character is the pose with the most ink surviving that. See `issues/normalize-does-not-trim-alpha/`.
- 2026-09-04: `smurfs` added from StickPNG (slot 7, 16 sprites) — one sprite per character out of the 30 images the category carries. The rest are the same characters in other poses (5 Clumsy, 4 Brainy, 3 Papa) and two pair shots; they were skipped because a per-pose agent name carries no meaning as a directory name, which is the whole interface. First theme added after the slot layout landed: verified in a real build that all 105 pre-existing sprite glyphs kept their codepoints.
- 2026-09-04: `powerrangers` (Megaforce, 8 sprites) and `cars` (11 sprites) added from StickPNG. Both had to work around the global `agentNames` namespace: `mega*` prefixes because Among Us already owns `red`/`green`/`yellow`, and `carslogo` because it owns `logo`. StickPNG labels were corrected against the source material — its "Phil Mcmissile" is Finn McMissile, and its "Police Car" is the Cars 2 British police car, not Sheriff.

## Files

- `claude_statusline_stickers/theme.py` — `Theme`/`Sprite`, `load()` via `--theme`/`STICKERS_THEME`, bundled-vs-work paths.
- `claude_statusline_stickers/fetch.py` — `run()` downloads + normalizes sprites into the work dir.
- `claude_statusline_stickers/themes/<name>/theme.json` — `codepointSlot` + sprite list + source URLs (+ optional `emoji_probe`).
- `claude_statusline_stickers/config.py` — `IMAGE_SIZE`, `BUNDLED_THEMES`, `WORK_THEMES`.
