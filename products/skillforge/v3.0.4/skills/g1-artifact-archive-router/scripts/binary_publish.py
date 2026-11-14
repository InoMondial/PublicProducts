#!/usr/bin/env python3
"""Byte-preserving staging in a trusted, exclusively coordinated repository.

This transport does not grant publication authorization or choose storage policy.
Document/media binaries remain subject to G1 SharePoint-only placement. Git
commits affect only the requested path, not unrelated pre-staged user changes.
"""
from pathlib import Path, PurePosixPath, PureWindowsPath
import argparse, hashlib, os, shutil, subprocess, tempfile

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()

def copy_exact(src,dst):
    src=Path(src);dst=Path(dst)
    if not src.is_file() or src.is_symlink():raise ValueError('SOURCE_FILE_INVALID')
    if src.resolve()==dst.resolve():raise ValueError('SOURCE_EQUALS_DESTINATION')
    dst.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix='.g1-stage-',dir=dst.parent)
    try:
        with os.fdopen(fd,'wb') as target,src.open('rb') as source:
            shutil.copyfileobj(source,target);target.flush();os.fsync(target.fileno())
        a,b=sha256(src),sha256(tmp)
        if a!=b:raise RuntimeError('STAGING_HASH_MISMATCH')
        os.replace(tmp,dst)
        return {'sha256':a,'size':dst.stat().st_size}
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

def _safe_target(repo_root,dest):
    repo=Path(repo_root).resolve()
    if not isinstance(dest,(str,Path)) or not str(dest):raise ValueError('DESTINATION_INVALID')
    text=str(dest);p=PurePosixPath(text)
    if (p.is_absolute() or PureWindowsPath(text).drive or '\\' in text or ':' in text
        or any(ord(c)<32 or ord(c)==127 for c in text)
        or any(x in ('.','..','') for x in text.split('/'))
        or any(x.lower().rstrip(' .')=='.git' for x in p.parts)):
        raise ValueError('DESTINATION_OUTSIDE_ALLOWED_REPOSITORY')
    if not repo.is_dir() or not (repo/'.git').exists():raise ValueError('REPOSITORY_REQUIRED')
    target=repo.joinpath(*p.parts)
    cursor=repo
    for part in p.parts:
        cursor=cursor/part
        if cursor.is_symlink():raise ValueError('DESTINATION_SYMLINK_PROHIBITED')
    if not target.resolve().is_relative_to(repo):raise ValueError('DESTINATION_ESCAPE')
    return repo,target,p.as_posix()

def publish_with_authenticated_git(src,repo_root,dest,commit_message=None,push=False,publication_context=None):
    repo,target,relative=_safe_target(repo_root,dest)
    if type(push) is not bool or (push and not commit_message):raise ValueError('PUSH_REQUIRES_EXPLICIT_COMMIT')
    if commit_message is not None and (not isinstance(commit_message,str) or not commit_message.strip()):raise ValueError('COMMIT_MESSAGE_INVALID')
    if push:
        from public_egress import assert_egress
        assert_egress(src, publication_context)
    meta=copy_exact(src,target)
    subprocess.run(['git','add','--',relative],cwd=repo,check=True)
    if commit_message:
        subprocess.run(['git','commit','--only','-m',commit_message,'--',relative],cwd=repo,check=True)
        if push:subprocess.run(['git','push'],cwd=repo,check=True)
    return meta

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('src');ap.add_argument('repo_root');ap.add_argument('dest');ap.add_argument('--commit-message');ap.add_argument('--push',action='store_true');a=ap.parse_args()
    print(publish_with_authenticated_git(a.src,a.repo_root,a.dest,a.commit_message,a.push))
