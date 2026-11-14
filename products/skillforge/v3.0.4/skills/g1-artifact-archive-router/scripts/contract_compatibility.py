#!/usr/bin/env python3

def parse(v):
    a=str(v).strip().split('.'); return int(a[0]),int(a[1] if len(a)>1 else 0)
def validate(observed,matrix):
    bad=[]
    for name,rule in matrix.get('contracts',{}).items():
        if name not in observed: bad.append({'contract':name,'reason':'MISSING'}); continue
        try: major,minor=parse(observed[name])
        except Exception: bad.append({'contract':name,'reason':'INVALID_VERSION'}); continue
        if major!=int(rule['schema_major']) or minor<int(rule['min_minor']) or minor>int(rule['max_minor']): bad.append({'contract':name,'reason':'UNSUPPORTED','observed':observed[name]})
    return {'ok':not bad,'incompatible':bad,'status':'PASS' if not bad else 'CONTRACT_COMPATIBILITY_FAILED'}
