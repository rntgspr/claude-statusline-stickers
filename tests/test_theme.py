import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from claude_statusline_stickers import theme as theme_module


def write_theme(root, name, sprites):
    """Write a minimal work theme manifest for a loader test."""
    folder = root / name
    folder.mkdir(parents=True)
    (folder / "theme.json").write_text(json.dumps({"name": name, "sprites": sprites}))


class ThemeTests(unittest.TestCase):
    """Verify theme source contract validation and loading."""

    def test_sprite_accepts_exactly_one_url_or_path(self):
        """Load a sprite manifest with either supported source field."""
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory) / "work"
            write_theme(
                work,
                "sources",
                [
                    {"name": "remote", "key": "remote", "url": "https://example.test/a.png"},
                    {"name": "local", "key": "local", "path": "sprite.png"},
                ],
            )
            with patch.object(theme_module, "WORK_THEMES", work):
                sprites = theme_module.Theme.load("sources").sprites

            self.assertEqual(sprites[0].url, "https://example.test/a.png")
            self.assertIsNone(sprites[0].path)
            self.assertIsNone(sprites[1].url)
            self.assertEqual(sprites[1].path, "sprite.png")

    def test_sprite_rejects_invalid_source_shapes(self):
        """Reject zero or multiple source fields using named context."""
        for source in ({}, {"url": "https://example.test/a.png", "path": "sprite.png"}):
            with self.subTest(source=source), tempfile.TemporaryDirectory() as directory:
                work = Path(directory) / "work"
                write_theme(
                    work,
                    "bad-theme",
                    [{"name": "bad-sprite", "key": "bad", **source}],
                )
                with patch.object(theme_module, "WORK_THEMES", work):
                    with self.assertRaisesRegex(ValueError, "bad-theme.*bad-sprite.*url.*path"):
                        theme_module.Theme.load("bad-theme")
