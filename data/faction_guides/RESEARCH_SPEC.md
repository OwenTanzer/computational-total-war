# Race campaign guide research specification

## Objective

Produce one source-grounded Markdown document for one playable race in the
Warhammer III 8.1.1 snapshot. Answer only this question:

> After the project's economy, army, character, and technology catalogs are accounted for,
> what mechanically relevant information is still needed to understand how this
> race and its individual playable factions operate in campaign?

This is documentation, not a campaign guide. Minimize commentary, evaluation,
speculation, optimization advice, suggested openings, army composition advice,
and lore that does not alter campaign rules.

## Scope boundary

Read the existing production material first. It is both evidence and a negative
boundary: do not reproduce facts that are already adequately represented there.

For the claimed `race_slug`, inspect:

1. `README.md` and the unit, skill-tree, economy, and technology-tree dataset README files.
2. The race row(s) and faction keys in
   `data/economy/faction_index__wh3__8.1.1.csv`.
3. Every economy CSV under `data/economy/factions/<race_slug>/`.
4. `data/unit_stats/normalized/<race_slug>__wh3__8.1.1__ultra.csv` and relevant
   rows in the typed unit lookups, especially roster permissions and abilities.
5. The race's rows in
   `data/skill_trees/character_index__wh3__8.1.1.csv` and the corresponding
   files under `data/skill_trees/characters/<race_slug>/`.
6. The race’s technology faction files, index, and script audit under
   `data/technology_trees/`; distinguish static rows from unresolved runtime rules.
7. Relevant manifests, schema inventories, and audit reports when needed to
   understand a field or an intentional omission.

The validated pilot guides for Bretonnia, Chaos Dwarfs, and Tzeentch may be read
only to preserve the established document form, claim density, applicability
labels, and evidence-register standard. Do not inherit their mechanic selection,
subheadings, or implicit cross-race checklist. Each race's content remains an
independent result of its own evidence.

## Required investigation order

### 1. Review the project material

Establish what is already covered and list candidate gaps. Differences in
buildings, units, or skill trees are not themselves guide content unless a
separate rule or campaign system is required to interpret their availability or
operation.

### 2. Search the web for grounding

Search using the race name, every playable faction name, relevant legendary-lord
names, “campaign mechanics,” and patch/version terms. Use this pass to discover
mechanic names, vocabulary, likely scripts/tables, and claims that require
verification.

Prefer Creative Assembly/Total War pages and patch notes. Community wikis,
guides, and discussions may be used as discovery aids, but are not sufficient
authority for precise current-patch rules. Record useful URLs for the evidence
register. Do not copy guide prose or inherit strategic judgments.

Do not stop at a race overview. Independently search faction and legendary-lord
pages, named mechanic and resource pages, legendary-character acquisition or
quest pages, campaign guides, and relevant patch notes. Maintain a candidate
ledger in which every discovered mechanic or campaign rule is classified as
cataloged, a Markdown candidate, excluded with a reason, or unresolved.

### 3. Investigate the installed game files

Treat the installed 8.1.1 game data as the primary authority. Use the existing
source exports where they contain the relevant relation. For uncatalogued
mechanics, use the read-only RPFM interface through `scripts/rpfm-call.mjs` to
search and decode vanilla `GameFiles`.

Search from concrete identifiers and vocabulary rather than from a fixed
cross-race checklist:

- every faction key from the economy index;
- relevant lord and character subtype keys from the skill-tree index;
- mechanic, resource, event, mission, dilemma, effect-bundle, and UI terms found
  during the material review and web pass;
- matching database tables, campaign Lua scripts, frontend/configuration files,
  and English localization entries.

Also perform a reverse-search pass from every in-scope faction key, legendary
lord and unique-character subtype, campaign feature/group, pooled resource, and
mission/ritual family discovered. This pass is intended to find material that
web mechanic summaries omit, including character acquisition, AI fallback,
settlement and occupation rules, climate and Growth replacements, army-economy
exceptions, movement stances, confederation restrictions, and campaign/DLC
branches. These are discovery categories, not mandatory output sections.

Useful RPFM operations include
`get_packed_files_names_starting_with_path_from_all_sources`,
`get_rfiles_from_all_sources`, and `decode_packed_file`. The RPFM server is a
read-only research dependency for this workflow. Do not edit or save game packs.
When an operation requires a `pack_key`, pass the literal placeholder `$CA` to
`scripts/rpfm-call.mjs`; the helper loads the merged vanilla packs and substitutes
their session-scoped key before making the research call.

