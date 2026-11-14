#!/usr/bin/env python3
"""Offline, explicit-allowlist export preparation; NEVER publishes or grants consent."""
from pathlib import Path
import hashlib, json, shutil
from public_boundary import Scanner, REVIEW_CLASSES, path_ok

def prepare(source, destination, review, policy=None):
    source=Path(source).resolve();destination=Path(destination).resolve()
    if destination.exists() or destination.is_relative_to(source) or source.is_relative_to(destination):
        raise ValueError('FRESH_DISJOINT_STAGING_REQUIRED')
    report=Scanner(policy).scan(source)
    if report['status']!='STATIC_SCAN_PASS':raise ValueError('SOURCE_PRIVACY_SCAN_FAILED')
    if review.get('tree_digest')!=report['tree_digest']:raise ValueError('STALE_REVIEW')
    rows=review.get('files')
    if not isinstance(rows,dict) or set(rows)!=set(report['units']):raise ValueError('UNREVIEWED_FILES')
    selected=[]
    for name,meta in report['units'].items():
        r=rows[name]
        if (not isinstance(r,dict) or r.get('sha256')!=meta['sha256']
            or r.get('classification') not in REVIEW_CLASSES or not r.get('reason')):
            raise ValueError('SEMANTIC_REVIEW_REQUIRED')
        if r['classification']=='APPROVED_DISCLOSURE' and not r.get('consent_id'):
            raise ValueError('FIELD_DISCLOSURE_CONSENT_REQUIRED')
        # Archive members were inspected but their parent archive alone is copied.
        if '!/' not in name:
            if not path_ok(name):raise ValueError('UNSAFE_PATH')
            selected.append((name,meta['sha256']))
    destination.mkdir(parents=True)
    try:
        for name,expected in selected:
            raw=(source/name).read_bytes()
            if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('SOURCE_CHANGED')
            p=destination/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
        final=Scanner(policy).scan(destination)
        if final['status']!='STATIC_SCAN_PASS' or final['tree_digest']!=report['tree_digest']:
            raise ValueError('STAGED_BYTES_DIFFER')
        return {'status':'STAGED_PRIVATELY','tree_digest':final['tree_digest'],
                'file_count':len(selected),'public_release_authorized':False}
    except Exception:
        shutil.rmtree(destination)
        raise
