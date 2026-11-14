# G16 Handoff Data Contract v1.1.0

**Status:** TEST-CANDIDATE CONTRACT  
**Logical format:** strict JSON object  
**Transport:** UTF-8 `text/plain`  
**File extension:** `.txt`  
**Schema:** `G16_HANDOFF_STATE_V1.schema.json`

## Canonical decision
G16 Handoffs are strict JSON serialized as UTF-8 and stored in SharePoint as `.txt` / `text/plain`. The `.txt` extension is transport compatibility only; payload MUST parse and validate before successful persistence can be claimed.

## Filename
Preferred: `<SanitizedTitle>__<handoff_id>__<created_date>.txt` when a reliable title exists.  
Fallback: `<handoff_id>__<created_date>.txt`.

`handoff_id` is identity; title is optional metadata.

## Mandatory top-level fields
`schema_version`, `handoff_id`, `chat_id`, `chat_title`, `created_at`, `updated_at`, `state`.

## Semantic completeness
A Schema-valid Handoff may still be incomplete. `state` must contain every transferable fact, requirement, correction, approved decision, artifact/reference, constraint, definition/ID, current-state fact, unresolved item, and other information whose omission could materially alter continuation in a completely new chat.

Semantic compression is allowed. Semantic loss is not.

## Validation
V1 strict JSON parse.  
V2 JSON Schema v1.  
V3 SharePoint persistence/read-back integrity.  
V4 clean-room continuation.

## Runtime boundary
No logging or notification subsystem is required by G16 runtime. Runtime no-logging is bounded by `INC_RUNTIME_LOGGING_EXCEPTION_V1` / `G16-NO-RUNTIME-LOGGING-001`.

## Migration note
This contract supersedes the provisional G17-named candidate contract. Runtime `handoff_id` values and existing SharePoint Handoff files do not need renaming because Skill visible ID is not part of Handoff identity.
