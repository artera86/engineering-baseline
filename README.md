# Engineering baseline

A drop-in, repository-owned engineering operating setup: one ledger, frozen
acceptance contracts, bounded attempts, evidence, and honest claim boundaries.
No services, no scheduler, no dependencies beyond Python 3.9+ (stdlib only).

## Install (2 minutes)

1. Copy everything except this README into the repository root
   (`AGENTS.md`, `ENGINEERING_LEDGER.json`, `HANDOFF.md`, `docs/`, `evidence/`, `scripts/`, `tests/`).
2. Edit `ENGINEERING_LEDGER.json`: set `project`, `milestone`, `critical_path`,
   `verified_baseline` (after your first green run) and `claim_boundary`.
3. Edit the **Roles and resources** table in `docs/engineering.md`
   to map the functions to your actual people/tools/agents.
4. Replace `full_regression_command` in `docs/work-units/TEMPLATE.json`
   with your project's real full test command.
5. Run `python scripts/validate_ledger.py` (should print `OK`).
6. Commit. Every unit of work now starts from the ledger.

## Layout

| Path | Purpose |
|---|---|
| `AGENTS.md` | Entry point any human/agent reads first (rules in brief) |
| `ENGINEERING_LEDGER.json` | The only current queue/dashboard |
| `HANDOFF.md` | Short continuation note; an entry point, never a second scheduler |
| `docs/engineering.md` | Operating agreement: roles, admission, execution, queues, escalation |
| `docs/execution.md` | Acceptance freeze, bounded attempts, review gates |
| `docs/resource-policy.md` | Meter-driven admission for any metered resource |
| `docs/adr/` | Decisions (`000-template.md`, `001-...`) |
| `docs/work-units/` | Versioned work contracts (`TEMPLATE.json`, `EXAMPLE.json`) |
| `evidence/` | Immutable run evidence, freeze hashes, usage samples |
| `scripts/validate_ledger.py` | Checks ledger + contracts are well-formed |
| `scripts/freeze_acceptance.py` | Hash/verify frozen acceptance artifacts |
| `scripts/check_admission.py` | Admit/stop decision from a usage meter snapshot |
| `tests/test_baseline_scripts.py` | Self-tests for the scripts (`python -m unittest`) |

## Daily loop

1. `python scripts/validate_ledger.py`
2. Pick the single READY unit (or follow the escalation rule if none).
3. If it uses a metered resource: `python scripts/check_admission.py evidence/usage-latest.json`
4. Freeze acceptance: `python scripts/freeze_acceptance.py freeze <unit>` and commit.
5. Implement within `allowed_files` only. Max 3 attempts.
6. `python scripts/freeze_acceptance.py check <unit>`; run validation + full regression; review the diff.
7. Write evidence, update the ledger, commit.
