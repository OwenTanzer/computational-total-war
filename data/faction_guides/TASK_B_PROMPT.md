# Task B — adversarial audit and repair

Replace `<RACE>` and `<RACE_SLUG>` before dispatch.

Adversarially audit and repair the existing `<RACE>` campaign document for the
Computational Total War project. Work only on `<RACE>`
(`race_slug=<RACE_SLUG>`). Read `data/faction_guides/RESEARCH_SPEC.md` and
`data/faction_guides/TASK_A_PROMPT.md` completely for the production scope and
validated document contract, but do not assume that Task A satisfied either.

The production file is
`data/faction_guides/races/<RACE_SLUG>.md`. Treat every current claim and every
current omission as a hypothesis to test. Task B is complete only after repairing
that file, not after producing a critique. Do not edit the queue, shared
specifications, scripts, datasets, indexes, or another race's guide.

Keep a restart-safe audit ledger at
`work/faction-guide-audits/<RACE_SLUG>.md`. The ledger is scratch evidence, not a
production deliverable. It must record enough state to resume after interruption.

## Independence rule

Do **not** read `work/faction-guide-ledgers/<RACE_SLUG>.md` during initial
discovery. First build an independent candidate and contradiction checklist from
the project catalogs, current guide, web, and installed game files. Only after
that independent pass is recorded may you read the Task A ledger and reconcile
whether its dispositions omitted, weakened, or misclassified anything.

Enforce this separation at the command level. Before reconciliation, do not open,
print, grep, index, or allow a recursive workspace search to include any path
under `work/faction-guide-ledgers/`. Restrict searches to named source roots or,
when running `rg` from the workspace root, include
`--glob '!work/faction-guide-ledgers/**'`. Apply the same exclusion to helper
scripts and file enumerations whose output could expose ledger contents. If an
accidental match still appears, record the exact contamination in the Task B
audit ledger, do not use it as evidence, and independently rebuild every affected
disposition before reconciliation.

The existing guide may provide identifiers to investigate, but it is not evidence
that a mechanic is complete or correct. A passing structural validator is not a
content finding.

## Required audit stages

1. **Re-establish the catalog boundary.** Review the race's economy, unit,
   typed-lookup, and character/skill-tree material. Identify facts that should
   remain in catalogs, facts that need campaign relationships explained in
   Markdown, and any current prose that redundantly flattens catalog rows.
2. **Inventory the current guide.** Convert every substantive guide claim into a
   checkable audit item. Pay special attention to numeric values, formulas,
   thresholds, costs, durations, applicability, human/AI differences,
   campaign/DLC branches, replacement rules, lifecycle state, and claims that no
   additional mechanic exists.
3. **Independent adversarial web pass.** Search current official descriptions and
   patch notes, race and every playable-faction page, every legendary-lord page,
   legendary-hero or unique-character acquisition material, individual mechanic
   and resource pages, and at least two useful current guides or discussions from
   different sources. Search with every playable faction and legendary-lord name.
   Seek omissions and contradictions, not confirmation. Web material discovers
   candidates; precise rules still require current installed-file verification
   unless a limitation is explicitly labeled official-source-only.
4. **Forward verification of every candidate and existing claim.** Trace the
   complete installed 8.1.1 evidence chain where relevant: primary tables,
   junctions, Lua listeners and saved state, missions/dilemmas/incidents and
   payloads, effect bundles, English localization/UI, campaign branches, and AI
   fallback. Executable fields and active dispatch override stale comments or
   localization.
5. **Independent reverse game-file audit.** Search from every playable faction
   key, legendary-lord subtype, in-scope unique-character subtype, campaign
   feature/group, pooled resource, mission/dilemma/incident/ritual family,
   settlement or occupation family, stance, foreign-slot family, and distinctive
   record prefix. Follow newly discovered prefixes recursively until their
   campaign effect and applicability are understood or an exact limitation is
   recorded. This pass is mandatory even if web sources expose nothing new.
6. **Reconcile against Task A.** Only now read
   `work/faction-guide-ledgers/<RACE_SLUG>.md`. Compare its candidate dispositions
   with the independent checklist. Every external and reverse-search item must be
   classified as: already correct in the guide; repair an incorrect or overstated
   claim; add an omission; move to a named catalog; exclude with a concrete scope
   reason; or retain as an explicitly bounded unresolved limitation.
7. **Repair the production guide.** Make the smallest coherent edits that leave a
   complete, factual document. Add missing systems, correct errors, narrow
   unsupported claims, remove catalog duplication, update applicability and
   faction coverage, and extend the evidence register. Preserve the asymmetric
   race-specific structure; do not impose standard mechanic headings or equal
   faction length.
8. **Hostile final reread and validation.** Re-read the repaired file as a skeptic.
   Check internal arithmetic, tables against prose, race-wide versus faction-only
   language, human/AI and IE/RoC branches, English names and keys, evidence
   provenance, and catalog-boundary discipline. Run
   `node scripts/faction-guide-queue.mjs validate <RACE_SLUG>` and repair until it
   passes.

## Audit-ledger contract

The audit ledger must include:

- scope, patch/build, race, faction count, and production path;
- the independent web and reverse-search checklist created before consulting the
  Task A ledger;
- one disposition for every candidate and every challenged existing claim;
- exact game paths, table names, stable keys/prefixes, and web URLs supporting
  repairs or exclusions;
- a repair log stating what changed and why;
- remaining limitations stated narrowly; and
- the final validation result.

Do not use “no issue found” as a blanket disposition. Record the concrete search
or evidence that closed the item.

## Completion gate

Before declaring Task B complete:

- every playable faction name and key is still present in Faction coverage;
- every substantive section states exact applicability;
- every existing numeric or lifecycle claim has been checked, corrected, or
  explicitly bounded;
- every independently discovered candidate has a recorded final disposition;
- unique-character acquisition, AI fallback, campaign/DLC branches, settlement
  and occupation rules, climate/Growth replacements, army-economy exceptions,
  caps/pools, stances/attrition, diplomacy/confederation/vassal rules, and
  progression/victory state have each been actively considered rather than
  assumed absent;
- evidence-register entries match the repaired claims and distinguish installed
  data, current official support, secondary discovery, and unresolved limits;
- commentary, strategy, rankings, and unsupported intent remain absent; and
- `node scripts/faction-guide-queue.mjs validate <RACE_SLUG>` passes.

Use the read-only RPFM workflow and query-discipline rules in the research
specification. For concurrent runs, invoke it only through
`scripts/rpfm-call-locked.ps1`, using the literal `$CA` placeholder where
required. If the endpoint is unavailable, confirm that state, restart the bundled
server hidden, and resume from the audit ledger. Never edit or save a game pack,
and never fabricate a relation that cannot be recovered.
