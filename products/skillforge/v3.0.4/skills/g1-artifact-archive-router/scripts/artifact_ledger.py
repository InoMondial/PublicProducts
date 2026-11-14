#!/usr/bin/env python3
from pathlib import Path
import copy, hashlib, json
from datetime import datetime, timezone
DURABLE_EXT={'.doc','.docx','.pdf','.xls','.xlsx','.csv','.ppt','.pptx','.png','.jpg','.jpeg','.svg','.webp','.zip','.py','.js','.ts','.cs','.ps1','.sh','.sql','.json','.yaml','.yml','.xml','.toml','.md','.html'}
EPHEMERAL_NAMES={'__pycache__','node_modules','.cache','cache','tmp','temp'}
REQUIRED_EXCLUSION={'transaction_id','artifact_id','path','producer','exclusion_reason','observed_at','evidence'}
REQUIRED_REMOTE={'remote_url','commit_sha','sha256'}

def classify(path:str, final=False, user_deliverable=False, explicit_ephemeral=False, exclusion_reason=None):
    p=Path(path); in_ephemeral=any(part in EPHEMERAL_NAMES for part in p.parts); durable_type=p.suffix.lower() in DURABLE_EXT
    if final or user_deliverable:
        return ('DURABLE','FINAL_OR_USER_DELIVERABLE')
    if explicit_ephemeral:
        return ('EPHEMERAL',exclusion_reason) if exclusion_reason else ('REVIEW','EXCLUSION_REASON_REQUIRED')
    if in_ephemeral and durable_type:
        return ('REVIEW','DURABLE_TYPE_IN_EPHEMERAL_CONTAINER')
    if in_ephemeral:
        return ('EPHEMERAL','KNOWN_EPHEMERAL_CONTAINER')
    if durable_type:
        return ('DURABLE','DURABLE_TYPE')
    return ('REVIEW','UNKNOWN_DURABILITY')

def _canon(obj): return json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def event_hash(event):
    x=dict(event); x.pop('hash',None); return hashlib.sha256(_canon(x).encode()).hexdigest()

def make_entry(transaction_id, artifact_id, path, producer, classification):
    return {'transaction_id':transaction_id,'artifact_id':artifact_id,'path':path,'producer':producer,'classification':classification,'history':[]}

def append_transition(entry,state,actor,evidence=None,observed_at=None):
    out=copy.deepcopy(entry); hist=out.setdefault('history',[]); prev=hist[-1]['hash'] if hist else None
    ev={'index':len(hist),'state':state,'actor':actor,'observed_at':observed_at or datetime.now(timezone.utc).isoformat(),'evidence':evidence or {},'prev_hash':prev}
    ev['hash']=event_hash(ev); hist.append(ev); return out

def verify_history(entry):
    prev=None
    for i,ev in enumerate(entry.get('history',[])):
        if ev.get('index')!=i or ev.get('prev_hash')!=prev or ev.get('hash')!=event_hash(ev): return False
        prev=ev['hash']
    return True

def valid_exclusion(item):
    return item.get('state')=='VALID_EXCLUSION' and REQUIRED_EXCLUSION.issubset(item) and bool(item.get('exclusion_reason')) and isinstance(item.get('evidence'),dict) and bool(item.get('evidence'))

def valid_verified(item):
    proof=item.get('remote_proof',{})
    return item.get('state')=='GITHUB_VERIFIED' and REQUIRED_REMOTE.issubset(proof) and all(proof.get(k) for k in REQUIRED_REMOTE)

def reconcile(items):
    verified=sum(valid_verified(i) for i in items); excluded=sum(valid_exclusion(i) for i in items); discovered=len(items); unaccounted=discovered-verified-excluded
    return {'discovered':discovered,'github_verified':verified,'valid_exclusions':excluded,'unaccounted':unaccounted,'ok':unaccounted==0}
