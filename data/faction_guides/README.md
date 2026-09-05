# Race campaign guides

This directory is the qualitative companion to the normalized unit, character, technology-tree,
and economy datasets. It contains one Markdown document per playable race for
*Total War: WARHAMMER III* patch 8.1.1.

The guides do not restate the catalogs. Their narrow purpose is to document the
mechanically relevant campaign information that remains unaccounted for after
the following production material has been reviewed:

- `data/unit_stats/`
- `data/skill_trees/`
- `data/economy/`
- `data/technology_trees/` — ordinary research structure and payloads; guides retain runtime conditions and unresolved precedence.

Each race document covers race-wide systems and any additional faction-specific
systems, rules, exceptions, permissions, resources, or state transitions. The
amount and organization of prose may differ substantially between races.

## Layout

- `RESEARCH_SPEC.md` — authoritative research and writing contract.
- `queue.json` — the 24-race work queue and run state.
- `races/<race_slug>.md` — completed race documents.

`scripts/faction-guide-queue.mjs` reports queue status and validates an individual
race document. Pilot tasks receive explicit race assignments and must not edit
the shared queue; their results can be reconciled after all pilots finish. Do not
read other completed race documents while researching a race; structural
compatibility comes from the specification, not imitation.
