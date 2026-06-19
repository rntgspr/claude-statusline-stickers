"""Build configuration: paths, geometry dials, codepoint layout.

Every value here is a tuning knob or a path — no theme content. A theme (sprite
set + source URLs) lives in <package>/themes/<name>/theme.json and is loaded by
theme.py. Read-only data (theme.json, the statusline script) ships inside the
package; read-write work (fetched PNGs, the local build) goes under STICKERS_HOME,
so the CLI behaves the same run from a clone or installed via pip/brew. The
geometry dials are documented in README.md; changing them needs a rebuild and a
terminal whose cell metrics match. Pixel/units math lives in geometry.py.
"""
import os
import time
from pathlib import Path

# --- package (read-only, shipped) --------------------------------------------
PACKAGE = Path(__file__).parent
# Bundled theme definitions (theme.json per theme) and the statusline script are
# included in the wheel and never written to at runtime.
BUNDLED_THEMES = PACKAGE / "themes"
BUNDLED_STATUSLINE = PACKAGE / "statusline" / "stickers-command.sh"

# --- work dir (read-write) ---------------------------------------------------
# Fetched sprite PNGs and the local build land here, so an installed (read-only)
# package never writes next to its code. Override with the STICKERS_HOME env var.
STICKERS_HOME = Path(os.environ.get("STICKERS_HOME") or Path.home() / ".cache/claude-statusline-stickers")
# Where fetch writes PNGs and where a user may drop a theme.json to override or
# add a theme. The build reads PNGs from here.
WORK_THEMES = STICKERS_HOME / "themes"
# Fetched sprites are normalized to IMAGE_SIZE×IMAGE_SIZE (contain-fit, no
# distortion, transparent pad), so every theme feeds the build uniform inputs.
IMAGE_SIZE = 256
# The skeleton font is read from the system font dir — it sizes the cells our
# fallback glyphs are drawn into, and must match the terminal's primary font;
# no glyph of it is shown.
SKELETON_DIR = Path.home() / "Library/Fonts"
SKELETON = "Anonymous Pro Minus.ttf"

# --- local build output (build.py writes here; nothing live) -----------------
# build/all/{fonts,cache} for the combined font, build/<theme>/ for one theme.
# install.py later copies each artifact to its live destination below.
BUILD_DIR = STICKERS_HOME / "build"

# --- live install destinations (used only by install.py) ---------------------
INSTALL_FONTS = Path.home() / "Library/Fonts"
INSTALL_CACHE = Path.home() / ".claude/claude-statusline-stickers"
# The statusline script is copied here; settings.json points Claude Code at it.
INSTALL_STATUSLINE = Path.home() / ".claude/stickers-command.sh"
# Claude Code's user settings — install wires its statusLine.command here.
SETTINGS_JSON = Path.home() / ".claude/settings.json"

# Generated font family — fixed across themes. All themes share one PUA codepoint
# space, resolved per agent via the manifest, so a single family name lets the
# terminal select it once; switching agent is just a manifest lookup. VER still
# versions each build to dodge stale font caches.
FAMILY = "ClaudeStatusLineStickers"
FAMILY_DISPLAY = "ClaudeStatusLineStickers"

# Matches every build of this family — used to purge prior builds both locally
# (build dir, before saving) and live (install, before copying).
FONT_GLOB = f"{FAMILY}*-Regular.ttf"

# --- cell geometry -----------------------------------------------------------
STRIKE_PX = 128      # sbix strike resolution basis (px): ppem = upem * STRIKE_PX / cell_h
CELL_SCALE_Y = 2.20  # vertical spacing — Warp: Anonymous Pro 20, LineHeight 2.2
SPLIT = 0.5          # fraction of extra vertical space assumed BELOW the box

# --- codepoint layout --------------------------------------------------------
CP_BASE = 0xF1D00    # first codepoint candidate for the sprite block
CP_STRIDE = 0x140    # codepoints reserved per sprite (icon + full glyph + headroom)
SPRITE_CP_OFF = 0x110  # offset of the single-glyph full sprite within a block

# --- single-glyph full sprite ------------------------------------------------
# The whole sprite is ONE glyph — Warp renders ink ~28 cells right and 7 up of
# the anchor without clipping. Ink LEFT of the anchor is clipped → extend right.
SPRITE_ANCHOR_CELLS = 0     # transparent cells left of the anchor (0 = none)
SPRITE_BOX_PX = (506, 510)  # raw-pixel box the trimmed art is contain-fit into

# Version tag baked into family name + filename on every build, so a renderer
# can never serve stale glyphs for a family it has never seen. STICKERS_VER
# overrides it for reproducible builds (used by the regression harness); unset
# in production → wall-clock timestamp.
VER = os.environ.get("STICKERS_VER") or time.strftime("%H%M%S")

# Built font naming — the skeleton family is renamed to this fixed, versioned
# family (VER busts stale font caches). One font ships all themes, so naming
# does not depend on the theme.
OUT_NAME = f"{FAMILY}{VER}-Regular.ttf"
RENAMES = [
    ("Anonymous Pro Minus", f"{FAMILY_DISPLAY} {VER}"),
    ("AnonymousProMinus", f"{FAMILY}{VER}"),
]
