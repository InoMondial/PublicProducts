#!/usr/bin/env python3
from __future__ import annotations
import re

RLM='\u200f'; LRI='\u2066'; PDI='\u2069'
ICON_CLASS='\U0001F300-\U0001FAFF\u2600-\u27BF'
RTL_SCRIPT=re.compile(r'[\u0590-\u05ff\u0600-\u06ff\u0700-\u074f\u0750-\u077f\u0780-\u07bf\u08a0-\u08ff]')
SEP_RE=re.compile(r'^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$')
RTL_SEGMENT_RE=re.compile(r'^'+RLM+r'(['+ICON_CLASS+r']) \*\*([^*]+)\*\*$')
LTR_SEGMENT_RE=re.compile(r'^(['+ICON_CLASS+r']) \*\*([^*]+)\*\*$')
RTL_TABLE_TITLE_RE=re.compile(r'^'+RLM+r'(['+ICON_CLASS+r']) \*\*جدول ([0-9]+) — ([^*]+)\*\*$')
LTR_TABLE_TITLE_RE=re.compile(r'^(['+ICON_CLASS+r']) \*\*Table ([0-9]+) — ([^*]+)\*\*$')
DUAL_HANDOFF_RE=re.compile(r'^'+RLM+r'\['+LRI+r'(HOF-[A-Z0-9]+) \| S:([0-9]+) \| M:([0-9]+)'+PDI+r'\]\((https://[^)\s]+)\)$')
LEGACY_HANDOFF_RE=re.compile(r'^'+RLM+r'\['+LRI+r'(HOF-[A-Z0-9]+) \| S:([0-9]+)'+PDI+r'\]\((https://[^)\s]+)\)$')

class ValidationError(ValueError):
    def __init__(self, code, detail=''):
        self.code=code; self.detail=detail
        super().__init__(f'{code}: {detail}')

def fail(code, detail=''): raise ValidationError(code, detail)
def clean(s): return s.replace(RLM,'').replace(LRI,'').replace(PDI,'').strip().strip('`').strip()

def split_row(line):
    s=line.strip()
    if s.startswith('|'): s=s[1:]
    if s.endswith('|'): s=s[:-1]
    sentinel='\ue000'; s=s.replace('\\|',sentinel)
    return [x.strip().replace(sentinel,'|') for x in s.split('|')]

def parse_tables(lines):
    out=[]; covered=set(); i=0
    while i+1<len(lines):
        if '|' in lines[i] and SEP_RE.match(lines[i+1] or ''):
            header=split_row(lines[i]); align=split_row(lines[i+1]); rows=[]; j=i+2
            covered.update((i,i+1))
            while j<len(lines) and lines[j].strip() and '|' in lines[j]:
                rows.append(split_row(lines[j])); covered.add(j); j+=1
            out.append({'start':i,'end':j-1,'header':header,'align':align,'rows':rows}); i=j
        else: i+=1
    return out,covered

def _title_match(line, rtl, table=False):
    rx=(RTL_TABLE_TITLE_RE if rtl else LTR_TABLE_TITLE_RE) if table else (RTL_SEGMENT_RE if rtl else LTR_SEGMENT_RE)
    return rx.fullmatch(line.strip(' \t'))

def _title_text_ok(text, rtl):
    first=next((ch for ch in text.strip() if not ch.isspace()),'')
    return bool(first and ((RTL_SCRIPT.match(first) is not None) if rtl else (RTL_SCRIPT.match(first) is None)))

