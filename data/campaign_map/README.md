# Immortal Empires campaign atlas

`campaign_atlas__wh3__8.1.1.gpkg` is the compact, machine-readable campaign reference for Total War: Warhammer III Immortal Empires on patch 8.1.1 / Steam build 24237342. It is a GeoPackage 1.3 SQLite database and should not be edited by hand.

## Coverage

- 641 current-map region records and 214 provinces from `wh3_main_combi_map_5`.
- Turn-one ownership and capital placement for all regions and 104 playable factions.
- Exact color-coded raster masks, derived centroids, and raster-border adjacency for 571 regions.
- 749 effective single-player short/long/domination victory objectives and 2,388 typed conditions for every playable faction.
- 1,533 battle-map records and 1,348 Immortal Empires catchment-selection rules.
- Route, area-of-interest, and teleportation nodes and links.
- Embedded region lookup, overview, height, and native-border assets.
- SHA-256 provenance for every source file used by the build.

The `coverage` and `evidence` tables are part of the atlas. Known boundaries are explicit: 70 black maritime/special regions share one lookup color and therefore have no individual raster geometry; starting armies and agents are not exposed by the decoded DB start-position relations; and the binary campaign-coordinate-to-battle-area catchment overlay is not yet decoded. Battle-area rules and their map groups are still preserved exactly.

## Important tables and views

- `regions`, `provinces`, `factions` — canonical map and turn-one scenario state.
- `region_points`, `region_adjacency`, `region_groups` — spatial and topological reference.
- `strategic_nodes`, `strategic_links` — routes, areas of interest, and teleportation.
- `objectives`, `objective_conditions` — relational short, long, and domination victory requirements with no list-valued cells.
- `battle_areas`, `battle_groups`, `battle_maps`, `battle_selection_rules` — the campaign-to-battle bridge.
- `map_assets`, `source_files`, `evidence`, `coverage` — embedded assets, hashes, provenance, and limitations.
- `region_reference`, `faction_start_reference`, `objective_reference`, `region_objective_pressure`, `battle_context_reference` — denormalized query views.

All ordinary tables are readable with a standard SQLite client. Spatial software can additionally read `region_points` as a GeoPackage feature layer in the game's custom logical coordinate system.

Example with Node.js 24:

```js
import { DatabaseSync } from "node:sqlite";

const atlas = new DatabaseSync("data/campaign_map/campaign_atlas__wh3__8.1.1.gpkg", {
  readOnly: true,
});

const neighbors = atlas.prepare(`
  SELECT rr.region_key, rr.region_name, rr.start_owner_name
  FROM region_adjacency a
  JOIN region_reference rr
    ON rr.region_key = CASE
      WHEN a.region_a = ? THEN a.region_b ELSE a.region_a
    END
  WHERE a.region_a = ? OR a.region_b = ?
  ORDER BY rr.region_name
`).all(
  "wh3_main_combi_region_altdorf",
  "wh3_main_combi_region_altdorf",
  "wh3_main_combi_region_altdorf",
);
```

## Rebuild and validation

Run from the repository root:

```powershell
node scripts/extract-campaign-atlas-source.mjs work/source_campaign_atlas__wh3__8.1.1
node scripts/build-campaign-atlas.mjs work/source_campaign_atlas__wh3__8.1.1 work/generated_campaign_atlas__wh3__8.1.1/campaign_atlas__wh3__8.1.1.gpkg
node scripts/validate-campaign-atlas.mjs work/generated_campaign_atlas__wh3__8.1.1/campaign_atlas__wh3__8.1.1.gpkg work/generated_campaign_atlas__wh3__8.1.1
```

Only install the generated candidate under `data/campaign_map/` after validation reports `passed` with no errors.
