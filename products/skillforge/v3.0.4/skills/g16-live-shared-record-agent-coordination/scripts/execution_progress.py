#!/usr/bin/env python3
"""Deterministic G16 execution/progress gates; no provider authorization or host timer.
Inputs are non-secret adapter observations. PASS is consistency, not certification.
"""
from __future__ import annotations
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import re
from pathlib import Path

CONTRACT = 'INC_G16_DURABLE_EXECUTION_PROGRESS_V1'
STATES = {'PLANNED','INTENT_RECORDED','APPLIED_UNVERIFIED','VERIFIED',
          'CHECKPOINT_COMMITTED','FAILED','BLOCKED','UNKNOWN_OUTCOME'}
LIMITS = {'heartbeat_seconds':480, 'actions_per_checkpoint':12,
          'no_progress_seconds':900,'slice_seconds':1500,
          'operation_attempts':3,'identical_error_count':2,
          'root_no_progress_attempts':6}

class Invalid(ValueError):
    pass

def require(ok, code):
    if not ok:
        raise Invalid(code)

def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=True, sort_keys=True,
        separators=(',', ':'), allow_nan=False).encode()).hexdigest()

def instant(value):
    require(isinstance(value, str), 'TIMESTAMP_REQUIRED')
    try:
        d = datetime.fromisoformat(value.replace('Z','+00:00'))
        require(d.tzinfo is not None, 'TIMEZONE_REQUIRED')
        return d.astimezone(timezone.utc)
    except (ValueError, TypeError) as e:
        raise Invalid('INVALID_TIMESTAMP') from e

def text(value):
    return isinstance(value, str) and bool(value.strip())

def integer(value, low=0, high=10000):
    return type(value) is int and low <= value <= high

def refs(value):
    return isinstance(value, list) and bool(value) and all(text(x) for x in value)

def plan_identity(plan):
    return digest(plan)

def validate_plan(plan):
    require(isinstance(plan, dict), 'PLAN_REQUIRED')
    require(plan.get('contract') == CONTRACT, 'CONTRACT_MISMATCH')
    require(text(plan.get('command_id')) and integer(plan.get('scope_revision'),1), 'COMMAND_IDENTITY_REQUIRED')
    steps = plan.get('steps')
    require(isinstance(steps,list) and bool(steps), 'STEPS_REQUIRED')
    require(refs(plan.get('required_requirement_ids')), 'REQUIREMENT_UNIVERSE_REQUIRED')
    require(len(set(plan['required_requirement_ids'])) == len(plan['required_requirement_ids']), 'DUPLICATE_REQUIREMENT')
    seen, covered = set(), set()
    weights = []
    for row in steps:
        require(isinstance(row,dict) and text(row.get('id')) and row['id'] not in seen, 'STEP_ID_INVALID')
        seen.add(row['id']);require(text(row.get('title')), 'STEP_TITLE_REQUIRED')
        require(integer(row.get('weight_bp'),1), 'STEP_WEIGHT_INVALID');weights.append(row['weight_bp'])
        require(refs(row.get('requirement_ids')), 'STEP_REQUIREMENTS_REQUIRED')
        covered.update(row['requirement_ids'])
        milestones = row.get('milestones')
        require(isinstance(milestones,list) and bool(milestones), 'MILESTONES_REQUIRED')
        mids = set();total=0
        for item in milestones:
            require(isinstance(item,dict) and text(item.get('id')) and item['id'] not in mids, 'MILESTONE_ID_INVALID')
            mids.add(item['id']);require(integer(item.get('weight_bp'),1),'MILESTONE_WEIGHT_INVALID')
            require(text(item.get('acceptance')), 'ACCEPTANCE_REQUIRED');total+=item['weight_bp']
        require(total==10000, 'MILESTONE_WEIGHTS_MUST_SUM_10000')
    require(sum(weights)==10000, 'STEP_WEIGHTS_MUST_SUM_10000')
    require(covered==set(plan['required_requirement_ids']), 'REQUIREMENT_COVERAGE_MISMATCH')

