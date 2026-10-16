---
human_revised: false
plan: maintenance-familyguy-theme
task: T5
status: complete
date: 2026-09-04
summary: Verified the Lead-authored themes spec against the implemented URL-or-path contract and completed the plan acceptance evidence.
---

# Hand-off — maintenance-familyguy-theme / T5

## Files touched

<!-- cumaru:touched -->
| Link | Description |
| --- | --- |
<!-- No repository files were changed by Dev; the themes spec was audited read-only. -->
<!-- /cumaru:touched -->

## Decisions made during implementation

- T5 was verified against the Lead-authored `.cumaru/specs/themes/index.md`; Dev did not edit the spec.
- The spec keeps Family Guy out of the bundled-theme list and records the local ignored-asset workflow as a decision.
- The plan remains unarchived as requested. `delta-draft.md` records the spec change for the later archive flow.

## Commands run / verification

- Read-only spec audit — PASS: the spec requires exactly one `url` or `path`, documents leading `~` expansion, cwd-relative local paths, and normalization by `fetch`; its current bundled-theme list contains only the eight existing themes and no Family Guy.
- `STICKERS_HOME="$PWD/.assets/work" python -m unittest discover -v tests` — PASS, 3 tests.
- `STICKERS_HOME="$PWD/.assets/work" python -m claude_statusline_stickers.stickers fetch --theme familyguy --force` — PASS; six local sources normalized to 256².
- `STICKERS_HOME="$PWD/.assets/work" STICKERS_VER=final python -m claude_statusline_stickers.stickers build --theme familyguy` — PASS; `themes 1, agents 6, slots [familyguy=9]`.
- Manifest/theme audit — PASS: six sprites, slot 9, six agent names, and all source/work PNGs have real transparency (`alpha` minimum below 255).
- Global uniqueness audit — PASS: 9 themes, 9 unique slots, 86 unique agent names.
- `git check-ignore` — PASS for `.assets/` and all source/work PNGs.
- Font cmap audit — PASS: six `.full` glyphs in U+F4108–U+F4158, all within slot 9.
- Fresh `sbix` extraction and visual inspection — PASS: Peter, Quagmire, Brian, Meg, Stewie, and Chris each appear alone and correctly.
- Rebuilt with `STICKERS_VER=t3` after the final audit to retain the previously recorded T3 font path; cmap/manifest checks remained PASS.
- Build output audit — PASS: `.assets/work/build` contains only `familyguy`, with font/cache artifacts under `.assets/work/build/familyguy/`.
- No `stickers install` command ran; no writes were made to `~/Library/Fonts`, `~/.claude`, or settings.
- `cumaru tree plans` — PASS; all T1–T5 are done and the plan remains discoverable.
- `cumaru doctor` — PASS with 0 errors, 0 warnings, and 8 checks OK.

## Pending / follow-ups

- None for the implementation plan. Archive remains intentionally out of scope for this turn.

## Suggestions for the Lead

- Validate `delta-draft.md` during the archive flow and absorb its URL/path requirements into the durable themes spec history.
