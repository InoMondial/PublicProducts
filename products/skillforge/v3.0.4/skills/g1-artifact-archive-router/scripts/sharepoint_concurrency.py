#!/usr/bin/env python3
"""Optimistic snapshot comparison only; never a substitute for provider CAS."""
import hashlib
import json

def _digest(items):
    return hashlib.sha256(json.dumps(items,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def snapshot(items, etag=None):
    if not isinstance(items,list) or (etag is not None and (not isinstance(etag,str) or not etag.strip())):
        raise ValueError('SHAREPOINT_SNAPSHOT_INVALID')
    canon=[]; seen=set()
    for item in items:
        if not isinstance(item,dict):raise ValueError('SHAREPOINT_SNAPSHOT_INVALID')
        ident=item.get('id'); size=item.get('size')
        if (not isinstance(ident,str) or not ident.strip() or ident in seen
            or not isinstance(item.get('name'),str) or not item['name']
            or type(size) is not int or size<0):
            raise ValueError('SHAREPOINT_SNAPSHOT_INVALID')
        seen.add(ident)
        canon.append({'id':ident,'name':item['name'],'size':size,'modified':item.get('modified')})
    canon.sort(key=lambda x:(x['id'],x['name']))
    return {'etag':etag,'digest':_digest(canon),'items':canon}

def assert_unchanged(before,current):
    try:
        if not isinstance(before,dict) or not isinstance(current,dict):raise ValueError()
        for value in (before,current):
            expected=snapshot(value['items'],value.get('etag'))
            if value.get('digest')!=expected['digest']:raise ValueError()
        # A matching etag never overrides changed bytes. An etag appearing or
        # disappearing is also a changed observation, not permission to proceed.
        ok=before['digest']==current['digest'] and before.get('etag')==current.get('etag')
    except (ValueError,TypeError,KeyError):
        ok=False
    return {'ok':ok,'status':'PASS' if ok else 'SHAREPOINT_CONCURRENCY_CONFLICT'}
