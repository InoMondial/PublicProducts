#!/usr/bin/env python3
from __future__ import annotations
import json, hashlib

CONTRACT='INC_G16_HANDOFF_TOPOLOGY_REGISTRY_V1'
ALLOWED_RELEASE_STATUS={'ACTIVE','CLOSED'}

class Invalid(ValueError):
    pass

def require(ok, code):
    if not ok:
        raise Invalid(code)

def text(v):
    return isinstance(v,str) and bool(v.strip())

def digest(v):
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()

def validate_topology(reg):
    require(isinstance(reg,dict),'G16_TOPOLOGY_REGISTRY_REQUIRED')
    require(reg.get('contract')==CONTRACT,'G16_TOPOLOGY_CONTRACT_MISMATCH')
    require(text(reg.get('project_id')),'G16_TOPOLOGY_PROJECT_ID_REQUIRED')
    h=reg.get('canonical_handoff')
    require(isinstance(h,dict),'G16_TOPOLOGY_CANONICAL_HANDOFF_REQUIRED')
    require(text(h.get('handoff_id')) and text(h.get('url')),'G16_TOPOLOGY_CANONICAL_HANDOFF_REQUIRED')
    require(h.get('kind')=='CANONICAL_PROJECT_HANDOFF','G16_TOPOLOGY_HANDOFF_KIND_INVALID')
    require(not reg.get('checkpoint_handoff_refs'),'G16_TOPOLOGY_CHECKPOINT_HANDOFF_PROHIBITED')
    releases=reg.get('releases')
    require(isinstance(releases,list),'G16_TOPOLOGY_RELEASES_REQUIRED')
    seen=set()
    for rel in releases:
        require(isinstance(rel,dict) and text(rel.get('release_id')),'G16_TOPOLOGY_RELEASE_ID_REQUIRED')
        rid=rel['release_id']
        require(rid not in seen,'G16_TOPOLOGY_DUPLICATE_RELEASE')
        seen.add(rid)
        require(rel.get('status') in ALLOWED_RELEASE_STATUS,'G16_TOPOLOGY_RELEASE_STATUS_INVALID')
        ledgers=rel.get('active_ledger_refs',[])
        closures=rel.get('closure_report_refs',[])
        require(isinstance(ledgers,list) and all(text(x) for x in ledgers),'G16_TOPOLOGY_LEDGER_REFS_INVALID')
        require(isinstance(closures,list) and all(text(x) for x in closures),'G16_TOPOLOGY_CLOSURE_REFS_INVALID')
        require(len(ledgers)<=1,'G16_TOPOLOGY_SECOND_ACTIVE_LEDGER_PROHIBITED')
        if rel['status']=='ACTIVE':
            require(len(closures)==0,'G16_TOPOLOGY_ACTIVE_RELEASE_CLOSURE_PROHIBITED')
        else:
            require(len(ledgers)==0,'G16_TOPOLOGY_CLOSED_RELEASE_ACTIVE_LEDGER_PROHIBITED')
            require(len(closures)==1,'G16_TOPOLOGY_CLOSED_RELEASE_EXACTLY_ONE_CLOSURE_REQUIRED')
            require(rel.get('closure_immutable') is True,'G16_TOPOLOGY_CLOSURE_IMMUTABLE_REQUIRED')
        require(rel.get('history_store_owner') in ('G11_G17','G11/G17'),'G16_TOPOLOGY_HISTORY_ROUTE_INVALID')
    require(sum(1 for r in releases if r.get('status')=='ACTIVE')<=1,'G16_TOPOLOGY_MULTIPLE_ACTIVE_RELEASES_PROHIBITED')
    return {
        'result':'PASS',
        'registry_sha256':digest(reg),
        'active_release_count':sum(1 for r in releases if r.get('status')=='ACTIVE')
    }
