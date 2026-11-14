#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, sys, re
from pathlib import Path
from typing import Any, Mapping

DISPOSITIONS={"UNCHANGED_CARRIED_FORWARD","MODIFIED_REVALIDATE","RETIRED_WITH_REASON","NEW","UNRESOLVED"}
REQUIRED_CATEGORIES={"REQUIREMENT","CONTRACT","TEST","SCRIPT","REFERENCE","ASSET","DEPENDENCY","NEGATIVE_TEST","BACKLOG_RECORD","FIX_REGISTER_RECORD","GENERATED_SKILL","SKILL_COMPONENT"}
CONTRACT_ID="INC_SKILLFORGE_CARRY_FORWARD_MANIFEST_V1"

def canonical_json(v:Any)->bytes:
    return json.dumps(v,sort_keys=True,ensure_ascii=True,separators=(",",":"),allow_nan=False).encode()
def digest(v:Any)->str:return hashlib.sha256(canonical_json(v)).hexdigest()
def _text(v:Any)->bool:return isinstance(v,str) and bool(v.strip())
def normalize_snapshot(doc:Mapping[str,Any])->list[dict[str,Any]]:
    if not isinstance(doc,Mapping):raise ValueError("SNAPSHOT_MAPPING_REQUIRED")
    rows=doc.get("items")
    if not isinstance(rows,list):raise ValueError("SNAPSHOT_ITEMS_REQUIRED")
    out=[];seen=set()
    for raw in rows:
        if not isinstance(raw,Mapping):raise ValueError("INVALID_SNAPSHOT_ITEM")
        row={k:raw.get(k) for k in ("item_id","category","stable_ref","source_ref","content_sha256")}
        if not all(_text(row[k]) for k in row):raise ValueError("INCOMPLETE_SNAPSHOT_ITEM")
        if not re.fullmatch(r"[0-9a-f]{64}",row["content_sha256"]):raise ValueError("SNAPSHOT_CONTENT_DIGEST_INVALID")
        if row["category"] not in REQUIRED_CATEGORIES:raise ValueError("INVALID_CATEGORY:"+row["category"])
        if row["item_id"] in seen:raise ValueError("DUPLICATE_ITEM_ID:"+row["item_id"])
        seen.add(row["item_id"]);out.append(dict(raw))
    return sorted(out,key=lambda x:x["item_id"])
def build_manifest(previous:Mapping[str,Any],current:Mapping[str,Any],decisions:Mapping[str,Any]|None=None)->dict[str,Any]:
    prev=normalize_snapshot(previous);cur=normalize_snapshot(current);p={x["item_id"]:x for x in prev};c={x["item_id"]:x for x in cur}
    decisions=decisions or {};modified=decisions.get("modified",{});retired=decisions.get("retired",{});rows=[]
    for item_id,old in p.items():
        now=c.get(item_id)
        if now is None:
            d=retired.get(item_id)
            if isinstance(d,Mapping):
                rows.append({"item_id":item_id,"category":old["category"],"previous":old,"current":None,"disposition":"RETIRED_WITH_REASON","owner_approved":d.get("owner_approved") is True,"reason":d.get("reason"),"successor_or_historical_ref":d.get("successor_or_historical_ref")})
            else:rows.append({"item_id":item_id,"category":old["category"],"previous":old,"current":None,"disposition":"UNRESOLVED","reason":"MISSING_FROM_CURRENT_WITHOUT_OWNER_RETIREMENT"})
            continue
        same=(old.get("stable_ref")==now.get("stable_ref") and old.get("content_sha256")==now.get("content_sha256") and old.get("category")==now.get("category"))
        if same:rows.append({"item_id":item_id,"category":old["category"],"previous":old,"current":now,"disposition":"UNCHANGED_CARRIED_FORWARD"})
        else:
            d=modified.get(item_id) or {}
            rows.append({"item_id":item_id,"category":old["category"],"previous":old,"current":now,"disposition":"MODIFIED_REVALIDATE","affected_tests":d.get("affected_tests"),"g12_scope":d.get("g12_scope"),"g13_scope":d.get("g13_scope"),"lineage_ref":d.get("lineage_ref")})
    for item_id,now in c.items():
        if item_id not in p:rows.append({"item_id":item_id,"category":now["category"],"previous":None,"current":now,"disposition":"NEW"})
    m={"schema_version":"1.0","contract_id":CONTRACT_ID,"previous_release_ref":previous.get("release_ref"),"current_release_ref":current.get("release_ref"),"previous_snapshot_sha256":digest(prev),"current_snapshot_sha256":digest(cur),"rows":sorted(rows,key=lambda x:x["item_id"])}
    m["summary"]=summarize(m);m["manifest_sha256"]=digest({k:v for k,v in m.items() if k!="manifest_sha256"});return m
