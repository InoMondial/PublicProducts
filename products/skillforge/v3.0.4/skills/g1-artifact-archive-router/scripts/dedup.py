#!/usr/bin/env python3

import re

def decide(expected_sha,canonical_path,remote_records):
    if not isinstance(expected_sha,str) or not re.fullmatch(r'[0-9a-f]{64}',expected_sha) or not isinstance(canonical_path,str) or not canonical_path.strip() or not isinstance(remote_records,list) or not all(isinstance(r,dict) for r in remote_records):
        raise ValueError('DEDUP_VERIFIED_IDENTITIES_REQUIRED')
    for r in remote_records:
        if r.get('path')==canonical_path and r.get('sha256')==expected_sha:
            return {'action':'NOOP_VERIFIED','canonical_satisfied':True}
    same=[r for r in remote_records if r.get('sha256')==expected_sha]
    if same: return {'action':'REUSE_CONTENT_OR_PUBLISH_CANONICAL_REFERENCE','canonical_satisfied':False,'matches':same}
    return {'action':'UPLOAD_REQUIRED','canonical_satisfied':False}
