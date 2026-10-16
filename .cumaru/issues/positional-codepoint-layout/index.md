---
human_revised: false
type: bug
priority: medium
status: open
targets: [engine, statusline]
summary: Adding a theme shifts every later theme's codepoints, so a stale font cache silently renders a different theme's sprite instead of failing visibly
---

# Positional codepoint layout makes a stale font cache render the wrong sprite

## Description

Sprite codepoints are assigned by **position**, not by identity. `build.build()`
walks `Theme.discover()` in alphabetical order and hands each theme the next
contiguous run of `(len(sprites) + 1) * CP_STRIDE` codepoints. Inserting a theme
therefore shifts the block of every theme that sorts after it.

The cache files (`font_*.txt`) written by the same build always agree with the
font that build produced, so a complete install is self-consistent. The defect
surfaces across builds: a terminal that still holds a **previous** build of the
font in its fallback cache resolves the new codepoints against the old cmap, and
those codepoints usually land on a real glyph belonging to some other theme.

The failure is silent and plausible — a wrong sprite, not a missing one.

## Context

Observed after adding the `cars` theme (11 sprites). `cars` sorts before
`memes`, `pokemon`, `powerrangers`, and `southpark`, so all four shifted by 12
blocks. Reported symptom: "o tema de pokemons tem alguns do southpark".

Reconstructing the three layouts confirmed it exactly — the same codepoint in
the terminal's stale 4-theme font maps to a South Park character:

| agent dir | codepoint | installed font | stale 4-theme font |
|---|---|---|---|
| `bulbasaur` | U+F4250 | `pokemon.bulbasaur` | `southpark.chef` |
| `pikachu` | U+F4610 | `pokemon.pikachu` | `southpark.damien` |
| `vulpix` | U+F4750 | `pokemon.vulpix` | `southpark.citywok` |
| `psyduck` | U+F4890 | `pokemon.psyduck` | unmapped (tofu) |

The installed font itself was verified correct: its eight `sprite.pokemon.*`
sbix bitmaps are the right Pokémon, and the statusline resolved `/tmp/pikachu`
to `sprite.pokemon.pikachu.full`. Restarting the terminal fixed the display.

`VER` in `config.FAMILY` exists to bust exactly this cache, and it does not
help here: the font is **fallback-only**. The terminal never selects the family
by name — it resolves an unmapped codepoint through fallback — so a versioned
family name is never consulted on this path.

<!-- cumaru:reference -->
| Link | Description |
|---|---|
| [claude_statusline_stickers/codepoints.py](claude_statusline_stickers/codepoints.py) | `CodepointLayout` — anchors a theme's blocks at a caller-supplied base; carries no theme identity |
| [claude_statusline_stickers/build.py](claude_statusline_stickers/build.py) | `build()` — the positional cursor walk over `sorted()` themes that assigns each base |
| [claude_statusline_stickers/config.py](claude_statusline_stickers/config.py) | `CP_BASE`, `CP_STRIDE`, `SPRITE_CP_OFF`, and the `FAMILY`/`VER` cache-busting comment this issue contradicts |
<!-- /cumaru:reference -->

## Impact

Hits any user who installs a build that added or removed a theme and does not
fully quit the terminal. Cosmetic in severity, but it reads as data corruption:
the sprite shown belongs to a different theme, so the natural conclusion is that
the theme files are wrong. Diagnosing it needs a cmap-level comparison against a
font that install has already purged from disk.

Grows with the theme count — every new theme shifts more of the existing set.

## Acceptance Criteria (EARS / RFC 2119)

- WHEN a theme is added or removed THE SYSTEM SHALL keep every unaffected
  theme's sprites at the codepoints they already had.
- WHERE a renderer resolves a codepoint against a stale build of the font THE
  SYSTEM SHALL NOT display a sprite belonging to a different theme.
- THE SYSTEM SHALL derive each theme's codepoint block from the theme's
  identity rather than from its position in the build's theme list.

## Notes

Two candidate directions, neither chosen:

- **Hash-anchored blocks** — derive a theme's base from a stable hash of its
  name. Adding a theme never moves an existing one. Needs collision handling,
  and the PUA range has to stay large enough for the sprawl.
- **Reserved fixed ranges** — pin each bundled theme to a declared range in
  `theme.json` or `config.py`. Simpler and inspectable; costs a manual
  allocation step per theme and needs a rule for user-added themes.

Neither removes the stale-cache window entirely — they convert the failure from
a *wrong* sprite into a *missing* one (tofu), which is the honest signal. Worth
weighing whether that is enough, or whether the statusline should also assert
the family it expects.

Non-goal: dropping the fallback-only design. That is what lets sprites pass
Claude Code's escape filter at all.

## Promotion / drop criteria

- Promote when one of the two layout strategies is chosen and its migration
  story for already-installed fonts is settled.
- Drop if the codepoint layout stops being positional for another reason, or if
  install gains a reliable way to force a font-cache flush.
