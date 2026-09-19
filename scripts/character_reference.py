"""Explicit character forms and mount-grant evidence, without name-key inference."""
import json
from collections import defaultdict
from modifier_reference import ROOT, records, compact


def build_characters(db, lock):
    db.executescript('''
    CREATE TABLE character_scope_policies(scope_key TEXT PRIMARY KEY,identity_policy TEXT);
    CREATE TABLE character_forms(owner_id INTEGER REFERENCES owners,unit_key TEXT,relation TEXT,evidence_json TEXT,PRIMARY KEY(owner_id,unit_key,relation));
    CREATE INDEX character_form_unit ON character_forms(unit_key,owner_id);
    CREATE TABLE mount_records(ancillary_key TEXT PRIMARY KEY,unit_key TEXT,evidence_json TEXT);
    CREATE TABLE mount_acquisitions(id INTEGER PRIMARY KEY,owner_id INTEGER REFERENCES owners,unit_key TEXT,ancillary_key TEXT REFERENCES mount_records,skill_key TEXT,skill_level TEXT,node_key TEXT,node_set_key TEXT,source_row INTEGER,node_rank TEXT,rank_status TEXT,level_evidence_json TEXT,effect_keys_json TEXT);
    CREATE INDEX mount_owner ON mount_acquisitions(owner_id,unit_key);
    ''')
    for scope_key,payload in db.execute("SELECT sc.scope_key,r.payload_json FROM scope_classifications sc JOIN source_records r ON r.id=sc.record_id").fetchall():
        r=json.loads(payload)
        policy='same_source_character' if r['source']=='character' and r['target']=='character' and r['location']=='character' and r['ownership']=='yours' else 'recipient_context_unresolved'
        db.execute('INSERT INTO character_scope_policies VALUES(?,?)',(scope_key,policy))
    db.executescript("""
    DROP VIEW classified_sources;
    CREATE VIEW classified_sources AS SELECT s.*,COALESCE(sc.classification,'unresolved_scope') scope_classification,sc.recipient,sc.record_id scope_record_id,COALESCE(cp.identity_policy,'recipient_context_unresolved') personal_identity_policy FROM sources s LEFT JOIN scope_classifications sc USING(scope_key) LEFT JOIN character_scope_policies cp USING(scope_key);
    """)
    def raw(table):
        for path in sorted((ROOT/'data/skill_trees/source_exports/db'/table).glob('*.tsv')):
            for line, row in records(lock(path),'\t'):
                yield row,dict(path=path.relative_to(ROOT).as_posix(),row=line,fields=row)
    subtypes={r['key']:(r,e) for r,e in raw('agent_subtypes_tables')}
    mounts={}
    for r,e in raw('ancillaries_tables'):
        if r['category']=='mount' and r['provided_bodyguard_unit']:
            mounts[r['key']]=(r,e)
            db.execute('INSERT INTO mount_records VALUES(?,?,?)',(r['key'],r['provided_bodyguard_unit'],compact(e)))
    for owner_id,owner_key,path in db.execute("SELECT id,owner_key,source_path FROM owners WHERE kind='skill' ORDER BY id").fetchall():
        subtype=subtypes.get(owner_key)
        if subtype and subtype[0]['associated_unit_override']:
            db.execute('INSERT INTO character_forms VALUES(?,?,?,?)',(owner_id,subtype[0]['associated_unit_override'],'associated_unit_override',compact(subtype[1])))
        rows=list(records(lock(ROOT/path)))
        for line,r in rows:
            if r['record_type']!='ancillary_grant' or r['ancillary_key'] not in mounts:
                continue
            ancillary,e=mounts[r['ancillary_key']]
            unit=ancillary['provided_bodyguard_unit']
            def same_context(x):
                return all(x[k]==r[k] for k in ('node_key','node_set_key','skill_key','skill_level'))
            levels=[dict(path=path,row=n,fields=x) for n,x in rows if x['record_type']=='skill_level' and same_context(x)]
            # Effect keys are related evidence from the SAME node/level, not the
            # acquisition route. A mount may have no effect binding at all.
            effects=sorted({x['effect_key'] for _,x in rows if x['effect_key'] and same_context(x)})
            ranks={x['fields']['level_unlocked_at_rank'] for x in levels}
            status='rank_fields_agree_effective_rank_unresolved' if ranks=={r['skill_unlocked_at_rank']} and r['skill_unlocked_at_rank'] else 'rank_fields_differ_effective_rank_unresolved' if ranks and r['skill_unlocked_at_rank'] else 'rank_evidence_incomplete'
            db.execute('INSERT INTO mount_acquisitions VALUES(NULL,?,?,?,?,?,?,?,?,?,?,?,?)',(owner_id,unit,r['ancillary_key'],r['skill_key'],r['skill_level'],r['node_key'],r['node_set_key'],line,r['skill_unlocked_at_rank'],status,compact(levels),compact(effects)))
            evidence=dict(grant=dict(path=path,row=line,fields=r),ancillary=e)
            # Multiple acquisition nodes remain in mount_acquisitions; identity
            # needs only a proven owner -> body relationship.
            db.execute('INSERT OR IGNORE INTO character_forms VALUES(?,?,?,?)',(owner_id,unit,'skill_granted_mount',compact(evidence)))


