#!/usr/bin/env python3
import argparse,json,re
from pathlib import Path

CONTRACT="INC_G16_HANDOFF_TRANSACTIONAL_WRITER_V1"
REQ=[
"current_stage","completed_stages","current_stage_percent","weighted_overall_percent","next_stage","next_state",
"handoff_id","interaction_seq","material_seq","visible_ref","handoff_url","handoff_updated_at","run_status",
"current_work_unit","last_completed_work_unit","resume_from","evidence_revision","evidence_timestamp",
"current_turn_S_receipt","material_M_receipts","post_write_readback_verified"
]

def fail(c,d):
    print(f"{c}: {d}"); return 1

def pct(v):
    return v is None or (isinstance(v,(int,float)) and not isinstance(v,bool) and 0<=v<=100)

def nonneg_int(v):
    return type(v) is int and v>=0

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("file"); a=ap.parse_args()
    d=json.loads(Path(a.file).read_text(encoding="utf-8"))
    miss=[k for k in REQ if k not in d]
    if miss:return fail("G16_PROJECT_RETURN_FIELD_MISSING",",".join(miss))
    if not isinstance(d["handoff_id"],str) or not re.fullmatch(r"HOF-[A-Z0-9]+",d["handoff_id"]):
        return fail("G16_HANDOFF_ID_INVALID","handoff_id")
    if not nonneg_int(d["interaction_seq"]):return fail("G16_HANDOFF_S_REQUIRED","interaction_seq")
    if not nonneg_int(d["material_seq"]):return fail("G16_HANDOFF_M_REQUIRED","material_seq")
    exp=f"{d['handoff_id']} | S:{d['interaction_seq']} | M:{d['material_seq']}"
    if d["visible_ref"]!=exp:return fail("G16_HANDOFF_VISIBLE_REF_MISMATCH",f"expected {exp}")
    if not isinstance(d["handoff_url"],str) or not d["handoff_url"].startswith("https://"):
        return fail("G16_HANDOFF_URL_INVALID","verified https URL required")
    if not pct(d["current_stage_percent"]) or not pct(d["weighted_overall_percent"]):
        return fail("G16_PROJECT_PERCENT_INVALID","percentages must be evidence-backed 0..100 or null")
    if d["evidence_revision"] in ("",None) or d["evidence_timestamp"] in ("",None):
        return fail("G16_PROJECT_EVIDENCE_REVISION_REQUIRED","evidence revision/timestamp required")
    sr=d["current_turn_S_receipt"]
    if not isinstance(sr,dict) or sr.get("contract")!=CONTRACT:
        return fail("G16_CURRENT_TURN_S_RECEIPT_REQUIRED","transactional writer receipt required")
    if sr.get("operation") not in ("ALLOCATE_INTERACTION","RESUME_INTERACTION"):
        return fail("G16_CURRENT_TURN_S_RECEIPT_INVALID","unexpected operation")
    if sr.get("S")!=d["interaction_seq"]:
        return fail("G16_CURRENT_TURN_S_RECEIPT_MISMATCH","receipt S differs from current S")
    mr=d["material_M_receipts"]
    if not isinstance(mr,list):return fail("G16_MATERIAL_M_RECEIPTS_INVALID","list required")
    for x in mr:
        if not isinstance(x,dict) or x.get("contract")!=CONTRACT or x.get("operation")!="COMMIT_MATERIAL":
            return fail("G16_MATERIAL_M_RECEIPT_INVALID","writer material receipt required")
        if x.get("S")!=d["interaction_seq"]:
            return fail("G16_HANDOFF_S_M_CAUSAL_BINDING_INVALID","M receipt causal S mismatch")
    if mr and mr[-1].get("M")!=d["material_seq"]:
        return fail("G16_MATERIAL_M_RECEIPT_STALE","terminal M receipt must equal current M")
    if not d["post_write_readback_verified"]:
        return fail("G16_HANDOFF_POSTWRITE_READBACK_REQUIRED","verified canonical readback required")
    print("G16_GOVERNED_PROJECT_RETURN_PASS"); return 0

if __name__=="__main__": raise SystemExit(main())
