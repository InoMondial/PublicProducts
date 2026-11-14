# INC_REMOTE_ARTIFACT_DELIVERY_V2

## Scope
Applies to every system-generated or materially modified artifact delivered under G18 on Chat, Work or Codex, including files, documents, spreadsheets, slides, PDFs, archives, code bundles, text/config artifacts, images, screenshots, diagrams, charts and infographics.

## Absolute pipeline
1. Create or modify only in non-user-visible transient staging.
2. Resolve the governed durable destination through G1.
3. Write the artifact remotely.
4. Read back the exact remote artifact and verify identity/version/hash when available.
5. Expose only the verified remote link to the user.

## Destination rules
- Generated images, infographics, charts, diagrams, screenshots and document/binary artifacts: SharePoint final delivery only.
- Repository-governed non-confidential source/code/text/config: GitHub may be the final destination when G1 declares it canonical.
- Confidential artifacts: SharePoint only.

## Prohibited final delivery
- sandbox:/ links; /mnt/data paths; file:// links; local filesystem paths.
- Direct Chat/Work/Codex generated attachment cards or local download cards.
- Inline display of a system-generated image/infographic as the final delivery path.
- A direct local copy shown in addition to a valid remote copy.

## Generated media execution gate
Do not invoke a media-generation route that necessarily renders the generated media directly to the user before governed publication. If no non-visible staging plus SharePoint publication/read-back route is available on the current surface, route the bounded generation unit through G16 to a compatible surface or mark it blocked. Never weaken the egress rule to obtain a preview.

## Validation
Use `scripts/validate_artifact_delivery.py`. Visible-response validation is mandatory for every substantive response. When an artifact was generated or modified, supply an artifact-event ledger and require verified remote write/read-back plus a remote-only terminal link.
