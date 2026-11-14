#!/usr/bin/env python3
from __future__ import annotations
import copy, hashlib, json, re

CONTRACT='INC_CROSS_SURFACE_INTERACTION_LEDGER_V1'
STATES={'OPEN','INTERRUPTED','COMPLETED','BLOCKED','TRANSFERRED'}
EVENTS={'ALLOCATED','LIFECYCLE','TERMINAL'}
TERMINAL_STATES={'COMPLETED','BLOCKED'}
ALLOWED_TRANSITIONS={
    'OPEN':{'INTERRUPTED','COMPLETED','BLOCKED','TRANSFERRED'},
    'INTERRUPTED':{'OPEN','COMPLETED','BLOCKED','TRANSFERRED'},
    'TRANSFERRED':{'OPEN','COMPLETED','BLOCKED'},
    'COMPLETED':set(),
    'BLOCKED':set(),
}

class Invalid(ValueError): pass

def require(ok, code):
    if not ok: raise Invalid(code)
def text(v): return isinstance(v,str) and bool(v.strip())
def integer(v): return type(v) is int and v>=0
def canonical(v): return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True)
def hash_record(rec):
    clean={k:v for k,v in rec.items() if k!='record_hash'}
    return hashlib.sha256(canonical(clean).encode()).hexdigest()
def _payload(e): return {k:v for k,v in e.items() if k not in {'record_hash','prev_hash','event_cursor'}}

def empty_ledger(project_id,handoff_id,release_id):
    require(all(text(x) for x in (project_id,handoff_id,release_id)),'XCUT034_ID_REQUIRED')
    return {'contract':CONTRACT,'project_id':project_id,'handoff_id':handoff_id,'release_id':release_id,'events':[],'recent_index':[],'last_event_cursor':0}

def _has_secret_field(value):
    blocked={'password','access_token','refresh_token','client_secret','private_key','api_key','cookie','otp','secret_value','raw_secret'}
    if isinstance(value,dict):
        return any(re.sub(r'([a-z0-9])([A-Z])',r'\1_\2',re.sub(r'([A-Z]+)([A-Z][a-z])',r'\1_\2',str(k))).lower().replace('-','_') in blocked or _has_secret_field(v) for k,v in value.items())
    if isinstance(value,list):return any(_has_secret_field(v) for v in value)
    return False

def validate_event_shape(e):
    require(isinstance(e,dict),'XCUT034_EVENT_REQUIRED')
    for k in ('event_id','idempotency_key','project_id','handoff_id','release_id','surface','conversation_ref','timestamp','event_type','status'):
        require(text(e.get(k)),'XCUT034_FIELD_REQUIRED:'+k)
    require(integer(e.get('S')) and e['S']>0,'XCUT034_S_INVALID')
    require(e['event_type'] in EVENTS,'XCUT034_EVENT_TYPE_INVALID'); require(e['status'] in STATES,'XCUT034_STATUS_INVALID')
    require(isinstance(e.get('causal_M'),list) and all(integer(x) for x in e['causal_M']),'XCUT034_CAUSAL_M_INVALID')
    require(e.get('classification') in ('PUBLIC','INTERNAL','CONFIDENTIAL_REDACTED'),'XCUT034_CLASSIFICATION_REQUIRED')
    require(e.get('secrets_present') is False and not _has_secret_field(e),'XCUT034_SECRET_REPLICATION_PROHIBITED')
    for k in ('knowledge_delta','decisions','approvals_rejections','requirements','evidence_refs','open_questions'): require(isinstance(e.get(k),list),'XCUT034_LIST_FIELD_REQUIRED:'+k)
    require(e.get('resume_point') is None or text(e.get('resume_point')),'XCUT034_RESUME_POINT_INVALID')

def _latest_for_s(events,S):
    rows=[x for x in events if x['S']==S]
    return rows[-1] if rows else None

def append_event(ledger,event,max_recent=32):
    require(type(max_recent) is int and 1<=max_recent<=128,'XCUT034_RECENT_BOUND_INVALID')
    validate_chain(ledger)
    require(isinstance(ledger,dict) and ledger.get('contract')==CONTRACT,'XCUT034_LEDGER_REQUIRED'); validate_event_shape(event)
    require(event['project_id']==ledger['project_id'] and event['handoff_id']==ledger['handoff_id'] and event['release_id']==ledger['release_id'],'XCUT034_LEDGER_IDENTITY_MISMATCH')
    out=copy.deepcopy(ledger); events=out['events']
    for old in events:
        if old.get('event_id')==event['event_id']:
            if _payload(old)==_payload(event): return out
            raise Invalid('XCUT034_EVENT_ID_CONFLICT')
        if old.get('idempotency_key')==event['idempotency_key']:
            raise Invalid('XCUT034_IDEMPOTENCY_CONFLICT')
    allocated=[x for x in events if x['S']==event['S'] and x['event_type']=='ALLOCATED']
    latest=_latest_for_s(events,event['S'])
    if event['event_type']=='ALLOCATED':
        require(not allocated,'XCUT034_DUPLICATE_S_ALLOCATION')
        alloc_s=[x['S'] for x in events if x['event_type']=='ALLOCATED']
        if alloc_s: require(event['S']>max(alloc_s),'XCUT034_S_ALLOCATION_ORDER_INVALID')
        require(event['status']=='OPEN','XCUT034_ALLOCATED_STATUS_MUST_BE_OPEN')
    else:
        require(bool(allocated),'XCUT034_LIFECYCLE_WITHOUT_ALLOCATION')
        require(latest is not None,'XCUT034_LATEST_STATE_REQUIRED')
        require(event['status'] in ALLOWED_TRANSITIONS[latest['status']],'XCUT034_ILLEGAL_LIFECYCLE_TRANSITION')
        if event['event_type']=='TERMINAL': require(event['status'] in {'COMPLETED','BLOCKED','TRANSFERRED'},'XCUT034_TERMINAL_STATUS_INVALID')
        if latest['event_type']=='TERMINAL' and latest['status']==event['status']: raise Invalid('XCUT034_DUPLICATE_TERMINAL')
    prev=events[-1]['record_hash'] if events else None
    e=copy.deepcopy(event); e['prev_hash']=prev; e['event_cursor']=int(out.get('last_event_cursor',0))+1; e['record_hash']=hash_record(e)
    events.append(e); out['last_event_cursor']=e['event_cursor']
    latest_map={}
    for x in events:
        latest_map[x['S']]={'S':x['S'],'status':x['status'],'surface':x['surface'],'conversation_ref':x['conversation_ref'],'causal_M':x['causal_M'],'record_hash':x['record_hash'],'event_cursor':x['event_cursor']}
    out['recent_index']=[latest_map[s] for s in sorted(latest_map)[-max_recent:]]
    return out

