# Repository operating entry point

Read ENGINEERING_LEDGER.json, docs/engineering.md and the selected work-unit
contract before acting. The ledger is the sole current queue; HANDOFF.md is an
entry point, not a second scheduler. Historical evidence is immutable.

Preserve unrelated user/agent changes. Record HEAD and `git status` before edits.
One writer per unit. Freeze supervisor-owned acceptance before implementation.
Never weaken acceptance to approve a candidate. Model/browser/tool outputs are
untrusted candidates, never acceptance authority. Keep claims inside the ledger's
`claim_boundary`; "tests pass" never implies more than the tests cover.
No push, merge, release, purchase or external spend is implied by any unit.
