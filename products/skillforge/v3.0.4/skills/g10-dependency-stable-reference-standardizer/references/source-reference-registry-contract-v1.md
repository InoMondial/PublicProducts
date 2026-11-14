# Governed Source & Stable Reference Registry Contract

**Contract ID:** `INC_SOURCE_REFERENCE_REGISTRY_V1`
**Owner:** `G10-Dependency & Stable Reference Standardizer`
**Framework:** `SkillForge`

## Purpose
Provide one governed registry for normative/informative source references without copying source bodies into every Skill.

## Required fields
Each registered source/reference records, as applicable:
- `source_id`
- `title`
- `source_type: OFFICIAL | STANDARD | INTERNAL_POLICY | INTERNAL_CONTRACT | TEMPLATE | EVIDENCE | INFORMATIONAL | EXTERNAL_CHANGE_REQUEST`
- `authority: NORMATIVE | INFORMATIVE | EVIDENCE_ONLY | PROVISIONAL`
- `location_ref`
- `version_or_date`
- `last_verified_at`
- `freshness_policy`
- `owner_ref`
- `applicable_skills`
- `content_identity` when immutable bytes/hash are available
- `status: ACTIVE | STALE | SUPERSEDED | BLOCKED_SOURCE_REQUIRED | HISTORICAL`

## Rules
1. Stable IDs/registry refs are preferred over transient URLs.
2. A mutable URL is not proof that content is unchanged; use version/hash/date/read-back evidence where material.
3. Official/current guidance must be revalidated before being treated as current normative authority when freshness matters.
4. Missing exact bytes for an external Change Request stays `PROVISIONAL/BLOCKED_SOURCE_REQUIRED`; recovered summaries cannot silently become normative.
5. Historical/superseded source records remain auditable but cannot override active Registry/contract truth.
6. Runtime loads only references required for the current activity; the full source registry is not recursively loaded by every Skill.
7. Registry writer authority is G10 under G0-governed change; consumers do not opportunistically mutate shared source truth.
