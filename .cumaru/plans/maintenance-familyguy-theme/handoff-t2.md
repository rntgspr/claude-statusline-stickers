---
human_revised: false
plan: maintenance-familyguy-theme
task: T2
status: complete
date: 2026-09-04
summary: Added exclusive URL-or-path sprite loading, local path fetch normalization, and the ignored Family Guy theme manifest.
---

# Hand-off — maintenance-familyguy-theme / T2

## Files touched

<!-- cumaru:touched -->
- `claude_statusline_stickers/theme.py` — modified (validates each sprite's exclusive URL-or-path source).
- `claude_statusline_stickers/fetch.py` — modified (normalizes local path sources through the existing save pipeline and reports contextual errors).
- `tests/test_theme.py` — created (covers URL/path source exclusivity).
- `tests/test_fetch.py` — created (covers home expansion and local-image normalization).
- `.assets/work/themes/familyguy/theme.json` — created (ignored six-sprite Family Guy manifest at slot 9).
<!-- /cumaru:touched -->

## Decisions made during implementation

- A sprite manifest must declare exactly one non-empty source, `url` or `path`.
- Local paths use `Path.expanduser()` and resolve relative to the current working directory, then use the same normalization and save path as URL sources.
- Source errors include the theme name, sprite name, and invalid source value.
- The local Family Guy manifest uses slot `9`, six sprite entries, and `.assets/familyguy/<key>.png` paths.
- Tests use the standard-library `unittest` runner because this environment does not provide `pytest`; a temporary virtual environment supplied the existing `fonttools` dependency for the fetch test.
- No T3 build/config changes were made.

## Commands run / verification

The required TDD red run was observed before the production changes: the theme test failed because `Sprite` had no `path` field and invalid source shapes were accepted; the fetch test reported the expected missing local PNG path. After the implementation, this fresh command passed:

```text
T2_VENV=$(mktemp -d /tmp/familyguy-t2-venv.XXXXXX)
python3 -m venv --system-site-packages "$T2_VENV"
"$T2_VENV/bin/pip" install -q fonttools
"$T2_VENV/bin/python" -m unittest discover -v tests
...
Ran 3 tests in ...s

OK
```

The local manifest loads as `familyguy`, slot `9`, with six sprites. The complete theme scan reports `86` agent names across `9` slots and no duplicate slot or agent-name collisions. `git diff --check` passed.

`cumaru doctor` — passed with 0 errors, 0 warnings, and 8 checks OK.

## Pending / follow-ups

- Lead should mark T2 done in the plan DAG.
- T3 remains the next task; do not start it as part of this handoff.

## Suggestions for the Lead

- Local, ignored manifests can use the same `Theme` discovery path as bundled manifests when `STICKERS_HOME` points at `.assets/work`.
