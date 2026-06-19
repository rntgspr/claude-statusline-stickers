---
human_revised: false
generated: false
name: install
summary: Apply a local build to the live font + cache + statusline; all themes ship in one font
depends-on: [font-build]
relates: [themes]
apps: [engine]
deltas: [maintenance-all-themes-one-font, maintenance-cli-and-brew]
---

# Install

## Overview

`stickers install` (module `install.py`) is the only step that mutates the live system. [font-build](../font-build/) writes everything under `$STICKERS_HOME/build/`; install copies that into the live directories — the font to `~/Library/Fonts`, the statusline text/probe/manifest files to `~/.claude/claude-statusline-stickers`, and the statusline script to `~/.claude/stickers-command.sh`, then points Claude Code's `settings.json` `statusLine.command` at that script — purging the prior font and the prior cache outputs first, so the live state reflects exactly the current build.

By default the build combines **every theme into one font** (`build/all/`), so a single install ships all themes and the statusline switches sprite per agent with no reinstall. A single-theme build (`--theme <name>` / `STICKERS_THEME` → `build/<name>/`) installs just that one. Either way the family is the fixed `ClaudeStatusLineStickers<VER>`; the `VER` busts stale font caches, and the font is fallback-only (resolved via its PUA codepoints, never selected as the primary).

## Requirements (EARS)

- WHEN install runs without a theme THE SYSTEM SHALL install `build/all/`; WHEN `--theme`/`STICKERS_THEME` is set, the matching `build/<name>/`.
- WHEN installing THE SYSTEM SHALL copy the font to `~/Library/Fonts`, the cache files (`font_*.txt`, `manifest.json`, probes) to `~/.claude/claude-statusline-stickers`, and the statusline script to `~/.claude/stickers-command.sh`.
- WHEN installing THE SYSTEM SHALL point `~/.claude/settings.json`'s `statusLine.command` at the installed script — backing the file up, preserving every other key, and printing the line instead if it is not valid JSON; `--no-settings` skips this.
- WHEN installing THE SYSTEM SHALL purge prior `ClaudeStatusLineStickers*` fonts and prior build outputs from the cache first.
- IF nothing has been built for the requested target THE SYSTEM SHALL abort with an error.
- WHILE building THE SYSTEM SHALL never write under `~/` — only install does.

## Decisions

- 2026-06-16: Build and install separated — the build is side-effect-free w.r.t. `~/`, with install as the single mutating step.
- 2026-06-17: All themes build into ONE font at distinct codepoint ranges (plan `maintenance-all-themes-one-font`) — replaced the earlier "one theme installed at a time". The statusline picks the agent's sprite from the manifest, so there is no per-theme reinstall.
- 2026-06-17: Fixed family `ClaudeStatusLineStickers` across all themes.
- 2026-06-17: Packaged as a CLI (plan `maintenance-cli-and-brew`) — install is `stickers install` → `install.run()`; it now also copies the statusline script. Read-write work lives under `STICKERS_HOME` (default `~/.cache/claude-statusline-stickers`); the live cache is `~/.claude/claude-statusline-stickers`.
- 2026-06-18: `stickers install` wires `~/.claude/settings.json` (`statusLine.command`) by default — backup to `settings.json.bak`, other keys preserved, idempotent, `--no-settings` to opt out. Closes the manual-edit gap that silently left the old script active.

## Files

- `claude_statusline_stickers/install.py` — `run(link=True)`: purge prior font + cache outputs, copy the build live, install the statusline script, wire settings.json (`_link_statusline`).
- `claude_statusline_stickers/config.py` — `INSTALL_FONTS`, `INSTALL_CACHE`, `INSTALL_STATUSLINE`, `SETTINGS_JSON`, `FONT_GLOB`, `FAMILY`.
- `claude_statusline_stickers/stickers.py` — the `stickers install` subcommand (`--no-settings`).
