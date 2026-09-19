"""Behavior tests for retrieval boundaries and dangerous targeting edge cases."""
import importlib.util
import json
import subprocess
import sys
import unittest
import sqlite3
from unittest.mock import patch
from pathlib import Path
from types import SimpleNamespace
from modifier_reference import ROOT, selector_match, membership_status, open_reference, scope_classification

DATA=Path(sys.argv.pop(1)).resolve() if len(sys.argv)>1 and not sys.argv[1].startswith('-') else ROOT/'data/effect_semantics'
spec=importlib.util.spec_from_file_location('query_reference',ROOT/'scripts/query-modifier-reference.py')
query_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(query_module)


class Targeting(unittest.TestCase):
    def test_scope_is_recipient_based_not_label_based(self):
        self.assertEqual(scope_classification({'key':'army_buff','target':'character'}),'character_only')
        self.assertEqual(scope_classification({'key':'personal','target':'force'}),'force_or_army')
        self.assertEqual(scope_classification({'target':'unrecognized'}),'unresolved_scope')
        self.assertEqual(scope_classification(None),'unresolved_scope')

    def test_compound_selector_keeps_disagreement_unknown(self):
        row=dict(unit_record='a',unit_class='',unit_category='',unit_caste='lord')
        self.assertEqual(selector_match(row,dict(unit_key='a',source_caste='infantry')),'possible')
        self.assertEqual(selector_match(row,dict(unit_key='a',source_caste='lord')),'match')

    def test_exclusion_and_special_category(self):
        self.assertEqual(membership_status(['match'],['match']),'excluded')
        self.assertEqual(membership_status(['match'],['possible']),'conditional_selector')
        self.assertEqual(membership_status(['match'],[],'mistwalker'),'conditional_selector')
        self.assertEqual(membership_status([],[]),'no_match')

    def test_base_query_never_needs_modifier_database(self):
        a=SimpleNamespace(command='unit',modifiers=False,key='wh2_main_hef_inf_lothern_sea_guard_0',data=Path('/does/not/exist'))
        result=query_module.query(a)
        self.assertIn('base_stats',result)
        self.assertNotIn('candidates',result)

    def test_unknown_unit_is_not_empty_success(self):
        with self.assertRaisesRegex(ValueError,'Unknown roster unit'):
            query_module.base_unit('nonexistent_unit')


