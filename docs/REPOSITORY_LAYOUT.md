# Public Products — structure and governance

## Principles
- Place each independent product beneath `products/<product-slug>/`.
- Give each product one `README.md` and immutable, explicit `v<version>/` source directories.
- Keep licenses, notices and release artifacts product-local; there is **no blanket root license**.
- Keep cross-product discovery data exclusively in `catalog/products.json`.
- Keep release automation in `.github/workflows/<product>-public-release.yml` with a path filter for that product.
- No secret files, private profiles, production configuration, keys, provider IDs, operational logs or historical private evidence may be committed.
- Never distribute a private ZIP as a public ZIP. Build downloadable packages from the reviewed public-source subtree only.
- Any future products (documents, applications, templates or Skills) are peers of `products/skillforge/`, never subfolders of SkillForge.

## Version identity
Separate core/runtime version (e.g. `3.0.4`) from the public packaging revision (e.g. `3.0.4-public.1`). Never modify an accepted immutable tag/asset: publish a new public packaging revision if a defect is found.

## Publication checks
Prior to a product release: perform full file/path/archive scan; inspect source and author metadata, license obligations, repository visibility and release notes; produce a per-file SHA-256 manifest and reviewed source count; validate the frozen ZIP against its source; publish only after success. A source scan is not proof that downstream caches or externally downloaded copies can be erased.

## Privacy incident reporting
Use a private support channel for actual identifiers and secrets. Public GitHub issues must not contain raw private details.
