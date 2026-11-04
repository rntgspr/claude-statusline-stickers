#!/usr/bin/env bash
# Install the `stickers` CLI from this checkout in editable mode via pipx, so
# every change in the repo (git pull included) is live without reinstalling.
# Re-run only when dependencies or pyproject.toml change.
set -euo pipefail

# Resolve the repo root from the script location, so it works from any cwd.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v pipx >/dev/null 2>&1; then
  echo "pipx not found. Install it first: brew install pipx" >&2
  exit 1
fi

# --force replaces any previous (non-editable) install of the same package.
pipx install --force --editable "$ROOT"

# Smoke test: the command resolves and points at this checkout.
hash -r
echo
echo "stickers -> $(command -v stickers)"
stickers --help | head -1
