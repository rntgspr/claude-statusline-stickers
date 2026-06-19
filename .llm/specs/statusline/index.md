---
human_revised: false
generated: false
name: statusline
summary: Render the agent's sprite (resolved via the build manifest) into the Claude Code statusline
depends-on: []
relates: [font-build]
apps: [statusline]
deltas: [maintenance-all-themes-one-font, maintenance-cli-and-brew]
---

# Statusline

## Overview

`statusline/stickers-command.sh` is the consumer end. It composes the Claude Code statusline — current directory + git branch, then model + context-window usage + estimated cost — and below that the **agent's sprite**. The agent is the folder right above the project dir (`agentic-workspace/<agent>/<project>`); the script resolves it against `~/.claude/claude-statusline-stickers/manifest.json` (via `jq`) and `cat`s the matching `font_<theme>_<key>.txt`, which is plain Private-Use-Area glyph text and so survives the statusline's escape filter. The glyph font is fallback-only, so macOS resolves it for those PUA codepoints without changing the terminal's primary font.

Because every theme ships in one font (see [font-build](../font-build/)), the manifest covers all agents at once: switching agent switches the sprite with no reinstall.

## Requirements (EARS)

- WHEN rendering THE SYSTEM SHALL print the cwd and git branch, the model with context-window usage and cost, then the agent's sprite — dropping any segment whose input field is missing.
- WHEN resolving the sprite THE SYSTEM SHALL look up an agent name from both the project dir itself and the folder above it in `manifest.json` — the current dir winning on conflict — then cat that sprite's txt.
- WHEN the agent is absent from the manifest but the project sits under `agentic-workspace/` THE SYSTEM SHALL fall back to the pokéball; outside `agentic-workspace` it SHALL draw no sprite.
- WHEN `hideStickers` is true in any consulted `settings.json` THE SYSTEM SHALL omit the sprite.

## Decisions

- Real image protocols (iTerm2 OSC 1337, kitty, sixel, DECDHL) are stripped by Claude Code's escape filter; font glyphs are text, so they pass — this is why the whole font approach exists.
- Rendering requires ligatures ON in Warp and cell geometry matching the build (Anonymous Pro 20, line height 2.2).
- 2026-06-17: The statusline is theme-aware via the manifest (plan `maintenance-all-themes-one-font`) — replaced the hardcoded agent→dex table and the per-theme image/symbols modes.
- 2026-06-17: Renamed `statusline-command.sh` → `stickers-command.sh`, installed by `stickers install` to `~/.claude/`; the hide toggle is `hideStickers` (plan `maintenance-cli-and-brew`).
- 2026-06-18: Agent name resolves from the project dir itself first, then its parent dir — the current dir wins on conflict (was: parent dir only).

## Files

- `claude_statusline_stickers/statusline/stickers-command.sh` — resolves the agent via `manifest.json` and cats the sprite's glyph text. Installed to `~/.claude/stickers-command.sh`.
