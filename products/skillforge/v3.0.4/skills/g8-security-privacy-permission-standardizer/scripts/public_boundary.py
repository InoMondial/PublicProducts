#!/usr/bin/env python3
"""Fail-closed content, archive and publication-boundary checks.

No network or publishing. Authentication belongs to the calling trusted adapter.
A scan is not semantic review, consent, or proof about GitHub caches/forks.
"""
from __future__ import annotations
import argparse, base64, hashlib, io, json, re, stat, unicodedata, zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

CONTRACT = 'INC_PUBLICIZATION_PRIVACY_GATE_V2'
SURFACES = ('files', 'archives', 'refs_history', 'authors', 'releases',
            'issues_pr_comments', 'logs_artifacts', 'wiki_pages', 'settings')
REVIEW_CLASSES = {'PUBLIC_GENERIC', 'APPROVED_DISCLOSURE', 'SYNTHETIC_FIXTURE'}
FORBIDDEN_PARTS = {'.git', '.env', 'private-overlay', 'private_overlay',
                   'private-evidence', 'owner-state', '__pycache__'}
TEXT_SUFFIXES = {'.md', '.txt', '.json', '.yaml', '.yml', '.csv', '.tsv', '.py',
                 '.js', '.mjs', '.cjs', '.ts', '.sql', '.sh', '.ps1', '.xml',
                 '.svg', '.toml', '.ini', '.cfg', '.lock', '.sha256', '.html'}
SECRET = re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|'
                    r'\bgh[pousr]_[A-Za-z0-9]{30,}\b|\bgithub_pat_[A-Za-z0-9_]{35,}\b|'
                    r'\bAKIA[0-9A-Z]{16}\b|\bsk-(?:proj-)?[A-Za-z0-9_-]{28,}\b')
EMAIL = re.compile(r'(?<![\w.+-])[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}', re.I)
URL = re.compile(r'https?://[^\s<>"`\\\[\]{}]+', re.I)
GUID = re.compile(r'\b[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}\b', re.I)
OPERATIONAL_ID = re.compile(r'\b(?:HOF-[0-9A-F]{12,}|proj_[A-Za-z0-9]{10,}|'
                            r'01[A-Z0-9]{24}|19:[A-Za-z0-9_-]{15,}@thread\.[a-z0-9]+)\b', re.I)
NOREPLY = re.compile(r'\b[0-9]+\+[\w-]+@users\.noreply\.github\.com\b', re.I)
CUSTODY = re.compile(r'(?:[A-Z]:[\\/](?:Users|Documents)[\\/]|'
                     r'/Users/[A-Za-z][A-Za-z0-9_.-]{1,50}/|/home/(?!runner\b)[a-zA-Z][\w.-]+/|'
                     r'(?:key|secret)[-_ ]?(?:file|path)\s*[:=]\s*["\']?(?:[A-Z]:|/))')
SECRET_FIELDS = {'password', 'accesstoken', 'refreshtoken', 'clientsecret',
                 'apikey', 'privatekey', 'cookie', 'authorization'}

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'),
                      ensure_ascii=False, allow_nan=False).encode('utf-8')

def unique_pairs(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ValueError('DUPLICATE_JSON_KEY')
        out[k] = v
    return out

def normal(text: str) -> str:
    s = unicodedata.normalize('NFKC', text)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Cf')
    for _ in range(2):
        s = unquote(s)
        s = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m[1], 16)), s)
        s = re.sub(r'\\x([0-9a-fA-F]{2})', lambda m: chr(int(m[1], 16)), s)
    return s

def keyname(s: str) -> str:
    return re.sub('[^a-z0-9]', '', s.lower())

def secret_field_key(key: str) -> bool:
    normalized = keyname(key)
    if normalized.endswith(('ref', 'reference')):
        return False
    return any(normalized.endswith(suffix) for suffix in SECRET_FIELDS | {'secretvalue', 'secretkey', 'keyb64', 'privatepem'})

def secret_fields(value) -> bool:
    if isinstance(value, dict):
        return any((secret_field_key(str(k)) and v not in (None, '', 'UNBOUND'))
                   or secret_fields(v) for k, v in value.items())
    return isinstance(value, list) and any(secret_fields(v) for v in value)

