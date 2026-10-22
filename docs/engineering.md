# Lightweight engineering operating agreement

ENGINEERING_LEDGER.json is the only current dashboard. Detailed contracts live in
docs/work-units/; decisions in docs/adr/; immutable run evidence in evidence/.
Git records history. No new scheduler, service or multi-agent platform is needed.

## Roles and resources (edit this table for your project)

| Function | Resource | Responsibility |
|---|---|---|
| Product Owner | <person> | Direction, money, consequential tradeoffs |
| Supervisor | <person or lead agent> | Critical path, scope, integration, checkpointing |
| Implementer | <person or agent> | Routine implementation, debugging, repository work |
| Specialist bench | <optional external tools/models> | Bounded research, review, candidate artifacts |
| Acceptance authority | Deterministic tests, validators, CI | Decide acceptance against independently controlled criteria |
| Archivist | Git + ADRs + evidence | Preserve provenance, failures and decisions |

One person may hold several functions; the rule is that the **implementer never
controls the acceptance criteria for the unit they implement**.

## Admission and execution

1. Read the ledger, inspect HEAD/status and resource availability. One writer owns
   an ACTIVE unit. READY means scoped and dependency-ready, not yet admitted.
2. Supervisor freezes a contract from TEMPLATE.json. Commit acceptance artifacts
   before implementation; record their hashes (`scripts/freeze_acceptance.py`)
   outside the implementer's allowlist. If acceptance is absent, the first step is
   acceptance preparation, not coding.
3. Deterministic tools first. Route routine work to the implementer, bounded
   specialist tasks to the bench only when useful, integration/review to the
   supervisor. A specialist request states scope, input provenance, output format
   and stop limit; capture source/provider/time and candidate hash; verify claims
   independently. No secrets or personal/regulated data in external packets.
   Never execute unreviewed code.
4. Maximum three attempts per unit. Never reset identity to conceal exhausted
   attempts. Preserve failed runs. Test-green output is provisional: inspect
   tracked and untracked mutations, acceptance hashes, relevant tests and the
   full regression before marking PASSED.
5. Acceptance comes from tests/validators and reviewed evidence, never model
   self-report. A justified contract change needs supervisor review and a new
   version, retaining the failures that prompted it.
6. Update the ledger sequentially after review. Evidence names the exact tested
   baseline plus diff/tree identity; checkpoint only owned files. Never absorb
   concurrent edits.

## Queues and authority

- ACTIVE: admitted unit with one owner.
- READY: concrete next unit, dependencies satisfied.
- BLOCKED: true dependency on the critical path; needs `owner` and `unblock_condition`.
- DEFERRED: valid noncritical work; needs `reason` and `reopen_when`.

Completed work belongs in evidence/history, not an ever-growing dashboard.
A resource-admission failure pauses admission; it does not turn unrelated work
into a critical dependency.

## Claims

The ledger's `claim_boundary` states what is established and what is not.
Narrow, honest claims beat broad ones: "zero observed errors in run X" is not
"conformant"; "hashes match" is not "authentic"; "scenario passes" is not
"works in production". Add a limitation the moment you discover one.

## Escalation

Escalate only for: irreversible or costly actions, credentials or user-only
information, meaningful product forks, or exhausted attempts that need changed
scope. First preserve evidence and name the concrete decision required (options
and consequences). Reversible setup and routine engineering decisions stay with
the supervisor. When the next step is a product fork, record it as DEFERRED with
`reason: MEANINGFUL_PRODUCT_FORK` and a `reopen_when` that names the decision.

## Failure assets

Every meaningful failure leaves a durable asset: a regression test/scenario for a
reproducible defect, an evidence fixture for an observation, a runbook for
recovery, an ADR for a tradeoff, or an explicit limitation if unresolved. Link it
in the run evidence. Retrying until green never erases a failed run.
