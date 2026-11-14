#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, re
from pathlib import Path
import yaml

REQUIRED_GATES = {
    'deployment_of_certified_skillforge_confirmed',
    'sf_g8_002_implementation_pass',
    'final_g12_pass',
    'independent_g13_pass',
    'namespace_and_ownership_blockers_resolved',
    'target_azure_environment_owner_confirmed',
    'good_recoverable_backup_present',
    'rollback_manifest_present',
    'live_consumer_inventory_complete',
    'explicit_owner_execution_approval',
}
REQUIRED_UNIT_FIELDS = {
    'migration_unit_id','secret_ref','secret_class','source_authority_ref',
    'target_environment_ref','target_provider','consumer_refs','backup_ref',
    'rollback_ref','observation_window','status'
}
FORBIDDEN_KEYS = {
    'raw_secret','raw_secret_value','secret_value','password','api_key','auth_token',
    'access_token','refresh_token','private_key','private_key_bytes',
    'client_secret_value','certificate_private_key','client_secret','token','cookie','otp','mfa'
}
ALLOWED_CLASSES = {'G17_ROOT_KEY','HATCHABLE_BOOTSTRAP','OTHER_MACHINE_SECRET'}

def scan_forbidden(obj, path=''):
    hits=[]
    if isinstance(obj, dict):
        for k,v in obj.items():
            p=f'{path}.{k}' if path else str(k)
            normalized=re.sub(r'([a-z0-9])([A-Z])',r'\1_\2',re.sub(r'([A-Z]+)([A-Z][a-z])',r'\1_\2',str(k))).lower().replace('-','_')
            if normalized in FORBIDDEN_KEYS:
                hits.append(p)
            hits.extend(scan_forbidden(v,p))
    elif isinstance(obj, list):
        for i,v in enumerate(obj):
            hits.extend(scan_forbidden(v,f'{path}[{i}]'))
    return hits

def validate(data):
    errors=[]
    if not isinstance(data,dict):
        return ['ROOT_NOT_MAPPING']
    if data.get('contract_ref')!='INC_G8_SECRET_MIGRATION_V1':
        errors.append('CONTRACT_REF_INVALID')
    hits=scan_forbidden(data)
    if hits:
        errors.append('FORBIDDEN_SECRET_FIELD:' + ','.join(hits))
    gates=data.get('gates')
    if not isinstance(gates,dict) or set(gates)!=REQUIRED_GATES:
        errors.append('GATE_SET_INVALID')
    units=data.get('migration_units')
    if not isinstance(units,list):
        errors.append('MIGRATION_UNITS_NOT_LIST')
        units=[]
    seen=set()
    for idx,u in enumerate(units):
        if not isinstance(u,dict):
            errors.append(f'UNIT_{idx}_NOT_MAPPING')
            continue
        missing=REQUIRED_UNIT_FIELDS-set(u)
        if missing:
            errors.append(f'UNIT_{idx}_MISSING_FIELDS:' + ','.join(sorted(missing)))
        mid=u.get('migration_unit_id')
        if not isinstance(mid,str) or not mid.strip():
            errors.append(f'UNIT_{idx}_IDENTITY_INVALID')
        elif mid in seen:errors.append(f'DUPLICATE_MIGRATION_UNIT_ID:{mid}')
        else:seen.add(mid)
        for field in REQUIRED_UNIT_FIELDS-{'consumer_refs'}:
            if not isinstance(u.get(field),str) or not u[field].strip():errors.append(f'UNIT_{idx}_INVALID_FIELD:{field}')
        if not isinstance(u.get('secret_class'),str) or u.get('secret_class') not in ALLOWED_CLASSES:
            errors.append(f'UNIT_{idx}_SECRET_CLASS_INVALID')
        if not isinstance(u.get('consumer_refs'),list) or not u.get('consumer_refs') or not all(isinstance(c,str) and c.strip() for c in u['consumer_refs']) or len(set(c for c in u['consumer_refs'] if isinstance(c,str)))!=len(u['consumer_refs']):
            errors.append(f'UNIT_{idx}_CONSUMER_REFS_INVALID')
        if not u.get('secret_ref'):
            errors.append(f'UNIT_{idx}_SECRET_REF_MISSING')
        if u.get('target_provider')!='AZURE_KEY_VAULT':
            errors.append(f'UNIT_{idx}_TARGET_PROVIDER_INVALID')
    return errors

def evaluate(data):
    errors=validate(data)
    if errors:
        return {'result':'INVALID','ready':False,'errors':errors}
    missing=[k for k,v in data['gates'].items() if v is not True]
    if not data['migration_units']:
        missing.append('migration_units')
    if missing:
        return {'result':'BLOCKED_G8_SECRET_MIGRATION_ACTIVATION','ready':False,'missing_gates':missing}
    return {'result':'READY_FOR_POSTDEPLOY_OWNER_GATED_MIGRATION','ready':True,'migration_unit_count':len(data['migration_units'])}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('manifest')
    args=ap.parse_args()
    data=yaml.safe_load(Path(args.manifest).read_text(encoding='utf-8'))
    result=evaluate(data)
    print(json.dumps(result,sort_keys=True))
    return 0 if result.get('ready') is True else 2

if __name__=='__main__':
    raise SystemExit(main())
