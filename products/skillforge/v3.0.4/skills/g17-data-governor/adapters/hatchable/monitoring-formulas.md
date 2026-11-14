# Hatchable Adapter Monitoring and Formula Baseline

Status: evidence-backed baseline from HATCH-USAGE-FORMULA derivative report dated 2026-09-15.

## Validated formulas

### AES-256-GCM envelope
- ciphertext_bytes = plaintext_bytes + 16
- iv_bytes = 12
- raw_crypto_envelope_overhead = 28 bytes
- excludes PostgreSQL row/page/index/storage-meter overhead.

Evidence:
- 36 B -> 52 B ciphertext in memory.
- DB read-back: 41 B -> 57 B and 73 B -> 89 B.
- wrong-key rejection and tamper detection passed.

## UNKNOWN formulas — remain UNKNOWN
No causal equation is accepted yet for:
- database time;
- storage quota accounting;
- function CPU/runtime;
- browser-facing bandwidth;
- outbound API;
- connection cost;
- transaction cost.

Reason:
- dashboard counters are account/all-project scoped;
- concurrent unrelated deployments/requests contaminated deltas;
- direct plugin does not expose equivalent cumulative/historical counters;
- the controlled probe was intentionally stopped rather than invent a formula.

## Monitoring rule
Every metric is labeled one of:
- MEASURED
- VALIDATED_ESTIMATE
- UNKNOWN / UNAVAILABLE

Do not infer a per-project/provider formula from account-wide deltas.

## 80% guardrail
Use authoritative current provider counters where available. Where direct plugin parity is absent, browser/UI observation or a future provider API may supply the source. An estimate may drive an alert only after its formula is versioned and validated.

## Reopen gate
Before Hatchable adapter build freeze, reload the newest formula study and reconcile each metric, formula, unit, reset window, confidence and source.