def summarize(m:Mapping[str,Any])->dict[str,Any]:
    counts={k:0 for k in sorted(DISPOSITIONS)}
    for r in m.get("rows",[]):
        if r.get("disposition") in counts:counts[r["disposition"]]+=1
    complete=counts['UNRESOLVED']==0
    for row in m.get('rows',[]):
        if row.get('disposition')=='MODIFIED_REVALIDATE':
            complete=complete and all(isinstance(row.get(k),list) and bool(row[k]) and all(_text(x) for x in row[k]) for k in ('affected_tests','g12_scope','g13_scope'))
        elif row.get('disposition')=='RETIRED_WITH_REASON':
            complete=complete and row.get('owner_approved') is True and _text(row.get('reason')) and _text(row.get('successor_or_historical_ref'))
    return {"row_count":len(m.get("rows",[])),"disposition_counts":counts,"unresolved_count":counts["UNRESOLVED"],"release_ready":bool(complete)}
def validate_manifest(m:Mapping[str,Any],previous:Mapping[str,Any],current:Mapping[str,Any],release_ready:bool=False)->list[str]:
    e=[]
    try:prev=normalize_snapshot(previous);cur=normalize_snapshot(current)
    except Exception as exc:return [str(exc)]
    if m.get("contract_id")!=CONTRACT_ID:e.append("CONTRACT_ID_MISMATCH")
    if m.get("previous_snapshot_sha256")!=digest(prev):e.append("PREVIOUS_SNAPSHOT_DIGEST_MISMATCH")
    if m.get("current_snapshot_sha256")!=digest(cur):e.append("CURRENT_SNAPSHOT_DIGEST_MISMATCH")
    rows=m.get("rows")
    if not isinstance(rows,list):return e+["ROWS_REQUIRED"]
    pindex={x["item_id"]:x for x in prev};cindex={x["item_id"]:x for x in cur}
    seen=set();expected=set(pindex)|set(cindex)
    for r in rows:
        if not isinstance(r,Mapping):e.append("ROW_MAPPING_REQUIRED");continue
        iid=r.get("item_id")
        if not _text(iid):e.append("ROW_ITEM_ID_REQUIRED");continue
        if iid in seen:e.append("DUPLICATE_ROW:"+iid)
        seen.add(iid);d=r.get("disposition")
        if d not in DISPOSITIONS:e.append("INVALID_DISPOSITION:"+iid);continue
        old=r.get("previous");now=r.get("current")
        if old!=pindex.get(iid):e.append('ROW_PREVIOUS_SNAPSHOT_MISMATCH:'+iid)
        if now!=cindex.get(iid):e.append('ROW_CURRENT_SNAPSHOT_MISMATCH:'+iid)
        expected_category=(pindex.get(iid) or cindex.get(iid) or {}).get('category')
        if r.get('category')!=expected_category:e.append('ROW_CATEGORY_MISMATCH:'+iid)
        if d=="UNCHANGED_CARRIED_FORWARD":
            if not isinstance(old,Mapping) or not isinstance(now,Mapping):e.append("UNCHANGED_REQUIRES_BOTH:"+iid)
            elif old.get("stable_ref")!=now.get("stable_ref") or old.get("content_sha256")!=now.get("content_sha256"):e.append("UNCHANGED_STALE_OR_MODIFIED:"+iid)
        elif d=="MODIFIED_REVALIDATE":
            if not isinstance(old,Mapping) or not isinstance(now,Mapping):e.append("MODIFIED_REQUIRES_BOTH:"+iid)
            for k in ("affected_tests","g12_scope","g13_scope"):
                v=r.get(k)
                if not isinstance(v,list) or not v or not all(_text(x) for x in v):e.append("MODIFIED_"+k.upper()+"_REQUIRED:"+iid)
            if isinstance(old,Mapping) and isinstance(now,Mapping) and old.get("stable_ref")!=now.get("stable_ref") and not _text(r.get("lineage_ref")):e.append("MODIFIED_LINEAGE_REF_REQUIRED:"+iid)
        elif d=="RETIRED_WITH_REASON":
            if not isinstance(old,Mapping) or now is not None:e.append("RETIRED_SHAPE_INVALID:"+iid)
            if r.get("owner_approved") is not True:e.append("RETIRE_OWNER_APPROVAL_REQUIRED:"+iid)
            if not _text(r.get("reason")):e.append("RETIRE_REASON_REQUIRED:"+iid)
            if not _text(r.get("successor_or_historical_ref")):e.append("RETIRE_REFERENCE_REQUIRED:"+iid)
        elif d=="NEW":
            if old is not None or not isinstance(now,Mapping):e.append("NEW_SHAPE_INVALID:"+iid)
        elif d=="UNRESOLVED":e.append("UNRESOLVED_ROW:"+iid)
    if expected-seen:e.append("MISSING_ROW_COUNT:"+str(len(expected-seen)))
    if seen-expected:e.append("EXTRA_ROW_COUNT:"+str(len(seen-expected)))
    if m.get("summary")!=summarize(m):e.append("SUMMARY_MISMATCH")
    if m.get("manifest_sha256")!=digest({k:v for k,v in m.items() if k!="manifest_sha256"}):e.append("MANIFEST_DIGEST_MISMATCH")
    if release_ready and e==[] and not summarize(m)["release_ready"]:e.append("CARRY_FORWARD_NOT_RELEASE_READY")
    return e
