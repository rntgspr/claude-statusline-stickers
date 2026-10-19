import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from claude_statusline_stickers import fetch as fetch_module
from claude_statusline_stickers import theme as theme_module


def write_local_theme(root, path):
    """Write a one-sprite local theme manifest for a fetch test."""
    folder = root / "local"
    folder.mkdir(parents=True)
    (folder / "theme.json").write_text(
        json.dumps(
            {
                "name": "local",
                "sprites": [
                    {"name": "sprite", "key": "sprite", "path": path},
                ],
            }
        )
    )


class FetchTests(unittest.TestCase):
    """Verify local sprite ingestion uses the normal fetch pipeline."""

    def test_fetch_path_expands_home_and_normalizes(self):
        """Fetch a home-relative local sprite into the normalized work theme folder."""
        with tempfile.TemporaryDirectory() as directory:
            tmp_path = Path(directory)
            work = tmp_path / "work"
            source = tmp_path / "sprite.png"
            Image.new("RGBA", (2, 1), (20, 40, 60, 128)).save(source)
            with patch.dict(os.environ, {"HOME": str(tmp_path)}):
                with patch.object(theme_module, "WORK_THEMES", work / "themes"):
                    write_local_theme(work / "themes", "~/sprite.png")
                    fetch_module.run("local")

            result = Image.open(work / "themes" / "local" / "sprite.png").convert("RGBA")
            self.assertEqual(result.size, (256, 256))
            self.assertLess(result.getchannel("A").getextrema()[0], 255)
