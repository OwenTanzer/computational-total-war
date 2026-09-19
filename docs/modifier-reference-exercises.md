# Modifier retrieval exercises

Snapshot: WARHAMMER III 8.1.1 / Steam build 24237342. These are source-backed
retrieval checks, not live campaign tests or a combined acquired build.

## Sea Guard regression

Both `wh2_main_hef_inf_lothern_sea_guard_0` and `_1`, source owner
`wh2_main_hef_teclis`, return 10 default bindings versus 17 in `--evidence`.
Seven personal-source bindings are excluded from ordinary-unit results. Army
sources for Bow Master and Militia Master remain; Favourable Winds' rank-7 armour
binding is absent at rank 6 and present at rank 7. Ordinary spearmen do not enter
Bow Master's ammunition target set. Distinct shielded-armour and unshielded
Sea Guard morale relationships remain variant-specific.

Seasoned Militia's weapon-enable binding remains **unresolved activation/rank**
at both queried ranks. Existing junction → weapon → projectile evidence contains
no independently established rank predicate. Its reload binding separately has
an explicit unit-set gate of ranks 7–9. No condition is transferred between them.

## Pink Horrors

Exact owners: skill subtype `wh3_main_tze_kairos`; technology faction
`wh3_main_tze_oracles_of_tzeentch` (Oracles of Tzeentch). Compare ordinary Pink
`wh3_main_tze_inf_pink_horrors_0`, Exalted Pink `_1`, and Blue
`wh3_main_tze_inf_blue_horrors_0`.

```bash
python3 scripts/query-modifier-reference.py unit wh3_main_tze_inf_pink_horrors_0
python3 scripts/query-modifier-reference.py unit wh3_main_tze_inf_pink_horrors_0 --modifiers --owner wh3_main_tze_kairos --rank 7 --limit 100
python3 scripts/query-modifier-reference.py unit wh3_main_tze_inf_pink_horrors_0 --modifiers --owner wh3_main_tze_oracles_of_tzeentch --limit 100
python3 scripts/query-modifier-reference.py effect wh3_main_effect_ability_enable_arcane_mirth_tze_horrors --owner wh3_main_tze_oracles_of_tzeentch
```

The base path remains independent of the modifier database. Ordinary Pink has
80 entities, 6,400 health, 25 armour, 20 ammunition and 130 range in the normalized
rank-0/ultra snapshot. Exalted Pink has 80/7,200/35/20/130; Blue has
160/7,680/5/4/90 for those same fields. These are not campaign-adjusted values.

At rank 7, all three have 12 Kairos-linked default binding results; at rank 6,
ordinary Pink has nine. The three added bindings are independently rank-gated
Horrific Advancement effects. Character-only Kairos sources remain in evidence
mode but do not mix into these ordinary-unit results.

| Source | Retained values and target |
|---|---|
| Accursed Horrors, level 3 | Missile damage source value 16 (separate base/AP bindings); barrier health source value 10; all three Horror types |
| Horrific Advancement | Leadership 6, missile resistance 15, battle speed 10; explicit unit ranks 7–9; all three |
| Oracle | Barrier replenishment delay -20; own force while commanding |
| Thaumaturgic Rejuvenation | Barrier replenishment delay -25 and replenishment rate 25; own force while commanding |
| Bewitching Potency | Barrier health 20; own force while commanding |
| Exalted Locus of Conjuration | Ammunition 25 and melee weapon strength 25 (base/AP bindings); all three; faction's own forces |
| Greater Locus of Change | Arcane Mirth enable value 1: ordinary Pink and Blue, not Exalted; recruitment cost -5: both Pink types, not Blue |

Values are the original source numbers. Their arithmetic/stacking is not
evaluated. Skill levels are alternatives, not additive repetitions. Relevant
canonical skill keys are `wh3_main_skill_tze_lord_army_buff_1_1`,
`wh3_main_skill_tze_lord_army_buff_3_1`, `wh3_main_skill_innate_tze_kairos`,
`wh3_main_skill_tze_kairos_self_6` and `_8`; technology keys are
`wh3_main_tech_tze_2_8` and `wh3_main_tech_tze_2_6`. Source pages retain their
exact owner CSV rows, node sets and prerequisites.

The technology view returns eight bindings for ordinary Pink, seven for Exalted,
seven for Blue. Equal totals for Exalted and Blue conceal different membership:
Exalted already has Arcane Mirth in the base ability lookup, while Blue does not
receive the Pink-specific recruitment reduction. Regression tests check identities,
not just counts.

### What this exercise does not establish

The Arcane Mirth grant is linked to its actual unit-set/ability junction, and the
retained special-ability record marks it passive. The base ability record has
`requires_effect_enabling=false`; that does not grant it to units lacking the
base ability or technology grant. Runtime trigger/phase transitions are not
evaluated by this reference. The retained phase with the same key contains
`mana_regen_mod=0.2000`, but matching names alone do not establish an activation
or phase-transition relationship. Do not promote that into an unconditional
mana contribution. A complete ability-to-phase/usage-condition trace remains a
separate unresolved question; this exercise did not extract more tables.

Character-owner identity across lord/hero bodies and mounts also remains
unresolved. Scope classification addresses ordinary troops, not that identity
mapping. All resulting lists remain candidates rather than active buffs.
