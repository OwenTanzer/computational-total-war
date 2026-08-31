# Unit stat data

This directory is the versioned, reproducible data layer for computational analysis of *Total War: WARHAMMER III* units.

## Baseline

- Game: `warhammer_3`
- Patch: `8.1.1`
- Steam build ID: `24237342`
- Unit scale: `ultra`
- Rank: `0`
- Context: unmodified custom-battle base stats
- Exclusions: technologies, red-line skills, lord effects, campaign difficulty bonuses, temporary abilities, fatigue, terrain, charge decay, and mods

## Directory layout

- `source_exports/` — untouched schema-decoded exports from the installed game packs, plus `source_manifest.json` with byte counts and SHA-256 hashes.
- `normalized/` — 24 analysis-ready race CSVs, each containing the deduplicated union of its core and configured faction-variant military groups.
- `lookups/` — one-to-many components, weapons, projectiles, explosions, abilities, attributes, contact effects, roster permissions, mount variants, and data-quality flags.
- `archive/` — previous extracts retained unchanged for comparison and recovery.
- `schema_inventory__v2.csv` — the authoritative dataset-to-column mapping and column order for every generated CSV.
- `dataset_manifest.json` — schema version, source path, row counts, and build timestamp.
- `audit_report.md` and `audit_report.json` — the most recent validation results.

Do not edit `source_exports/` by hand. Regenerate normalized and lookup files from the source snapshot.

## CSV conventions

- UTF-8, comma delimiter, CRLF line endings, one header row, and lowercase `snake_case` headers.
- Stable game keys are identifiers; display names are labels.
- The normalized unique key is `(game, patch, unit_scale, subculture_key, unit_key)`. A source unit may legitimately appear in multiple race rosters.
- Numbers use an unformatted decimal point and no thousands separators.
- Percentage-like game stats use percentage points: `20`, not `0.20` or `20%`.
- Booleans are lowercase `true` or `false`.
- Blank means not applicable or unavailable from the source relation. Zero means an observed zero.
- Lists are never stored in cells. One-to-many relationships belong in `lookups/`.
- Derived outputs such as hit chance, AP ratio, expected damage, or DPS are calculated downstream and are not stored here.

The full header inventory is machine-readable in `schema_inventory__v2.csv`; that file is generated from the same column definitions as the CSV writers and is checked against every output header during validation.

## Normalized schema v2 semantics

The 24 files in `normalized/` retain convenient one-row-per-unit statistics, but the following fields have precise meanings:

- `entity_count` and `model_count` are the number of primary targetable bodies represented on the unit card. They are identical compatibility fields in schema v2.
- `source_total_component_count` preserves CA's `main_units.num_men`, which can include crew, riders, engines, or decorative sub-entities and must not be treated as the displayed model count.
- `hp_per_entity` is the primary body's hit-point contribution and is never an average across heterogeneous components.
- `total_hp` is the source-derived unit health pool. It equals `entity_count × hp_per_entity` for homogeneous and composite-body units; crewed artillery additionally includes its separately modeled crew health. `unit_components` exposes the exact summands.
- `primary_component_role` identifies whether the primary body is a man, mount, or engine.
- `primary_target_size` is the raw battle-entity size class. `is_large` is true for `large` and `very_large` primary bodies.
- `has_missile_weapon` is derived from all supported attachment paths: the land unit, unit/weapon junctions, the primary artillery engine, and extra engines.
- Inline missile and explosion columns describe the selected default projectile for convenient comparisons. Every attached weapon and alternate projectile is retained in `lookups/unit_weapon_links__wh3__8.1.1__ultra.csv`.
- Missile-only fields, including `accuracy`, are blank on units without a resolved missile weapon.
- `source_*` columns preserve the exact joined CA keys used for the normalized row.
- `roster_scope` distinguishes core, core-and-variant, faction-exclusive, and shared-variant availability. `is_faction_exclusive` is true when a unit is supplied only by a configured faction-variant military group.
- `military_group_count` and `permitted_faction_count` provide convenient structured availability counts without embedding lists in normalized rows.
- `availability_notes` provides a concise human-readable qualification when availability needs explanation. Exact memberships and permissions remain authoritative in the typed `unit_rosters` lookup rather than being encoded as prose or delimited lists.
- `data_quality_status` is `complete` only when all required joins resolve. Any failure is also written to the data-quality lookup.

## Companion relations

- `unit_components__wh3__8.1.1__ultra.csv` separates primary bodies, crew/riders, and extra engines. Secondary-component targetability is left blank where the source tables do not encode it.
- `unit_weapon_links__wh3__8.1.1__ultra.csv` records melee and missile attachment paths, component roles, slots, ammunition pools, missile weapons, every projectile variant, and the default-projectile flag.
- `projectiles__wh3__8.1.1.csv` preserves direct damage, AP damage, bonuses, timing, burst/volley counts, collision, calibration, penetration, expiry, homing, friendly-fire, building-damage, contact-effect, shrapnel, and explosion references.
- `explosions__wh3__8.1.1.csv` preserves radius, direct/AP damage, force, ignition, magical/spell flags, ally interaction, contact effects, and shrapnel.
- `unit_abilities`, `unit_attributes`, and `unit_contact_effects` provide normalized one-to-many keys.
- `unit_rosters` uses typed rows to preserve exact race-specific military-group memberships and custom-battle faction permissions separately.
- `unit_mount_variants` preserves base-to-mounted unit relationships.
- `data_quality_flags` is empty only when no unresolved join or extraction error remains.

## Reproduction

The installed game stores its records inside `.pack` archives. RPFM 5.0.6 supplies the versioned Warhammer III schemas used for this snapshot.

From the workspace root, with `rpfm_server.exe` running locally:

```powershell
node .\scripts\extract-source.mjs data\unit_stats\source_exports
node .\scripts\build-unit-dataset.mjs data\unit_stats\source_exports work\generated_unit_stats__final
node .\scripts\validate-unit-dataset.mjs data\unit_stats\source_exports work\generated_unit_stats__final
```

Install generated files only after the validator exits successfully. The validator checks source hashes, roster completeness, keys, headers, types, primary components, health identities, size classifications, every missile/projectile/explosion link, companion-table references, and representative golden units.

## Historical repair

The original six normalized files are preserved under `archive/8.1.1__initial_extract_2026-08-24/`. Schema v2 repairs the failed missile joins, component-count/health averaging, large-unit classification, undocumented headers, non-applicable accuracy values, missing one-to-many relations, and absent raw-source provenance.
