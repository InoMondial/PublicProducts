#!/usr/bin/env python3
"""Capability requirements follow the selected destination, not repository presence."""
COMMON={'remote_readback','binary_safe_transport','secret_scan','atomic_lock'}
BASE=COMMON|{'github_read','github_write','git_push','pr_merge'}
def required(release=False,p0_p1=False,notification=False,*,target_provider='GITHUB',github_release_channel=False):
    if target_provider not in {'GITHUB','SHAREPOINT'}:
        raise ValueError('TARGET_PROVIDER_REQUIRED')
    r=set(BASE if target_provider=='GITHUB' else COMMON|{'sharepoint_read','sharepoint_write','sharepoint_readback'})
    if github_release_channel:
        if target_provider!='GITHUB' or release is not True: raise ValueError('RELEASE_CHANNEL_SCOPE_INVALID')
        r|={'release_write','release_asset_write','release_asset_readback'}
    if p0_p1: r|={'sharepoint_read','sharepoint_write','sharepoint_readback'}
    if notification: r|={'teams_post','teams_readback','teams_deeplink'}
    return r
def evaluate(capabilities,**kwargs):
    req=required(**kwargs)
    if not isinstance(capabilities,dict):capabilities={}
    missing=sorted(req-{k for k,v in capabilities.items() if v is True})
    return {'ok':not missing,'required':sorted(req),'missing':missing,'status':'PASS' if not missing else 'CAPABILITY_PREFLIGHT_FAILED'}
