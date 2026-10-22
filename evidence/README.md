# Evidence

Immutable. Add new files; never edit or delete historical evidence. A correction
is a new, dated file that says what it supersedes.

Per unit: `evidence/<id>/freeze.json` (acceptance hashes), `review.json`
(outcome), `regression.txt` (full test output), plus any failed-run fixtures.
Resource readings: `usage-latest.json` (current) and dated `usage-*.json`.
Never store credentials, tokens or personal/regulated data here.
