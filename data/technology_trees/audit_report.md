# Technology tree audit

Status: **PASSED**

104 faction files; 112 variants; 6399 nodes; 1620 distinct technologies; 6755 dependency rows; 13250 ordinary effect rows; 230 script-lock reason rows; 1063 direct unlock rows.

## Checks

- 104 unique indexed faction files; 24 race representatives; hashes, sizes, context, canonical schema, selector variants and source fields verified.
- All nodes, technologies, prerequisite links, research costs, effect junctions, scopes, priorities and localizations reconcile to source.
- Prerequisite DAGs checked; zero required_parents means all source parents. Hidden and repeated technology nodes are retained and classified.
- Nakai wh2_dlc13 branches, ordering, prerequisites, costs and effects verified against complete lzd_nakai source membership.
- Shared fingerprints recomputed and faction-specific Wood Elf structure distinguished.
- Two independent builds and the candidate are byte-identical across all builder artifacts.

## Warnings and evidence limits

- 5685 missing localization occurrences (1490 distinct keys); structural records retained.
- 39 campaign script mutation sites retain unresolved runtime conditions. Literal script references are not static effects.
- Generic and faction-specific candidate node sets are both preserved; engine precedence is not proven by decoded records.
- Feature forests and transitions are retained in source, but runtime feature transitions and script-controlled effect/unlock behavior are not statically executed.

## Errors

None.
