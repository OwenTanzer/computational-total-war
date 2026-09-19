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

- Technology data is owned by `data/technology_trees/`; the economy snapshot does not own technology records.
- In faction technology files, filter by `variant_key`. Faction-specific overrides replace generic fallbacks according to `source_exports/node_set_precedence.json`; only legitimate campaign variants are emitted.
- Read `script_audit.json` and `audit_report.json` before asserting research availability. Typed scripted requirements and rewards retain their scopes, triggers and targets; bounded script references are evidence pointers, not unconditional effects; the Daemon Prince explicitly has no ordinary research tree.

## Optional modifier retrieval

Ordinary unit comparisons continue to use `data/unit_stats/` without loading the
modifier reference. For modifier questions, read `data/effect_semantics/README.md`
and its coverage report, then use `unit_index.csv` or the paginated query tool.
Start with `query:modifiers -- unit <unit_key> --modifiers`; filter by bonus,
source kind or exact source owner when useful. Follow an effect, source or record
ID only for the details needed. Numeric IDs are snapshot-local; game keys are
canonical across datasets. Never dump the full database into context.

The generated reference preserves all 220 extracted tables, but per-unit results
are candidate relevance, not active campaign buffs. `--owner` filters the owner
of the source, not recruitment legality or scope. Skill levels are alternatives;
technology variants and conditional initiatives remain distinct. Read scope,
rank bounds, special-category requirements and owner prerequisites before using
a value. Unindexed relations remain available through effect/table/gaps queries;
an empty result is not proof of absence. No stacking or final-stat arithmetic is
certified by this first pass. Unit progression/ability evidence is retained here
as source material; future normalized progression stays owned by unit_stats.

Default ordinary-unit modifier queries omit sources whose retained scope targets
only characters; `--evidence` restores them. Unknown scopes remain visible.
Effect/source detail queries preserve all source scopes. Self-character sources
use explicit base-body anchors and compare mount grants with custom-battle identity
paths. Only distinct supported base identities justify exclusion; conflicting or
incomplete paths remain unresolved. Custom-battle evidence never proves campaign
acquisition. Forms outside normalized coverage retain evidence, without base-query links.
Use `character <subtype_key>` to inspect supported forms and mount acquisition
without relying on effect bindings. Mount node and skill-level rank fields stay
separate; no effective unlock rank is inferred. Other character-recipient scopes
remain contextual rather than being equated to the source character. Weapon-junction routes
carry explicit unresolved activation/rank even when a sibling unit-set binding
has a rank gate; never transfer that gate or infer one from a key suffix.

## Repository maintenance

Production data under `data/` is generated and must not be edited manually.
Build candidates belong under ignored `work/` paths and may replace production
files only after their validator passes. When changing a schema or snapshot,
update `context_catalog.json`, the relevant manifest and README, and validation
expectations together.
