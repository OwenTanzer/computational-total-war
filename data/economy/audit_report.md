# Faction economy dataset audit

Status: **PASSED**

Checked 104 playable faction files and 24108 building rows.

## Passed checks

- All 33 authoritative source-export hashes match their manifest.
- The source frontend roster resolves to exactly 104 non-prologue playable faction keys.
- The faction index contains every playable faction exactly once.
- All 104 faction economy CSV files are present.
- Every faction CSV is valid UTF-8 with CRLF endings, the canonical header, typed numeric fields, lowercase booleans, and unique building rows.
- All 24108 constructible building rows reconcile to faction availability, visibility, enabled culture variants, and English localisation.
- Every intrinsic building field, localized label, uniqueness flag, and standardized economic metric recomputes exactly from the source tables.
- The faction index reconciles every path, row count, byte count, and SHA-256 file hash.
- The machine-readable schema inventory matches every faction CSV column and position.
- Faction totals reconcile across all 24 playable races.
- Golden checks cover conventional, Skaven, and Chaos Dwarf building systems.
- Faction-specific Eshin, Avelorn, and Golden Order levels remain with their owners and do not leak into peer factions.

## Warnings

- None.

## Errors

- None.
