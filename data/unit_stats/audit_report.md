# Unit dataset audit

Status: **PASSED**

Checked 2000 normalized units across 24 faction files.

## Passed checks

- All 2000 roster rows are present.
- Unit keys are unique within each of the 24 race rosters; intentional cross-race sharing is preserved.
- All populated numeric and boolean fields have valid CSV representations.
- Every production CSV is valid UTF-8 with CRLF endings and consistent row widths.
- The machine-readable schema inventory matches every CSV header and column position.
- Primary model counts, health pools, and target-size classifications are internally consistent.
- Every missile, projectile, and explosion reference resolves, including engine-attached weapons.
- Roster membership exactly matches all configured source military-group unions for 24 races.
- Structured roster availability and exact military-group/faction-permission lookup rows reconcile to source.
- Golden checks pass for Bestigors, Cygors, Ghorgons, Preytons, Sea Guard, Skaven weapon teams/artillery, Doomwheel, Black Orcs, Doom Divers, Rogue Idols, Arachnaroks, Necrofex, and Skycutters.
- All 276 raw source-export hashes match the manifest.
- No unresolved extraction or join flags remain.

## Warnings

- None.

## Errors

- None.
