"""Behavior tests for retrieval boundaries and dangerous targeting edge cases."""
import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from modifier_reference import ROOT, selector_match, membership_status, open_reference

DATA=Path(sys.argv.pop(1)).resolve() if len(sys.argv)>1 and not sys.argv[1].startswith('-') else ROOT/'data/effect_semantics'
spec=importlib.util.spec_from_file_location('query_reference',ROOT/'scripts/query-modifier-reference.py')
query_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(query_module)


class Targeting(unittest.TestCase):
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