def main()->int:
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="cmd",required=True)
    g=sub.add_parser("generate");g.add_argument("--previous",type=Path,required=True);g.add_argument("--current",type=Path,required=True);g.add_argument("--decisions",type=Path);g.add_argument("--out",type=Path,required=True)
    v=sub.add_parser("validate");v.add_argument("--previous",type=Path,required=True);v.add_argument("--current",type=Path,required=True);v.add_argument("--manifest",type=Path,required=True);v.add_argument("--release-ready",action="store_true")
    a=p.parse_args();load=lambda x:json.loads(x.read_text())
    try:
        prev,cur=load(a.previous),load(a.current)
        if a.cmd=="generate":
            m=build_manifest(prev,cur,load(a.decisions) if a.decisions else None);a.out.write_text(json.dumps(m,indent=2)+"\n");print(json.dumps({"result":"PASS","manifest_sha256":m["manifest_sha256"],**m["summary"]},sort_keys=True));return 0
        m=load(a.manifest);errs=validate_manifest(m,prev,cur,a.release_ready);print(json.dumps({"result":"PASS" if not errs else "FAIL","errors":errs,"summary":m.get("summary")},sort_keys=True));return 0 if not errs else 1
    except Exception as exc:print(json.dumps({"result":"FAIL","errors":[type(exc).__name__+":"+str(exc)]},sort_keys=True));return 2
if __name__=="__main__":sys.exit(main())
