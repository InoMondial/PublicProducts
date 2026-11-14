#!/usr/bin/env python3
import argparse,json
from pathlib import Path

CONTRACT="INC_G16_HANDOFF_TRANSACTIONAL_WRITER_V1"

def fail(c,d):
    print(f"{c}: {d}"); return 1

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("file"); a=ap.parse_args()
    d=json.loads(Path(a.file).read_text(encoding="utf-8"))
    req=["contract","operation","S","M","remote_revision_before","remote_revision_after","postwrite_readback_verified","state_sha256_after"]
    miss=[k for k in req if k not in d]
    if miss:return fail("G16_TX_RECEIPT_FIELD_MISSING",",".join(miss))
    if d["contract"]!=CONTRACT:return fail("G16_TX_CONTRACT_MISMATCH",str(d["contract"]))
    if d["operation"] not in ("ALLOCATE_INTERACTION","RESUME_INTERACTION","COMMIT_MATERIAL","CLOSE_INTERACTION"):
        return fail("G16_TX_OPERATION_INVALID",str(d["operation"]))
    if type(d["S"]) is not int or d["S"]<0:return fail("G16_TX_S_INVALID","S")
    if type(d["M"]) is not int or d["M"]<0:return fail("G16_TX_M_INVALID","M")
    if "next_S" in d or "next_M" in d:return fail("G16_TX_CALLER_SUPPLIED_NEXT_COUNTER_PROHIBITED","next_S/next_M")
    if not d["remote_revision_before"] or not d["remote_revision_after"]:
        return fail("G16_TX_REMOTE_REVISION_REQUIRED","before/after")
    if d["remote_revision_before"]==d["remote_revision_after"]:
        return fail("G16_TX_REMOTE_REVISION_NOT_ADVANCED","write receipt requires changed remote revision")
    if d["postwrite_readback_verified"] is not True:
        return fail("G16_TX_POSTWRITE_READBACK_REQUIRED","verified readback required")
    if d["operation"]=="ALLOCATE_INTERACTION" and d.get("increment_S")!=1:
        return fail("G16_TX_S_EXACTLY_ONCE_REQUIRED","allocate must increment S exactly one")
    if d["operation"]=="RESUME_INTERACTION" and d.get("increment_S")!=0:
        return fail("G16_TX_RESUME_DUPLICATE_S","resume must not increment S")
    if d["operation"]=="COMMIT_MATERIAL":
        if d.get("increment_M")!=1:return fail("G16_TX_M_EXACTLY_ONCE_REQUIRED","material commit must increment M exactly one")
        if not d.get("ledger_digest"):return fail("G16_TX_TOOL_LEDGER_DIGEST_REQUIRED","ledger_digest")
    print("G16_HANDOFF_TRANSACTION_RECEIPT_PASS"); return 0

if __name__=="__main__": raise SystemExit(main())
