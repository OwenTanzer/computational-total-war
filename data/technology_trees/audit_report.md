# Technology tree audit

Status: **PASSED**

104 faction files; 104 variants; 6016 nodes; 1620 distinct technologies; 6272 dependency rows; 12425 ordinary effect rows; 230 script-lock reason rows; 703 direct unlock rows.

## Checks

- 104 unique indexed faction files; 24 race representatives; hashes, sizes, context, canonical schema, selector variants and source fields verified.
- All nodes, technologies, prerequisite links, research costs, effect junctions, scopes, priorities and localizations reconcile to source.
- Prerequisite DAGs checked; zero required_parents means all source parents. Hidden and repeated technology nodes are retained and classified.
- Nakai wh2_dlc13 branches, ordering, prerequisites, costs and effects verified against complete lzd_nakai source membership.
- Independent gameplay override totals and the two Changeling campaigns verified; 96 structured script definitions and bounded evidence validated; zero whole Lua files.
- Shared fingerprints recomputed and faction-specific Wood Elf structure distinguished.
- Two independent builds and the candidate are byte-identical across all builder artifacts.

## Warnings and evidence limits

- 5269 missing localization occurrences (1490 distinct keys); structural records retained.
- 35 bounded lock sites are not normalized: Beastmen challenge predicates/counters, Ostankya hex progression, and Changeling saved-state-guarded rift release (Empire minor-2 mission or at least two Rift Gems). See script_audit.json for individual locations.
- Seven explicit faction DB assignments replace generic fallbacks using reviewed gameplay exceptions; the binary engine selector is not decoded. See node_set_precedence.json.
- Feature forests and transitions are retained in source, but runtime feature transitions and script-controlled effect/unlock behavior are not statically executed.

## Errors

None.