def initial(plan, actor, timestamp):
    validate_plan(plan);instant(timestamp);require(text(actor), 'ACTOR_REQUIRED')
    return {'contract':CONTRACT,'command_id':plan['command_id'],'scope_revision':plan['scope_revision'],
        'plan_sha256':plan_identity(plan),'actor_id':actor,'revision':0,'last_event_id':None,
        'run_status':'PAUSED','started_at':timestamp,'slice_started_at':timestamp,
        'last_evidence_at':timestamp,'last_checkpoint_at':timestamp,'actions_since_checkpoint':0,
        'root_no_progress_attempts':0,'operation_attempts':{},'error_counts':{},'pending_operation':None,
        'resume_from':{'step_id':plan['steps'][0]['id'],'milestone_id':plan['steps'][0]['milestones'][0]['id']},
        'last_error':None, 'last_event_at':timestamp, 'event_digests':{}, 'last_checkpoint':None,
        'steps':{r['id']:{m['id']:{'status':'PLANNED','evidence_refs':[],'checkpoint_receipt':None}
                         for m in r['milestones']} for r in plan['steps']}}

def validate_state(plan, state):
    validate_plan(plan);require(isinstance(state,dict), 'STATE_REQUIRED')
    require(state.get('contract')==CONTRACT and state.get('command_id')==plan['command_id'] and
            state.get('scope_revision')==plan['scope_revision'] and state.get('plan_sha256')==plan_identity(plan),
            'STALE_OR_WRONG_PLAN')
    require(integer(state.get('revision'),0,10**12),'REVISION_INVALID')
    require(state.get('run_status') in {'PAUSED','RUNNING','BLOCKED','INTERRUPTED','COMPLETE'},'RUN_STATUS_INVALID')
    require(set(state.get('steps',{}))=={r['id'] for r in plan['steps']}, 'STATE_STEP_COVERAGE_MISMATCH')
    for row in plan['steps']:
        actual=state['steps'][row['id']]
        require(isinstance(actual,dict) and set(actual)=={m['id'] for m in row['milestones']}, 'STATE_MILESTONE_COVERAGE_MISMATCH')
        for entry in actual.values():
            require(isinstance(entry,dict) and entry.get('status') in STATES,'MILESTONE_STATE_INVALID')
            if entry['status'] in {'VERIFIED','CHECKPOINT_COMMITTED'}:
                require(refs(entry.get('evidence_refs')), 'EVIDENCE_REQUIRED')
            if entry['status']=='CHECKPOINT_COMMITTED':
                rec=entry.get('checkpoint_receipt',{})
                require(isinstance(rec,dict) and refs(rec.get('sink_refs')) and text(rec.get('event_id')) and
                        isinstance(rec.get('payload_sha256'),str) and re.fullmatch(r'[0-9a-f]{64}',rec['payload_sha256']) is not None and len(set(rec['sink_refs']))>=2, 'CHECKPOINT_RECEIPT_REQUIRED')
    for key in ('started_at','slice_started_at','last_evidence_at','last_checkpoint_at','last_event_at'):
        instant(state.get(key))
    for key in ('actions_since_checkpoint','root_no_progress_attempts'):
        require(integer(state.get(key),0,10**12), 'COUNTER_INVALID:'+key)
    for key in ('operation_attempts','error_counts'):
        require(isinstance(state.get(key),dict) and all(integer(n,0,10**12) for n in state[key].values()),'COUNTER_MAP_INVALID')

def before_action(plan,state,observations):
    """Read-only guard. Called by the real executor before EVERY material action.
    Clock/quota/persistence authenticity belongs to the adapter, never this module.
    """
    validate_state(plan,state);require(isinstance(observations,dict),'OBSERVATIONS_REQUIRED')
    now=instant(observations.get('now'));reasons=[]
    age={key:(now-instant(state[key])).total_seconds() for key in
         ('started_at','slice_started_at','last_evidence_at','last_checkpoint_at')}
    if any(n<0 for n in age.values()) or now<instant(state['last_event_at']):reasons.append('CLOCK_REGRESSION')
    if state['run_status']!='RUNNING':reasons.append('NOT_RUNNING')
    if observations.get('observed_state_revision')!=state['revision']:reasons.append('REMOTE_STATE_STALE')
    if observations.get('observed_plan_sha256')!=state['plan_sha256']:reasons.append('REMOTE_PLAN_STALE')
    if observations.get('single_writer_verified') is not True:reasons.append('WRITER_NOT_VERIFIED')
    if observations.get('dual_sink_reconciled') is not True:reasons.append('CHECKPOINT_SYNC_PENDING')
    if state['pending_operation'] is not None:reasons.append('PENDING_OUTCOME_RECONCILE_FIRST')
    if age['last_checkpoint_at']>=LIMITS['heartbeat_seconds'] or state['actions_since_checkpoint']>=LIMITS['actions_per_checkpoint']:
        reasons.append('CHECKPOINT_DUE')
    if age['last_evidence_at']>=LIMITS['no_progress_seconds'] or state['root_no_progress_attempts']>=LIMITS['root_no_progress_attempts']:
        reasons.append('ROOT_NO_PROGRESS_CIRCUIT_OPEN')
    if age['slice_started_at']>=LIMITS['slice_seconds']:reasons.append('SLICE_BUDGET_EXHAUSTED')
    op=observations.get('operation_key');require(text(op),'OPERATION_KEY_REQUIRED')
    if state['operation_attempts'].get(op,0)>=LIMITS['operation_attempts']:reasons.append('OPERATION_RETRY_EXHAUSTED')
    signature=observations.get('error_signature')
    if signature and state['error_counts'].get(signature,0)>=LIMITS['identical_error_count']:
        reasons.append('REPEATED_ERROR_CIRCUIT_OPEN')
    budget=observations.get('bounded_call_seconds')
    if not integer(budget,1,LIMITS['heartbeat_seconds']):reasons.append('CALL_TIMEOUT_UNVERIFIED_PRECHECKPOINT_REQUIRED')
    elif age['last_checkpoint_at']+budget>LIMITS['heartbeat_seconds']:reasons.append('PRECHECKPOINT_REQUIRED')
    return {'decision':'ALLOW_BOUNDED_ACTION' if not reasons else 'BLOCKED', 'reasons':sorted(set(reasons)),
            'enforcement':'COOPERATIVE_PRE_ACTION_ONLY','host_failure_prevented':False,
            'resume_from':state['resume_from']}