def path_ok(name: str) -> bool:
    p = PurePosixPath(name)
    return (bool(name) and not p.is_absolute() and '\\' not in name and ':' not in name
            and all(x not in {'', '.', '..'} for x in name.split('/'))
            and not any(x.casefold() in FORBIDDEN_PARTS for x in p.parts)
            and not any(ord(c) < 32 or unicodedata.category(c) == 'Cf' for c in name))

class Scanner:
    def __init__(self, policy: dict | None = None):
        self.policy = policy or {}
        self.findings: list[dict] = []
        self.units: dict[str, dict] = {}
        self.total = 0
        self.max_bytes = min(int(self.policy.get('max_expanded_bytes', 64000000)), 256000000)
        self.max_files = min(int(self.policy.get('max_files', 5000)), 20000)
        self.max_depth = min(int(self.policy.get('max_archive_depth', 4)), 8)
        self.max_ratio = min(int(self.policy.get('max_compression_ratio', 250)), 1000)
        self.allow_emails = {v.casefold() for v in self.policy.get('approved_emails', [])}
        self.deny = [(str(x['id']), normal(str(x['value'])).casefold())
                     for x in self.policy.get('private_terms', []) if len(str(x.get('value', ''))) >= 3]

    def fail(self, code: str, path: str, line: int = 0):
        # Do not echo a discovered value or source excerpt into an output/log.
        row = {'code': code, 'path': path, 'line': line}
        if row not in self.findings:
            self.findings.append(row)

    def text(self, value: str, path: str):
        s = normal(value)
        for label, pat in [('SECRET', SECRET), ('PERSONAL_NOREPLY', NOREPLY),
                           ('PERSONAL_CUSTODY_PATH', CUSTODY), ('OPERATIONAL_IDENTIFIER', OPERATIONAL_ID)]:
            for m in pat.finditer(s):
                self.fail(label, path, s[:m.start()].count('\n') + 1)
        for m in EMAIL.finditer(s):
            email = m[0].lower()
            domain = email.split('@')[-1]
            if email not in self.allow_emails and domain not in {'example.invalid', 'example.com', 'example.org'}:
                self.fail('UNAPPROVED_EMAIL', path, s[:m.start()].count('\n') + 1)
        for m in GUID.finditer(s):
            if len(set(m[0].replace('-', ''))) > 1:
                self.fail('REALISTIC_PROVIDER_ID', path, s[:m.start()].count('\n') + 1)
        for m in URL.finditer(s):
            try:
                u = urlsplit(m[0].rstrip('.,);'))
                if u.username or u.password or re.search(r'(?i)(?:token|sig|secret|key|code|credential)=', u.query):
                    self.fail('CREDENTIAL_OR_SIGNED_URL', path, s[:m.start()].count('\n') + 1)
                host = (u.hostname or '').lower()
                if host.endswith(('.sharepoint.com', '.onmicrosoft.com', '.vault.azure.net', '.local')):
                    self.fail('PRIVATE_SERVICE_ENDPOINT', path, s[:m.start()].count('\n') + 1)
            except ValueError:
                self.fail('INVALID_URL', path)
        folded = s.casefold()
        for term_id, value in self.deny:
            if value in folded:
                self.fail('PRIVATE_TERM:' + term_id, path, folded[:folded.index(value)].count('\n') + 1)
        # Decode bounded, plausibly encoded text once. Unknown binary remains covered by file policy.
        for m in re.finditer(r'(?<![A-Za-z0-9+/])[A-Za-z0-9+/]{16,2048}={0,2}(?![A-Za-z0-9+/])', s):
            try:
                decoded = base64.b64decode(m[0], validate=True).decode('utf-8')
                if '@' in decoded or 'http' in decoded or any(v in normal(decoded).casefold() for _, v in self.deny):
                    self.text_decoded(decoded, path)
            except (ValueError, UnicodeError):
                pass

    def text_decoded(self, value: str, path: str):
        # No recursive decoding loops or recursive base64 matching.
        n = normal(value).casefold()
        if SECRET.search(value) or NOREPLY.search(value) or OPERATIONAL_ID.search(value):
            self.fail('ENCODED_PRIVATE_DATA', path)
        for e in EMAIL.findall(value):
            if e.lower() not in self.allow_emails and not e.lower().endswith(('@example.invalid','@example.com','@example.org')):
                self.fail('ENCODED_PRIVATE_DATA', path)
        if any(v in n for _, v in self.deny):
            self.fail('ENCODED_PRIVATE_DATA', path)

    def data(self, path: str, data: bytes, depth: int = 0):
        if len(self.units) >= self.max_files or self.total + len(data) > self.max_bytes:
            self.fail('RESOURCE_LIMIT', path)
            return
        if path in self.units:
            self.fail('DUPLICATE_MEMBER', path)
            return
        self.total += len(data)
        self.units[path] = {'sha256': digest(data), 'bytes': len(data)}
        self.text(path, path)
        if data[:4] in (b'PK\x03\x04', b'PK\x05\x06', b'PK\x07\x08') or path.lower().endswith('.zip'):
            if depth >= self.max_depth:
                self.fail('ARCHIVE_DEPTH_LIMIT', path)
                return
            try:
                with zipfile.ZipFile(io.BytesIO(data)) as z:
                    if z.comment:
                        self.fail('ARCHIVE_COMMENT', path)
                    if len(z.infolist()) + len(self.units) > self.max_files:
                        self.fail('ARCHIVE_MEMBER_LIMIT', path)
                        return
                    names = set()
                    for member in z.infolist():
                        n = member.filename.rstrip('/')
                        if not path_ok(n):
                            self.fail('UNSAFE_ARCHIVE_PATH', path)
                            continue
                        if n.casefold() in names:
                            self.fail('DUPLICATE_ARCHIVE_MEMBER', path)
                            continue
                        names.add(n.casefold())
                        mode = member.external_attr >> 16
                        if stat.S_ISLNK(mode) or (stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR)):
                            self.fail('ARCHIVE_LINK_OR_SPECIAL', path)
                            continue
                        if member.flag_bits & 1 or member.comment or member.extra:
                            self.fail('UNREVIEWED_ARCHIVE_METADATA', path)
                            continue
                        if member.is_dir():
                            continue
                        if (member.file_size > self.max_bytes - self.total
                                or member.file_size / max(1, member.compress_size) > self.max_ratio):
                            self.fail('ARCHIVE_EXPANSION_LIMIT', path)
                            continue
                        self.data(path + '!/' + n, z.read(member), depth + 1)
            except (zipfile.BadZipFile, OSError, RuntimeError, NotImplementedError, EOFError):
                self.fail('ARCHIVE_UNREADABLE', path)
            return
        suffix = Path(path).suffix.lower()
        name = Path(path).name
        if suffix not in TEXT_SUFFIXES and name not in {'LICENSE', 'NOTICE', 'TRADEMARKS', 'THIRD_PARTY_NOTICES', 'CODEOWNERS', '.gitignore'}:
            self.fail('UNSUPPORTED_CONTENT_TYPE', path)
            return
        try:
            text = data.decode('utf-8')
            if '\x00' in text:
                raise UnicodeError('NUL')
        except UnicodeError:
            self.fail('UNREADABLE_TEXT', path)
            return
        self.units[path]['lines'] = len(text.splitlines())
        self.text(text, path)

    def scan(self, root: Path | str) -> dict:
        root = Path(root)
        try:
            if root.is_symlink():
                self.fail('SYMLINK', '<root>')
            elif root.is_file():
                self.data(root.name, root.read_bytes())
            elif root.is_dir():
                for p in sorted(root.rglob('*')):
                    n = p.relative_to(root).as_posix()
                    if not path_ok(n):
                        self.fail('FORBIDDEN_PATH', n)
                        continue
                    if p.is_symlink():
                        self.fail('SYMLINK', n)
                    elif p.is_file():
                        try:
                            self.data(n, p.read_bytes())
                        except OSError:
                            self.fail('UNREADABLE_FILE', n)
                    elif not p.is_dir():
                        self.fail('SPECIAL_FILE', n)
            else:
                self.fail('MISSING_SOURCE', '<root>')
        except OSError:
            self.fail('INVENTORY_UNREADABLE', '<root>')
        return {'contract': CONTRACT, 'status': 'FAIL' if self.findings else 'STATIC_SCAN_PASS',
                'tree_digest': digest(canonical(self.units)), 'units': self.units,
                'unit_count': len(self.units), 'expanded_bytes': self.total,
                'findings': self.findings, 'public_release_authorized': False}

