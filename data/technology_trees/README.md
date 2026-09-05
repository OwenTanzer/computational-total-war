# Faction technology trees

Pinned to patch 8.1.1, Steam build 24237342. This is the authoritative technology source and normalized tree dataset. There are 104 self-contained faction files covering all 24 races. The Daemon Prince file explicitly records the absence of an ordinary research tree.

## Retrieval

Read the manifest, schema inventory and audit report, select a faction in faction_index__wh3__8.1.1.csv, then filter its file by record_type and variant_key. Keep node-set candidates and campaign variants separate. Keys are canonical; blank is unavailable or inapplicable, never zero. One-to-many relations use typed rows.

## Applicability and reconstruction

Faction ownership comes from frontend_faction_leaders joined to factions and cultures_subcultures. Each nonblank node-set faction, culture and subculture selector must match. Nodes additionally match the faction and campaign. Campaign-specific overlays are complete separate variants, including common nodes. An unspecified_campaign variant contains only nodes with blank campaign selectors.

The source has both generic and faction-specific node sets for some factions (including Nakai). Both are retained as distinguishable candidates. generic_candidate_with_faction_override is not a second simultaneously active research tree. Database columns identify the candidates, but decoded sources do not expose the engine precedence rule. Do not combine or automatically choose candidates. This is an intentional evidence boundary, not a claim of verified runtime selection.

Node rows preserve tier, indent, pixel offsets, required_parents, research points, per-round and food costs, resource cost keys and UI groups. Zero required_parents means all linked parents, per decoded schema. Dependency links preserve arrow geometry and visibility; no link-type field exists in this snapshot, so node_parent identifies the relation rather than an invented game enum. technology_prerequisite rows are separate explicit technology requirements. Research points are not a fixed turn duration. Technologies preserve hidden flags and all registry fields; technology_building_level is not silently converted to a prerequisite.

UI bounds are source corner-node references, not membership lists. Conditional corner nodes may be absent from a faction variant. Tab membership, tab offsets/order, category modules, resource transactions, ancillary/trait grants, mercenary and unit-upgrade requirements, and initiative-dependent effect payloads remain separate typed rows. Effects preserve signed source values, scopes, priorities and English text. No localized label is inferred from a key.

## Scripts and limitations

The extractor enumerates actual database and localization paths and reverse-checks schema references across every decoded version. discovery.json records that inventory and the bounded campaign/shared-library Lua scan. Whole matching Lua files are retained. script_audit.json inventories every retained file, literal technology references, mutating API sites and exclusions. script_reference rows are evidence pointers, not unconditional effects or inferred ownership. Runtime conditions, execution order, progress counters and save-state are not evaluated; 39 campaign mutation sites are explicitly unresolved.

Known conditional systems include Beastmen achievements, Norscan region/battle requirements, Khorne battle wins, Ostankya hex unlocks and Changeling rifts. Other script references can govern ancillary grants, confederation, units and initiative unlocks. Consult the retained code and faction guides before modeling these as static rules. Binary engine logic, save files, mods, UI animations/audio, AI research priorities and tutorial/narrative mission behavior are excluded from normalized mechanics. AI/audio tables remain in source exports for a transparent discovery boundary. Feature records are retained and faction feature-forest keys are repeated, but feature runtime transitions are not flattened into technology ownership.

classification_inventory.json classifies unused registry/nodes and links excluded by faction/campaign selectors. The validator reports topology, hidden nodes, duplicate technologies, missing localization and source scope limitations. Distinct source keys are retained even when text is missing or structures are shared. Fingerprints exclude faction ownership, text and provenance but include node conditions, layout, cost and effect payloads. They are structural comparisons, not proof of identical scripted campaign behavior.

## Rebuild and install

```powershell
node scripts/extract-technology-source.mjs work/source_technology__wh3__8.1.1
node scripts/build-technology-trees.mjs work/source_technology__wh3__8.1.1 work/generated_technology__wh3__8.1.1
node scripts/validate-technology-trees.mjs work/source_technology__wh3__8.1.1 work/generated_technology__wh3__8.1.1
```

Install only after validation. Extraction refuses a game executable or Steam build mismatch and uses RPFM read operations only. CTW_GAME_PATH may select a verified Steam installation; RPFM must point at that same installation. Builders and validators do not need the game or RPFM. Output contains no wall-clock timestamps and must reproduce byte-for-byte.
