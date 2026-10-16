---
human_revised: false
plan: maintenance-familyguy-theme
task: T6
status: complete
date: 2026-09-04
summary: Installed the verified single-theme Family Guy font, cache, statusline script, and settings wiring into the live paths.
---

# Hand-off — maintenance-familyguy-theme / T6

## Files touched

<!-- cumaru:touched -->
| Link | Description |
| --- | --- |
| [.assets/work/build/familyguy/fonts/ClaudeStatusLineStickerst3-Regular.ttf](.assets/work/build/familyguy/fonts/ClaudeStatusLineStickerst3-Regular.ttf) | rebuilt — verified slot-9 Family Guy font used for installation. |
| [.assets/work/build/familyguy/cache/manifest.json](.assets/work/build/familyguy/cache/manifest.json) | rebuilt — six-agent Family Guy manifest copied to the live cache. |
<!-- /cumaru:touched -->

## Decisions made during implementation

- Reused `STICKERS_VER=t3` so the historical T3 artifact reference remains valid while installing the fresh build.
- Used the default settings-link behavior (no `--no-settings`) as explicitly authorized; the installer backed up the existing settings file before wiring `statusLine.command`.
- The live statusline script is invoked through `bash`, matching the settings command written by the installer.

## Commands run / verification

- `STICKERS_HOME="$PWD/.assets/work" python -m unittest discover -v tests` — PASS, 3 tests.
- `STICKERS_HOME="$PWD/.assets/work" python -m claude_statusline_stickers.stickers fetch --theme familyguy --force` — PASS; all six local sources normalized to 256².
- `STICKERS_HOME="$PWD/.assets/work" STICKERS_VER=t3 python -m claude_statusline_stickers.stickers build --theme familyguy` — PASS; `themes 1, agents 6, slots [familyguy=9]`.
- `STICKERS_HOME="$PWD/.assets/work" python -m claude_statusline_stickers.stickers install --theme familyguy` — PASS with settings enabled. Output purged `ClaudeStatusLineStickers113810-Regular.ttf`, copied `ClaudeStatusLineStickerst3-Regular.ttf`, copied 9 cache files, installed `~/.claude/stickers-command.sh`, and wired `settings.json`.
- Pre-install state — 1 prior matching live font and 83 prior live cache files; the old settings hash was `c728a8e27a9078ff57967222e4ddb32757bbbeee0397a817e2394729548a9d13`.
- Font parity — PASS; live and work font SHA-256 are both `1d6a47bbf6ec659c863666f6864a3d335c6fc802d680daa5875c5d56410b0429`.
- Live cmap/manifest — PASS; six `sprite.familyguy.*.full` glyphs U+F4108–U+F4158 in slot 9, with 6 agents under theme `familyguy`.
- Settings — PASS; `settings.json.bak` matches the pre-install hash, all non-`statusLine` keys are preserved, and `statusLine.command` points to `bash ~/.claude/stickers-command.sh`.
- Smoke test — PASS; `/tmp/stewie` resolved through `bash ~/.claude/stickers-command.sh` to the Stewie glyph U+F4148, present in the installed cmap.
- `~/.claude/stickers-command.sh` and `~/.claude/settings.json.bak` exist; no `--no-settings` flag was used.
- Cmd+Q is required for the terminal to reload the newly installed font.
- `cumaru tree plans`, `git diff --check`, and `cumaru doctor` — PASS; doctor reports 0 errors, 0 warnings, and 8 checks OK.

## Pending / follow-ups

- None for T6. The plan remains unarchived as requested.

## Suggestions for the Lead

- The install spec already covers the exercised purge/copy/settings contract; no install-spec delta is proposed beyond the existing no-spec-change note in `delta-draft.md`.
