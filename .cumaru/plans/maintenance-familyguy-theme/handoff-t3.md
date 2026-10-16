---
human_revised: false
plan: maintenance-familyguy-theme
task: T3
status: complete
date: 2026-09-04
summary: Fetched the six local Family Guy sprites, built the slot-9 font under ignored work assets, and verified its sbix glyphs visually.
---

# Hand-off — maintenance-familyguy-theme / T3

## Files touched

<!-- cumaru:touched -->
| Link | Description |
| --- | --- |
| [.assets/work/themes/familyguy/peter.png](.assets/work/themes/familyguy/peter.png) | created — normalized local Peter sprite. |
| [.assets/work/themes/familyguy/quagmire.png](.assets/work/themes/familyguy/quagmire.png) | created — normalized local Quagmire sprite. |
| [.assets/work/themes/familyguy/brian.png](.assets/work/themes/familyguy/brian.png) | created — normalized local Brian sprite. |
| [.assets/work/themes/familyguy/meg.png](.assets/work/themes/familyguy/meg.png) | created — normalized local Meg sprite. |
| [.assets/work/themes/familyguy/stewie.png](.assets/work/themes/familyguy/stewie.png) | created — normalized local Stewie sprite. |
| [.assets/work/themes/familyguy/chris.png](.assets/work/themes/familyguy/chris.png) | created — normalized local Chris sprite. |
| [.assets/work/build/familyguy/fonts/ClaudeStatusLineStickerst3-Regular.ttf](.assets/work/build/familyguy/fonts/ClaudeStatusLineStickerst3-Regular.ttf) | created — slot-9 Family Guy font. |
| [.assets/work/build/familyguy/cache/font_familyguy_peter.txt](.assets/work/build/familyguy/cache/font_familyguy_peter.txt) | created — Peter glyph cache. |
| [.assets/work/build/familyguy/cache/font_familyguy_quagmire.txt](.assets/work/build/familyguy/cache/font_familyguy_quagmire.txt) | created — Quagmire glyph cache. |
| [.assets/work/build/familyguy/cache/font_familyguy_brian.txt](.assets/work/build/familyguy/cache/font_familyguy_brian.txt) | created — Brian glyph cache. |
| [.assets/work/build/familyguy/cache/font_familyguy_meg.txt](.assets/work/build/familyguy/cache/font_familyguy_meg.txt) | created — Meg glyph cache. |
| [.assets/work/build/familyguy/cache/font_familyguy_stewie.txt](.assets/work/build/familyguy/cache/font_familyguy_stewie.txt) | created — Stewie glyph cache. |
| [.assets/work/build/familyguy/cache/font_familyguy_chris.txt](.assets/work/build/familyguy/cache/font_familyguy_chris.txt) | created — Chris glyph cache. |
| [.assets/work/build/familyguy/cache/manifest.json](.assets/work/build/familyguy/cache/manifest.json) | created — six-agent Family Guy manifest. |
| [.assets/work/build/familyguy/cache/probe.txt](.assets/work/build/familyguy/cache/probe.txt) | created — local build probe cache. |
| [.assets/work/build/familyguy/cache/probe_gray.png](.assets/work/build/familyguy/cache/probe_gray.png) | created — local build probe bitmap. |
<!-- /cumaru:touched -->

## Decisions made during implementation

- Used a temporary virtual environment with the existing Pillow plus `fonttools`, because the ambient interpreter lacked `fontTools`; no project or user installation command was run.
- Used `--force` for the local fetch so each work-theme PNG was freshly normalized from `.assets/familyguy/`.
- Extracted the `sbix` strike at ppem 58 to `/tmp/familyguy-t3-sbix.DxmxLR` for visual inspection; the temporary inspection files are outside the repository and build output.

## Commands run / verification

- `STICKERS_HOME="$PWD/.assets/work" python -m unittest discover -v tests` — passed, 3 tests.
- `STICKERS_HOME="$PWD/.assets/work" python -m claude_statusline_stickers.stickers fetch --theme familyguy --force` — passed; all six sources normalized to 256².
- `STICKERS_HOME="$PWD/.assets/work" STICKERS_VER=t3 python -m claude_statusline_stickers.stickers build --theme familyguy` — passed with `themes 1, agents 6, slots [familyguy=9]`.
- Font cmap verification — passed with `full=6`, codepoints U+F4108 through U+F4158, all inside slot 9.
- `sbix` extraction and visual inspection — passed; Peter, Quagmire, Brian, Meg, Stewie, and Chris each appear alone and correctly.
- Build artifact audit — passed; generated font/cache files are only under `.assets/work/build/familyguy/`.
- No `stickers install` command ran and no files were written under `~/Library/Fonts`, `~/.claude`, or settings.
- `cumaru doctor` — passed with 0 errors, 0 warnings, and 8 checks OK.

## Pending / follow-ups

- T4 remains the next task; do not advance it as part of this handoff.

## Suggestions for the Lead

- The six full glyphs use the slot-9 base with the expected full-sprite offset: U+F4108, U+F4118, U+F4128, U+F4138, U+F4148, and U+F4158.
