#!/usr/bin/env python3
"""`stickers` command-line entry point: fetch · build · install · probe.

A thin dispatcher — each subcommand calls the matching module's run() in this
package (the actual work lives there, so it stays importable and testable).
Run `stickers <command> --help` for options.
"""
import argparse

from . import build, fetch, install
from .config import INSTALL_CACHE


def _probe():
    """Print the installed ruler probe — a calibration aid for sizing glyphs."""
    path = INSTALL_CACHE / "probe.txt"
    if not path.is_file():
        raise SystemExit("no probe.txt installed yet — run `stickers install` first")
    print(path.read_text(), end="")


def main(argv=None):
    """Parse arguments and dispatch to the chosen subcommand."""
    parser = argparse.ArgumentParser(
        prog="stickers",
        description="Themed sprite-glyph font for the Claude Code statusline.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --theme is shared by the pipeline stages: omit it to act on every theme.
    themed = argparse.ArgumentParser(add_help=False)
    themed.add_argument("--theme", metavar="NAME",
                        help="act on a single theme (default: every theme)")

    p_fetch = sub.add_parser("fetch", parents=[themed],
                             help="download + normalize each theme's sprite PNGs")
    p_fetch.add_argument("--force", action="store_true",
                         help="re-download even if the PNG already exists")
    sub.add_parser("build", parents=[themed],
                   help="pack themes into the glyph font under the work dir")
    p_install = sub.add_parser("install", parents=[themed],
                               help="copy the build live: font, cache, statusline, settings.json")
    p_install.add_argument("--no-settings", action="store_true",
                           help="don't touch ~/.claude/settings.json")
    sub.add_parser("probe", help="print the installed terminal ruler probe")

    args = parser.parse_args(argv)
    if args.command == "fetch":
        fetch.run(theme=args.theme, force=args.force)
    elif args.command == "build":
        build.run(theme=args.theme)
    elif args.command == "install":
        install.run(theme=args.theme, link=not args.no_settings)
    elif args.command == "probe":
        _probe()


if __name__ == "__main__":
    main()
