# Task A — race campaign document

Replace `<RACE>` and `<RACE_SLUG>` before dispatch.

Create the `<RACE>` race campaign document for the Computational Total War
project. Read `data/faction_guides/RESEARCH_SPEC.md` completely and follow it as
the authoritative research and document contract. Work only on `<RACE>`
(`race_slug=<RACE_SLUG>`). The production deliverable is only
`data/faction_guides/races/<RACE_SLUG>.md`; do not edit the queue, shared
specifications, scripts, datasets, indexes, or another race's guide.

Preserve the validated pilot form. Read `bretonnia.md`, `chaos_dwarfs.md`, and
`tzeentch.md` only to match their top-level document contract, factual density,
applicability labeling, faction-coverage appendix, and evidence-register quality.
Do not copy their mechanic selection, subsection structure, or prose. The body
must remain asymmetric and organized around what is actually distinctive about
`<RACE>` and its individual factions.

Conduct Task A in these stages:

1. **Catalog boundary.** Review the project README and all economy, unit, typed
   lookup, and character/skill-tree material for `<RACE>`. Establish exactly what
   those catalogs already capture. Do not mistake the presence of a character or
   building row for coverage of its campaign acquisition or operating rules.
2. **Breadth-first web discovery.** Build a candidate ledger before drafting.
   Search at least the following source layers independently: current official
   descriptions and patch notes; race and individual playable-faction pages;
   legendary-lord and legendary-hero/quest or acquisition pages; individual
   mechanic/resource pages; and at least one current campaign guide or discussion
   useful as an omission checklist. Search using every playable faction and
   legendary-lord name, not only the race name. Web sources discover candidates;
   they do not establish precise current-patch rules unless the source is current
   and official.
3. **Candidate ledger.** For every discovered item, assign one disposition:
   already represented by a named catalog; Markdown candidate; excluded with a
   concrete scope reason; or unresolved. The discovery net must consider pooled
   resources and panels, progression and victory state, settlement/occupation and
   colonization rules, climate or Growth replacements, army economics and Supply
   Lines exceptions, caps and recruitment pools, movement/attrition stances,
   diplomacy/confederation/vassal rules, foreign-slot systems, unique-character
   acquisition, mission/dilemma chains, AI fallback, and faction/campaign/DLC
   branches. These are audit categories, not required Markdown headings.
4. **Forward game-file verification.** Trace every Markdown candidate through
   the installed patch 8.1.1 vanilla files. Follow the full evidence chain when
   relevant: primary table, junction/link tables, Lua listeners and saved state,
   mission options and payloads, effect bundles, and English localization/UI.
   Report operative triggers, costs, outputs, gates, limits, durations,
   replacement behavior, interactions, and exact applicability. Executable data
   and active listener dispatch override stale comments or localization.
5. **Reverse game-file audit.** Independently search from every in-scope faction
   key, legendary-lord and unique-character subtype, campaign feature/group,
   pooled resource, mission family, ritual family, and distinctive record prefix.
   This is mandatory and must occur even if the web-derived ledger seems complete.
   Its purpose is to find mechanics and exceptions that online summaries omit.
6. **Reconciliation before writing.** Revisit the web sources after the game-file
   pass. Every online checklist item must now be documented, assigned to a named
   catalog, excluded with a reason, or identified as unresolved. Do not make a
   blanket completeness claim merely because the obvious named mechanics were
   found.
7. **Write and validate.** Write the race Markdown in the validated pilot form,
   while choosing race-specific subsections independently. Include every playable
   faction name and key in Faction coverage. Maintain a precise evidence register
   and limitations section. Run
   `node scripts/faction-guide-queue.mjs validate <RACE_SLUG>` and repair the file
   until it passes.

Use the read-only RPFM workflow described in the research specification and pass
the literal `$CA` placeholder where required. For concurrent Task A runs, invoke
RPFM through `scripts/rpfm-call-locked.ps1` rather than calling
`scripts/rpfm-call.mjs` directly; the wrapper serializes access to the shared
service. Follow the research specification's constrained-memory query discipline:
use narrow path/key queries, prefer exports and existing narrow extracts, do not
issue concurrent RPFM calls from this task, and never retry a large decode after
it destabilizes the endpoint. Keep a restart-safe
working ledger at `work/faction-guide-ledgers/<RACE_SLUG>.md`; this is scratch
research state, not a production deliverable. If the endpoint drops, first check
whether the server recovers; restart the bundled server hidden only when it is
actually unavailable, then resume from the ledger. Never fabricate missing
evidence. If a necessary relation remains unavailable, state the exact limitation
in the guide or report the precise blocker.
