#!/usr/bin/env python3
import argparse, json, re, sys
from pathlib import Path

FAIL=[]
def fail(code,msg): FAIL.append((code,msg))

def validate_visible(text):
    low=text.lower()
    forbidden=[('sandbox:/','ARTIFACT_SANDBOX_OR_LOCAL_PATH_VISIBLE'),('/mnt/data/','ARTIFACT_SANDBOX_OR_LOCAL_PATH_VISIBLE'),('file://','ARTIFACT_DIRECT_LOCAL_DELIVERY_PROHIBITED'),('data:image/','ARTIFACT_INLINE_GENERATED_MEDIA_PROHIBITED')]
    for token,code in forbidden:
        if token in low: fail(code,f'visible forbidden token: {token}')
    # Inline image markdown is prohibited in governed final delivery; use a verified remote link instead.
    if re.search(r'!\[[^\]]*\]\([^\)]+\)', text):
        fail('ARTIFACT_INLINE_GENERATED_MEDIA_PROHIBITED','inline image markdown found in final response')

def validate_events(data):
    if not isinstance(data,dict) or not isinstance(data.get('generated_artifacts'),list):
        fail('ARTIFACT_EVENT_LEDGER_INVALID','generated_artifacts list required');return
    arts=data['generated_artifacts']
    for i,a in enumerate(arts,1):
        if not isinstance(a,dict) or type(a.get('generated_or_modified_by_system')) is not bool:
            fail('ARTIFACT_EVENT_INVALID',f'artifact {i} identity flag invalid');continue
        if not a['generated_or_modified_by_system']:
            continue
        cls=str(a.get('artifact_class','')).upper()
        if a.get('direct_user_surface_emitted'):
            fail('ARTIFACT_DIRECT_CHAT_OR_WORK_ATTACHMENT_PROHIBITED',f'artifact {i} directly emitted to user surface')
        if a.get('staging_visibility')!='NON_USER_VISIBLE_TRANSIENT':
            fail('GENERATED_MEDIA_NONVISIBLE_STAGING_REQUIRED',f'artifact {i} staging is not non-user-visible transient')
        if a.get('remote_write_verified') is not True or a.get('remote_readback_verified') is not True:
            fail('ARTIFACT_REMOTE_WRITE_READBACK_REQUIRED',f'artifact {i} lacks verified remote write/readback')
        if a.get('final_delivery_kind')!='VERIFIED_REMOTE_LINK_ONLY' or not a.get('remote_url'):
            fail('ARTIFACT_REMOTE_LINK_REQUIRED',f'artifact {i} terminal delivery is not a verified remote link')
        provider=str(a.get('remote_provider','')).upper()
        media={'IMAGE','INFOGRAPHIC','CHART','DIAGRAM','SCREENSHOT'}
        if cls in media and provider!='SHAREPOINT':
            fail('GENERATED_MEDIA_SHAREPOINT_ONLY',f'artifact {i} media provider is {provider or "missing"}')
        if provider=='GITHUB' and cls not in {'SOURCE_CODE','REPOSITORY_TEXT','REPOSITORY_CONFIG'}:
            fail('ARTIFACT_REMOTE_LINK_REQUIRED',f'artifact {i} class {cls} is not eligible for GitHub final delivery')
        if a.get('generation_route_auto_surfaces_to_user'):
            fail('ARTIFACT_INLINE_GENERATED_MEDIA_PROHIBITED',f'artifact {i} generation route auto-surfaces to user')

def main():
    FAIL.clear()
    ap=argparse.ArgumentParser()
    ap.add_argument('response_file')
    ap.add_argument('--events-json')
    ap.add_argument('--tool-events-json')
    a=ap.parse_args()
    text=Path(a.response_file).read_text(encoding='utf-8')
    validate_visible(text)
    if a.events_json:
        validate_events(json.loads(Path(a.events_json).read_text(encoding='utf-8')))
    if a.tool_events_json:
        data=json.loads(Path(a.tool_events_json).read_text(encoding='utf-8'))
        for i,e in enumerate(data.get('tool_events',[]),1):
            bg=e.get('purpose') in {'BACKGROUND_GOVERNANCE_READ','BACKGROUND_SOURCE_READ','HANDOFF_STATE_READ'}
            if bg and e.get('route_preflight_status')!='PASS':
                fail('ARTIFACT_TOOL_ROUTE_PREFLIGHT_REQUIRED',f'tool event {i} lacks PASS preflight')
            if bg and e.get('execution_visibility')!='INTERNAL_ANALYSIS_NON_SURFACING':
                fail('ARTIFACT_BACKGROUND_READ_USER_VISIBLE_CHANNEL_PROHIBITED',f'tool event {i} is not on an internal non-surfacing route')
            if bg and e.get('user_visible_side_effect_possible'):
                fail('ARTIFACT_TOOL_ROUTE_USER_VISIBLE_SIDE_EFFECT_PROHIBITED',f'tool event {i} background read may surface file/media')
            if bg and (e.get('raw_download') or e.get('materialize') or e.get('direct_file_return')):
                fail('ARTIFACT_BACKGROUND_READ_RAW_ROUTE_PROHIBITED',f'tool event {i} uses raw/materialize/direct-return route')
            if e.get('observed_user_visible_file_card'):
                fail('ARTIFACT_TOOL_SIDE_FILE_CARD_LEAK',f'tool event {i} surfaced file card; there is no direct-card exception')
    if FAIL:
        for c,m in FAIL: print(f'{c}: {m}')
        return 1
    print('ARTIFACT_DELIVERY_PASS')
    return 0
if __name__=='__main__': sys.exit(main())
