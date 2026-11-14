# SkillForge 3.0.4-public.1 — Public Release Verification

## Release identification

- Public repository: `InoMondial/PublicProducts` (repository ID `1458006835`, default branch `main`)
- Product path: `products/skillforge/v3.0.4/`
- Edition: `3.0.4-public.1` (core: `3.0.4`)
- Public tag: `skillforge-v3.0.4-public.1`
- Public GitHub Release: https://github.com/InoMondial/PublicProducts/releases/tag/skillforge-v3.0.4-public.1
- GitHub Release ID: `445480791`
- Frozen source commit: `0cdf16e8956806fd4838d42634ecab75d2405ee4`
- GitHub Release status: published, not draft, not prerelease
- Package: `SkillForge-3.0.4-public.1-SOURCE.zip`
- Package bytes: `781895`
- Package SHA-256: `56497c0e707d125c8bec24b00342b780ecc294cc6c623f60bcb18092e68320a0`
- Other release assets: `SHA256SUMS.txt` and `PUBLIC_RELEASE_VALIDATION.json`

## Actual acceptance

- Real workflow: https://github.com/InoMondial/PublicProducts/actions/runs/43623390477 — `completed/success`.
- Source file inventory: `422` files with `19` `SKILL.md` entrypoints; the immutable private-package manifest was not copied.
- Source privacy scanning: `STATIC_SCAN_PASS`, no reported findings.
- Archive nested-content scanning: `STATIC_SCAN_PASS`, no reported findings (`424` units including ZIP and internal public manifest).
- Python source syntax: `74` files compiled as syntax checks.
- JavaScript syntax: GitHub Actions Node check completed successfully.
- Archive integrity: CRC check and per-file SHA-256 compare passed; `sha256sum --check` completed successfully.
- Machine-readable product discovery: `catalog/products.json`.

## Publication and license boundary

This is a public **source-available** product, NOT an OSI-approved open-source product. The product-local `LICENSE`, `RIGHTS_PROFILE.yaml`, `NOTICE`, `THIRD_PARTY_NOTICES` and `TRADEMARKS` govern usage. Commercial/organizational deployment requires prior express written permission under the published license.

No owner-specific environment values, live credentials or private incident evidence were knowingly included in the public source. All external service integrations, telemetry and public feedback remain disabled by default or dependent on independent host authorization. Publication does NOT prove native ChatGPT installation or permissions to external apps.

## Repository layout

Every future product is a sibling at `products/<slug>/`, each with its own `README.md`, version directories, rights, release tag, tests and publication procedure. This release affects only `products/skillforge/`; it is not a repository-wide release for future products.

## Historical exposure limitations

The formerly distributed product was withdrawn and its original public repository has been reported deleted. GitHub API now returns 404 for that prior repository, but a 404 does not prove deletion of cached data, downloads, forks, mirrors or externally copied files. This newly created repository is a separate public destination with an independent initial history.
