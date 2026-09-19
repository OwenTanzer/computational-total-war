"""Progressive retrieval: base unit -> candidate index -> shared evidence."""
import argparse
import json
from pathlib import Path
from modifier_reference import ROOT, DEFAULT_DATA, open_reference, records


def dicts(cursor):
    return [dict(r) for r in cursor.fetchall()]


def page(db, sql, params, limit, offset):
    total = db.execute('SELECT COUNT(*) FROM (' + sql + ')', params).fetchone()[0]
    entries = dicts(db.execute(sql + ' LIMIT ? OFFSET ?', [*params,limit,offset]))
    return {'total':total,'offset':offset,'limit':limit,'next_offset':offset+limit if offset+limit<total else None,'entries':entries}


def base_unit(key):
    found = []
    for p in sorted((ROOT / 'data/unit_stats/normalized').glob('*.csv')):
        for line, row in records(p):
            if row['unit_key'] == key:
                found.append((p,line,row))
    if not found:
        raise ValueError('Unknown roster unit key: '+key)
    path,line,r = found[0]
    fields = ['unit_key','unit_name','tactical_category','tier','entity_count','total_hp','armour',
              'melee_attack','melee_defence','leadership','speed','weapon_base_damage','weapon_ap_damage',
              'charge_bonus','ammunition','range','reload_time','missile_base_damage','missile_ap_damage',
              'campaign_recruit_cost','campaign_upkeep','multiplayer_cost','data_quality_status']
    return {'base_stats':{k:r[k] for k in fields},'context':'unmodified rank-0 base; original unit dataset remains authoritative',
            'base_record_references':[{'path':p.relative_to(ROOT).as_posix(),'row':n} for p,n,_ in found],
            'modifier_query':f'python3 scripts/query-modifier-reference.py unit {key} --modifiers'}


