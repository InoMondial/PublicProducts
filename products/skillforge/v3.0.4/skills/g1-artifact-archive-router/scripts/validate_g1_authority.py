#!/usr/bin/env python3
"""Read-only G1 runtime-identity audit; historical evidence is not executable."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any
import yaml

SID = 'G01-SKL-001'
CANONICAL = 'skills/router/g1-artifact-archive-router/'
LEGACY = 'skills/router/g01-artifact-archive-router/'
MIRROR = 'plugins/inomondial-skillforge-private/skills/g1-artifact-archive-router/'


def load_yaml(text: str) -> dict[str, Any]:
    class UniqueLoader(yaml.SafeLoader):
        pass
    def mapping(loader, node, deep=False):
        loader.flatten_mapping(node)
        result = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node, deep=deep)
            if key in result:
                raise ValueError('DUPLICATE_YAML_KEY')
            result[key] = loader.construct_object(value_node, deep=deep)
        return result
    UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
    value = yaml.load(text, Loader=UniqueLoader)
    if not isinstance(value, dict):
        raise ValueError('MAPPING_REQUIRED')
    return value


def metadata(text: str) -> dict[str, Any]:
    lines = text.splitlines()
    if not lines or lines[0] != '---':
        raise ValueError('FRONTMATTER_REQUIRED')
    end = lines.index('---', 1)
    value = load_yaml('\n'.join(lines[1:end])).get('metadata', {})
    if not isinstance(value, dict):
        raise ValueError('METADATA_REQUIRED')
    return value


def audit(root: Path) -> dict[str, Any]:
    root = root.resolve()
    errors = []
    def read(relative: str) -> bytes:
        path = (root/relative).resolve()
        if not path.is_relative_to(root):
            raise ValueError('PATH_ESCAPE')
        return path.read_bytes()
    def check(condition: bool, code: str) -> None:
        if not condition:
            errors.append(code)
    registry = load_yaml(read('registries/skill-namespace-registry.yaml').decode('utf-8'))
    assigned = registry['governance_namespace']['assigned']
    g1 = assigned['G1']
    check(g1.get('stable_id') == SID and g1.get('canonical_active_path') == CANONICAL,
          'CANONICAL_REGISTRY_MISMATCH')
    check(sum(x.get('stable_id') == SID for x in assigned.values()) == 1,
          'DUPLICATE_REGISTERED_G1_IDENTITY')
    check(LEGACY in g1.get('legacy_read_only_paths', []), 'LEGACY_PATH_NOT_REGISTERED')
    active = []
    for path in sorted((root/'skills').glob('*/*/SKILL.md')):
        relative = path.relative_to(root).as_posix()
        meta = metadata(read(relative).decode('utf-8'))
        if meta.get('stable_id') != SID:
            continue
        check('executable' not in meta or isinstance(meta['executable'], bool), 'INVALID_EXECUTABLE_FLAG')
        if meta.get('executable') is not False and meta.get('lifecycle') not in ('legacy_alias', 'historical', 'superseded'):
            active.append(relative)
    check(active == [CANONICAL + 'SKILL.md'], 'EXECUTABLE_G1_AUTHORITY_NOT_UNIQUE')
    canonical = metadata(read(CANONICAL + 'SKILL.md').decode('utf-8'))
    check(canonical.get('stable_id') == SID and canonical.get('visible_id') == 'G1', 'CANONICAL_IDENTITY_MISMATCH')
    for name, parse in [('SKILL.md', metadata), ('GOVERNANCE.yaml', load_yaml)]:
        record = parse(read(LEGACY + name).decode('utf-8'))
        check(record.get('stable_id') == SID and record.get('canonical_visible_id') == 'G1' and
              record.get('executable') is False and record.get('lifecycle') == 'legacy_alias' and
              record.get('canonical_skill_path') == CANONICAL + 'SKILL.md', 'LEGACY_REDIRECT_INVALID:' + name)
    artifact = load_yaml(read(LEGACY + 'artifact.yaml').decode('utf-8'))
    check(artifact.get('stable_artifact_id') == SID and artifact.get('executable') is False and
          artifact.get('lifecycle') == 'legacy_alias' and artifact.get('canonical_active_path') == CANONICAL,
          'LEGACY_ARTIFACT_IS_EXECUTABLE')
    ui = load_yaml(read(LEGACY + 'agents/openai.yaml').decode('utf-8'))
    check(ui.get('policy', {}).get('allow_implicit_invocation') is False, 'LEGACY_IMPLICIT_INVOCATION_ENABLED')
    migration = registry['migration_controls']['G01_to_G1']
    exception = migration.get('compatibility_metadata_exception', {})
    check(migration.get('preserve_history') is True and migration.get('preserve_old_tags_and_releases') is True and
          migration.get('new_managed_writes_to_legacy_path') == 'prohibited' and
          exception.get('change_id') == 'SF-G1-006' and exception.get('runtime_development_or_reactivation') == 'prohibited',
          'HISTORY_PRESERVATION_BOUNDARY_INVALID')
    preserved_commit = exception.get('preserved_source_commit', '')
    preserved_tree = exception.get('preserved_tree_sha', '')
    check(isinstance(preserved_commit, str) and re.fullmatch('[0-9a-f]{40}', preserved_commit) is not None and
          isinstance(preserved_tree, str) and re.fullmatch('[0-9a-f]{40}', preserved_tree) is not None,
          'HISTORICAL_IDENTITY_REQUIRED')
    for name, parse in [('SKILL.md', metadata), ('GOVERNANCE.yaml', load_yaml)]:
        record = parse(read(LEGACY + name).decode('utf-8'))
        check(record.get('historical_source_commit') == preserved_commit and
              record.get('historical_tree_sha') == preserved_tree, 'HISTORICAL_POINTER_DRIFT:' + name)
    expected = {'SKILL.md', 'GOVERNANCE.yaml', 'artifact.yaml', 'agents/openai.yaml'}
    seen = set()
    for line in read(LEGACY + 'MANIFEST.sha256').decode('utf-8').splitlines():
        if not line or line.startswith('#'):
            continue
        sha, relative = line.split('  ', 1)
        check(relative in expected and relative not in seen, 'ALIAS_MANIFEST_SCOPE_INVALID')
        if relative in expected:
            check(hashlib.sha256(read(LEGACY + relative)).hexdigest() == sha, 'ALIAS_HASH_MISMATCH:' + relative)
            seen.add(relative)
    check(seen == expected, 'ALIAS_MANIFEST_INCOMPLETE')
    check(read(CANONICAL + 'SKILL.md') == read(MIRROR + 'SKILL.md'), 'CANONICAL_PACKAGE_SKILL_DRIFT')
    packaged_legacy = root/'plugins/inomondial-skillforge-private/skills/g01-artifact-archive-router'
    check(not packaged_legacy.exists(), 'LEGACY_G01_MUST_NOT_BE_BUNDLED')
    return {'result': 'PASS_G1_NAMESPACE_ONLY' if not errors else 'BLOCKED', 'errors': sorted(set(errors)),
            'active_identity_count': len(active), 'canonical_skill_path': CANONICAL + 'SKILL.md',
            'historical_source_verified_remotely_by_this_script': False,
            'independent_release_certification': False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = audit(args.repo_root)
    except Exception as exc:
        result = {'result': 'BLOCKED', 'errors': ['INPUT_INVALID'], 'error_type': type(exc).__name__}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not result['errors'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