def authorize(report: dict, review: dict, consent: dict, surfaces: dict, target: dict) -> list[str]:
    """Consistency only. The host must independently authenticate identity, time and observations."""
    errors = []
    if report.get('status') != 'STATIC_SCAN_PASS' or report.get('findings'):
        errors.append('CONTENT_SCAN_FAILED')
    td = report.get('tree_digest')
    if not td or review.get('tree_digest') != td or consent.get('tree_digest') != td:
        errors.append('STALE_OR_UNBOUND_EVIDENCE')
    rows = review.get('files')
    units = report.get('units', {})
    if not isinstance(rows, dict) or set(rows) != set(units):
        errors.append('REVIEW_COVERAGE_INCOMPLETE')
    else:
        for path, unit in units.items():
            r = rows[path]
            if (not isinstance(r,dict) or r.get('sha256') != unit['sha256']
                    or r.get('classification') not in REVIEW_CLASSES or not r.get('reason')
                    or (r.get('classification') == 'APPROVED_DISCLOSURE' and
                        (not r.get('consent_id') or r.get('consent_id') != consent.get('consent_id')))):
                errors.append('FILE_REVIEW_INVALID')
                break
    if (target.get('visibility') != 'PUBLIC' or target.get('observation_verified') is not True
            or not target.get('repository_id') or not target.get('observation_id')):
        errors.append('ACTUAL_PUBLIC_TARGET_UNVERIFIED')
    if (consent.get('owner_authenticated') is not True or consent.get('publish') is not True
            or consent.get('target_repository_id') != target.get('repository_id')
            or not consent.get('consent_id') or consent.get('expired') is not False):
        errors.append('OWNER_PUBLICATION_CONSENT_REQUIRED')
    binding = surfaces.get('_binding', {})
    if (binding.get('tree_digest') != td or binding.get('target_repository_id') != target.get('repository_id')
            or binding.get('verified') is not True or not binding.get('observed_at')):
        errors.append('SURFACE_SNAPSHOT_NOT_BOUND')
    for name in SURFACES:
        s = surfaces.get(name)
        if not isinstance(s,dict) or s.get('status') not in {'PASS','NOT_PRESENT'} or not s.get('evidence_id') or s.get('complete') is not True:
            errors.append('SURFACE_UNREVIEWED:' + name)
    return sorted(set(errors))

