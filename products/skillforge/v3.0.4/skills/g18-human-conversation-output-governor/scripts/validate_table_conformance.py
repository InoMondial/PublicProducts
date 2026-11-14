#!/usr/bin/env python3
import argparse, re
from pathlib import Path

RTL_LANGS = {"fa", "ar", "he", "ur", "ps", "dv", "ku-arab"}
RLM = "\u200f"; LRI = "\u2066"; PDI = "\u2069"
NBSP="\u00a0"; LRM="\u200e"; RLI="\u2067"; FSI="\u2068"
RTL_SCRIPT_RE = re.compile(r"[\u0590-\u05ff\u0600-\u06ff\u0700-\u074f\u0750-\u077f\u0780-\u07bf\u07c0-\u07ff\u08a0-\u08ff\ufb1d-\ufdff\ufe70-\ufeff]")
ASCII_ALNUM_RE=re.compile(r"[A-Za-z0-9]")
VISIBLE_RAW_URL_RE=re.compile(r"https?://",re.I)
LEADING_MARKUP_RE = re.compile(r"^[\s*_~>\[\](){}]+")
SEP_RE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$")
MD_LINK_DEST_RE = re.compile(r"\]\((https?://[^)\s]+)\)",re.I)
NEUTRAL_OPEN=set('«\"\'([{')
NEUTRAL_CLOSE=set('»\"\')]}')


def split_row(line):
    s=line.strip()
    if s.startswith('|'): s=s[1:]
    if s.endswith('|'): s=s[:-1]
    sentinel='\ue000'
    s=s.replace('\\|',sentinel)
    cells=[c.strip(' \t') for c in s.split('|')]
    return [c.replace(sentinel,'|') for c in cells]

def tables(text):
    lines=text.splitlines(); out=[]; i=0
    while i+1 < len(lines):
        if '|' in lines[i] and SEP_RE.match(lines[i+1] or ''):
            header=split_row(lines[i]); align=split_row(lines[i+1]); rows=[]; j=i+2
            while j < len(lines) and '|' in lines[j] and lines[j].strip():
                rows.append(split_row(lines[j])); j+=1
            out.append((header,align,rows,i+1)); i=j
        else: i+=1
    return out

def strip_controls(s):
    return s.replace(RLM,'').replace(LRI,'').replace(PDI,'').replace(LRM,'').replace(RLI,'').replace(FSI,'').replace(NBSP,'')

def is_row_header(cell,lang):
    c=strip_controls(cell).strip()
    if c=='NUM#': return True
    if lang in RTL_LANGS and c in {'ردیف','الصف','שורה','قطار'}: return True
    return False

def has_persian_row_header_like_text(cell): return 'ردیف' in strip_controls(cell).strip()

def parse_int(cell):
    trans=str.maketrans('۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩','01234567890123456789')
    m=re.search(r"\d+",cell.translate(trans)); return int(m.group()) if m else None

def semantic_ascii_int(cell,allow_single_leading_rlm=False):
    c=cell.strip(' \t')
    if allow_single_leading_rlm and c.startswith(RLM): c=c[1:]
    return int(c) if re.fullmatch(r"[0-9]+",c) else None

def exact_rtl_chat_row_cell(cell): return re.fullmatch(RLM+r"[0-9]+",cell.strip(' \t')) is not None

def prohibited_rtl_chat_row_wrapper(cell):
    c=cell.strip(' \t')
    if '`' in c or any(x in c for x in (NBSP,LRM,LRI,RLI,FSI,PDI)): return True
    return c.count(RLM)!=1

def right_aligned(marker):
    c=marker.strip().replace(' ',''); return c.endswith(':') and not c.startswith(':') and '-' in c
def left_aligned(marker):
    c=marker.strip().replace(' ',''); return c.startswith(':') and not c.endswith(':') and '-' in c

def strip_one_rlm(cell):
    c=cell.strip(' \t'); return c[1:] if c.startswith(RLM) else c

def rtl_word_first(cell):
    c=strip_one_rlm(cell); c=LEADING_MARKUP_RE.sub('',c)
    return bool(c and RTL_SCRIPT_RE.match(c))

def exact_chat_text_lead(cell):
    c=cell.strip(' \t')
    return c.startswith(RLM) and not c.startswith(RLM+RLM) and c.count(RLM)==1 and rtl_word_first(c)

def visible_projection_for_url_scan(body):
    # Markdown destinations are source-only; keep visible label text and erase only destination URLs.
    return MD_LINK_DEST_RE.sub('](__HIDDEN_LINK_DEST__)',body)