def validate_body(text, language='fa'):
    lines=text.splitlines(); rtl=language.lower() in {'fa','ar','he','ur','ps','dv','ku-arab'}
    nonempty=[i for i,l in enumerate(lines) if l.strip()]
    if nonempty:
        last=lines[nonempty[-1]].strip(' \t')
        if DUAL_HANDOFF_RE.fullmatch(last) or LEGACY_HANDOFF_RE.fullmatch(last): lines=lines[:nonempty[-1]]
    if any(l.lstrip().startswith(('# ','## ','### ','#### ','##### ','###### ')) for l in lines if l.strip()):
        fail('PROJECT_SEGMENT_MARKDOWN_HEADING_PROHIBITED','use directional bold title lines')

    tables,covered=parse_tables(lines)
    if not tables: fail('PROJECT_TABLE_REQUIRED','governed project body requires at least one table')

    serials=[]; title_lines=set(); segment_lines=set()
    for t in tables:
        ti=t['start']-1
        if ti<0 or not lines[ti].strip(): fail('PROJECT_TABLE_TITLE_NOT_ADJACENT',f'table at line {t["start"]+1}')
        m=_title_match(lines[ti],rtl,table=True)
        if not m:
            if _title_match(lines[ti],not rtl,table=True): fail('PROJECT_TABLE_SERIAL_LANGUAGE_PREFIX_INVALID',f'line {ti+1}')
            if _title_match(lines[ti],rtl,table=False): fail('PROJECT_TABLE_SERIAL_MISSING',f'line {ti+1}')
            fail('PROJECT_TABLE_TITLE_MISSING',f'line {ti+1}')
        n=int(m.group(2)); title=m.group(3).strip()
        if n<1: fail('PROJECT_TABLE_SERIAL_MISSING',f'line {ti+1}')
        if not _title_text_ok(title,rtl): fail('PROJECT_TABLE_TITLE_LEXICAL_SERIAL_PREFIX_INVALID',f'line {ti+1}')
        serials.append(n); title_lines.add(ti)

    expected=list(range(1,len(serials)+1))
    if len(set(serials))!=len(serials): fail('PROJECT_TABLE_SERIAL_DUPLICATE','duplicate table serial')
    if serials!=expected: fail('PROJECT_TABLE_SERIAL_GAP',f'expected {expected}, got {serials}')

    for i,l in enumerate(lines):
        if not l.strip() or i in covered or i in title_lines: continue
        m=_title_match(l,rtl,table=False)
        if m:
            title=m.group(2).strip()
            if (rtl and title.startswith('جدول')) or ((not rtl) and title.startswith('Table')):
                fail('PROJECT_TABLE_TITLE_GRAMMAR_CONFLICT',f'line {i+1}')
            if not _title_text_ok(title,rtl):
                fail('PROJECT_SEGMENT_TITLE_NOT_RTL_WORD_FIRST' if rtl else 'PROJECT_SEGMENT_TITLE_LANGUAGE_INVALID',f'line {i+1}')
            segment_lines.add(i); continue
        fail('PROJECT_RESPONSE_NON_TABLE_CONTENT',f'line {i+1}')

    body_nonempty=[i for i,l in enumerate(lines) if l.strip()]
    if len(tables)>1 and (not body_nonempty or body_nonempty[0] not in segment_lines):
        fail('PROJECT_SEGMENT_TITLE_MISSING','multi-table response must begin with a directional segment title')
    if len(tables)==1 and body_nonempty and body_nonempty[0] not in segment_lines and body_nonempty[0] not in title_lines:
        fail('PROJECT_SEGMENT_TITLE_MISSING','single-table response must begin with a segment or numbered table title')

    for si in sorted(segment_lines):
        j=si+1
        while j<len(lines) and not lines[j].strip(): j+=1
        if j>=len(lines) or j not in title_lines:
            fail('PROJECT_SEGMENT_TITLE_NOT_ADJACENT_TO_TABLE',f'line {si+1}')

    return {'table_count':len(tables),'serials':serials,'tables':tables,'segment_count':len(segment_lines)}

def _field_map(table):
    h=[clean(x) for x in table['header']]
    for fk,vk in [('فیلد','مقدار'),('Field','Value')]:
        if fk in h and vk in h:
            fi=h.index(fk); vi=h.index(vk)
            return {clean(r[fi]):clean(r[vi]) for r in table['rows'] if len(r)==len(h)}
    return None

