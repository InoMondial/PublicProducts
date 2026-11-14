#!/usr/bin/env python3
from datetime import datetime, timezone, timedelta

def dt(v):
    if isinstance(v,datetime):result=v
    elif isinstance(v,str):result=datetime.fromisoformat(v.replace('Z','+00:00'))
    else:raise ValueError('TIMESTAMP_REQUIRED')
    if result.tzinfo is None or result.utcoffset() is None:raise ValueError('TIMESTAMP_ZONE_REQUIRED')
    return result.astimezone(timezone.utc)

def validate(captured_at,transaction_started_at,now=None,ttl_seconds=86400,skew_seconds=300):
    try:
        if type(ttl_seconds) is not int or ttl_seconds<=0 or type(skew_seconds) is not int or skew_seconds<0:raise ValueError('FRESHNESS_POLICY_INVALID')
        current=dt(now if now is not None else datetime.now(timezone.utc));cap=dt(captured_at);start=dt(transaction_started_at);skew=timedelta(seconds=skew_seconds)
        ok=start<=current+skew and cap>=start-skew and cap<=current+skew and (current-cap).total_seconds()<=ttl_seconds
    except (ValueError,TypeError,OverflowError):ok=False
    return {'ok':ok,'status':'PASS' if ok else 'EVIDENCE_STALE_OR_WRONG_TRANSACTION'}

def validate_object(obj,transaction_id,transaction_started_at,now=None,ttl_seconds=86400):
    if (not isinstance(obj,dict) or not isinstance(transaction_id,str) or not transaction_id.strip()
        or obj.get('transaction_id')!=transaction_id or not obj.get('observed_at')):
        return {'ok':False,'status':'EVIDENCE_STALE_OR_WRONG_TRANSACTION'}
    return validate(obj['observed_at'],transaction_started_at,now,ttl_seconds)
