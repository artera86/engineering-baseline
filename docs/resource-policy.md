# Resource policy: meter-driven admission

Applies to any metered resource (agent subscription windows, API quotas, CI
minutes, paid compute). Plans, windows, models and reset credits are account
state, not project configuration; never hard-code a cadence.

## Rule
Admit a new unit only when a **fresh** measurement shows every active window
below the threshold (default **85% used**). Block on missing, invalid, stale
(default >600 s old), expired (`resets_at` in the past) or future-dated samples.
In-flight work may finish and checkpoint; do not start the next unit after
crossing. This is an admission threshold, not a hard cap on spend.

## Sample format (`evidence/usage-latest.json`)
```json
[{"provider": "name", "window_minutes": 43200, "used_percent": 67,
  "observed_at": 1791560976, "resets_at": 1794152340, "source": "tool-or-endpoint"}]
```
Timestamps are Unix seconds. Persist no account identifiers or credentials.

## Check
`python scripts/check_admission.py evidence/usage-latest.json`
Exit 0 = ADMIT, exit 1 = STOP/BLOCK (reason printed).

## Separate budgets
Each resource has its own meter and domain. Never borrow one resource's headroom
to justify spending another, and never infer a paid API budget from a
subscription meter. Unknown capacity is recorded as `unknown`, work stays bounded.

## Plan changes
A plan or window change requires a new dated evidence file and a ledger update
before the next admission. Do not rewrite historical readings.
