# Instructions for any AI coding/hardware agent — FAC-IO-HARDWARE

Read **PROJECT_STATUS.md first**, then `README.md`, `docs/requirements.md`, `docs/validation.md`, `hardware/architecture.md`, `hardware/component-selection-v1.md`, `hardware/gpio-map-v0.md` and `hardware/design-review-v0.md`.

## Operating rules
1. Work on the actual repository and make concrete, reviewable changes. Prefer integrated schematic/PCB correctness over incremental unvalidated manual footprint additions.
2. **Use installed local KiCad CLI** when running locally. On user's Apple Silicon Mac, KiCad 10.0.8 was installed through Homebrew and `kicad-cli` linked to `/opt/homebrew/bin/kicad-cli`. Verify with `kicad-cli version`.
3. Before editing, run `git status --short`, inspect branch and read status docs. Do not overwrite uncommitted work.
4. Before declaring success, run appropriate KiCad ERC/DRC and capture exit codes and reports. Distinguish CAD parse success, ERC, DRC, electrical completeness and production readiness.
5. Don't fabricate schematic pinouts, exact MPNs, KiCad library names or footprints. Verify with manufacturer datasheets and installed libraries.
6. Never generate/approve manufacturing files from a partially routed or disconnected PCB. Keep outputs clearly labelled DRAFT until reviewed.
7. Hardware safety: only low-voltage barrier-controller command contacts, not motor/mains. Relay OFF at reset, brownout, power loss, crash and network failure; verify in hardware.
8. GitHub Actions workflows are useful, but a workflow file is NOT proof of a passing run. Inspect actual logs/artifacts.
9. Update `PROJECT_STATUS.md` after each significant milestone with exact files changed, test results, remaining blockers and next action. Include commit SHAs only when known.
10. Keep schematic, PCB, firmware pin map, BOM and documentation in sync. Prefer small commits for coherent milestones, not cosmetic progress.
11. If access to local shell/GitHub is unavailable, explicitly say so rather than claiming commands ran.

## First task for the incoming agent
Execute real local `kicad-cli` parsing/ERC/DRC against existing drafts, capture results, then correct actual errors. After that, build the complete integrated schematic with verified parts. Do not continue speculative manual PCB routing.
