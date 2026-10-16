---
human_revised: false
plan: maintenance-familyguy-theme
status: draft
date: 2026-09-04
summary: Propose the themes-spec delta for exclusive URL-or-path sources and local path-backed fetch behavior.
---

# Delta draft — maintenance-familyguy-theme

Proposed changes to `specs/` resulting from this plan. **The Lead validates and finalizes** as `archive/maintenance-familyguy-theme/delta.md` during the archive flow. No spec files were edited by Dev during this closeout.

## specs/themes/index.md

### Added Requirements

- THE SYSTEM SHALL require every sprite to declare exactly one source: `url` or `path`.
- WHERE a sprite declares `path` THE SYSTEM SHALL expand a leading `~`, resolve a relative path from the command's working directory, and read that local image as its source.
- WHEN a path-backed sprite is fetched THE SYSTEM SHALL normalize it through the same pipeline used for URL sources and save it into the work theme folder.

### Modified Requirements

- The theme model SHALL allow a local work-directory `theme.json` override and represent each sprite with exactly one URL or local path (was: the packaged `theme.json` represented sprites with source URLs and fetched PNGs only).
- WHEN fetching THE SYSTEM SHALL ingest each sprite into `$STICKERS_HOME/themes/<name>/<key>.png`, skipping existing files unless `--force` is given (was: fetching SHALL download each sprite into that work path).
- The documented bundled-theme catalog SHALL list only bundled themes; local Family Guy remains an ignored work theme (was: the overview's current-theme wording did not distinguish bundled themes from local work themes).

### Removed Requirements

- `WHERE a sprite has no url THE SYSTEM SHALL treat its PNG as user-supplied and leave the local file in place.` Removed because local sources now have an explicit `path` field and pass through fetch normalization before build.

## specs/install/index.md

> No spec change required — T6 exercised the existing single-theme install contract (font/cache purge and copy, statusline script installation, settings backup/update, and preservation of unrelated settings keys) without changing install behavior. T7 corrected the operational invocation by building and installing without `--theme`, which exercised the existing combined all-themes install contract without changing install behavior.
