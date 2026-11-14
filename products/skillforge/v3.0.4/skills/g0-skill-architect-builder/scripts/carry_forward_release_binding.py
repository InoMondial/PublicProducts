#!/usr/bin/env python3
from __future__ import annotations
import re
from typing import Any, Mapping
HEX64=re.compile(r"[0-9a-f]{64}")
def _m(v:Any)->Mapping[str,Any]:return v if isinstance(v,Mapping) else {}
def validate(candidate:Mapping[str,Any],trusted:Mapping[str,Any])->list[str]:
    if candidate.get("carry_forward_gate_required") is not True:return []
    e=[];md=candidate.get("carry_forward_manifest_sha256");pd=candidate.get("carry_forward_previous_snapshot_sha256");cd=candidate.get("carry_forward_current_snapshot_sha256")
    for name,val in (("MANIFEST",md),("PREVIOUS_SNAPSHOT",pd),("CURRENT_SNAPSHOT",cd)):
        if not isinstance(val,str) or HEX64.fullmatch(val) is None:e.append("CARRY_FORWARD_"+name+"_DIGEST_INVALID")
    r=_m(trusted.get("carry_forward_manifest"))
    checks=[(r.get("verified") is True,"CARRY_FORWARD_NOT_VERIFIED"),(r.get("result")=="PASS","CARRY_FORWARD_NOT_PASS"),(r.get("release_ready") is True,"CARRY_FORWARD_NOT_RELEASE_READY"),(r.get("unresolved_count")==0,"CARRY_FORWARD_UNRESOLVED"),(r.get("manifest_sha256")==md,"CARRY_FORWARD_MANIFEST_DIGEST_MISMATCH"),(r.get("previous_snapshot_sha256")==pd,"CARRY_FORWARD_PREVIOUS_SNAPSHOT_DIGEST_MISMATCH"),(r.get("current_snapshot_sha256")==cd,"CARRY_FORWARD_CURRENT_SNAPSHOT_DIGEST_MISMATCH")]
    e.extend(code for ok,code in checks if not ok);return e
def certificate_error(candidate:Mapping[str,Any],receipt:Mapping[str,Any],role:str)->str|None:
    if candidate.get("carry_forward_gate_required") is not True:return None
    for key,code in (("carry_forward_manifest_sha256","MANIFEST"),("carry_forward_previous_snapshot_sha256","PREVIOUS_SNAPSHOT"),("carry_forward_current_snapshot_sha256","CURRENT_SNAPSHOT")):
        if receipt.get(key)!=candidate.get(key):return f"CARRY_FORWARD_CERTIFICATE_{code}_DIGEST_MISMATCH:{role}"
    return None
