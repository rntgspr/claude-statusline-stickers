---
human_revised: false
scope:
  - font-build
  - themes
status: done
completed-at: 2026-09-04
delta: delta.md
summary: Anchor each theme's codepoint block to a declared slot in theme.json so adding or removing a theme never moves another theme's sprites
apps: [engine, themes]
aux: []
---

# Stable, identity-anchored codepoint layout

## Overview

Promoted from `issues/positional-codepoint-layout/`. Sprite codepoints are
assigned by position: `build.build()` walks `Theme.discover()` alphabetically
and hands each theme the next contiguous run. Adding a theme shifts every theme
that sorts after it, so a terminal holding a previous build in its fallback
cache resolves the new codepoints against the old cmap and draws a *different
theme's* sprite. Observed twice — `pokemon` showing South Park characters, then
`cars` showing memes one-for-one.

The fix is to derive each theme's base from the theme's **identity** rather than
its position. Each `theme.json` declares a `codepointSlot`, the build multiplies
it by a fixed span, and a theme's block is then the same in every build that
ships it.

Two mechanisms were considered. **Hash-anchored blocks** (base from a hash of
the theme name) need no declaration but collide: at 49 sprites over the ~3600
16-wide slots that fit in Plane 15, the birthday probability of at least one
collision is ~28%, and it worsens as themes are added. Resolving collisions by
probing reintroduces exactly the order-dependence being removed. **Declared
slots** cost one integer per theme, are inspectable in the file that already
defines the theme, and make overlap a build-time error rather than a
probability. Declared slots win.

`CP_STRIDE` shrinks from `0x140` to `0x10` as part of this. 320 codepoints per
sprite is vestigial headroom from the per-cell mosaic path removed in
`maintenance-drop-mosaic`; only two codepoints per sprite are ever mapped (icon
at `+0`, full sprite at `SPRITE_CP_OFF`). At the old stride a fixed per-theme
span leaves room for ~11 themes in Plane 15 — not enough to reserve slots with.
At `0x10` a `0x400` span holds 63 sprites and Plane 15 holds 56 themes.

This moves every codepoint **once**, on the build that lands it. That is the
last such move; every later theme addition leaves existing themes where they
are.

## Acceptance Criteria (EARS / RFC 2119)

- WHEN a theme is added or removed THE SYSTEM SHALL keep every other theme's
  sprites at the codepoints they already had.
- WHEN two themes declare the same `codepointSlot` THE SYSTEM SHALL fail the
  build naming both themes, rather than emit an overlapping font.
- WHERE a `theme.json` omits `codepointSlot` THE SYSTEM SHALL fail the build
  naming that theme.
- WHEN a theme declares more sprites than its span holds THE SYSTEM SHALL fail
  the build rather than write into the next theme's range.
- THE SYSTEM SHALL keep the built font byte-equivalent in glyph content — only
  the cmap and the `font_*.txt` codepoints change.

## Plan / DAG

| Task | Title | Status | Depends on |
|------|-------|--------|-----------|
| [T1](t1.md) | Slot-anchored layout in config + codepoints | done | — |
| [T2](t2.md) | Declare `codepointSlot` in every bundled theme.json | done | — |
| [T3](t3.md) | Build assigns from slots and validates | done | T1, T2 |
| [T4](t4.md) | Verify stability across theme add/remove | done | T3 |

## Out of scope

- The stale-cache window itself. After this change a stale font shows the
  *correct* sprite for every theme it already knew and tofu for a genuinely new
  one — the honest signal. Forcing a font-cache flush from `install` is a
  separate question.
- The fallback-only font design. That is what lets sprites pass Claude Code's
  escape filter.
- Per-sprite identity anchoring. Sprite offset stays index-based inside a
  theme's own span, so inserting a sprite mid-list still shifts the sprites
  after it *within that theme*. Documented as append-only instead.

## Risks

- **One-time move of every codepoint.** Anyone on an older font sees tofu until
  they restart the terminal. Unavoidable, and strictly better than the current
  wrong-sprite failure.
- **Slot allocation becomes a manual step.** A new theme that forgets the field
  fails the build loudly, which is the intended trade.