def embedded_ltr_isolation_error(cell):
    c=cell.strip(' \t')
    if not exact_chat_text_lead(c): return ('RTL_CHAT_TEXT_CELL_RLM_ENVELOPE_INVALID','RTL Chat text cell must start with exactly one RLM then an RTL-script word')
    body=c[1:]
    if '`' in body: return ('RTL_TABLE_INLINE_CODE_TOKEN_PROHIBITED','Inline-code/backtick styling is prohibited in human-facing RTL Chat table cells; isolate technical runs with LRI/PDI instead')
    if any(x in body for x in (NBSP,LRM,RLI,FSI,RLM)):
        return ('RTL_CHAT_TEXT_CELL_WRAPPER_PROHIBITED','NBSP/LRM/RLI/FSI or extra RLM is prohibited in RTL Chat table text cells')
    projected=visible_projection_for_url_scan(body)
    if VISIBLE_RAW_URL_RE.search(projected):
        return ('RTL_TABLE_VISIBLE_RAW_URL_FORBIDDEN','Raw visible URL is prohibited; use a Persian/RTL link label with the URL only as the Markdown destination')
    in_iso=False; start=None; iso_segments=[]
    for i,ch in enumerate(body):
        if ch==LRI:
            if in_iso: return ('RTL_TABLE_LTR_ISOLATE_NESTED','Nested LRI is prohibited')
            if i>0 and body[i-1] in NEUTRAL_OPEN:
                return ('RTL_TABLE_LTR_NEUTRAL_WRAPPER_PROHIBITED','Do not wrap an isolated LTR technical run in quotes/guillemets/parentheses')
            in_iso=True; start=i+1; continue
        if ch==PDI:
            if not in_iso: return ('RTL_TABLE_LTR_ISOLATE_UNBALANCED','PDI without matching LRI')
            seg=body[start:i]
            if not ASCII_ALNUM_RE.search(seg): return ('RTL_TABLE_LTR_ISOLATE_EMPTY','LRI/PDI technical run must contain ASCII letters or digits')
            if RTL_SCRIPT_RE.search(seg): return ('RTL_TABLE_LTR_ISOLATE_CONTAINS_RTL','RTL-script text must not be placed inside an LTR technical isolate')
            if i+1<len(body) and body[i+1] in NEUTRAL_CLOSE:
                return ('RTL_TABLE_LTR_NEUTRAL_WRAPPER_PROHIBITED','Do not wrap an isolated LTR technical run in quotes/guillemets/parentheses')
            iso_segments.append(seg); in_iso=False; start=None; continue
        if ASCII_ALNUM_RE.match(ch) and not in_iso:
            # Ignore ASCII characters that exist only inside a Markdown destination URL.
            prefix=body[:i+1]
            # crude but deterministic: if this position is between '](' and the next ')' and destination starts http, skip.
            op=body.rfind('](',0,i+1); cl=body.find(')',i)
            if op!=-1 and cl!=-1 and body[op+2:].startswith(('http://','https://')):
                continue
            return ('RTL_TABLE_BARE_LTR_RUN_NOT_ISOLATED','Every visible ASCII letter/digit inside an RTL Chat text cell must be inside one balanced LRI/PDI technical run')
    if in_iso: return ('RTL_TABLE_LTR_ISOLATE_UNBALANCED','LRI without matching PDI')
    return None


def unescaped_pipe_inside_lri_segment(line):
    in_iso=False; esc=False; saw_unescaped_pipe=False
    for ch in line:
        if esc:
            esc=False; continue
        if ch=='\\':
            esc=True; continue
        if ch==LRI:
            if not in_iso:
                in_iso=True; saw_unescaped_pipe=False
            continue
        if ch==PDI:
            if in_iso and saw_unescaped_pipe:
                return True
            in_iso=False; saw_unescaped_pipe=False; continue
        if ch=='|' and in_iso:
            saw_unescaped_pipe=True
    return False

