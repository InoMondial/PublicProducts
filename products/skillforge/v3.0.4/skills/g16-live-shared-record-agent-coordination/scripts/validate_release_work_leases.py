#!/usr/bin/env python3
"""Read-only lease consistency. No authentication or distributed-lock claim."""
import argparse,json,re
from datetime import datetime,timezone
from pathlib import PurePosixPath,PureWindowsPath
REQ={'lease_id','agent_surface_id','owned_paths','base_sha','expires_at','dependencies','acceptance_criteria','return_target'}
def text(v):return isinstance(v,str) and bool(v.strip())
def path_prefix(value):
    if not text(value) or '\\' in value or PureWindowsPath(value).drive or PurePosixPath(value).is_absolute():raise ValueError('PATH_INVALID')
    clean=value.rstrip('/')
    if not clean or any(x in ('','..','.') for x in clean.split('/')):raise ValueError('PATH_INVALID')
    # Glob scopes conservatively own the prefix before the first wildcard.
    parts=[]
    for part in clean.split('/'):
        if any(c in part for c in '*?['):break
        parts.append(part)
    return tuple(x.casefold() for x in parts)
def validate(data,now=None):
    errors=[]
    if not isinstance(data,dict):return ['LEASE_LEDGER_INVALID']
    head=data.get('integration_head');leases=data.get('active_leases')
    if not isinstance(head,str) or not re.fullmatch('[0-9a-f]{40}',head):errors.append('RELEASE_HEAD_INVALID')
    if type(data.get('integration_writer_count')) is not int or data['integration_writer_count']!=1:errors.append('RELEASE_INTEGRATION_WRITER_COUNT_INVALID')
    if not isinstance(leases,list):return errors+['RELEASE_LEASES_REQUIRED']
    current=now or datetime.now(timezone.utc)
    if not isinstance(current,datetime) or current.tzinfo is None:return errors+['RELEASE_CLOCK_UNVERIFIED']
    seen_ids=set();scopes=[]
    for lease in leases:
        if not isinstance(lease,dict) or not REQ<=set(lease):errors.append('RELEASE_WORK_LEASE_FIELDS_MISSING');continue
        if not all(text(lease.get(k)) for k in ('lease_id','agent_surface_id','base_sha','expires_at','return_target')):
            errors.append('RELEASE_WORK_LEASE_IDENTITY_INVALID');continue
        lid=lease['lease_id']
        if lid in seen_ids:errors.append('RELEASE_WORK_LEASE_DUPLICATE_ID')
        seen_ids.add(lid)
        if lease['base_sha']!=head:errors.append('RELEASE_WORK_LEASE_STALE_BASE')
        try:
            expiry=datetime.fromisoformat(lease['expires_at'].replace('Z','+00:00'))
            if expiry.tzinfo is None or expiry<=current:raise ValueError()
        except (ValueError,TypeError):errors.append('RELEASE_WORK_LEASE_EXPIRED_OR_INVALID')
        if not isinstance(lease['dependencies'],list) or not all(text(x) for x in lease['dependencies']):errors.append('RELEASE_WORK_LEASE_DEPENDENCIES_INVALID')
        if not isinstance(lease['acceptance_criteria'],list) or not lease['acceptance_criteria'] or not all(text(x) for x in lease['acceptance_criteria']):errors.append('RELEASE_WORK_LEASE_ACCEPTANCE_INVALID')
        if not isinstance(lease['owned_paths'],list) or not lease['owned_paths']:errors.append('RELEASE_WORK_LEASE_PATHS_INVALID');continue
        for value in lease['owned_paths']:
            try:scope=path_prefix(value)
            except ValueError:errors.append('RELEASE_WORK_LEASE_PATH_INVALID');continue
            for prior,owner in scopes:
                overlap=scope[:len(prior)]==prior or prior[:len(scope)]==scope
                if overlap and owner!=lid:errors.append('RELEASE_WORK_LEASE_PATH_CONFLICT')
            scopes.append((scope,lid))
    if type(data.get('freeze_requested',False)) is not bool:errors.append('RELEASE_FREEZE_FLAG_INVALID')
    if data.get('freeze_requested') and leases:errors.append('RELEASE_FREEZE_WITH_ACTIVE_LEASES')
    return sorted(set(errors))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('ledger');a=ap.parse_args()
    try:
        with open(a.ledger,encoding='utf-8') as stream:errors=validate(json.load(stream))
    except (OSError,ValueError,TypeError):errors=['RELEASE_LEASE_INPUT_INVALID']
    print('\n'.join(errors) if errors else 'RELEASE_WORK_LEASES_PASS');return 1 if errors else 0
if __name__=='__main__':raise SystemExit(main())
