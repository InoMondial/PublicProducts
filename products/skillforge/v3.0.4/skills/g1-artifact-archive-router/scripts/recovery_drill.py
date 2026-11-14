#!/usr/bin/env python3
"""Validate a bounded self-contained recovery archive, without executing it.

Internal hashes prove byte consistency, not publisher authenticity or live
restore. Provider authorization and trusted expected archive hash are external.
"""
from pathlib import Path, PurePosixPath, PureWindowsPath
import hashlib, re, stat, tempfile, zipfile
MAX_ENTRIES=10000
MAX_EXPANDED_BYTES=100*1024*1024

def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def safe_name(name):
    p=PurePosixPath(name)
    return (isinstance(name,str) and bool(name) and not p.is_absolute()
            and not PureWindowsPath(name).drive and '\\' not in name and ':' not in name
            and not any(ord(c)<32 or ord(c)==127 for c in name)
            and all(part not in ('','..','.') for part in name.rstrip('/').split('/')))

def verify(bundle):
    try:
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'restore';out.mkdir()
            with zipfile.ZipFile(Path(bundle)) as archive:
                infos=archive.infolist();names=[i.filename for i in infos]
                if len(infos)>MAX_ENTRIES or sum(i.file_size for i in infos)>MAX_EXPANDED_BYTES:
                    return {'ok':False,'status':'RECOVERY_RESOURCE_LIMIT'}
                if len(names)!=len(set(names)) or len(names)!=len({n.casefold() for n in names}):
                    return {'ok':False,'status':'RECOVERY_DUPLICATE_MEMBER'}
                for item in infos:
                    if not safe_name(item.filename) or stat.S_ISLNK(item.external_attr>>16) or item.flag_bits&1:
                        return {'ok':False,'status':'RECOVERY_UNSAFE_MEMBER'}
                required={'RECOVERY.md','metadata/MANIFEST.sha256','metadata/github-provenance.yaml'}
                files={i.filename for i in infos if not i.is_dir()}
                if not required<=files:return {'ok':False,'status':'RECOVERY_REQUIRED_MEMBER_MISSING'}
                # Names validated before any extraction. Only regular byte data.
                for item in infos:
                    target=out/item.filename
                    if item.is_dir():target.mkdir(parents=True,exist_ok=True);continue
                    target.parent.mkdir(parents=True,exist_ok=True)
                    target.write_bytes(archive.read(item))
            checked=set()
            for line in (out/'metadata/MANIFEST.sha256').read_text(encoding='utf-8').splitlines():
                if not line.strip():continue
                parts=line.split('  ',1)
                if len(parts)!=2:return {'ok':False,'status':'RECOVERY_MANIFEST_INVALID'}
                digest,rel=parts
                if not re.fullmatch('[0-9a-f]{64}',digest) or not safe_name(rel) or rel in checked or rel not in files:
                    return {'ok':False,'status':'RECOVERY_MANIFEST_INVALID'}
                if sha(out/rel)!=digest:return {'ok':False,'status':'RECOVERY_HASH_MISMATCH'}
                checked.add(rel)
            if checked!=files-{'metadata/MANIFEST.sha256'}:
                return {'ok':False,'status':'RECOVERY_MANIFEST_COVERAGE_MISMATCH'}
            return {'ok':True,'status':'RECOVERY_PROVEN','checked':len(checked),
                    'verification_scope':'OFFLINE_COMPLETE_BYTES_NOT_LIVE_RESTORE'}
    except (OSError,ValueError,KeyError,UnicodeError,zipfile.BadZipFile,RuntimeError):
        return {'ok':False,'status':'RECOVERY_ARCHIVE_INVALID'}
