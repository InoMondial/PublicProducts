#!/usr/bin/env python3
"""Cooperative local-file exclusion, NOT a distributed lease or provider CAS.

Expired locks require explicit reconciliation. Read-then-unlink reclamation is
unsafe: a racing contender can delete a replacement lock after expiry checks.
"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import json, os, secrets

def now(): return datetime.now(timezone.utc)
def acquire(path,lineage,owner,ttl_seconds=300):
    if type(ttl_seconds) is not int or not 0<ttl_seconds<=86400:
        raise ValueError('LINEAGE_LOCK_TTL_INVALID')
    if not all(isinstance(v,str) and v.strip() for v in (lineage,owner)):
        raise ValueError('LINEAGE_LOCK_IDENTITY_INVALID')
    p=Path(path); stamp=now(); token=secrets.token_hex(16)
    payload={'lineage':lineage,'owner':owner,'token':token,'acquired_at':stamp.isoformat(),'expires_at':(stamp+timedelta(seconds=ttl_seconds)).isoformat()}
    try:
        fd=os.open(str(p),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    except FileExistsError:
        # Do not reclaim even a corrupt, expired or symlinked lock automatically.
        raise RuntimeError('LINEAGE_LOCK_CONFLICT_RECONCILIATION_REQUIRED') from None
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as stream:
            json.dump(payload,stream,sort_keys=True);stream.flush();os.fsync(stream.fileno())
    except BaseException:
        # Leave uncertain partial acquisition for reconciliation, not blind retry.
        raise
    return payload

def release(path,token):
    p=Path(path)
    if p.is_symlink() or not isinstance(token,str) or not token:
        raise RuntimeError('LINEAGE_LOCK_TOKEN_MISMATCH')
    try:cur=json.loads(p.read_text(encoding='utf-8'))
    except (OSError,ValueError):raise RuntimeError('LINEAGE_LOCK_STATE_UNVERIFIED') from None
    if not isinstance(cur,dict) or cur.get('token')!=token:
        raise RuntimeError('LINEAGE_LOCK_TOKEN_MISMATCH')
    p.unlink();return True