def validate_chain(ledger):
    require(isinstance(ledger,dict) and ledger.get('contract')==CONTRACT,'XCUT034_LEDGER_REQUIRED')
    require(isinstance(ledger.get('events'),list),'XCUT034_EVENTS_REQUIRED')
    require(all(text(ledger.get(k)) for k in ('project_id','handoff_id','release_id')),'XCUT034_ID_REQUIRED')
    require(type(ledger.get('last_event_cursor')) is int and ledger['last_event_cursor']>=0,'XCUT034_LEDGER_CURSOR_MISMATCH')
    prev=None; allocated=set(); cursor=0; ids=set(); idem=set(); latest={}
    for e in ledger.get('events',[]):
        validate_event_shape(e); require(e.get('event_id') not in ids,'XCUT034_DUPLICATE_EVENT_ID'); require(e.get('idempotency_key') not in idem,'XCUT034_DUPLICATE_IDEMPOTENCY_KEY')
        require(all(e[k]==ledger[k] for k in ('project_id','handoff_id','release_id')),'XCUT034_LEDGER_IDENTITY_MISMATCH')
        ids.add(e['event_id']); idem.add(e['idempotency_key'])
        require(e.get('event_cursor')==cursor+1,'XCUT034_EVENT_CURSOR_NONMONOTONIC'); cursor=e['event_cursor']
        require(e.get('prev_hash')==prev,'XCUT034_HASH_CHAIN_PREV_MISMATCH'); require(e.get('record_hash')==hash_record(e),'XCUT034_HASH_CHAIN_RECORD_MISMATCH')
        if e['event_type']=='ALLOCATED':
            require(e['S'] not in allocated,'XCUT034_DUPLICATE_S_ALLOCATION')
            require(not allocated or e['S']>max(allocated),'XCUT034_S_ALLOCATION_ORDER_INVALID')
            require(e['status']=='OPEN','XCUT034_ALLOCATED_STATUS_MUST_BE_OPEN')
            allocated.add(e['S'])
        else:
            require(e['S'] in allocated,'XCUT034_LIFECYCLE_WITHOUT_ALLOCATION')
            require(e['status'] in ALLOWED_TRANSITIONS[latest[e['S']]['status']],'XCUT034_ILLEGAL_LIFECYCLE_TRANSITION')
        if e['event_type']=='TERMINAL':require(e['status'] in {'COMPLETED','BLOCKED','TRANSFERRED'},'XCUT034_TERMINAL_STATUS_INVALID')
        latest[e['S']]=e; prev=e['record_hash']
    require(int(ledger.get('last_event_cursor',0))==cursor,'XCUT034_LEDGER_CURSOR_MISMATCH')
    return {'result':'PASS','event_count':len(ledger.get('events',[])),'allocated_count':len(allocated),'head_hash':prev,'last_event_cursor':cursor}

def retrieve_newer_than(ledger,last_seen_S):
    validate_chain(ledger)
    require(integer(last_seen_S),'XCUT034_LAST_SEEN_S_INVALID')
    latest={}
    for e in ledger.get('events',[]):
        if e['S']>last_seen_S: latest[e['S']]=e
    return [copy.deepcopy(latest[s]) for s in sorted(latest)]

def retrieve_delta(ledger,last_seen_S,last_seen_event_cursor):
    validate_chain(ledger)
    require(integer(last_seen_S),'XCUT034_LAST_SEEN_S_INVALID'); require(integer(last_seen_event_cursor),'XCUT034_LAST_SEEN_EVENT_CURSOR_INVALID')
    events=[copy.deepcopy(e) for e in ledger.get('events',[]) if e.get('event_cursor',0)>last_seen_event_cursor]
    next_s=max([last_seen_S]+[e['S'] for e in events]); next_cursor=max([last_seen_event_cursor]+[e.get('event_cursor',0) for e in events])
    return {'events':events,'next_last_seen_S':next_s,'next_last_seen_event_cursor':next_cursor}