Treat RPFM memory as a constrained research resource. Prefer project source
exports, existing narrow extracts, exact packed-file paths, stable keys, and
prefix-filtered lookups. Never begin discovery by decoding an entire
high-cardinality DB table or broad script tree merely to search for a term. If a
necessary relation has no narrower route, record the reason in the working ledger
before attempting one full decode. Do not retry the same large decode after it
resets or terminates the endpoint; restart only after confirming unavailability,
then pivot to exports, narrower linked relations, localization, or an explicitly
bounded evidence limitation. Run only one RPFM request at a time within a task.

Trace enough of each mechanic to report its operative rules: applicability,
inputs, outputs, triggers, gates, limits, durations, state changes, unlocks,
replacement behavior, and interactions with other campaign systems. Do not
infer a rule solely from a localized tooltip when its implementation can be
checked. When implementation is split across database records and scripts,
inspect both.

Do not assume that a cataloged unit or character has its campaign lifecycle
cataloged. Check recruitment or acquisition triggers, mission chains, dilemmas,
spawn rules, ownership requirements, AI fallback behavior, and campaign-specific
variants. Likewise, check whether apparently generic campaign rules are disabled
or replaced for the race. Executable fields, active listener dispatch, and linked
database relations take precedence over stale Lua comments or localization.

Some behavior may be executable-bound or otherwise absent from decoded files.
State that limitation explicitly. A current official source may support a
high-level claim that cannot be independently located, but such a claim must be
identified as official-source-only. Do not present a secondary web claim as
game-file-verified.

### 4. Write the qualitative report

Write `data/faction_guides/races/<race_slug>.md`. Organize the body around the
systems actually found. Do not manufacture empty standard sections or give each
faction equal space.

The document must contain:

1. A title and compact scope block with game, patch, Steam build, race name,
   race slug, and playable faction count.
2. A short **Catalog boundary** stating what the existing CSV material already
   covers and therefore is not repeated.
3. A **Mechanically relevant material not captured elsewhere** body. Subheadings
   are chosen independently for this race. Each subsection must identify its
   applicability as race-wide or name the exact faction key(s).
4. A **Faction coverage** appendix listing every playable faction name and key.
   For each faction, point to the relevant subsection(s), or state that no
   additional faction-specific mechanic was located beyond the documented
   race-wide systems and cataloged differences. This is a coverage check, not a
   demand for symmetric prose.
5. An **Evidence register** containing the exact game paths/table names, stable
   record keys or search terms, project files consulted, web URLs used for
   grounding, and any unresolved evidence limitations.

## Selection test

Include a fact when all of the following are true:

- it changes or constrains campaign operation;
- it is not already adequately represented by the normalized catalogs;
- its applicability can be assigned to the race or named faction key(s); and
- it has traceable evidence.

Typical qualifying material includes scripted campaign systems, pooled-resource
loops, faction-specific currencies or panels, recruitment pools and caps,
special movement/settlement/occupation rules, confederation or diplomacy rules,
campaign-only unit transformation or upgrading, unusual victory/progression
state, unique missions and dilemma systems, and conditional interactions whose
meaning would be distorted by universal CSV columns. These are examples, not a
required checklist.

Exclude ordinary catalog rows, generic game rules shared broadly across races,
tooltip flavor, lore without mechanical consequence, player recommendations,
rankings, inferred intent, and claims that cannot be sourced.

## Claim discipline

- Prefer stable game keys and exact paths over paraphrased provenance.
- Use English localized names for readability, paired with keys where identity
  could be ambiguous.
- Distinguish observed data, script behavior, official web description, and
  unresolved inference. Omit unsupported inference whenever possible.
- Numeric claims must be current to the 8.1.1 snapshot and traceable to game
  data/scripts or an explicitly identified current official source.
- If sources conflict, report the conflict and do not silently choose the more
  convenient value.
- Keep prose factual and compact. Explain relationships that tables cannot
  express; do not turn the document into strategy commentary.

## Completion gate

Before marking the race complete:

- every faction in the economy index for the race appears in Faction coverage;
- every substantive mechanic states its applicability;
- cataloged facts are referenced rather than redundantly transcribed;
- every substantive claim has a corresponding evidence-register entry;
- web-only and unresolved claims are labeled accurately;
- no other race guide was used as a content template;
- every candidate-ledger item has been disposed as documented, cataloged,
  excluded with a concrete reason, or explicitly unresolved;
- `node scripts/faction-guide-queue.mjs validate <race_slug>` passes.

If evidence is inadequate, release the queue claim with a concise failure reason
instead of writing confident filler.
