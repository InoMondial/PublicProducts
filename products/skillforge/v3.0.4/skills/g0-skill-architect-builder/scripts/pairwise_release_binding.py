#!/usr/bin/env python3
from __future__ import annotations
import re
from typing import Any, Mapping
HEX64=re.compile(r"[0-9a-f]{64}")
def _mapping(value:Any)->Mapping[str,Any]: return value if isinstance(value,Mapping) else {}
def validate_pairwise_release_binding(candidate:Mapping[str,Any],trusted_context:Mapping[str,Any])->list[str]:
    e=[]
    if candidate.get("pairwise_gate_required") is not True:return e
    ms=candidate.get("pairwise_matrix_sha256");hs=candidate.get("pairwise_member_set_sha256")
    if not isinstance(ms,str) or HEX64.fullmatch(ms) is None:e.append("PAIRWISE_MATRIX_DIGEST_INVALID")
    if not isinstance(hs,str) or HEX64.fullmatch(hs) is None:e.append("PAIRWISE_MEMBER_SET_DIGEST_INVALID")
    r=_mapping(trusted_context.get("pairwise_matrix"))
    checks=[(r.get("verified") is True,"PAIRWISE_MATRIX_NOT_VERIFIED"),(r.get("result")=="PASS","PAIRWISE_MATRIX_NOT_PASS"),(r.get("release_ready") is True,"PAIRWISE_MATRIX_NOT_RELEASE_READY"),(r.get("member_count")==19,"PAIRWISE_MEMBER_COUNT_INVALID"),(r.get("directed_relationship_count")==342,"PAIRWISE_DIRECTED_COUNT_INVALID"),(r.get("unique_unordered_pair_count")==171,"PAIRWISE_UNORDERED_COUNT_INVALID"),(r.get("matrix_sha256")==ms,"PAIRWISE_MATRIX_DIGEST_MISMATCH"),(r.get("member_set_sha256")==hs,"PAIRWISE_MEMBER_SET_DIGEST_MISMATCH")]
    e.extend(code for ok,code in checks if not ok);return e
def certificate_pairwise_error(candidate:Mapping[str,Any],receipt:Mapping[str,Any],role:str)->str|None:
    if candidate.get("pairwise_gate_required") is not True:return None
    if receipt.get("pairwise_matrix_sha256")!=candidate.get("pairwise_matrix_sha256"):return f"PAIRWISE_CERTIFICATE_DIGEST_MISMATCH:{role}"
    if receipt.get("pairwise_member_set_sha256")!=candidate.get("pairwise_member_set_sha256"):return f"PAIRWISE_CERTIFICATE_MEMBER_SET_MISMATCH:{role}"
    return None
