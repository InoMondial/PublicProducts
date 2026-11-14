#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from typing import Any,Mapping
DISPOSITIONS={"NEW_CHANGE_ID","EXISTING_CHANGE_ID_AGGREGATED","SUPERSEDED_WITH_REFERENCE","DUPLICATE_WITH_REFERENCE","EXPLICITLY_NOT_BACKLOG_WITH_OWNER_REASON"}
def _digest(v:Any)->str:return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def _text(v:Any)->bool:return isinstance(v,str) and bool(v.strip())
def evaluate(decision_delta:Mapping[str,Any],reconciliation:Mapping[str,Any],*,interaction_s:int|None=None,canonical_sha_before:str|None=None,canonical_sha_after:str|None=None,mirror_parity:bool=False)->dict[str,Any]:
    events=decision_delta.get("events")
    if not isinstance(events,list):raise ValueError("DECISION_DELTA_EVENTS_REQUIRED")
    mapped=reconciliation.get("mappings")
    if not isinstance(mapped,list):raise ValueError("MAPPINGS_REQUIRED")
    by_id={};dups=[]
    for row in mapped:
        rid=row.get("decision_id")
        if not _text(rid):raise ValueError("MAPPING_DECISION_ID_REQUIRED")
        if rid in by_id:dups.append(rid)
        by_id[rid]=row
    rows=[];unmapped=[];seen=set()
    for event in events:
        did=event.get("decision_id")
        if not _text(did):raise ValueError("DECISION_ID_REQUIRED")
        if did in seen:raise ValueError("DUPLICATE_DECISION_ID:"+did)
        seen.add(did);relevant=event.get("backlog_relevant") is True;row=by_id.get(did)
        if not relevant:rows.append({"decision_id":did,"status":"NOT_BACKLOG_RELEVANT"});continue
        if not row or row.get("disposition") not in DISPOSITIONS:unmapped.append(did);rows.append({"decision_id":did,"status":"UNMAPPED"});continue
        disp=row["disposition"];refs=row.get("change_ids") or row.get("reference_ids")
        if disp in {"NEW_CHANGE_ID","EXISTING_CHANGE_ID_AGGREGATED","SUPERSEDED_WITH_REFERENCE","DUPLICATE_WITH_REFERENCE"} and (not isinstance(refs,list) or not refs or not all(_text(x) for x in refs)):
            unmapped.append(did);rows.append({"decision_id":did,"status":"UNMAPPED_REFERENCE_MISSING"});continue
        if disp=="EXPLICITLY_NOT_BACKLOG_WITH_OWNER_REASON" and (event.get("owner_approved") is not True or not _text(row.get("owner_reason"))):
            unmapped.append(did);rows.append({"decision_id":did,"status":"UNMAPPED_OWNER_REASON_REQUIRED"});continue
        if event.get("authority_class")=="OWNER_MANDATE" and row.get("authority_class")!="OWNER_MANDATE":
            unmapped.append(did);rows.append({"decision_id":did,"status":"UNMAPPED_OWNER_AUTHORITY_LOST"});continue
        rows.append({"decision_id":did,"status":"MAPPED","disposition":disp,"references":refs or []})
    extras=sorted(set(by_id)-seen)
    if extras:unmapped.extend("EXTRA:"+x for x in extras)
    if dups:unmapped.extend("DUPLICATE_MAPPING:"+x for x in dups)
    receipt={"contract":"INC_OWNER_CONVERSATION_BACKLOG_COVERAGE_V1","interaction_s":interaction_s,"mapped":rows,"mapped_change_ids":sorted({ref for row in rows for ref in row.get("references",[])}),"canonical_backlog_sha_before":canonical_sha_before,"canonical_backlog_sha_after":canonical_sha_after,"mirror_parity":bool(mirror_parity),"unmapped_count":len(unmapped),"unmapped":sorted(unmapped)}
    receipt["status"]="PASS" if receipt["unmapped_count"]==0 and mirror_parity and _text(canonical_sha_after) else "BLOCKED";receipt["receipt_sha256"]=_digest(receipt);return receipt
def completeness_claim_allowed(receipt:Mapping[str,Any])->bool:return receipt.get("status")=="PASS" and receipt.get("unmapped_count")==0 and receipt.get("mirror_parity") is True and _text(receipt.get("canonical_backlog_sha_after"))
