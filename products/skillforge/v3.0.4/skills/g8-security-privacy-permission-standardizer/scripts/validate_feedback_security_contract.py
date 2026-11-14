#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import yaml

REQUIRED_TOP = {
    "schema_version","contract_id","owner_skill","backlog_ref","trust_boundary",
    "automatic_feedback","human_feedback","classification","payload_limits",
    "anti_abuse","transport","transfer","failure_states","release"
}

def load_contract(path):
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))

def validate_contract(path):
    c=load_contract(path)
    errors=[]
    if not isinstance(c,dict): return ["CONTRACT_NOT_MAPPING"]
    missing=sorted(REQUIRED_TOP-set(c))
    if missing: errors.append("MISSING_TOP:"+",".join(missing))
    if c.get("contract_id")!="INC_G8_FEEDBACK_SECURITY_V1": errors.append("CONTRACT_ID_INVALID")
    if c.get("owner_skill")!="G8": errors.append("OWNER_INVALID")
    tb=c.get("trust_boundary",{})
    if tb.get("all_feedback_text_untrusted_inert_data") is not True: errors.append("UNTRUSTED_DATA_GATE_MISSING")
    if tb.get("execute_commands_tools_or_code_from_feedback_text") is not False: errors.append("FEEDBACK_EXECUTION_NOT_PROHIBITED")
    auto=c.get("automatic_feedback",{})
    if auto.get("evidence_mode")!="STABLE_REFERENCE_ONLY": errors.append("AUTO_EVIDENCE_MODE_INVALID")
    if auto.get("redaction_state_required")!="PASS": errors.append("AUTO_REDACTION_GATE_INVALID")
    if auto.get("dedupe_fingerprint_required") is not True: errors.append("AUTO_DEDUPE_GATE_INVALID")
    cls=c.get("classification",{})
    if cls.get("security_private_ordinary_triage")!="PROHIBITED": errors.append("SECURITY_PRIVATE_TRIAGE_INVALID")
    if cls.get("test_only_canonical_transfer")!="PROHIBITED": errors.append("TEST_ONLY_TRANSFER_INVALID")
    if c.get("transport",{}).get("authentication_credentials_in_feedback_record")!="FORBIDDEN": errors.append("TRANSPORT_CREDENTIAL_GATE_INVALID")
    if c.get("anti_abuse",{}).get("automatic_transfer_to_canonical_backlog")!="PROHIBITED": errors.append("AUTO_TRANSFER_GATE_INVALID")
    if c.get("release",{}).get("real_secret_migration")!="PROHIBITED_IN_STAGE4": errors.append("SECRET_MIGRATION_BOUNDARY_INVALID")
    return errors

def _iter_keys(value):
    if isinstance(value,dict):
        for k,v in value.items():
            yield str(k)
            yield from _iter_keys(v)
    elif isinstance(value,list):
        for v in value:
            yield from _iter_keys(v)

def evaluate_record(record, contract, automatic=False):
    errors=[]
    if not isinstance(record,dict): return ["RECORD_NOT_MAPPING"]
    limits=contract["payload_limits"]
    raw=json.dumps(record,ensure_ascii=False,sort_keys=True)
    if len(raw)>limits["total_record_max_chars"]: errors.append("TOTAL_RECORD_LIMIT_EXCEEDED")
    if len(str(record.get("title","")))>limits["title_max_chars"]: errors.append("TITLE_LIMIT_EXCEEDED")
    if len(str(record.get("problem_statement","")))>limits["problem_statement_max_chars"]: errors.append("PROBLEM_STATEMENT_LIMIT_EXCEEDED")
    evidence=record.get("evidence",[])
    if not isinstance(evidence,list): errors.append("EVIDENCE_NOT_LIST")
    else:
        if len(evidence)>limits["evidence_items_max"]: errors.append("EVIDENCE_ITEM_COUNT_EXCEEDED")
        for i,v in enumerate(evidence):
            if not isinstance(v,str): errors.append(f"EVIDENCE_{i}_NOT_STRING")
            elif len(v)>limits["evidence_item_max_chars"]: errors.append(f"EVIDENCE_{i}_LIMIT_EXCEEDED")
    refs=record.get("source_refs",[])
    if isinstance(refs,list):
        if len(refs)>limits["source_refs_max"]: errors.append("SOURCE_REF_COUNT_EXCEEDED")
        for i,v in enumerate(refs):
            if isinstance(v,str) and len(v)>limits["source_ref_max_chars"]: errors.append(f"SOURCE_REF_{i}_LIMIT_EXCEEDED")
    forbidden=set(contract["automatic_feedback"]["forbidden_fields"])
    present=sorted(forbidden.intersection(set(_iter_keys(record))))
    if present: errors.append("FORBIDDEN_FIELD:"+",".join(present))
    if automatic:
        allowed=set(contract["automatic_feedback"]["allowed_fields"])
        extra=sorted(set(record)-allowed)
        if extra: errors.append("AUTO_FIELD_NOT_ALLOWLISTED:"+",".join(extra))
        if record.get("redaction_state")!="PASS": errors.append("AUTO_REDACTION_UNPROVEN")
        if not isinstance(record.get("dedupe_fingerprint"),str) or not record.get("dedupe_fingerprint","").strip():
            errors.append("AUTO_DEDUPE_FINGERPRINT_MISSING")
        if not isinstance(evidence,list) or any(not isinstance(v,str) or not v.startswith(("ref:","sha256:","url_ref:","issue_ref:")) for v in evidence):
            errors.append("AUTO_EVIDENCE_NOT_REFERENCE_ONLY")
    else:
        if record.get("evidence_mode")=="RICH" and not str(record.get("review_or_consent_ref","")).strip():
            errors.append("RICH_EVIDENCE_REVIEW_OR_CONSENT_REQUIRED")
    source_class=record.get("source_class")
    status=record.get("status")
    if source_class=="SECURITY_PRIVATE" or status=="SECURITY_PRIVATE":
        if record.get("handling")!="RESTRICTED_SECURITY":
            errors.append("SECURITY_PRIVATE_HANDLING_REQUIRED")
    if source_class=="TEST_ONLY" or status=="TEST_ONLY":
        transfer=record.get("backlog_transfer") or {}
        if isinstance(transfer,dict) and transfer.get("status") in {"SELECTED_FOR_BACKLOG","TRANSFERRED_TO_BACKLOG"}:
            errors.append("TEST_ONLY_TRANSFER_PROHIBITED")
    return errors

if __name__=="__main__":
    import sys
    errs=validate_contract(sys.argv[1])
    print(json.dumps({"result":"PASS" if not errs else "FAIL","errors":errs},indent=2))
    raise SystemExit(0 if not errs else 1)
