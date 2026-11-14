# INC_G18_CONSERVATIVE_TURN_SEGMENTATION_V1

Status: Stage-30 candidate hard gate.
Owner: G18, with G16 checkpoint/Handoff integration for governed multi-surface work.

## Problem
Observed Chat delivery failures include `Connection interrupted. Waiting for the complete answer` and `Message delivery timed out. Please try again.` Existing segmentation was not conservative enough for long multi-tool, multi-system, or mutation-heavy turns.

## Hard rule
For Chat, segmentation MUST optimize for delivery reliability, not maximum work per turn.

When there is any meaningful timeout/delivery risk, divide the originally estimated turn into at least 2x as many resumable chunks as the prior estimate. When the work includes multiple remote writes, multiple systems, broad repository audit, large document generation, independent verification, or repeated tool loops, prefer approximately 3x the prior chunk count.

A chunk should normally contain only one material atomic objective plus its verification/read-back. Do not combine independent large objectives merely because they are logically related.

## Conservative admission triggers
Treat the request as `SEGMENTED_REQUIRED` when ANY of the following applies:
- more than one material external system or repository scope;
- more than one state-changing remote write plus read-back;
- full-tree/full-framework audit or many-file reconciliation;
- more than one independent validation/remediation cycle;
- large artifact generation plus remote publication;
- prior timeout/delivery failure in the same workflow;
- tool responses are large/truncated or connector latency is material;
- uncertainty exists about whether the remaining turn can complete with verification.

Prior timeout in the same project is a strong trigger: subsequent planning MUST reduce chunk size again rather than retrying the same workload shape.

## Atomic-chunk protocol
Each chunk MUST:
1. declare one bounded objective;
2. perform only the minimum tool calls needed for that objective;
3. complete or safely stop the atomic mutation;
4. read back/verify material writes;
5. persist checkpoint/Handoff when governed;
6. report what completed and the exact next chunk;
7. avoid redoing completed work after Retry/Continue unless verification is missing.

## Preemption
If a tool response becomes unexpectedly large, repeated conflicts occur, or a second large objective remains, stop after the current verified atomic unit and defer the rest to the next turn.

## Delivery-failure recovery
A UI delivery timeout is not proof that the underlying tool action failed. On Retry/Continue, first resolve the latest durable checkpoint / remote state, then resume from the first unverified action. Never blindly replay state-changing operations.

## Failure codes
- `TURN_SEGMENTATION_TOO_AGGRESSIVE`
- `RETRY_REPLAY_WITHOUT_STATE_RECONCILIATION`
- `TIMEOUT_RISK_NOT_PREEMPTED`

## Release tests
- prior timeout -> next plan has at least 2x chunking;
- multi-system + multiple writes -> approximately 3x conservative chunking;
- one atomic write + read-back completes in one chunk;
- timeout followed by Retry reconciles state before mutation replay;
- broad G0..G19 audit is split by bounded Skill/document batches, never one monolithic turn.
