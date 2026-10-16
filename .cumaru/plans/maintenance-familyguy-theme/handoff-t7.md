---
human_revised: false
plan: maintenance-familyguy-theme
task: T7
status: complete
date: 2026-09-04
summary: Rebuilt and installed the combined nine-theme font so bundled agents and local Family Guy resolve from one live manifest.
---

# Hand-off — maintenance-familyguy-theme / T7

## Files touched

<!-- cumaru:touched -->
| Link | Description |
| --- | --- |
| [.assets/work/build/all/fonts/ClaudeStatusLineStickerst7-Regular.ttf](.assets/work/build/all/fonts/ClaudeStatusLineStickerst7-Regular.ttf) | rebuilt — combined nine-theme font installed live. |
| [.assets/work/build/all/cache/manifest.json](.assets/work/build/all/cache/manifest.json) | rebuilt — combined 86-agent manifest installed live. |
<!-- /cumaru:touched -->

## Decisions made during implementation

- Ran fetch, build, and install without `--theme` as required; this is the operational correction for T6's intentional single-theme install.
- Kept `STICKERS_VER=t7` on the combined build so the live font and build artifact have a stable, auditable name/hash.
- No source code or specs were changed; the install behavior was already specified and the delta records no spec change for this operational correction.

## Commands run / verification

- `STICKERS_HOME="$PWD/.assets/work" python -m unittest discover -v tests` — PASS, 3 tests.
- `STICKERS_HOME="$PWD/.assets/work" python -m claude_statusline_stickers.stickers fetch --force` — PASS; refreshed all bundled and local sources without a theme selector.
- `STICKERS_HOME="$PWD/.assets/work" STICKERS_VER=t7 python -m claude_statusline_stickers.stickers build` — PASS; `themes 9, agents 86, slots [amongus=3, cars=6, familyguy=9, memes=4, pokemon=1, powerrangers=5, smurfs=7, southpark=2, zootopia=8]`.
- `STICKERS_HOME="$PWD/.assets/work" python -m claude_statusline_stickers.stickers install` — PASS; purged `ClaudeStatusLineStickerst3-Regular.ttf`, replaced the prior 9-file single-theme cache with 89 combined cache files, installed the t7 font/statusline/cache, and rewired settings.
- Font parity — PASS; build/all and live font SHA-256 are both `36b21958675fd8df4a9d553f308d0c5c81e9d3c47c6510dc66aa33aaaea81fbd`.
- Manifest parity — PASS; build/all and live manifests are identical, with 9 themes and 86 agents.
- Slot/cmap — PASS; Family Guy has six `.full` glyphs U+F4108–U+F4158 in slot 9; all declared slots are unique and correct.
- Settings — PASS; the pre-T7 settings hash `fe4d670ce9df231c2656ebfb04c6a0188d18710c00ab9d171ced9b6cf32d8b9a` matches `settings.json.bak`, unrelated keys remain preserved, and `statusLine.command` remains wired to `bash ~/.claude/stickers-command.sh`.
- Smoke tests — PASS; `/tmp/pikachu` resolves to the existing bundled Pokémon manifest entry, and `/tmp/stewie` resolves to `font_familyguy_stewie.txt` / U+F4148.
- Live state — PASS; one combined `ClaudeStatusLineStickerst7-Regular.ttf`, 89 live cache files, and the installed statusline script are present.
- Cmd+Q is required for the terminal to reload the combined font.
- `cumaru tree plans`, `git diff --check`, and `cumaru doctor` — PASS; doctor reports 0 errors, 0 warnings, and 8 checks OK.

## Pending / follow-ups

- None for T7. The plan remains unarchived as requested.

## Suggestions for the Lead

- The delta draft now records that install behavior required no spec change; the operational correction is the no-`--theme` invocation that restores the combined live manifest.
