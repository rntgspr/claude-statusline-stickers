#!/usr/bin/env python3
"""Build a themed glyph font (build stage).

With no theme selected, builds EVERY theme into ONE font — each theme at a
distinct PUA codepoint range — and writes a manifest mapping each sprite's
agentNames to its glyph text, so the statusline can show any agent's sprite
without reinstalling. With a theme selected, builds only that theme.

Output is local under BUILD_DIR (build/all/ for the combined font,
build/<theme>/ for a single theme); install.py applies it. Per sprite the build
emits an icon glyph and the whole-sprite glyph — bitmaps are sbix colour with a
traced-outline fallback. Orchestrated by the `stickers build` CLI subcommand.
"""
import json
import os

from fontTools.ttLib import TTFont
from PIL import Image

from . import renderers
from .codepoints import CodepointLayout, find_free_base
from .config import (
    BUILD_DIR,
    CP_STRIDE,
    FONT_GLOB,
    OUT_NAME,
    RENAMES,
    SKELETON,
    SKELETON_DIR,
)
from .fontcanvas import FontCanvas
from .geometry import CellMetrics
from .theme import Theme

_SUFFIX = "-Regular.ttf"


def build(themes, out_fonts, out_cache):
    """Build the given themes into one font + per-sprite txt + a manifest."""
    font = TTFont(SKELETON_DIR / SKELETON)
    metrics = CellMetrics.from_font(font)
    canvas = FontCanvas(font, metrics)
    out_cache.mkdir(parents=True, exist_ok=True)

    # one contiguous region: a leading block for the probes, then one
    # (sprites + blank) block per theme
    total = CP_STRIDE + sum((len(t.sprites) + 1) * CP_STRIDE for t in themes)
    base = find_free_base(font, total)
    cursor = base

    # probes once, in their own block
    probe_layout = CodepointLayout(cursor, 0)
    renderers.add_blank(canvas, probe_layout, glyph="sprite.blank")
    renderers.render_probes(canvas, probe_layout, cache_dir=out_cache)
    cursor += CP_STRIDE

    manifest = {"family": OUT_NAME[: -len(_SUFFIX)], "agents": {}, "themes": {}}
    for theme in themes:
        layout = CodepointLayout(cursor, len(theme.sprites))
        cursor += (len(theme.sprites) + 1) * CP_STRIDE
        renderers.add_blank(canvas, layout, glyph=f"sprite.{theme.name}.blank")

        keys = []
        for i, sprite in enumerate(theme.sprites):
            image = Image.open(theme.images_dir / f"{sprite.key}.png").convert("RGBA")
            gname = f"{theme.name}.{sprite.name}"

            icon = renderers.render_icon(canvas, layout, i, gname, image)
            if theme.emoji_probe and theme.emoji_probe[1] == sprite.name:
                canvas.map_cp(theme.emoji_probe[0], icon)

            lines = renderers.render_sprite_full(canvas, layout, i, gname, image)
            txt = f"font_{theme.name}_{sprite.key}.txt"
            (out_cache / txt).write_text("\n".join(lines) + "\n")

            keys.append(sprite.key)
            for agent in sprite.agent_names:
                if agent in manifest["agents"]:
                    other = manifest["agents"][agent]["theme"]
                    raise SystemExit(
                        f"agentName collision: {agent!r} claimed by both "
                        f"{other!r} and {theme.name!r}"
                    )
                manifest["agents"][agent] = {"theme": theme.name, "key": sprite.key, "txt": txt}
        manifest["themes"][theme.name] = keys

    canvas.finalize(out_fonts, OUT_NAME, RENAMES, purge=FONT_GLOB)
    (out_cache / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    print(
        f"saved: {out_fonts.parent.name}/{OUT_NAME}  "
        f"themes {len(themes)}, agents {len(manifest['agents'])}, base U+{base:05X}"
    )
    return manifest


def run(theme=None):
    """Build the selected theme, or every theme into one font when none is set."""
    selected = theme or os.environ.get("STICKERS_THEME")
    if selected:
        t = Theme.load(selected)
        build([t], t.build_fonts, t.build_cache)
    else:
        themes = Theme.discover()
        build(themes, BUILD_DIR / "all" / "fonts", BUILD_DIR / "all" / "cache")


if __name__ == "__main__":
    run()
