#!/usr/bin/env python3
"""Reconcile evidence against a host-supplied authority; no embedded tenant IDs."""
from urllib.parse import urlparse,unquote
from evidence_freshness import validate_object
GH_HOST='github.com'
TEAMS_HOSTS={'teams.microsoft.com','teams.cloud.microsoft'}

def good_url(v,hosts):
    try:
        u=urlparse(v)
        return u.scheme=='https' and u.hostname in hosts and not (u.username or u.password)
    except (TypeError,ValueError):return False

def validate(evidence,require_sharepoint=False,require_teams=False,transaction_id=None,
             transaction_started_at=None,now=None,*,expected_authority=None):
    missing=[];bad=[];g=evidence.get('github',{})
    if not good_url(g.get('canonical_folder_url',''),{GH_HOST}):bad.append('github.canonical_folder_url')
    if transaction_id:
        if evidence.get('transaction_id')!=transaction_id:bad.append('transaction_id')
        if transaction_started_at and not validate_object(evidence,transaction_id,transaction_started_at,now).get('ok'):bad.append('evidence.freshness')
    if require_sharepoint:
        s=evidence.get('sharepoint',{})
        for k in ('folder_url','folder_id','site_id','drive_id','backup_root_id','readback_state','ancestry_verified'):
            if s.get(k) in (None,'',False):missing.append('sharepoint.'+k)
        auth=expected_authority if isinstance(expected_authority,dict) else {}
        if auth.get('verified') is not True or not auth.get('profile_sha256'):
            bad.append('sharepoint.external_authority_required')
        for k in ('host','site_id','drive_id','backup_root_id','backup_root_path'):
            if not isinstance(auth.get(k),str) or not auth[k].strip():bad.append('authority.'+k)
        if not good_url(s.get('folder_url',''),{auth.get('host')}):bad.append('sharepoint.folder_url')
        path=unquote(urlparse(s.get('folder_url','')).path)
        root=str(auth.get('backup_root_path') or '')
        if not root or not (path.rstrip('/')==root.rstrip('/') or path.startswith(root.rstrip('/')+'/')):
            bad.append('sharepoint.backup_root_path')
        for k in ('site_id','drive_id','backup_root_id'):
            if not auth.get(k) or s.get(k)!=auth[k]:bad.append('sharepoint.'+k)
        if s.get('readback_state')!='PASS':bad.append('sharepoint.readback_state')
        if s.get('ancestry_verified') is not True:bad.append('sharepoint.ancestry_verified')
    if require_teams:
        t=evidence.get('teams',{})
        for k in ('team_id','channel_id','message_id','post_url','readback_state'):
            if not t.get(k):missing.append('teams.'+k)
        if not good_url(t.get('post_url',''),TEAMS_HOSTS):bad.append('teams.post_url')
        if t.get('readback_state')!='PASS':bad.append('teams.readback_state')
    ok=not missing and not bad
    return {'ok':ok,'missing':sorted(set(missing)),'invalid':sorted(set(bad)),
            'status':'PASS' if ok else 'EVIDENCE_LINK_RECONCILIATION_FAILED'}
