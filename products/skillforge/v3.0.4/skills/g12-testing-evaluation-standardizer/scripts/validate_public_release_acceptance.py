#!/usr/bin/env python3
"""Complete public release privacy boundary; PRIVATE is not a public waiver."""
from __future__ import annotations
import hashlib, importlib.util, json, pathlib, sys
import yaml
CONTRACT='INC_SKILLFORGE_PUBLIC_RELEASE_ACCEPTANCE_V1'
REQUIRED_ROOT={'LICENSE','NOTICE','THIRD_PARTY_NOTICES','TRADEMARKS','CONTRIBUTING.md','SECURITY.md','RIGHTS_PROFILE.yaml','PUBLIC_EXPORT_MANIFEST.json'}
ALGORITHM='SHA256_SORTED_PATH_NUL_FILE_SHA256_V1'

def engine():
    skills=next(p for p in pathlib.Path(__file__).resolve().parents if p.name=='skills')
    candidates=list(skills.glob('g8-*/scripts/public_boundary.py'))+list(skills.glob('quality/g8-*/scripts/public_boundary.py'))
    if len(candidates)!=1:raise ValueError('PRIVACY_BOUNDARY_AUTHORITY_AMBIGUOUS')
    scripts=candidates[0]
    spec=importlib.util.spec_from_file_location('public_boundary',scripts)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def export_tree_digest(root):
    h=hashlib.sha256();root=pathlib.Path(root)
    for p in sorted(root.rglob('*')):
        if p.is_file() and p.name!='PUBLIC_EXPORT_MANIFEST.json':
            h.update(p.relative_to(root).as_posix().encode());h.update(b'\0');h.update(hashlib.sha256(p.read_bytes()).digest())
    return h.hexdigest()

def validate(contract_path,export_root,visibility='PUBLIC',*,policy=None,review=None,consent=None,surfaces=None,target=None):
    v=str(visibility or '').strip().upper()
    if v not in {'PRIVATE','INTERNAL','PUBLIC'}:return ['DISTRIBUTION_VISIBILITY_INVALID']
    if v!='PUBLIC':
        if target and target.get('visibility')=='PUBLIC':return ['DECLARED_PRIVATE_ACTUAL_PUBLIC_MISMATCH']
        return []
    errors=[];root=pathlib.Path(export_root)
    try:c=yaml.safe_load(pathlib.Path(contract_path).read_text(encoding='utf-8'))
    except (OSError,ValueError,yaml.YAMLError):return ['CONTRACT_UNREADABLE']
    if not isinstance(c,dict) or c.get('contract_id')!=CONTRACT:errors.append('CONTRACT_ID_INVALID')
    if any(not (root/n).is_file() or (root/n).is_symlink() for n in REQUIRED_ROOT):errors.append('REQUIRED_PUBLIC_SURFACE_MISSING')
    try:
        m=json.loads((root/'PUBLIC_EXPORT_MANIFEST.json').read_text())
        if m.get('source_history_copied') is not False or m.get('private_overlay_exported') is not False:errors.append('PRIVATE_BOUNDARY_UNPROVEN')
        if m.get('digest_algorithm')!=ALGORITHM or m.get('tree_digest')!=export_tree_digest(root):errors.append('TREE_DIGEST_MISMATCH')
    except (OSError,ValueError,AttributeError):errors.append('MANIFEST_INVALID')
    b=engine();report=b.Scanner(policy).scan(root)
    if any(f['code'] in {'FORBIDDEN_PATH','SYMLINK','UNSAFE_ARCHIVE_PATH'} for f in report['findings']):errors.append('PRIVATE_PATH_IN_EXPORT')
    errors.extend(b.authorize(report,review or {},consent or {},surfaces or {},target or {}))
    return sorted(set(errors))

if __name__=='__main__':
    # No review/consent envelope via the legacy CLI means PUBLIC fails closed.
    e=validate(sys.argv[1],sys.argv[2],sys.argv[3] if len(sys.argv)>3 else 'PUBLIC')
    print('PASS' if not e else 'FAIL:'+','.join(e));raise SystemExit(bool(e))
