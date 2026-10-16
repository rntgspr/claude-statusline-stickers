---
human_revised: false
plan: maintenance-familyguy-theme
task: T1
status: complete
date: 2026-09-04
summary: Downloaded and visually verified six transparent Family Guy character PNGs from the PNGWing browser download flow.
---

# Hand-off — maintenance-familyguy-theme / T1

## Files touched

<!-- cumaru:touched -->
| Link | Description |
|---|---|
| [`.gitignore`](.gitignore) | modified — keeps `.assets/` ignored |
| [`.assets/familyguy/peter.png`](.assets/familyguy/peter.png) | modified — transparent Peter Griffin original |
| [`.assets/familyguy/quagmire.png`](.assets/familyguy/quagmire.png) | created — transparent Glenn Quagmire original |
| [`.assets/familyguy/brian.png`](.assets/familyguy/brian.png) | created — transparent Brian Griffin original |
| [`.assets/familyguy/meg.png`](.assets/familyguy/meg.png) | created — transparent Meg Griffin original |
| [`.assets/familyguy/stewie.png`](.assets/familyguy/stewie.png) | created — transparent Stewie Griffin original |
| [`.assets/familyguy/chris.png`](.assets/familyguy/chris.png) | created — transparent Chris Griffin original |
<!-- /cumaru:touched -->

## Decisions made during implementation

- Preserved the earlier finding that the five inspected `w7.pngwing.com/pngs/...` preview URLs are opaque checkerboard images, even though they decode as RGBA.
- Used the original PNG URLs returned by each page's `/download` flow. The embedded browser exposed the alphabet challenge image through the `notbot` endpoint; its displayed order was completed for Meg, Stewie, and Chris, while Quagmire and Brian released their originals directly after opening `/download`.
- Replaced the previously present Peter file with the transparent 512×512 original returned for the selected `bdnyh` page. The separate 920×512 Wayback preview currently serves an opaque checkerboard and therefore was not retained.

## Commands run / verification

- Embedded browser/CUA — opened all six selected `/download` pages and visually inspected the resulting original PNGs. Each image shows only its named character: Peter, Quagmire, Brian, Meg, Stewie, or Chris.
- Browser original URLs and dimensions:

| Character | Original URL | Dimensions |
|---|---|---:|
| Peter | `https://r7.pngwing.com/path/979/269/154/brian-griffin-peter-griffin-glenn-quagmire-family-guy-online-griffin-family-family-guy-png-photos-3f8ae67c8ad3efb45654b23e20cb1dc1.png` | 512×512 |
| Quagmire | `https://r7.pngwing.com/path/189/313/185/family-guy-the-quest-for-stuff-glenn-quagmire-brian-griffin-cleveland-brown-chris-griffin-family-guy-d32805e88a6354b10b2c16f8dfc15386.png` | 512×512 |
| Brian | `https://r7.pngwing.com/path/910/50/331/brian-griffin-stewie-griffin-roger-peter-griffin-griffin-family-family-guy-peter-and-brian-e743c6ebd685f09054496a2132a56bb6.png` | 643×1018 |
| Meg | `https://r7.pngwing.com/path/217/549/213/meg-griffin-peter-griffin-stewie-griffin-lois-griffin-glenn-quagmire-others-5589838855ff1ba1773b91162859b951.png` | 586×884 |
| Stewie | `https://r7.pngwing.com/path/736/942/463/stewie-griffin-lois-griffin-meg-griffin-griffin-family-character-family-guy-png-transparent-picture-915f420889e18b6547b5c2317cc89939.png` | 912×1024 |
| Chris | `https://r7.pngwing.com/path/234/1007/793/peter-griffin-chris-griffin-brian-griffin-lois-griffin-meg-griffin-others-ebcebcece65686c69e185d927b6f1a44.png` | 1024×1448 |

- The prescribed Pillow check passed for all six files:

```text
brian     (643, 1018) ink=(0, 0, 643, 1018) alpha=(0, 255)
chris     (1024, 1448) ink=(8, 186, 1024, 1262) alpha=(0, 255)
meg       (586, 884) ink=(76, 0, 510, 883) alpha=(0, 255)
peter     (512, 512) ink=(112, 11, 401, 505) alpha=(0, 255)
quagmire  (512, 512) ink=(6, 120, 510, 399) alpha=(0, 255)
stewie    (912, 1024) ink=(30, 24, 892, 1003) alpha=(0, 255)
```

- `git check-ignore` confirmed all six files and `.assets/` are ignored by `.gitignore`.

## Pending / follow-ups

None for T1. T2 remains the next task; no T2 work was performed.

## Suggestions for the Lead

- Keep the existing opaque-preview evidence above when updating the plan history; the `r7.pngwing.com/path/...` originals are distinct files and pass the alpha check.
