#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from copy import deepcopy
from typing import Any, Mapping
ORIGINS={"USER_DIRECT","SYSTEM_DISCOVERED"}; AUTHORITIES={"OWNER_MANDATE","USER_REQUEST","SYSTEM_EVIDENCE"}; PRIORITIES={"P0","P1","P2","P3"}
AUTHORITY_ORDER={"SYSTEM_EVIDENCE":0,"USER_REQUEST":1,"OWNER_MANDATE":2}
def _digest(v:Any)->str:return hashlib.sha256(json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
def _text(v:Any)->bool:return isinstance(v,str) and bool(v.strip())
def normalize_intake(event:Mapping[str,Any])->dict[str,Any]:
    origin=event.get("origin")
    if origin not in ORIGINS: raise ValueError("INVALID_ORIGIN")
    if not _text(event.get("dedupe_key")): raise ValueError("DEDUPE_KEY_REQUIRED")
    if event.get("priority") not in PRIORITIES: raise ValueError("VALID_PRIORITY_REQUIRED")
    owner=event.get("owner_mandate") is True
    if owner and origin!="USER_DIRECT": raise ValueError("OWNER_MANDATE_REQUIRES_USER_DIRECT")
    inferred="OWNER_MANDATE" if owner else ("USER_REQUEST" if origin=="USER_DIRECT" else "SYSTEM_EVIDENCE")
    authority=event.get("authority_class",inferred)
    if authority not in AUTHORITIES or authority!=inferred: raise ValueError("AUTHORITY_CLASS_ORIGIN_MISMATCH")
    override=event.get("priority_override")
    if override is not None:
        if not owner: raise ValueError("PRIORITY_OVERRIDE_REQUIRES_OWNER_MANDATE")
        if override not in PRIORITIES or not _text(event.get("priority_override_reason")): raise ValueError("PRIORITY_OVERRIDE_REASON_REQUIRED")
    for key in ("source_skill","source_version"):
        if not _text(event.get(key)): raise ValueError(key.upper()+"_REQUIRED")
    refs=event.get("evidence_refs")
    if not isinstance(refs,list) or not refs or not all(_text(x) for x in refs): raise ValueError("EVIDENCE_REFS_REQUIRED")
    row=dict(event);row["authority_class"]=authority;row["owner_mandate"]=owner;row["effective_priority"]=override or event["priority"];row["origins"]=sorted(set(event.get("origins",[]))|{origin})
    row["event_digest"]=_digest({k:row[k] for k in sorted(row) if k!="event_digest"});return row
def aggregate(existing:Mapping[str,Any]|None,intake:Mapping[str,Any])->dict[str,Any]:
    new=normalize_intake(intake)
    if not existing:
        out=deepcopy(new);out["occurrence_count"]=max(1,int(new.get("occurrence_count",1)));return out
    old=dict(existing)
    if old.get("dedupe_key")!=new.get("dedupe_key"):raise ValueError("DEDUPE_KEY_MISMATCH")
    old_auth=old.get("authority_class","SYSTEM_EVIDENCE")
    if old_auth not in AUTHORITIES:raise ValueError("EXISTING_AUTHORITY_INVALID")
    out=deepcopy(old);out["origins"]=sorted(set(old.get("origins",[]))|set(new.get("origins",[]))|{new["origin"]})
    if AUTHORITY_ORDER[new["authority_class"]]>AUTHORITY_ORDER[old_auth]:out["authority_class"]=new["authority_class"];out["owner_mandate"]=new["authority_class"]=="OWNER_MANDATE"
    else:out["authority_class"]=old_auth;out["owner_mandate"]=old.get("owner_mandate") is True
    out["occurrence_count"]=int(old.get("occurrence_count",1))+1;out["evidence_refs"]=sorted(set(old.get("evidence_refs",[]))|set(new.get("evidence_refs",[])))
    out["priority"]=old.get("priority",new["priority"]);out["effective_priority"]=old.get("effective_priority",out["priority"])
    if new.get("priority_override"):out["priority_override"]=new["priority_override"];out["priority_override_reason"]=new["priority_override_reason"];out["effective_priority"]=new["priority_override"]
    out["last_event_digest"]=new["event_digest"];return out
def make_receipt(aggregated:Mapping[str,Any],direct_write_available:bool,canonical_readback:Mapping[str,Any]|None=None)->dict[str,Any]:
    base={"contract":"INC_SKILLFORGE_FEEDBACK_INTAKE_V1","dedupe_key":aggregated.get("dedupe_key"),"origin":aggregated.get("origin"),"origins":aggregated.get("origins"),"authority_class":aggregated.get("authority_class"),"priority":aggregated.get("effective_priority"),"record_type":aggregated.get("record_type"),"source_skill":aggregated.get("source_skill"),"source_version":aggregated.get("source_version"),"canonical_registered":False,"canonical_readback_verified":False}
    if not direct_write_available:base.update({"status":"PENDING_CANONICAL_INGESTION","receipt_id":"PENDING-"+_digest(base)[:20]});return base
    rb=dict(canonical_readback or {})
    if rb.get("verified") is not True or not _text(rb.get("change_id")):base.update({"status":"CANONICAL_WRITE_UNVERIFIED","receipt_id":"UNVERIFIED-"+_digest(base)[:20]});return base
    if rb.get("origin")!=aggregated.get("origin") and aggregated.get("origin") not in set(rb.get("origins",[])):raise ValueError("READBACK_ORIGIN_MISMATCH")
    if rb.get("authority_class")!=aggregated.get("authority_class"):raise ValueError("READBACK_AUTHORITY_MISMATCH")
    base.update({"status":"CANONICAL_REGISTERED","canonical_registered":True,"canonical_readback_verified":True,"change_id":rb["change_id"],"dedupe_result":rb.get("dedupe_result","NEW_CHANGE_ID"),"receipt_id":"CANONICAL-"+_digest({"base":base,"change_id":rb["change_id"]})[:20]});return base