def validate_footer(text, state):
    lines=text.splitlines(); nonempty=[(i,l) for i,l in enumerate(lines) if l.strip()]
    if not nonempty: fail('PROJECT_TERMINAL_HANDOFF_FOOTER_MISSING','empty response')
    raw=nonempty[-1][1].strip(' \t'); dual=DUAL_HANDOFF_RE.fullmatch(raw); legacy=LEGACY_HANDOFF_RE.fullmatch(raw)
    if not dual and not legacy:
        fail('PROJECT_TERMINAL_HANDOFF_FOOTER_MISSING','absolute-final line must be exactly one clickable canonical Handoff alias')
    count=sum(1 for _,l in nonempty if 'HOF-' in l and '](' in l)
    if count!=1: fail('PROJECT_HANDOFF_FOOTER_SINGLE_ANCHOR_REQUIRED',f'found {count}')

    req=['handoff_id','interaction_seq','visible_ref','handoff_url','post_write_readback_verified']
    miss=[k for k in req if k not in state]
    if miss or state.get('post_write_readback_verified') is not True:
        fail('PROJECT_HANDOFF_STATE_UNAVAILABLE',','.join(miss) or 'canonical Handoff readback not verified')

    hid=state['handoff_id']; S=state['interaction_seq']; url=state['handoff_url']
    dual_active=('material_seq' in state and state.get('material_seq') is not None) or ('| M:' in str(state.get('visible_ref','')))
    if dual_active:
        if not dual: fail('PROJECT_HANDOFF_DUAL_SEQUENCE_STALE','S/M alias required after dual-sequence cutover')
        rhid,rS,rM,rurl=dual.group(1),int(dual.group(2)),int(dual.group(3)),dual.group(4); M=state.get('material_seq')
        if (rhid,rS,rM,rurl)!=(hid,S,M,url): fail('PROJECT_HANDOFF_VISIBLE_REF_MISMATCH','rendered alias differs from verified current state')
        expected=f'{hid} | S:{S} | M:{M}'
    else:
        if not legacy: fail('PROJECT_HANDOFF_VISIBLE_REF_MISMATCH','legacy S-only alias required before dual-sequence cutover')
        rhid,rS,rurl=legacy.group(1),int(legacy.group(2)),legacy.group(3)
        if (rhid,rS,rurl)!=(hid,S,url): fail('PROJECT_HANDOFF_VISIBLE_REF_MISMATCH','legacy alias differs from verified current state')
        expected=f'{hid} | S:{S}'
    if state.get('visible_ref')!=expected: fail('PROJECT_HANDOFF_VISIBLE_REF_MISMATCH',f'expected {expected}')

    sr=state.get('current_turn_S_receipt')
    if dual_active and not isinstance(sr,dict): fail('PROJECT_HANDOFF_CURRENT_TURN_S_RECEIPT_MISSING','current-turn S receipt required')
    if isinstance(sr,dict) and sr.get('S')!=S: fail('PROJECT_HANDOFF_CURRENT_TURN_S_RECEIPT_MISSING','S receipt mismatch')
    if state.get('material_project_change_detected'):
        receipts=state.get('material_M_receipts') or []
        if dual_active and not any(isinstance(x,dict) and x.get('S')==S and x.get('M')==state.get('material_seq') for x in receipts):
            fail('PROJECT_HANDOFF_MATERIAL_M_RECEIPT_MISSING','material M receipt for displayed S/M required')
    return {'dual_sequence':dual_active,'handoff_id':hid,'S':S,'M':state.get('material_seq')}

def validate_terminal_tables(text, language='fa'):
    body=validate_body(text,language); tables=body['tables']
    if len(tables)<2: fail('PROJECT_G16_HANDOFF_CONTROL_TABLE_MISSING','control and summary tables are required')
    cfm=_field_map(tables[-2]); sfm=_field_map(tables[-1])
    if cfm is None: fail('PROJECT_G16_HANDOFF_CONTROL_TABLE_MISSING','penultimate table must use Field/Value semantics')
    if sfm is None: fail('PROJECT_SUMMARY_FOOTER_MISSING','final table must use Field/Value semantics')
    rtl=language.lower() in {'fa','ar','he','ur','ps','dv','ku-arab'}
    if rtl:
        creq={'شناسه هندزآف','شماره تعامل S','شماره ماده M','مرجع قابل مشاهده','آخرین به‌روزرسانی','وضعیت اجرا','واحد کار جاری','آخرین واحد تکمیل‌شده','نقطه ازسرگیری','بازبینی شواهد'}
        sreq={'مرحله جاری','درصد مرحله جاری','درصد وزنی کل','مرحله بعدی'}
    else:
        creq={'Handoff ID','Interaction S','Material M','Visible reference','Updated at','Run status','Current work unit','Last completed work unit','Resume point','Evidence revision'}
        sreq={'Current stage','Current-stage percent','Weighted overall percent','Next stage'}
    miss=creq-set(cfm)
    if miss: fail('PROJECT_G16_HANDOFF_FIELD_MISSING',','.join(sorted(miss)))
    if len(tables[-1]['rows'])!=4 or set(sfm)!=sreq:
        fail('PROJECT_SUMMARY_FOOTER_ROW_COUNT_INVALID','final summary table must contain exactly four required semantic rows')
    return body

def validate_response(text, state, language='fa'):
    foot=validate_footer(text,state)
    body=validate_terminal_tables(text,language)
    return {'result':'PASS',**body,**foot}
