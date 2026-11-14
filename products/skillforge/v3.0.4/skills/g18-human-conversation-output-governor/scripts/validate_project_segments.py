#!/usr/bin/env python3
import argparse
from pathlib import Path
from project_response_grammar import validate_body, ValidationError

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('file')
    ap.add_argument('--language',default='fa')
    a=ap.parse_args()
    try:
        r=validate_body(Path(a.file).read_text(encoding='utf-8'),a.language)
    except ValidationError as e:
        print(str(e)); return 1
    print(f'PROJECT_SEGMENT_PRESENTATION_PASS tables={r["table_count"]} serials={r["serials"]}')
    return 0
if __name__=='__main__': raise SystemExit(main())