def transition(plan, state, event):
    """Pure reducer. Persist output through adapter before another side effect.
    Re-delivery is idempotent only for the exact same event ID and contents.
    """
    validate_state(plan,state);require(isinstance(event,dict),'EVENT_REQUIRED')
    eid=event.get('event_id');require(text(eid),'EVENT_ID_REQUIRED');ed=digest(event)
    if eid in state['event_digests']:
        require(state['event_digests'][eid]==ed,'EVENT_ID_COLLISION');return copy.deepcopy(state)
    require(event.get('expected_revision')==state['revision'],'REVISION_CONFLICT')
    require(event.get('command_id')==state['command_id'] and event.get('actor_id')==state['actor_id'],'EVENT_OWNER_MISMATCH')
    now=instant(event.get('at'));require(now>=instant(state['last_event_at']),'CLOCK_REGRESSION')
    out=copy.deepcopy(state);typ=event.get('type');data=event.get('data',{})
    require(isinstance(data,dict),'EVENT_DATA_REQUIRED')
    if typ=='activate':
        require(data.get('owner_authorization_verified') is True and data.get('remote_reconciled') is True,'RESUME_AUTHORITY_REQUIRED')
        require(out['pending_operation'] is None,'PENDING_OUTCOME_RECONCILE_FIRST');out['run_status']='RUNNING'
        out['slice_started_at']=event['at']
    elif typ=='intent':
        require(out['run_status']=='RUNNING' and out['pending_operation'] is None,'INTENT_NOT_ALLOWED')
        observations=data.get('observations');require(isinstance(observations,dict),'OBSERVATIONS_REQUIRED')
        require(observations.get('operation_key')==data.get('operation_key'),'INTENT_OPERATION_IDENTITY_MISMATCH')
        require(observations.get('now')==event.get('at'),'INTENT_CLOCK_IDENTITY_MISMATCH')
        decision=before_action(plan,state,observations)
        require(decision['decision']=='ALLOW_BOUNDED_ACTION','PRE_ACTION_GATE_BLOCKED:'+','.join(decision['reasons']))
        require(all(text(data.get(k)) for k in ('operation_key','target_ref','before_identity','reconcile_rule','step_id','milestone_id')),'INTENT_FIELDS_REQUIRED')
        row=out['steps'].get(data['step_id'],{}).get(data['milestone_id'])
        require(isinstance(row,dict) and row['status'] not in {'CHECKPOINT_COMMITTED','VERIFIED'},'INTENT_TARGET_INVALID')
        require(out['operation_attempts'].get(data['operation_key'],0)<LIMITS['operation_attempts'],'OPERATION_RETRY_EXHAUSTED')
        out['pending_operation']=dict(data, intent_event_id=eid, outcome='UNKNOWN')
        out['operation_attempts'][data['operation_key']]=out['operation_attempts'].get(data['operation_key'],0)+1
        out['root_no_progress_attempts']+=1;out['actions_since_checkpoint']+=1
        row['status']='INTENT_RECORDED';out['resume_from']={k:data[k] for k in ('step_id','milestone_id')}
    elif typ in {'applied','not_applied','unknown'}:
        pending=out['pending_operation'];require(isinstance(pending,dict),'PENDING_OPERATION_REQUIRED')
        require(data.get('operation_key')==pending['operation_key'],'OUTCOME_OPERATION_MISMATCH')
        require(refs(data.get('observation_refs')), 'OUTCOME_OBSERVATION_REQUIRED')
        row=out['steps'][pending['step_id']][pending['milestone_id']]
        row['status']={'applied':'APPLIED_UNVERIFIED','not_applied':'PLANNED','unknown':'UNKNOWN_OUTCOME'}[typ]
        if typ!='unknown':out['pending_operation']=None
        else:out['run_status']='INTERRUPTED'
    elif typ=='action':
        observations=data.get('observations');require(isinstance(observations,dict),'OBSERVATIONS_REQUIRED')
        require(observations.get('now')==event['at'],'ACTION_CLOCK_IDENTITY_MISMATCH')
        require(data.get('kind') in {'READ','DISCOVER','TEST'},'NONMUTATING_ACTION_KIND_REQUIRED')
        decision=before_action(plan,state,observations)
        require(decision['decision']=='ALLOW_BOUNDED_ACTION','PRE_ACTION_GATE_BLOCKED:'+','.join(decision['reasons']))
        op=observations['operation_key']
        out['operation_attempts'][op]=out['operation_attempts'].get(op,0)+1
        out['root_no_progress_attempts']+=1;out['actions_since_checkpoint']+=1
    elif typ=='verified':
        require(out['pending_operation'] is None,'PENDING_OUTCOME_RECONCILE_FIRST')
        row=out['steps'].get(data.get('step_id'),{}).get(data.get('milestone_id'))
        require(isinstance(row,dict) and row['status'] not in {'VERIFIED','CHECKPOINT_COMMITTED'},'VERIFICATION_TARGET_INVALID')
        require(refs(data.get('evidence_refs')) and data.get('independent_readback') is True,'VERIFICATION_EVIDENCE_REQUIRED')
        row.update(status='VERIFIED',evidence_refs=data['evidence_refs'],verified_at=event['at'])
        out['last_evidence_at']=event['at'];out['root_no_progress_attempts']=0
    elif typ=='checkpoint':
        require(refs(data.get('sink_refs')) and len(set(data['sink_refs']))>=2,'DUAL_SINK_RECEIPTS_REQUIRED')
        require(isinstance(data.get('payload_sha256'),str) and re.fullmatch(r'[0-9a-f]{64}',data['payload_sha256']) is not None,'CHECKPOINT_DIGEST_REQUIRED')
        # Receipts refer to a prior persisted checkpoint candidate, avoiding self-hash recursion.
        require(data.get('persisted_revision')==state['revision'],'CHECKPOINT_REVISION_MISMATCH')
        for row in out['steps'].values():
            for item in row.values():
                if item['status']=='VERIFIED':
                    item.update(status='CHECKPOINT_COMMITTED',checkpoint_receipt={'sink_refs':data['sink_refs'],
                        'event_id':eid,'payload_sha256':data['payload_sha256']})
        out['last_checkpoint_at']=event['at'];out['actions_since_checkpoint']=0
        out['last_checkpoint']={'event_id':eid,'persisted_revision':data['persisted_revision'],'sink_refs':data['sink_refs']}
    elif typ=='error':
        require(text(data.get('signature')) and text(data.get('step_id')) and text(data.get('milestone_id')),'ERROR_FIELDS_REQUIRED')
        row=out['steps'].get(data['step_id'],{}).get(data['milestone_id']);require(isinstance(row,dict),'ERROR_TARGET_INVALID')
        require(row['status']!='CHECKPOINT_COMMITTED','COMMITTED_WORK_CANNOT_BE_SILENTLY_REWRITTEN')
        row.update(status='FAILED',error_code=data['signature']);out['last_error']={k:data[k] for k in ('signature','step_id','milestone_id')};out['last_error']['at']=event['at']
        out['error_counts'][data['signature']]=out['error_counts'].get(data['signature'],0)+1
        out['root_no_progress_attempts']+=1
    elif typ=='split':
        require(out['pending_operation'] is None and out['actions_since_checkpoint']==0,'CHECKPOINT_BEFORE_SPLIT')
        require(text(data.get('child_unit_id')) and text(data.get('narrowed_scope_ref')),'CHILD_SCOPE_REQUIRED')
        out['slice_started_at']=event['at'];out['child_unit_id']=data['child_unit_id']
        # Root counters, attempts, errors and last_evidence_at deliberately remain unchanged.
    elif typ in {'pause','block','interrupt'}:
        out['run_status']={'pause':'PAUSED','block':'BLOCKED','interrupt':'INTERRUPTED'}[typ]
    elif typ=='complete':
        require(out['pending_operation'] is None and all(m['status']=='CHECKPOINT_COMMITTED' for row in out['steps'].values() for m in row.values()),'UNFINISHED_WORK_REMAINS')
        out['run_status']='COMPLETE';out['resume_from']=None
    else:raise Invalid('UNKNOWN_EVENT_TYPE')
    out['revision']+=1;out['last_event_id']=eid;out['last_event_at']=event['at'];out['event_digests'][eid]=ed
    validate_state(plan,out);return out

