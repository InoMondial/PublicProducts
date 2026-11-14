"""Evidence-bound remote egress. Caller/host authenticates supplied observations."""
import importlib.util,pathlib

def assert_egress(source,context):
    if not isinstance(context,dict):raise ValueError('EGRESS_CONTEXT_REQUIRED')
    skills=next(p for p in pathlib.Path(__file__).resolve().parents if p.name=='skills')
    candidates=list(skills.glob('g8-*/scripts/public_boundary.py'))+list(skills.glob('quality/g8-*/scripts/public_boundary.py'))
    if len(candidates)!=1:raise ValueError('PRIVACY_BOUNDARY_AUTHORITY_AMBIGUOUS')
    script=candidates[0]
    spec=importlib.util.spec_from_file_location('public_boundary',script)
    b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
    target=context.get('target',{})
    if target.get('visibility') in {'PRIVATE','INTERNAL'}:
        b.private_destination(target)
        return
    # Public output always rescans actual final bytes at the write boundary.
    report=b.Scanner(context.get('policy')).scan(source)
    errors=b.authorize(report,context.get('review',{}),context.get('consent',{}),context.get('surfaces',{}),target)
    if errors:raise ValueError('PUBLIC_EGRESS_BLOCKED:'+','.join(errors))
