#!/usr/bin/env python3
"""Apply a local build to the live font + cache + statusline (install stage).

build.py writes under BUILD_DIR (build/all/ for the combined all-themes font,
build/<theme>/ for a single theme); this copies it live: the font to
~/Library/Fonts (purging prior ClaudeStatusLineStickers* builds), the statusline
files (font_*.txt, manifest.json, probes) to ~/.claude/claude-statusline-stickers
(cleared first), and the statusline script to ~/.claude/stickers-command.sh —
then points Claude Code's settings.json at that script. Orchestrated by the
`stickers install` CLI subcommand.
"""
import json
import os
import shutil

from .config import (
    BUILD_DIR,
    BUNDLED_STATUSLINE,
    FONT_GLOB,
    INSTALL_CACHE,
    INSTALL_FONTS,
    INSTALL_STATUSLINE,
    SETTINGS_JSON,
)
from .theme import Theme

# Build outputs to clear from the live cache before copying the new ones.
CACHE_GLOBS = ("font_*.txt", "manifest.json", "probe.txt", "probe_gray.png")


def _link_statusline():
    """Point ~/.claude/settings.json's statusLine at the installed script.

    Backs the file up first and preserves every other key. If it is not valid
    JSON, prints the line to add by hand rather than risk corrupting it.
    """
    desired = f"bash {INSTALL_STATUSLINE}"
    SETTINGS_JSON.parent.mkdir(parents=True, exist_ok=True)

    data = {}
    if SETTINGS_JSON.is_file():
        shutil.copy2(SETTINGS_JSON, str(SETTINGS_JSON) + ".bak")
        try:
            data = json.loads(SETTINGS_JSON.read_text() or "{}")
        except json.JSONDecodeError:
            print(f"  ! {SETTINGS_JSON} is not valid JSON — add this by hand:")
            print(f'      "statusLine": {{ "type": "command", "command": "{desired}" }}')
            return

    was = (data.get("statusLine") or {}).get("command")
    data["statusLine"] = {"type": "command", "command": desired}
    SETTINGS_JSON.write_text(json.dumps(data, indent=2) + "\n")
    suffix = "" if was == desired else f" (was: {was or 'unset'})"
    print(f"  settings.json -> statusLine wired{suffix}")


def run(theme=None, link=True):
    """Install build/all (or one theme's build) into the live dirs."""
    selected = theme or os.environ.get("STICKERS_THEME")
    src = Theme.load(selected).build_fonts.parent if selected else BUILD_DIR / "all"
    label = selected or "all"

    fonts, cache = src / "fonts", src / "cache"
    if not fonts.is_dir() or not cache.is_dir():
        raise SystemExit(f"nothing built for {label!r} — run `stickers build` first")

    print(f"installing: {label}")
    INSTALL_FONTS.mkdir(parents=True, exist_ok=True)
    for old in INSTALL_FONTS.glob(FONT_GLOB):
        old.unlink()
        print(f"  purged {old.name}")
    for ttf in sorted(fonts.glob("*.ttf")):
        shutil.copy2(ttf, INSTALL_FONTS / ttf.name)
        print(f"  font  -> {INSTALL_FONTS / ttf.name}")

    INSTALL_CACHE.mkdir(parents=True, exist_ok=True)
    for pat in CACHE_GLOBS:
        for old in INSTALL_CACHE.glob(pat):
            old.unlink()
    n = 0
    for art in sorted(p for p in cache.iterdir() if p.is_file()):
        shutil.copy2(art, INSTALL_CACHE / art.name)
        n += 1
    print(f"  cache -> {INSTALL_CACHE}  ({n} files)")

    INSTALL_STATUSLINE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BUNDLED_STATUSLINE, INSTALL_STATUSLINE)
    print(f"  statusline -> {INSTALL_STATUSLINE}")

    if link:
        _link_statusline()
    else:
        print(f'  → wire it up by hand: "statusLine": {{ "type": "command", "command": "bash {INSTALL_STATUSLINE}" }}')

    print("  done — Cmd+Q the terminal to load the new font; the sticker shows in dirs named after an agent.")


if __name__ == "__main__":
    run()