def report(plan,state):
    validate_state(plan,state);rows=[];earned_total=0
    for n,step in enumerate(plan['steps'],1):
        milestones=state['steps'][step['id']]
        earned_bp=sum(m['weight_bp'] for m in step['milestones'] if milestones[m['id']]['status']=='CHECKPOINT_COMMITTED')
        weighted=step['weight_bp']*earned_bp/1000000
        earned_total+=weighted
        statuses={m['status'] for m in milestones.values()}
        status='COMPLETE' if earned_bp==10000 else ('PARTIAL' if earned_bp else 'NOT_STARTED')
        if statuses & {'UNKNOWN_OUTCOME','FAILED','BLOCKED'}:status='PARTIAL_OR_BLOCKED'
        rows.append({'row':n,'step_id':step['id'],'title':step['title'],'weight_percent':step['weight_bp']/100,
          'verified_complete_percent':earned_bp/100,'earned_percentage_points':round(weighted,4),
          'remaining_percentage_points':round(step['weight_bp']/100-weighted,4),'status':status,
          'remaining_milestones':[m['id'] for m in step['milestones'] if milestones[m['id']]['status']!='CHECKPOINT_COMMITTED']})
    return {'contract':CONTRACT,'command_id':plan['command_id'],'scope_revision':plan['scope_revision'],
        'state_revision':state['revision'],'as_of':state['last_event_at'],'last_durable_checkpoint_at':state['last_checkpoint_at'],'run_status':state['run_status'],
        'verified_complete_percent':round(earned_total,4),'remaining_percent':round(100-earned_total,4),
        'last_error':state['last_error'],'resume_from':state['resume_from'],'rows':rows,
        'limitation':'Adapter receipts and host enforcement must be verified externally; not G12/G13 certification.'}