def identity_status(db, owner_id, unit):
    if unit['source_caste'] not in ('lord','hero'):
        return 'recipient_is_not_character'
    if db.execute('SELECT 1 FROM character_forms WHERE owner_id=? AND unit_key=?',(owner_id,unit['unit_key'])).fetchone():
        return 'source_character_identity_match'
    owner_known=db.execute('SELECT 1 FROM character_forms WHERE owner_id=?',(owner_id,)).fetchone()
    unit_known=db.execute('SELECT 1 FROM character_forms WHERE unit_key=?',(unit['unit_key'],)).fetchone()
    return 'source_character_identity_mismatch' if owner_known and unit_known else 'unresolved_character_identity'


def personal_allowed_sql(unit):
    """Predicate for occurrence alias o; unresolved identities remain explicit."""
    if unit['source_caste'] not in ('lord','hero'):
        return '0',[]
    return "(s.personal_identity_policy!='same_source_character' OR EXISTS(SELECT 1 FROM character_forms cf WHERE cf.owner_id=o.id AND cf.unit_key=?) OR NOT EXISTS(SELECT 1 FROM character_forms cf WHERE cf.owner_id=o.id) OR NOT EXISTS(SELECT 1 FROM character_forms cf WHERE cf.unit_key=?))",[unit['unit_key'],unit['unit_key']]


