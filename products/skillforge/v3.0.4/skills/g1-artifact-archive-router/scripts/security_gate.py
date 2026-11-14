#!/usr/bin/env python3
"""G1 scan delegates to the single G8 engine; never silently skips archives."""
import importlib.util,json,pathlib,sys

def scan(root,policy=None):
    skills=next(p for p in pathlib.Path(__file__).resolve().parents if p.name=='skills')
    candidates=list(skills.glob('g8-*/scripts/public_boundary.py'))+list(skills.glob('quality/g8-*/scripts/public_boundary.py'))
    if len(candidates)!=1:raise ValueError('PRIVACY_BOUNDARY_AUTHORITY_AMBIGUOUS')
    script=candidates[0]
    spec=importlib.util.spec_from_file_location('public_boundary',script)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    return m.Scanner(policy).scan(root)
if __name__=='__main__':
    r=scan(sys.argv[1]);print(json.dumps({'status':r['status'],'finding_count':len(r['findings']),'unit_count':r['unit_count']}));raise SystemExit(bool(r['findings']))
