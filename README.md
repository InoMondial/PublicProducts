# INOMondial Public Products

Public distribution hub for **independent, versioned INOMondial products**. Each product has its own source, license, documentation and release lifecycle. This repository is designed to accommodate many sibling products without mixing their files or histories.

## Products
| Product | Description | Latest version | Documentation |
| --- | --- | --- | --- |
| **SkillForge** | A factory for creating and governing reusable Skills | 3.0.4-public.1 | [SkillForge](products/skillforge/README.md) |

The canonical machine-readable catalog is [catalog/products.json](catalog/products.json).

## Repository layout
```text
catalog/
  products.json                  # Product discovery index
docs/
  REPOSITORY_LAYOUT.md           # Structure and publishing policy
products/
  skillforge/
    README.md                    # Product home and version index
    v3.0.4/                      # Complete versioned public source
  <next-product>/
    README.md
    v<version>/
.github/workflows/             # Product-scoped independent release workflows
```

**Distribution license:** This repository contains *source-available* products, not necessarily open-source software. Read each product's own `LICENSE`, `NOTICE`, `THIRD_PARTY_NOTICES` and `TRADEMARKS` before use. Public availability does not grant commercial-use rights.

**Privacy:** Product packages contain no live credentials or owner-specific service configuration. Never post secrets, operational IDs, private reports or user environments in public issues, commits or release assets.

**Release status:** Published source is on `main`; downloadable immutable binaries are published through product-specific GitHub Releases after the product validation workflow passes.
