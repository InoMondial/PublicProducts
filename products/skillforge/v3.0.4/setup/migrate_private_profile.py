#!/usr/bin/env python3
"""Non-activating, lossless owner-profile schema migration planner.

Input must be a private file outside the installable. This tool does not access
service APIs, migrate secrets or grant permissions. Unknown inputs are rejected.
The result remains REVALIDATION_REQUIRED until a trusted host verifies it.
"""
from __future__ import annotations
import argparse,hashlib,json,os,stat
from pathlib import Path
from onboarding import catalog,load_json,no_raw_secrets,ROOT

def migrate(source:dict)->dict:
    if not isinstance(source,dict) or source.get('schema_version')!='1.0':
        raise ValueError('INVALID_SOURCE_PROFILE')
    parameters=source.get('parameters')
    if not isinstance(parameters,dict) or not no_raw_secrets(parameters):
        raise ValueError('RAW_SECRET_OR_INVALID_PARAMETERS')
    schema=load_json(ROOT/'config/private-parameters.schema.json')
    allnames=set(schema['parameters'])
    if any(not isinstance(key,str) or not key or key not in allnames for key in parameters):
        raise ValueError('UNKNOWN_PARAMETER_FAIL_CLOSED')
    old=source.get('environment_profile')
    if not isinstance(old,dict):
        raise ValueError('OLD_ENVIRONMENT_PROFILE_REQUIRED')
    updated=dict(old)
    updated.update({'profile_version':'3.0.4','state':'DRAFT','acceptance_mode':'SIMULATION_ONLY',
      'setup_status':'REVALIDATION_REQUIRED','authorization_source':'HOST_CONNECTOR_CURRENT_READBACK_REQUIRED'})
    # Retain references for review but never claim BOUND authorization from an old version.
    refs=updated.get('references')
    if isinstance(refs,dict):
        updated['references']={k:{**v,'state':'REVALIDATION_REQUIRED'} if isinstance(v,dict)
                               else v for k,v in refs.items()}
    updated['selected_services']=[]
    merged={key:parameters.get(key) for key in sorted(allnames)}
    out={'schema_version':'1.0','version':'3.0.4','state':'REVALIDATION_REQUIRED',
         'classification':'PRIVATE_OWNER_ENVIRONMENT_CONFIGURATION',
         'source_version':str(source.get('version','3.0.3')),
         'public_export_allowed':False,'runtime_permissions_granted':False,
         'parameters':merged,'environment_profile':updated,
         'added_unresolved_parameters':sorted(allnames-set(parameters)),
         'preserved_existing_parameter_count':sum(key in parameters for key in allnames),
         'migration_activation_state':'NOT_AUTHORIZED'}
    if not no_raw_secrets(out):raise ValueError('RAW_SECRET_IN_MIGRATED_PROFILE')
    return out

def migrate_files(source:Path,sha256:str,destination:Path)->dict:
    if source.resolve().is_relative_to(ROOT) or destination.absolute().is_relative_to(ROOT):
        raise ValueError('OWNER_PROFILE_MUST_BE_OUTSIDE_DISTRIBUTABLE')
    data=source.read_bytes()
    if len(data)>1000000 or hashlib.sha256(data).hexdigest()!=sha256:
        raise ValueError('SOURCE_SHA256_MISMATCH')
    model=migrate(load_json(source))
    if destination.exists() or destination.is_symlink():raise ValueError('DESTINATION_ALREADY_EXISTS')
    if not destination.parent.is_dir():raise ValueError('DESTINATION_PARENT_MISSING')
    if os.name!='nt' and stat.S_IMODE(destination.parent.stat().st_mode)&0o002:
        raise ValueError('DESTINATION_PARENT_WORLD_WRITABLE')
    blob=(json.dumps(model,indent=2,sort_keys=True,ensure_ascii=False)+'\n').encode('utf-8')
    fd=os.open(str(destination),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    try:
        with os.fdopen(fd,'wb') as fp:fp.write(blob);fp.flush();os.fsync(fp.fileno())
    except BaseException:
        destination.unlink(missing_ok=True);raise
    return {'status':'REVALIDATION_REQUIRED','new_schema_version':'3.0.4',
            'output_sha256':hashlib.sha256(blob).hexdigest(),
            'preserved_existing_parameter_count':model['preserved_existing_parameter_count'],
            'added_unresolved_count':len(model['added_unresolved_parameters']),
            'secrets_transferred':False,'external_connectors_authorized':False,
            'public_export_allowed':False}

def main()->int:
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',required=True)
    p.add_argument('--source-sha256',required=True);p.add_argument('--destination',required=True)
    a=p.parse_args()
    try:print(json.dumps(migrate_files(Path(a.source),a.source_sha256,Path(a.destination)),sort_keys=True));return 0
    except (OSError,ValueError,TypeError) as e:
        print(json.dumps({'status':'FAIL_CLOSED','reason_code':str(e)[:120]}));return 2
if __name__=='__main__':raise SystemExit(main())
