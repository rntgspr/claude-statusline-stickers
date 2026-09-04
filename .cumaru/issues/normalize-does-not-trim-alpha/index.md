---
human_revised: false
type: improvement
priority: medium
status: open
apps: [engine, themes]
summary: normalize() contain-fits the padded source instead of the art, so a sprite with wide transparent margins is downscaled and renders soft
---

# `normalize()` fits the padding, not the art

## Description

`imaging.normalize()` contain-fits the *whole source canvas* into
`IMAGE_SIZE`², including whatever transparent margin the source carries. The
art is then a fraction of the 256² result, and `renderers.render_sprite_full()`
alpha-trims it and scales it back up to `SPRITE_BOX_PX` — so the padding is
paid for twice: once as lost resolution at fetch, once as upscale blur at build.

Alpha-trimming before the contain-fit costs one line and makes the 256² grid
hold art instead of emptiness.

## Context

Found while picking poses for the `zootopia` theme. StickPNG sources vary wildly
in how much margin they carry, and the effect is severe at the extreme:

| sprite | source | ink in source | ink after `normalize` | trimming first |
|---|---|---|---|---|
| `nick` (Nick Wilde the Fox) | 640×320 | 110×248 | **44×99** | 113×256 |
| Judy Hopps Showing Police ID | 702×336 | 343×287 | 125×105 | 256×214 |
| `judy` (Arms Crossed) | 284×558 | 272×544 | 125×250 | 125×256 |
| `priscilla` | 1552×1417 | 1523×1387 | 251×229 | 251×229 |

A tight source loses nothing; a padded one loses most of its resolution. Nick
keeps 18% of the pixels he could have. Rendered side by side at final size the
difference is plainly visible — the trimmed version is sharper at the same
dimensions.

The zootopia theme worked around it by choosing, per character, the pose with
the most ink surviving `normalize` rather than the most canonical pose. That is
the wrong axis to pick art on.

<!-- cumaru:reference -->
| Link | Description |
|---|---|
| [claude_statusline_stickers/imaging.py](claude_statusline_stickers/imaging.py) | `normalize()` — contain-fits `img` whole; the fix is to crop to `img.getbbox()` first |
| [claude_statusline_stickers/fetch.py](claude_statusline_stickers/fetch.py) | calls `normalize` on download; a re-fetch with `--force` is what applies the change |
| [claude_statusline_stickers/renderers.py](claude_statusline_stickers/renderers.py) | `render_sprite_full()` — already alpha-trims, which is why the padding is pure loss |
<!-- /cumaru:reference -->

## Impact

Cosmetic but across the board: every theme has some sprites softer than their
source allows. It also distorts theme curation, since art gets chosen for how
little margin it ships with.

The fix changes rendering for all existing sprites — they get slightly larger
and sharper — and only takes effect after `stickers fetch --force`, because the
work dir already holds the padded 256² PNGs.

## Acceptance Criteria (EARS / RFC 2119)

- WHEN normalizing a fetched sprite THE SYSTEM SHALL contain-fit the art's alpha
  bounding box, not the source canvas.
- WHERE a source carries no transparent margin THE SYSTEM SHALL produce the same
  output it produces today.
- THE SYSTEM SHALL leave the sprite centred on the transparent `IMAGE_SIZE`²
  canvas, so cell geometry is unaffected.

## Notes

- One line: `img = img.crop(img.getbbox())` before computing `fit`, guarding the
  fully-transparent case where `getbbox()` returns `None`.
- Needs a `stickers fetch --force` plus a rebuild to land, and every sprite
  changes size slightly — worth confirming a few against the probe grid before
  and after.
- Open question: whether to trim at fetch (fewer pixels stored, work dir becomes
  lossy about the original framing) or keep fetch faithful and trim at build.
  Build-time trimming already happens, so the cheaper fix is fetch-time; the
  cleaner one may be to store the source untouched and normalize later.

## Promotion / drop criteria

- Promote when the fetch-time vs build-time question is settled.
- Drop if sprite sourcing changes such that padded inputs no longer occur.
