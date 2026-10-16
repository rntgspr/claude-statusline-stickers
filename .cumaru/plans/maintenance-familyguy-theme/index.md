---
human_revised: false
scope:
  - themes
  - install
status: in-progress
summary: Add a local, ignored Family Guy theme backed by an exclusive url-or-path sprite source contract, then build and install it alongside the bundled themes
targets: [themes, engine]
aux: []
---

# Local Family Guy theme via url-or-path sprite sources

> **Reconstructed.** The original `index.md` and `t1.md`..`t4.md` were never
> committed and could not be recovered. This index was rebuilt during the v9
> framework migration from `delta-draft.md`, `t5.md`..`t7.md`, and every
> `handoff-t<N>.md` in this directory. Review before archiving.

## Overview

Sprites used to be fetched from a URL only; a sprite without a `url` was
treated as a user-supplied PNG left in place. This plan replaces that implicit
rule with an explicit, exclusive source per sprite: `url` **or** `path`. A
path-backed sprite is expanded (`~`), resolved from the working directory, and
normalized through the same pipeline as URL sources. The motivating consumer is
a local Family Guy theme (slot 9) whose art lives under the ignored `.assets/`
tree and is never bundled.

## Acceptance Criteria (EARS / RFC 2119)

See `delta-draft.md` — its Added / Modified / Removed requirements for
`specs/themes/` are the acceptance contract of this plan.

## Plan / DAG

- T1 — Download and visually verify six transparent Family Guy PNGs into `.assets/familyguy/`.
- T2 — Exclusive url-or-path loading in `theme.py` / `fetch.py`, tests, and the ignored `.assets/work/themes/familyguy/theme.json` (slot 9).
- T3 — Fetch the local sprites and build the slot-9 font under the ignored work assets.
- T4 — Document the url-or-path contract and the local Family Guy workflow in `README.md`.
- T5 — Reconcile `specs/themes/` with the implemented contract.
- T6 — Build and install the single-theme Family Guy font live.
- T7 — Replace T6's single-theme install with one combined all-themes build and install.

All tasks are complete; the plan is pending the archive flow.

## Out of scope

- Bundling Family Guy: it stays a local, ignored work theme and is not listed among bundled themes or slots.
- Any change to install behavior (T6/T7 exercised the existing contract only).

## Risks

- `t1.md`..`t4.md` are missing; their scope above is inferred from the hand-offs.