def fail(code,line,detail): print(f"{code}: line {line}: {detail}"); return 1

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('file'); ap.add_argument('--surface',default='chat',choices=['chat','work','codex','document','other']); ap.add_argument('--language',default='fa')
    args=ap.parse_args(); text=Path(args.file).read_text(encoding='utf-8')
    for n,raw in enumerate(text.splitlines(),1):
        if raw.lstrip().startswith('|') and unescaped_pipe_inside_lri_segment(raw):
            return fail('RTL_TABLE_LITERAL_PIPE_NOT_ESCAPED',n,r'A visible literal | inside an LRI/PDI technical run must be escaped as \\| in Markdown table source')
    found=tables(text)
    if not found: print('TABLE_CONFORMANCE_PASS: no actual Markdown table detected'); return 0
    lang=args.language.lower(); rtl=lang in RTL_LANGS
    for header,align,rows,line in found:
        refs=[i for i,c in enumerate(header) if is_row_header(c,lang)]
        if lang=='fa' and not refs and any(has_persian_row_header_like_text(c) for c in header): return fail('PERSIAN_TABLE_ROW_HEADER_NOT_EXACT',line,'Persian row-reference header must be exactly ردیف')
        if not refs: return fail('TABLE_ROW_REFERENCE_MISSING',line,'exactly one row-reference column is required')
        if len(refs)>1: return fail('TABLE_ROW_REFERENCE_DUPLICATE',line,'more than one row-reference column found')
        idx=refs[0]
        if len(align)!=len(header): return fail('TABLE_COLUMN_COUNT_MISMATCH',line,'alignment column count must match header')
        if rtl:
            if args.surface=='chat' and idx!=0:
                return fail('RTL_CHAT_ROW_REFERENCE_SOURCE_POSITION_INVALID',line,'ABSOLUTE HARD GATE: Persian Chat requires row-reference as FIRST source column; source-last/reverse-universal serialization is prohibited')
            if args.surface=='codex' and idx!=len(header)-1:
                return fail('RTL_CODEX_ROW_REFERENCE_SOURCE_POSITION_INVALID',line,'Windows Codex uses the separate reverse-source serializer with row-reference LAST')
            if any(not right_aligned(a) for a in align): return fail('RTL_TABLE_NON_REFERENCE_ALIGNMENT_NOT_RIGHT',line,'Every RTL column, including row-reference, must use ---:')
            for j,hcell in enumerate(header):
                if j==idx: continue
                if not rtl_word_first(hcell): return fail('RTL_TABLE_HEADER_NOT_RTL_WORD_FIRST',line,'Every RTL table header must begin visibly with an RTL-script word')
                if args.surface=='chat':
                    err=embedded_ltr_isolation_error(hcell)
                    if err: return fail(err[0],line,err[1])
        else:
            if idx!=0: return fail('LTR_TABLE_ROW_REFERENCE_NOT_LEFTMOST',line,'LTR Markdown requires row-reference as first source column')
            if any(not left_aligned(a) for a in align): return fail('LTR_TABLE_ALIGNMENT_NOT_LEFT',line,'Every LTR column must explicitly use :---')
            if any(any(ctrl in c for ctrl in (RLM,RLI,FSI)) for c in header): return fail('LTR_TABLE_DIRECTION_CONTROL_PROHIBITED',line,'Ordinary LTR table headers must not contain RTL direction anchors')
        vals=[]
        for row in rows:
            if len(row)!=len(header): return fail('TABLE_COLUMN_COUNT_MISMATCH',line,f'header has {len(header)} columns but body row has {len(row)}')
            if rtl:
                for j,tcell in enumerate(row):
                    if j==idx: continue
                    if not rtl_word_first(tcell): return fail('RTL_TABLE_CELL_NOT_RTL_WORD_FIRST',line,'Every non-row-reference RTL table cell must begin visibly with an RTL-script word')
                    if args.surface=='chat':
                        err=embedded_ltr_isolation_error(tcell)
                        if err: return fail(err[0],line,err[1])
            cell=row[idx]
            if rtl and args.surface=='chat':
                if prohibited_rtl_chat_row_wrapper(cell): return fail('RTL_CHAT_ROW_REFERENCE_WRAPPER_PROHIBITED',line,'Row-reference permits exactly one leading RLM plus bare ASCII digits')
                if not exact_rtl_chat_row_cell(cell): return fail('RTL_CHAT_ROW_REFERENCE_RLM_ENVELOPE_INVALID',line,'Row-reference source must be exactly RLM + bare ASCII digits')
                v=semantic_ascii_int(cell,True)
            elif rtl:
                if any(x in cell for x in (NBSP,LRM,RLM,LRI,RLI,FSI,PDI)) or '`' in cell: return fail('PERSIAN_TABLE_ROW_VALUE_NOT_BARE_ASCII_INTEGER',line,'Non-Chat RTL row-reference must be bare ASCII digits')
                v=semantic_ascii_int(cell)
            else: v=parse_int(cell)
            if v is None: return fail('PERSIAN_TABLE_ROW_VALUE_NOT_BARE_ASCII_INTEGER',line,'row-reference semantic payload must be bare ASCII integer')
            vals.append(v)
        expected=list(range(1,len(vals)+1))
        if vals!=expected: return fail('TABLE_ROW_REFERENCE_NONSEQUENTIAL',line,f'expected {expected}, got {vals}')
    print(f'TABLE_CONFORMANCE_PASS: {len(found)} table(s) validated'); return 0
if __name__=='__main__': raise SystemExit(main())