def query(args):
    if args.command == 'unit' and not args.modifiers:
        return base_unit(args.key)  # No modifier database is opened for base queries.
    db, manifest = open_reference(args.data)
    envelope = {'patch':manifest['patch'],'interpretation':'potential relevance only; acquisition, active scope and stacking are not evaluated'}
    if args.command == 'unit':
        unit = db.execute('SELECT * FROM units WHERE unit_key=?',(args.key,)).fetchone()
        if unit is None:
            raise ValueError('Unknown roster unit key: '+args.key)
        where,params = ['c.unit_key=?'],[args.key]
        if args.bonus:
            where.append('b.bonus_key=?');params.append(args.bonus)
        if args.rank is not None:
            where.append("(c.kind!='unit_set' OR ts.rank_enabled!='true' OR (? BETWEEN CAST(ts.min_rank AS INTEGER) AND CAST(ts.max_rank AS INTEGER)))")
            params.append(args.rank)
        sw,sp = [],[]
        evidence = getattr(args,'evidence',False)
        omit_personal = not evidence and unit['source_caste'] not in ('lord','hero')
        if args.source_kind:
            sw.append('s.kind=?');sp.append(args.source_kind)
        if args.owner:
            sw.append('o.owner_key=?');sp.append(args.owner)
        if sw:
            where.append('EXISTS(SELECT 1 FROM classified_sources s JOIN source_occurrences so ON so.source_id=s.id JOIN owners o ON o.id=so.owner_id WHERE s.effect_key=b.effect_key AND '+' AND '.join(sw)+(" AND s.scope_classification!='character_only'" if omit_personal else '')+')')
            params.extend(sp)
        elif omit_personal:
            where.append("(NOT EXISTS(SELECT 1 FROM sources s WHERE s.effect_key=b.effect_key) OR EXISTS(SELECT 1 FROM classified_sources s WHERE s.effect_key=b.effect_key AND s.scope_classification!='character_only'))")
        common = ' FROM unit_binding_candidates c JOIN bindings b ON b.id=c.binding_id JOIN effects e ON e.effect_key=b.effect_key LEFT JOIN target_sets ts ON c.kind=\'unit_set\' AND ts.set_key=c.target_key WHERE '+' AND '.join(where)
        sql = 'SELECT DISTINCT b.id binding_id,b.effect_key,e.label,b.bonus_key,b.route,b.record_id'+common+' ORDER BY b.effect_key,b.bonus_key,b.id'
        result = page(db,sql,params,args.limit,args.offset)
        for entry in result['entries']:
            entry['candidate_paths'] = dicts(db.execute('SELECT c.kind,c.target_key,c.status,ts.rank_enabled,ts.min_rank,ts.max_rank,ts.special_category FROM unit_binding_candidates c LEFT JOIN target_sets ts ON c.kind=\'unit_set\' AND ts.set_key=c.target_key WHERE c.unit_key=? AND c.binding_id=? ORDER BY c.kind,c.target_key',(args.key,entry['binding_id'])))
            source_filter = 's.effect_key=?'
            source_params = [entry['effect_key']]
            if sw:
                source_filter += ' AND EXISTS(SELECT 1 FROM source_occurrences so JOIN owners o ON o.id=so.owner_id WHERE so.source_id=s.id AND '+' AND '.join(sw)+')'
                source_params.extend(sp)
            entry['omitted_character_only_source_count'] = db.execute("SELECT COUNT(*) FROM classified_sources s WHERE "+source_filter+" AND s.scope_classification='character_only'",source_params).fetchone()[0] if omit_personal else 0
            if omit_personal:
                source_filter += " AND s.scope_classification!='character_only'"
            entry['matching_source_counts'] = dict(db.execute('SELECT s.kind,COUNT(*) FROM classified_sources s WHERE '+source_filter+' GROUP BY s.kind',source_params))
            entry['scope_keys_to_check'] = [r[0] for r in db.execute('SELECT DISTINCT s.scope_key FROM classified_sources s WHERE '+source_filter+' ORDER BY s.scope_key',source_params)]
            entry['source_scope_classifications'] = dict(db.execute('SELECT s.scope_classification,COUNT(*) FROM classified_sources s WHERE '+source_filter+' GROUP BY s.scope_classification',source_params)) or {'unresolved_source':0}
            activation = db.execute('SELECT status,rank_status,evidence_json FROM binding_activation WHERE binding_id=?',(entry['binding_id'],)).fetchone()
            entry['activation_status'] = activation['status'] if activation else 'not_evaluated'
            for candidate_path in entry['candidate_paths']:
                candidate_path['rank_match'] = None if args.rank is None or candidate_path['rank_enabled'] != 'true' else int(candidate_path['min_rank']) <= args.rank <= int(candidate_path['max_rank'])
                candidate_path['rank_status'] = activation['rank_status'] if activation else 'rank_not_queried' if args.rank is None else 'rank_predicate_match' if candidate_path['rank_match'] is True else 'rank_predicate_mismatch' if candidate_path['rank_match'] is False else 'no_rank_predicate_in_target_path'
                candidate_path['eligibility'] = 'unresolved_activation' if activation else 'candidate_only'
            entry['details_query'] = 'effect '+entry['effect_key']
        envelope.update(unit=dict(unit),filters={'bonus':args.bonus,'unit_rank':args.rank,'source_kind':args.source_kind,'source_owner':args.owner},
                        view='evidence' if evidence else 'ordinary_unit_candidates',
                        scope_policy='character-only sources omitted for non-character units; unknown scopes retained; effect/source queries preserve all evidence' if omit_personal else 'all source scopes retained; source owner is not recipient or mount identity',
                        filter_meaning='owner selects source ownership, not proof that this owner can recruit or buff this unit',
                        bonus_groups=page(db,'SELECT b.bonus_key,COUNT(DISTINCT b.id) candidate_bindings'+common+' GROUP BY b.bonus_key ORDER BY candidate_bindings DESC,b.bonus_key',params,min(args.limit,10),args.offset),
                        candidates=result,
                        shared_bindings_not_indexed_per_unit=db.execute("SELECT COUNT(*) FROM bindings WHERE status!='unit_target_indexed'").fetchone()[0],
                        gaps_query='gaps --kind bindings')
    elif args.command == 'effect':
        effect = db.execute('SELECT * FROM effects WHERE effect_key=?',(args.key,)).fetchone()
        if effect is None:
            raise ValueError('Unknown effect: '+args.key)
        source_filter, params = 's.effect_key=?',[args.key]
        if args.source_kind:
            source_filter += ' AND s.kind=?';params.append(args.source_kind)
        if args.owner:
            source_filter += ' AND EXISTS(SELECT 1 FROM source_occurrences so JOIN owners o ON o.id=so.owner_id WHERE so.source_id=s.id AND o.owner_key=?)';params.append(args.owner)
        envelope.update(effect=dict(effect),bindings=page(db,'SELECT * FROM bindings WHERE effect_key=? ORDER BY id',[args.key],args.limit,args.offset),
                        sources=page(db,'SELECT s.id,s.kind,s.source_key,s.label,s.skill_level,s.scope_key,s.scope_classification,s.scope_record_id,s.value,s.record_type,s.conditions_json FROM classified_sources s WHERE '+source_filter+' ORDER BY s.kind,s.source_key,s.skill_level,s.id',params,args.limit,args.offset),
                        source_details='source <id> returns owner/variant/node references; levels are alternatives, not independent bonuses')
        for binding in envelope['bindings']['entries']:
            activation = db.execute('SELECT * FROM binding_activation WHERE binding_id=?',(binding['id'],)).fetchone()
            if activation:
                activation=dict(activation);activation['evidence']=json.loads(activation.pop('evidence_json'))
                binding['activation']=activation
    elif args.command == 'source':
        row = db.execute('SELECT * FROM classified_sources WHERE id=?',(args.key,)).fetchone()
        if row is None:
            raise ValueError('Unknown source id')
        source = dict(row);source.pop('canonical_key')
        source['conditions'] = json.loads(source.pop('conditions_json'))
        scope = db.execute("SELECT id,payload_json FROM source_records WHERE table_key='campaign_effect_scopes_tables' AND json_extract(payload_json,'$.key')=?",(source['scope_key'],)).fetchone()
        where,params = ['so.source_id=?'],[args.key]
        if args.owner:
            where.append('o.owner_key=?');params.append(args.owner)
        sql = 'SELECT o.kind,o.owner_key,o.label,o.race_slug,o.faction_key,o.source_path,so.source_row,so.node_key,so.node_set_key,so.variant_key,so.campaign_key FROM source_occurrences so JOIN owners o ON o.id=so.owner_id WHERE '+' AND '.join(where)+' ORDER BY o.owner_key,so.node_set_key,so.node_key,so.source_row'
        envelope.update(source=source,scope={'record_id':scope['id'],'fields':json.loads(scope['payload_json'])} if scope else {'status':'unresolved_scope'},occurrences=page(db,sql,params,args.limit,args.offset),
                        prerequisites='Follow each owner source_path and node_key to the existing skill/technology dataset; they remain authoritative for prerequisites and locks.')
    elif args.command == 'record':
        row = db.execute('SELECT r.*,t.source_path FROM source_records r JOIN source_tables t USING(table_key) WHERE r.id=?',(args.key,)).fetchone()
        if row is None:
            raise ValueError('Unknown source-record id')
        row = dict(row);row['fields'] = json.loads(row.pop('payload_json'))
        links = dicts(db.execute('SELECT * FROM schema_links WHERE table_key=? ORDER BY column_key',(row['table_key'],)))
        for link in links:
            link['value'] = row['fields'].get(link['column_key'])
            if link['status']=='in_extraction' and link['value']:
                sql = 'SELECT id,source_row,payload_json FROM source_records WHERE table_key=? AND json_extract(payload_json,?)=? ORDER BY id'
                link['matching_records'] = page(db,sql,[link['target_table'],'$.'+link['target_column'],link['value']],args.limit,args.offset)
        envelope.update(record=row,references=links)
    elif args.command == 'table':
        row = db.execute('SELECT * FROM source_tables WHERE table_key=?',(args.key,)).fetchone()
        if row is None:
            raise ValueError('Unknown table')
        envelope.update(table=dict(row),schema=dicts(db.execute('SELECT * FROM schema_fields WHERE table_key=? ORDER BY column_key',(args.key,))),
                        records=page(db,'SELECT id,source_row,payload_json FROM source_records WHERE table_key=? ORDER BY id',[args.key],args.limit,args.offset))
    elif args.command == 'gaps':
        options = {
            'bindings':("SELECT * FROM bindings WHERE status!='unit_target_indexed' ORDER BY target_table,id",[]),
            'sets':("SELECT * FROM set_coverage WHERE status!='selector_candidates_indexed' ORDER BY status,set_key",[]),
            'sources':('SELECT o.source_path,g.* FROM source_gaps g JOIN owners o ON o.id=g.owner_id ORDER BY owner_id,source_row',[]),
            'schema':("SELECT * FROM schema_links WHERE status='unresolved_reference' ORDER BY table_key,column_key",[]),
            'effects':('SELECT * FROM effect_coverage WHERE source_count>0 AND binding_count=0 ORDER BY effect_key',[]),
        }
        sql,params = options[args.kind]
        envelope.update(kind=args.kind,meaning='Unindexed/unresolved does not mean absent in the game or necessarily worth further extraction.',results=page(db,sql,params,args.limit,args.offset))
    elif args.command == 'inventory':
        envelope.update(tables=page(db,'SELECT table_key,family,row_count FROM source_tables ORDER BY family,table_key',[],args.limit,args.offset))
    db.close()
    return envelope


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command',choices=['unit','effect','source','record','table','gaps','inventory'])
    p.add_argument('key',nargs='?')
    p.add_argument('--data',type=Path,default=DEFAULT_DATA)
    p.add_argument('--modifiers',action='store_true')
    p.add_argument('--evidence',action='store_true',help='Unit modifier view including character-only sources; does not disable an explicit rank filter')
    p.add_argument('--bonus')
    p.add_argument('--rank',type=int)
    p.add_argument('--source-kind',choices=['skill','technology'])
    p.add_argument('--owner',help='Exact character subtype or technology-owning faction key; a source-ownership filter only')
    p.add_argument('--kind',choices=['bindings','sets','sources','schema','effects'],default='bindings')
    p.add_argument('--limit',type=int,default=10)
    p.add_argument('--offset',type=int,default=0)
    args = p.parse_args()
    if args.command not in ('gaps','inventory') and not args.key:
        p.error('A key is required')
    if not 1 <= args.limit <= 100 or args.offset < 0 or (args.rank is not None and args.rank < 0):
        p.error('Use limit 1–100, nonnegative offset and rank')
    if args.command == 'unit' and not args.modifiers and (args.bonus or args.rank is not None or args.source_kind or args.owner or args.evidence):
        p.error('Add --modifiers when filtering modifier relationships')
    try:
        print(json.dumps(query(args),ensure_ascii=False,indent=2))
    except (ValueError,FileNotFoundError) as e:
        p.exit(1,str(e)+'\n')


if __name__ == '__main__':
    main()
