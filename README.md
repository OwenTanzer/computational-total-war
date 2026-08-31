# Computational Total War

This repository is a machine-readable context source for AI agents assisting with Total War: Warhammer III. It contains source-backed datasets, qualitative mechanic guides, and the scripts used to rebuild and validate them. Production data is under `data/`; `work/` is scratch space and is not authoritative.

Agents and retrieval pipelines should begin with [`context_catalog.json`](context_catalog.json). It identifies the authoritative entry point, schema, index, validation report, and efficient loading strategy for each dataset. [`AGENTS.md`](AGENTS.md) defines evidence and retrieval rules for agentic use.

This is an unofficial research project and is not affiliated with Creative Assembly or SEGA. See [NOTICE.md](NOTICE.md) for third-party content and trademark information.

## Current scope

- Game: Total War: Warhammer III
- Patch: 8.1.1
- Steam build: 24237342
- Races: all 24 playable race rosters in the patch 8.1.1 source snapshot
- Unit data: 24 race CSVs containing 2,000 race-roster rows
- Skill trees: 500 unique character files containing 521 conditional node sets
- Economy: 104 playable-faction CSVs containing the standardized building catalog
- Campaign atlas: one Immortal Empires GeoPackage containing 641 regions, 214 provinces, 104 playable starts, effective victory objectives, topology, and battle-map relations
- Faction mechanics: 24 source-grounded race guides covering all 104 playable factions and bespoke campaign systems omitted from the standardized catalogs

Faction-specific military groups remain inside their parent race dataset. Normalized unit rows carry structured scope, exclusivity, and availability counts; the typed roster lookup preserves exact military-group memberships and faction permissions without storing lists in cells or creating separate faction CSVs.

## Directory layout

- `data/unit_stats/` — normalized unit statistics, weapon and projectile lookups, raw source exports, manifests, schema documentation, and audit reports.
- `data/skill_trees/` — one self-contained CSV per character subtype, plus the character index, schema inventory, raw source exports, manifests, and audit reports.
- `data/economy/` — one narrow building-economy CSV per playable faction, plus the faction index, schema inventory, raw source exports, manifest, and audit reports.
- `data/campaign_map/` — the compact Immortal Empires GeoPackage, documentation, and validation reports.
- `scripts/` — repeatable extraction, build, and validation programs for all production datasets.
- `work/` — downloaded tooling, dependency caches, and disposable intermediate builds. Nothing here should be treated as production data.
- `relations.tex` — project notes on combat-stat relationships and interpretation.
- `context_catalog.json` — compact machine-readable routing metadata for agents and retrieval systems.
- `AGENTS.md` — retrieval order, evidence rules, and dataset maintenance instructions for agents.

Each production dataset has its own `README.md`. Start with:

- `data/unit_stats/README.md`
- `data/skill_trees/README.md`
- `data/economy/README.md`
- `data/campaign_map/README.md`

## Validation

The scripts require Node.js 24 or newer. They use only Node.js built-in modules; no package installation is required for validation.

Run the complete validation suite from the repository root:

```powershell
npm run validate
```

Or run individual validators from the repository root:

```powershell
node scripts/validate-unit-dataset.mjs data/unit_stats/source_exports data/unit_stats
node scripts/validate-skill-trees.mjs data/skill_trees/source_exports data/skill_trees
node scripts/validate-economy-dataset.mjs data/economy/source_exports data/economy
node scripts/validate-campaign-atlas.mjs data/campaign_map/campaign_atlas__wh3__8.1.1.gpkg data/campaign_map
```

Each validator writes machine-readable and Markdown audit reports into its production dataset directory. A production dataset is ready only when its audit status is `passed` and its error list is empty.

## Rebuilding

The pipelines follow the same three stages:

1. Extract authoritative game tables with the corresponding `extract-*.mjs` script.
2. Build into a versioned directory under `work/`.
3. Validate the candidate before replacing anything under `data/`.

Candidate directories under `work/` are disposable after the installed production dataset passes validation. Source exports and production audit reports remain under `data/` and must not be removed as part of candidate cleanup.

Relevant scripts:

- Unit data: `extract-source.mjs`, `build-unit-dataset.mjs`, `validate-unit-dataset.mjs`
- Skill trees: `extract-skill-source.mjs`, `build-skill-trees.mjs`, `validate-skill-trees.mjs`
- Economy: `extract-economy-source.mjs`, `build-economy-dataset.mjs`, `validate-economy-dataset.mjs`
- Campaign atlas: `extract-campaign-atlas-source.mjs`, `build-campaign-atlas.mjs`, `validate-campaign-atlas.mjs`

Do not edit generated CSVs by hand. Stable database keys are the canonical identifiers; localized English labels are descriptive metadata and may be absent for hidden or scripted game records.

## License

Project source code and project-authored documentation are available under the [MIT License](LICENSE). Third-party game content and derived datasets are not relicensed; see [NOTICE.md](NOTICE.md).
