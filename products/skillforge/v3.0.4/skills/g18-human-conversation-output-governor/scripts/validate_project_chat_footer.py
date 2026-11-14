#!/usr/bin/env python3
import argparse,json
from pathlib import Path
from project_response_grammar import validate_response, ValidationError

def extract_state(obj):
    if isinstance(obj,dict) and 'state' in obj and isinstance(obj['state'],dict):
        c=obj['state'].get('continuity',{})
        p=c.get('current_project_return_payload') if isinstance(c,dict) else None
        if isinstance(p,dict):
            out=dict(p)
            out.setdefault('handoff_id',obj.get('handoff_id'))
            return out
    if isinstance(obj,dict) and isinstance(obj.get('current_project_return_payload'),dict):
        return dict(obj['current_project_return_payload'])
    return obj

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('file')
    ap.add_argument('--g16-state',required=True)
    ap.add_argument('--language',default='fa')
    a=ap.parse_args()
    state=extract_state(json.loads(Path(a.g16_state).read_text(encoding='utf-8')))
    try:
        r=validate_response(Path(a.file).read_text(encoding='utf-8'),state,a.language)
    except ValidationError as e:
        print(str(e)); return 1
    print(f'PROJECT_CHAT_FOOTER_PASS S={r["S"]} M={r.get("M")} tables={r["table_count"]}')
    return 0
if __name__=='__main__': raise SystemExit(main())
