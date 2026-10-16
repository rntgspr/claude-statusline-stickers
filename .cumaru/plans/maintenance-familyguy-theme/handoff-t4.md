---
human_revised: false
plan: maintenance-familyguy-theme
task: T4
status: complete
date: 2026-09-04
summary: Documented the exclusive URL-or-path source contract and local Family Guy work-directory workflow in README.
---

# Hand-off — maintenance-familyguy-theme / T4

## Files touched

<!-- cumaru:touched -->
| Link | Description |
| --- | --- |
| [README.md](README.md) | modified — documents URL/path sources, path resolution, normalization, and the ignored local Family Guy example. |
<!-- /cumaru:touched -->

## Decisions made during implementation

- Kept Family Guy out of the bundled-theme list; the example is explicitly a work-directory override/local theme.
- Replaced the old “no URL means pre-populated PNG” wording with the exclusive `url`/`path` contract so the README matches the implemented loader.
- Did not edit `.cumaru/specs/`; the Lead owns the planned T5 spec reconciliation.

## Commands run / verification

- README content audit — passed; the document includes exactly-one `url`/`path`, `Path.expanduser()`, cwd-relative resolution, `.assets/familyguy/meg.png`, `.assets/work/themes/familyguy/theme.json`, and `STICKERS_HOME="$PWD/.assets/work"` commands.
- Bundled-theme wording audit — passed; the bundled list remains the eight existing themes and does not include Family Guy.
- `python -m unittest discover -v tests` in the T3 temporary dependency environment — passed, 3 tests.
- `cumaru tree plans` — passed; the plan remains discoverable with T4 done and T5 pending.
- `cumaru doctor` — passed with 0 errors, 0 warnings, and 8 checks OK.
- No git add/commit/push and no T5 work performed.

## Pending / follow-ups

- T5 remains the next task: reconcile the path-backed source contract into the themes spec.

## Suggestions for the Lead

- The README now treats `theme.json` as the single source of truth for either remote URLs or cwd-relative local paths; keep the spec update aligned with that wording.