class FullSnapshot(unittest.TestCase):
    def unit_query(self,key='wh2_main_hef_inf_lothern_sea_guard_0',**kwargs):
        args=dict(command='unit',key=key,data=DATA,modifiers=True,bonus=None,rank=None,source_kind=None,owner='wh2_main_hef_teclis',limit=100,offset=0,evidence=False)
        args.update(kwargs)
        return query_module.query(SimpleNamespace(**args))

    @classmethod
    def setUpClass(cls):
        cls.db,_=open_reference(DATA)

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_seaguard_variants_and_spearmen(self):
        effect='wh2_main_effect_force_stat_ammunition_hef_archer_seaguard_boltthrower_sister_shadow'
        found={r[0] for r in self.db.execute('SELECT DISTINCT c.unit_key FROM unit_binding_candidates c JOIN bindings b ON b.id=c.binding_id WHERE b.effect_key=?',(effect,))}
        self.assertIn('wh2_main_hef_inf_lothern_sea_guard_0',found)
        self.assertIn('wh2_main_hef_inf_lothern_sea_guard_1',found)
        self.assertNotIn('wh2_main_hef_inf_spearmen_0',found)

    def test_rank_filter_does_not_invent_permanence(self):
        base=dict(command='unit',key='wh2_main_hef_inf_lothern_sea_guard_0',data=DATA,modifiers=True,bonus='armour_mod',source_kind='skill',owner='wh2_main_hef_teclis',limit=100,offset=0)
        before=query_module.query(SimpleNamespace(**base,rank=6))
        after=query_module.query(SimpleNamespace(**base,rank=7))
        effect='wh2_main_effect_force_stat_armour_archers_seaguard_boltthrower_sister_shadow_rank7'
        self.assertNotIn(effect,{r['effect_key'] for r in before['candidates']['entries']})
        self.assertIn(effect,{r['effect_key'] for r in after['candidates']['entries']})
        self.assertIn('potential relevance',after['interpretation'])

    def test_skill_levels_remain_alternatives(self):
        effect='wh2_main_effect_force_stat_ammunition_hef_archer_seaguard_boltthrower_sister_shadow'
        rows=self.db.execute('SELECT skill_level,value FROM sources WHERE kind=\'skill\' AND effect_key=? ORDER BY skill_level',(effect,)).fetchall()
        self.assertEqual(len(rows),3)
        self.assertEqual([r['skill_level'] for r in rows],['1','2','3'])

    def test_personal_sources_separated_for_both_variants(self):
        for suffix in ('0','1'):
            key='wh2_main_hef_inf_lothern_sea_guard_'+suffix
            ordinary=self.unit_query(key)['candidates']
            evidence=self.unit_query(key,evidence=True)['candidates']
            self.assertEqual(ordinary['total'],10)
            self.assertEqual(evidence['total'],17)
            self.assertTrue(all('character_only' not in x['source_scope_classifications'] for x in ordinary['entries']))
            self.assertTrue(any('character_only' in x['source_scope_classifications'] for x in evidence['entries']))
            bonuses={x['bonus_key'] for x in ordinary['entries']}
            self.assertTrue({'ammo_mod','melee_attack_mod','melee_defence_mod'} <= bonuses)
            # Favourable Winds must remain genuinely rank-filtered in both variants.
            effect='wh2_main_effect_force_stat_armour_archers_seaguard_boltthrower_sister_shadow_rank7'
            self.assertNotIn(effect,{x['effect_key'] for x in self.unit_query(key,rank=6)['candidates']['entries']})
            self.assertIn(effect,{x['effect_key'] for x in self.unit_query(key,rank=7)['candidates']['entries']})

    def test_unknown_and_mixed_scopes_are_not_discarded_by_effect_key(self):
        # Perturb a snapshot copy: a newly encountered recipient must survive,
        # while mixed personal/army sources must filter only the personal source.
        for classification in ('unresolved_scope','force_or_army'):
            db=sqlite3.connect(':memory:');self.db.backup(db);db.row_factory=sqlite3.Row
            effect='wh2_main_effect_force_stat_ammunition_hef_archer_seaguard_boltthrower_sister_shadow'
            db.execute("UPDATE sources SET scope_key='character_to_character_own' WHERE effect_key=? AND skill_level='1'",(effect,))
            db.execute("UPDATE scope_classifications SET classification=? WHERE scope_key='general_to_force_own'",(classification,))
            with patch.object(query_module,'open_reference',return_value=(db,{'patch':'test'})):
                result=self.unit_query()['candidates']['entries']
            entry=next(x for x in result if x['effect_key']==effect)
            self.assertEqual(entry['source_scope_classifications'],{classification:2})
            self.assertEqual(entry['omitted_character_only_source_count'],1)

    def test_weapon_activation_is_unresolved_independently_of_rank_set(self):
        effect='wh3_dlc27_effect_tech_vs_infantry_bows_hef_inf_r7'
        for suffix in ('0','1'):
            for rank in (6,7):
                entries=self.unit_query('wh2_main_hef_inf_lothern_sea_guard_'+suffix,rank=rank,owner='wh2_main_hef_order_of_loremasters')['candidates']['entries']
                entries=[x for x in entries if x['effect_key']==effect]
                weapon=next(x for x in entries if x['bonus_key']=='enable')
                self.assertEqual(weapon['activation_status'],'unresolved_weapon_activation')
                self.assertTrue(all(x['rank_status']=='unresolved_rank_activation' and x['rank_match'] is None for x in weapon['candidate_paths']))
                self.assertEqual(any(x['bonus_key']=='reload' for x in entries),rank==7)

    def test_actual_variant_specific_bindings_remain_distinct(self):
        sql='SELECT DISTINCT b.effect_key FROM unit_binding_candidates c JOIN bindings b ON b.id=c.binding_id WHERE c.unit_key=?'
        a={r[0] for r in self.db.execute(sql,('wh2_main_hef_inf_lothern_sea_guard_0',))}
        b={r[0] for r in self.db.execute(sql,('wh2_main_hef_inf_lothern_sea_guard_1',))}
        self.assertIn('wh3_dlc27_tech_upgrade_sea_guard',a-b)
        self.assertIn('wh2_dlc15_effect_force_unit_stat_armour_hef_shields',b-a)

    def test_pink_horror_technology_controls(self):
        owner='wh3_main_tze_oracles_of_tzeentch'
        units=['wh3_main_tze_inf_pink_horrors_0','wh3_main_tze_inf_pink_horrors_1','wh3_main_tze_inf_blue_horrors_0']
        effects=[{x['effect_key'] for x in self.unit_query(k,owner=owner)['candidates']['entries']} for k in units]
        grant='wh3_main_effect_ability_enable_arcane_mirth_tze_horrors'
        cost='wh3_main_effect_recruitment_cost_tze_pink_horrors'
        self.assertEqual([grant in x for x in effects],[True,False,True])
        self.assertEqual([cost in x for x in effects],[True,True,False])
        # Exalted does not need that grant: its base ability lookup already has it.
        base={r[0] for r in self.db.execute("SELECT unit_key FROM unit_targets WHERE kind='ability' AND target_key='wh3_main_unit_passive_arcane_mirth'")}
        self.assertNotIn(units[0],base);self.assertIn(units[1],base);self.assertNotIn(units[2],base)

    def test_pink_horror_rank_and_personal_scope(self):
        key='wh3_main_tze_inf_pink_horrors_0';owner='wh3_main_tze_kairos'
        low=self.unit_query(key,owner=owner,rank=6)['candidates']
        high=self.unit_query(key,owner=owner,rank=7)['candidates']
        raw=self.unit_query(key,owner=owner,rank=7,evidence=True)['candidates']
        self.assertEqual((low['total'],high['total']),(9,12))
        self.assertGreater(raw['total'],high['total'])
        self.assertTrue(all('character_only' not in x['source_scope_classifications'] for x in high['entries']))
        difference={x['bonus_key'] for x in high['entries'] if x['binding_id'] not in {x['binding_id'] for x in low['entries']}}
        self.assertEqual(difference,{'morale','unit_damage_resistance_missile_mod','mod_land_movement_battle'})

    def test_coverage_includes_entire_extraction(self):
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM source_tables').fetchone()[0],220)
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM source_records').fetchone()[0],109408)
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM bindings').fetchone()[0],23110)
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM units').fetchone()[0],1669)

    def test_pagination_is_complete_without_duplicates(self):
        base=dict(command='unit',key='wh2_main_hef_inf_lothern_sea_guard_0',data=DATA,modifiers=True,bonus=None,rank=None,source_kind='skill',owner='wh2_main_hef_teclis',limit=5)
        ids=[];offset=0;total=None
        while offset is not None:
            result=query_module.query(SimpleNamespace(**base,offset=offset))['candidates']
            total=result['total'];ids.extend(r['binding_id'] for r in result['entries']);offset=result['next_offset']
        self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual(len(ids),total)


if __name__=='__main__':
    unittest.main()