def markdown(data):
    def safe(v):return str(v).replace('|','\\|').replace('\n',' ')
    out=['## Execution progress - '+safe(data['command_id']),
         '| NUM# | Step | Weight % | Verified % | Earned pp | Remaining pp | State |',
         '|---:|---|---:|---:|---:|---:|---|']
    for r in data['rows']:
        out.append('| '+ ' | '.join(safe(r[k]) for k in ['row','title','weight_percent','verified_complete_percent','earned_percentage_points','remaining_percentage_points','status'])+' |')
    out.extend(['',f"Verified completion: {data['verified_complete_percent']}%; remaining: {data['remaining_percent']}%.",
        'Resume: '+safe(data['resume_from']), 'Last error: '+safe(data['last_error'])])
    return '\n'.join(out)+'\n'

def load(path):
    def pairs(seq):
        d={}
        for k,v in seq:
            require(k not in d,'DUPLICATE_JSON_KEY');d[k]=v
        return d
    return json.loads(Path(path).read_text(encoding='utf-8'),object_pairs_hook=pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(Invalid('NONFINITE_NUMBER')))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('plan');p.add_argument('state');p.add_argument('--observations');p.add_argument('--markdown',action='store_true');a=p.parse_args()
    try:
        plan,state=load(a.plan),load(a.state)
        result=before_action(plan,state,load(a.observations)) if a.observations else report(plan,state)
        print(markdown(result) if a.markdown and not a.observations else json.dumps(result,ensure_ascii=False,indent=2))
        return 2 if result.get('decision')=='BLOCKED' else 0
    except (Invalid,ValueError,TypeError,KeyError,OSError) as exc:
        print(json.dumps({'result':'BLOCKED','error':str(exc) if isinstance(exc,Invalid) else type(exc).__name__}));return 2
if __name__=='__main__':raise SystemExit(main())
