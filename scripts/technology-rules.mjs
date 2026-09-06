// Patch 8.1.1 replacement semantics. These are deliberately narrow overrides,
// not a generic rule that all database selectors are additive or interchangeable.
// Each pair must reconcile to technology_node_sets.faction_key/culture/subculture.
// The review's observed playable trees independently corroborate replacement.
export const OVERRIDES = [
  ["wh2_dlc13_lzd_spirits_of_the_jungle", "lzd_nakai", "lzd_mil"],
  ["wh3_dlc20_chs_azazel", "chs_mil_azazel", "chs_mil"],
  ["wh3_dlc20_chs_festus", "chs_mil_festus", "chs_mil"],
  ["wh3_dlc20_chs_valkia", "chs_mil_valkia", "chs_mil"],
  ["wh3_dlc20_chs_vilitch", "chs_mil_vilitch", "chs_mil"],
  ["wh3_main_chs_shadow_legion", "chs_mil_belakor", "chs_mil"],
  ["wh3_dlc24_tze_the_deceivers", "tze_the_changeling", "tze_mil"],
].map(([faction_key, selected_node_set_key, overridden_node_set_key]) => ({
  faction_key,
  selected_node_set_key,
  overridden_node_set_key,
  rule: "faction_specific_replaces_generic",
  interpretation_status: "source_selector_with_review_confirmed_replacement",
  corroborating_review:
    "https://github.com/OwenTanzer/computational-total-war/pull/3#issuecomment-5552741940",
}));

export function resolveSets(tables, p, precedence) {
  const matches = tables.technology_node_sets.filter(
    (r) =>
      (!r.faction_key || r.faction_key === p.faction.key) &&
      (!r.culture || r.culture === p.culture) &&
      (!r.subculture || r.subculture === p.faction.subculture),
  );
  const rule = precedence.overrides.find(
    (r) => r.faction_key === p.faction.key,
  );
  if (rule) {
    const selected = matches.find((r) => r.key === rule.selected_node_set_key);
    const overridden = matches.find(
      (r) => r.key === rule.overridden_node_set_key,
    );
    if (
      !selected ||
      selected.faction_key !== p.faction.key ||
      !overridden ||
      overridden.faction_key ||
      matches.length !== 2
    )
      throw new Error(`Override source evidence changed: ${p.faction.key}`);
    return [selected];
  }
  if (matches.length > 1)
    throw new Error(
      `Unreviewed overlapping node-set selectors: ${p.faction.key}`,
    );
  return matches;
}

export const SCRIPT_COLUMNS = [
  "mechanic_id",
  "mechanic_type",
  "technology_key",
  "scope_kind",
  "scope_faction_key",
  "scope_culture_key",
  "script_campaign_key",
  "campaign_scope",
  "operation",
  "trigger",
  "target_type",
  "target_key",
  "threshold",
  "comparison",
  "value",
  "reward_type",
  "human_only",
  "allow_allies",
  "counter_policy",
  "initially_locked",
  "relock_policy",
  "combination_rule",
  "interpretation_status",
  "source_file",
  "source_start_line",
  "source_end_line",
  "source_sha256",
  "evidence_id",
  "behavior_evidence_id",
];
