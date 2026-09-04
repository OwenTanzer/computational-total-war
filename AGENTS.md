# Agent usage guide

This repository is a machine-readable context source for agents assisting with
*Total War: WARHAMMER III*. Answers must remain scoped to patch 8.1.1, Steam
build 24237342, unless the user supplies newer evidence.

## Retrieval order

1. Read `context_catalog.json`.
2. Select the relevant dataset and read its `README.md`.
3. Read its manifest and schema inventory.
4. Use an index to locate only the relevant race, faction, or character file.
5. Filter rows or query SQLite before bringing records into model context.
6. Check the dataset's validation report and carry its caveats into the answer.

Do not load all character CSVs, all source exports, or the entire GeoPackage
into context. The self-contained character files intentionally repeat metadata
to support independent retrieval; that repetition is not evidence of distinct
mechanics.

## Evidence rules

- Stable database keys are canonical. Localized English names are labels and
  may be missing.
- Prefer normalized production data for ordinary facts and typed relations.
- Use source exports to audit provenance or answer questions outside normalized
  coverage; do not silently override normalized semantics with a raw column.
- In unit data, use `tactical_category` for body-plan comparisons and retrieval.
  `source_unit_class` and `source_caste` are provenance, not the canonical
  tactical ontology.
- Use faction guides for bespoke campaign systems, conditional rules, and
  omissions explicitly called out by the economy or catalog documentation.
- Distinguish base unit-card data from technologies, skills, lord effects,
  difficulty, fatigue, terrain, temporary abilities, and mods.
- Never present blank as zero. Never infer a missing label from a similar key.
- When datasets disagree or a requested mechanic is out of scope, report the
  boundary rather than inventing a value.

## Repository maintenance

Production data under `data/` is generated and must not be edited manually.
Build candidates belong under ignored `work/` paths and may replace production
files only after their validator passes. When changing a schema or snapshot,
update `context_catalog.json`, the relevant manifest and README, and validation
expectations together.
