#!/usr/bin/env python3
from __future__ import annotations
import sys, yaml
REQ={'CORPORATE_PROPRIETARY','COMMUNITY_PERSONAL_SOURCE_AVAILABLE','OSI_OPEN_SOURCE'}

def validate(path):
    with open(path,encoding='utf-8') as f:
        d=yaml.safe_load(f)
    errs=[]
    if d.get('contract_id')!='INC_SKILLFORGE_PUBLIC_LICENSE_PROVENANCE_V1': errs.append('CONTRACT_ID')
    rp=d.get('rights_profiles') or {}
    if not REQ.issubset(rp): errs.append('RIGHTS_PROFILES')
    if rp.get('COMMUNITY_PERSONAL_SOURCE_AVAILABLE',{}).get('osi_open_source') is not False: errs.append('COMMUNITY_NOT_OSI')
    if d.get('ownership',{}).get('blanket_company_ownership')!='prohibited': errs.append('BLANKET_OWNERSHIP')
    mr=d.get('moral_rights',{})
    if mr.get('canada_rule')!='NOT_ASSIGNABLE_MAY_BE_WAIVED_IN_WHOLE_OR_PART' or mr.get('assignment_alone_is_waiver') is not False: errs.append('MORAL_RIGHTS')
    if d.get('trademark',{}).get('claim_registration_without_verified_approval')!='prohibited': errs.append('TRADEMARK')
    required={'LICENSE','NOTICE','THIRD_PARTY_NOTICES','TRADEMARKS','CONTRIBUTING.md','SECURITY.md','RIGHTS_PROFILE.yaml'}
    if not required.issubset(set(d.get('required_distribution_surfaces') or [])): errs.append('SURFACES')
    return errs
if __name__=='__main__':
    e=validate(sys.argv[1]); print('PASS' if not e else 'FAIL:'+','.join(e)); raise SystemExit(bool(e))