def private_destination(observation: dict) -> None:
    if (observation.get('visibility') != 'PRIVATE' or observation.get('verified') is not True
            or not observation.get('repository_id') or not observation.get('observed_at')):
        raise ValueError('PRIVATE_DESTINATION_OBSERVATION_REQUIRED')

def load_external_profile(path: str, expected_sha256: str, package_root: str) -> dict:
    p = Path(path)
    if p.is_symlink() or not p.is_file():
        raise ValueError('EXTERNAL_PROFILE_UNREADABLE')
    try:
        p.resolve().relative_to(Path(package_root).resolve())
    except ValueError:
        pass
    else:
        raise ValueError('PROFILE_MUST_BE_OUTSIDE_DISTRIBUTABLE')
    raw = p.read_bytes()
    if len(raw)>1000000 or digest(raw) != expected_sha256:
        raise ValueError('PROFILE_HASH_MISMATCH')
    profile = json.loads(raw, object_pairs_hook=unique_pairs, parse_constant=lambda value: (_ for _ in ()).throw(ValueError('NONFINITE_JSON')))
    if not isinstance(profile,dict) or secret_fields(profile):
        raise ValueError('RAW_SECRET_OR_INVALID_PROFILE')
    if SECRET.search(raw.decode('utf-8')):
        raise ValueError('RAW_SECRET_IN_PROFILE')
    if profile.get('state') != 'BOUND' or not isinstance(profile.get('parameters'),dict):
        raise ValueError('PROFILE_UNBOUND')
    return profile

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source'); p.add_argument('--policy'); p.add_argument('--output')
    a = p.parse_args()
    try:
        policy = json.loads(Path(a.policy).read_text(), object_pairs_hook=unique_pairs) if a.policy else {}
        report = Scanner(policy).scan(a.source)
    except (OSError,ValueError,TypeError):
        report = {'status':'FAIL','findings':[{'code':'INVALID_POLICY_OR_SOURCE'}]}
    if a.output:
        Path(a.output).write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in {'units','findings'}} | {'finding_count':len(report['findings'])}))
    return int(report['status'] != 'STATIC_SCAN_PASS')
if __name__ == '__main__':
    raise SystemExit(main())
