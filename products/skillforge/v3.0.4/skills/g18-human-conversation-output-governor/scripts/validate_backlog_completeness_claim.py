#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
from typing import Any,Mapping
def allowed(receipt:Mapping[str,Any])->bool:
    return receipt.get("contract")=="INC_OWNER_CONVERSATION_BACKLOG_COVERAGE_V1" and receipt.get("status")=="PASS" and receipt.get("unmapped_count")==0 and receipt.get("mirror_parity") is True and isinstance(receipt.get("canonical_backlog_sha_after"),str) and bool(receipt.get("canonical_backlog_sha_after").strip())
def main()->int:
    p=argparse.ArgumentParser();p.add_argument("--receipt",type=Path,required=True);a=p.parse_args()
    try:r=json.loads(a.receipt.read_text(encoding="utf-8"))
    except Exception:print("BACKLOG_COMPLETENESS_RECEIPT_INVALID");return 2
    if allowed(r):print("BACKLOG_COMPLETENESS_CLAIM_ALLOWED");return 0
    print("BACKLOG_COMPLETENESS_CLAIM_BLOCKED");return 1
if __name__=="__main__":sys.exit(main())