def validate_characters(db, check):
    cache={}
    def evidence(e):
        if e['path'] not in cache:
            cache[e['path']]=dict(records(ROOT/e['path'],'\t' if e['path'].endswith('.tsv') else ','))
        check(cache[e['path']].get(e['row'])==e['fields'],'Character evidence changed')
    for row in db.execute('SELECT * FROM mount_records'):
        e=json.loads(row['evidence_json']);evidence(e)
        check(e['fields']['category']=='mount' and e['fields']['provided_bodyguard_unit']==row['unit_key'] and e['fields']['key']==row['ancillary_key'],'Invalid mount record')
    for row in db.execute('SELECT cf.*,o.owner_key FROM character_forms cf JOIN owners o ON o.id=cf.owner_id'):
        e=json.loads(row['evidence_json'])
        if row['relation']=='associated_unit_override':
            evidence(e);check(e['fields']['associated_unit_override']==row['unit_key'] and e['fields']['key']==row['owner_key'],'Incorrect subtype identity')
        else:
            evidence(e['grant']);evidence(e['ancillary'])
            check(e['grant']['fields']['agent_subtype_key']==row['owner_key'] and e['grant']['fields']['ancillary_key']==e['ancillary']['fields']['key'] and e['ancillary']['fields']['provided_bodyguard_unit']==row['unit_key'],'Incorrect mount identity')
    for row in db.execute('SELECT cp.*,r.payload_json FROM character_scope_policies cp JOIN scope_classifications sc USING(scope_key) JOIN source_records r ON r.id=sc.record_id'):
        fields=json.loads(row['payload_json'])
        own=(fields['source'],fields['target'],fields['location'],fields['ownership'])==('character','character','character','yours')
        check(row['identity_policy']==('same_source_character' if own else 'recipient_context_unresolved'),'Character identity scope policy mismatch')
    check(db.execute('SELECT COUNT(*) FROM character_scope_policies').fetchone()[0]==db.execute('SELECT COUNT(*) FROM scope_classifications').fetchone()[0],'Character identity scope coverage differs')
    subtypes={}
    for path in sorted((ROOT/'data/skill_trees/source_exports/db/agent_subtypes_tables').glob('*.tsv')):
        for _,r in records(path,'\t'):
            subtypes[r['key']]=r['associated_unit_override']
    expected=0
    expected_forms=set()
    for owner in db.execute("SELECT * FROM owners WHERE kind='skill'").fetchall():
        if subtypes.get(owner['owner_key']):
            expected_forms.add((owner['id'],subtypes[owner['owner_key']],'associated_unit_override'))
        rows=dict(records(ROOT/owner['source_path']))
        grants={n:r for n,r in rows.items() if r['record_type']=='ancillary_grant' and db.execute('SELECT 1 FROM mount_records WHERE ancillary_key=?',(r['ancillary_key'],)).fetchone()}
        actual=db.execute('SELECT * FROM mount_acquisitions WHERE owner_id=?',(owner['id'],)).fetchall()
        check(len(actual)==len(grants),'Mount grant coverage mismatch');expected+=len(grants)
        for a in actual:
            r=grants[a['source_row']]
            check(all(a[k]==r[k] for k in ('ancillary_key','skill_key','skill_level','node_key','node_set_key')) and a['node_rank']==r['skill_unlocked_at_rank'],'Mount grant context changed')
            levels=json.loads(a['level_evidence_json'])
            wanted=[dict(path=owner['source_path'],row=n,fields=x) for n,x in rows.items() if x['record_type']=='skill_level' and all(x[k]==r[k] for k in ('node_key','node_set_key','skill_key','skill_level'))]
            check(levels==wanted,'Mount skill-level rank evidence lost')
            ranks={x['fields']['level_unlocked_at_rank'] for x in wanted}
            expected_status='rank_fields_agree_effective_rank_unresolved' if ranks=={r['skill_unlocked_at_rank']} and r['skill_unlocked_at_rank'] else 'rank_fields_differ_effective_rank_unresolved' if ranks and r['skill_unlocked_at_rank'] else 'rank_evidence_incomplete'
            check(a['rank_status']==expected_status,'Mount rank classification changed')
            effects=sorted({x['effect_key'] for x in rows.values() if x['effect_key'] and all(x[k]==r[k] for k in ('node_key','node_set_key','skill_key','skill_level'))})
            check(json.loads(a['effect_keys_json'])==effects,'Mount related-effect context changed')
            body=db.execute('SELECT unit_key FROM mount_records WHERE ancillary_key=?',(r['ancillary_key'],)).fetchone()[0]
            check(a['unit_key']==body,'Mount acquisition body mismatch')
            expected_forms.add((owner['id'],body,'skill_granted_mount'))
            check(db.execute("SELECT 1 FROM character_forms WHERE owner_id=? AND unit_key=? AND relation='skill_granted_mount'",(owner['id'],a['unit_key'])).fetchone(),'Mount identity missing')
    check(expected_forms=={tuple(r) for r in db.execute('SELECT owner_id,unit_key,relation FROM character_forms')},'Character body form coverage mismatch')
    return expected
