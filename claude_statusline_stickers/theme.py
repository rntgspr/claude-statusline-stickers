"""Theme loading: a theme is a self-contained folder of sprites + font config.

Each theme is themes/<name>/ — a theme.json (sprite list: name, cache key,
optional source URL, optional agentNames; plus an optional emoji probe) and the
sprite PNGs. theme.json ships in the package (read-only); the PNGs live in the
work dir, fetched there. The active theme is chosen by STICKERS_THEME (default
"pokemon"); building with no theme set builds every theme into one font. The
font family name is fixed (config.FAMILY), shared by all.
"""
import json
import os
from dataclasses import dataclass
from typing import Optional

from .config import BUILD_DIR, BUNDLED_THEMES, WORK_THEMES


@dataclass(frozen=True)
class Sprite:
    """One sprite: display name, cache key, optional source URL, and the agent
    names that should display it in the statusline."""

    name: str
    key: str
    url: Optional[str] = None      # None → user-supplied local PNG (no fetch)
    agent_names: tuple = ()        # workspace/agent names that map to this sprite


@dataclass(frozen=True)
class Theme:
    """A named sprite set rendered into the (fixed-family) glyph font."""

    name: str
    sprites: tuple         # tuple[Sprite, ...]
    emoji_probe: Optional[tuple] = None  # (codepoint:int, sprite_name:str) or None

    @classmethod
    def _theme_json(cls, name):
        """Locate a theme's theme.json — a user override in the work dir wins
        over the definition bundled in the package."""
        for base in (WORK_THEMES, BUNDLED_THEMES):
            path = base / name / "theme.json"
            if path.is_file():
                return path
        raise FileNotFoundError(f"no theme.json for theme {name!r}")

    @classmethod
    def load(cls, name=None):
        """Load <name>/theme.json (or STICKERS_THEME, default "pokemon")."""
        name = name or os.environ.get("STICKERS_THEME") or "pokemon"
        data = json.loads(cls._theme_json(name).read_text())

        sprites = tuple(
            Sprite(
                name=s["name"],
                key=s["key"],
                url=s.get("url"),
                agent_names=tuple(s.get("agentNames", [])),
            )
            for s in data["sprites"]
        )
        probe = data.get("emoji_probe")
        emoji_probe = (int(probe["codepoint"], 16), probe["sprite"]) if probe else None

        return cls(name=data["name"], sprites=sprites, emoji_probe=emoji_probe)

    @classmethod
    def discover(cls):
        """Load every theme (alphabetical) — bundled themes plus any the user
        added under the work dir."""
        names = set()
        for base in (BUNDLED_THEMES, WORK_THEMES):
            if base.is_dir():
                names |= {d.name for d in base.iterdir() if (d / "theme.json").is_file()}
        return [cls.load(n) for n in sorted(names)]

    # --- per-theme paths (PNGs in the work dir, single-theme build output) ---

    @property
    def images_dir(self):
        """The theme's working folder — where the sprite PNGs are fetched."""
        return WORK_THEMES / self.name

    @property
    def build_fonts(self):
        """Local dir a single-theme build writes its font to."""
        return BUILD_DIR / self.name / "fonts"

    @property
    def build_cache(self):
        """Local dir a single-theme build writes its statusline files to."""
        return BUILD_DIR / self.name / "cache"
