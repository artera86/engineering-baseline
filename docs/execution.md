# Execution contract

Each unit has a fixed allowlist, acceptance criteria and validation command,
declared in docs/work-units/<id>.json.

## Before implementation
- Acceptance artifacts (tests, fixtures, validators) are written and committed
  first, and are NOT in the implementer's `allowed_files`.
- `python scripts/freeze_acceptance.py freeze <id>` records SHA-256 hashes in
  `evidence/<id>/freeze.json`. Commit that file.
- Record `baseline_sha` (HEAD) and `git status` in the evidence directory.

## During implementation
- Edit only `allowed_files`. Anything else is a scope change (see Escalation).
- Attempt limit is 3. Each attempt is recorded; failed attempts are kept.

## Before marking PASSED
1. `python scripts/freeze_acceptance.py check <id>` — acceptance unchanged.
2. Run `approved_validation_command`, then `full_regression_command`.
3. Inspect actual tracked **and untracked** mutations against `allowed_files`.
4. Review the diff by reading it; test-green is provisional until this is done.
5. Write `evidence/<id>/review.json` (status, baseline sha, attempts, acceptance
   and runtime hashes, test counts, limits, scope). If the full regression cannot
   run, status is `ACCEPTED_WITH_ENVIRONMENT_LIMIT` and the limit is recorded
   verbatim, never papered over.

## Isolation honesty
State what your sandbox actually isolates. Environment stripping and monkeypatched
sockets are not an OS sandbox. Run only trusted local code in a checkout without
credentials; hostile or generated-and-unreviewed code needs real OS-level
isolation before it is executed. Do not describe weaker controls as isolation.

## Provider/API honesty
No fabricated calls, budgets or failover claims. A gate that needs real external
evidence stays closed until real evidence exists.
