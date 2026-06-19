#!/usr/bin/env python3
"""Download sprite PNGs into each theme's work folder, normalized to 256².

By default fetches EVERY theme; a theme name fetches just one. Each sprite is
pulled from its URL and normalized to IMAGE_SIZE×IMAGE_SIZE (contain-fit, no
distortion) into the work dir (config.WORK_THEMES/<theme>/) for build.py.
Idempotent: existing files are skipped unless force is set. Orchestrated by the
`stickers fetch` CLI subcommand.
"""
import io
import os
import urllib.request

from PIL import Image

from .config import IMAGE_SIZE
from .imaging import normalize
from .theme import Theme

# A browser-ish UA — some sprite CDNs reject the default urllib agent.
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) claude-statusline-stickers/1.0"


def fetch(sprite, dest_dir, force=False):
    """Download <key>.png, normalize to IMAGE_SIZE², and save.

    A sprite with no url is user-supplied — its PNG must already sit in the
    theme folder, so fetch leaves it untouched.
    """
    dest = dest_dir / f"{sprite.key}.png"
    if sprite.url is None:
        return "local PNG (no url)" if dest.exists() else "MISSING — no url and no local PNG"
    if dest.exists() and not force:
        return "skip (exists)"

    req = urllib.request.Request(sprite.url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
    img = Image.open(io.BytesIO(data))
    src = f"{img.width}x{img.height}"
    normalize(img, IMAGE_SIZE).save(dest)
    return f"{src} -> {IMAGE_SIZE}^2"


def run(theme=None, force=False):
    """Fetch + normalize sprites: every theme by default, or one theme."""
    selected = theme or os.environ.get("STICKERS_THEME")
    themes = [Theme.load(selected)] if selected else Theme.discover()
    for th in themes:
        th.images_dir.mkdir(parents=True, exist_ok=True)
        print(f"theme: {th.name}  ->  {th.images_dir}")
        for sprite in th.sprites:
            print(f"  {sprite.key:12s} {sprite.name:12s} {fetch(sprite, th.images_dir, force)}")


if __name__ == "__main__":
    run()
