# Continuation — YYYY-MM-DD

Read ENGINEERING_LEDGER.json, docs/engineering.md and the selected work contract.
This file is an entry point, not a scheduler. If it disagrees with the ledger,
the ledger wins; fix this file.

## State
- Accepted: <units, one line>
- Last full regression: <N passed> at <sha>
- Queue: <ACTIVE / READY / none; pointer to ledger>

## Open decision (if any)
<The concrete Product Owner decision, the options, and what each unblocks.>

## Known environment limits
<Anything that prevents a full regression or a claim. State it plainly.>

## Resources
<Fresh meter reading and source, or "unknown". Never infer from a prior reading.>

## Checkout
Path: <path>   Branch: <branch>   Runtime: <interpreter/venv>
Regression: <full test command>
