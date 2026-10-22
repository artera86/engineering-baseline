#!/usr/bin/env python3
"""Validate ENGINEERING_LEDGER.json and the work-unit contracts it references.

Usage: python scripts/validate_ledger.py [repo_root]
Exit 0 = OK, 1 = problems (printed one per line).
"""
import json
import sys
from pathlib import Path

LEDGER_KEYS = ["schema_version", "project", "updated_date", "milestone", "critical_path",
               "verified_baseline", "queues", "known_limitations", "claim_boundary",
               "resource_policy", "next_checkpoint", "operating_agreement", "last_completed"]
QUEUE_REQUIRED = {
    "ACTIVE": ["id", "owner"],
    "READY": ["id"],
    "BLOCKED": ["id", "owner", "unblock_condition"],
    "DEFERRED": ["id", "reason", "reopen_when"],
}
CONTRACT_KEYS = ["id", "goal", "owner", "baseline_sha", "allowed_files", "acceptance_owner",
                 "acceptance_artifacts", "acceptance_criteria", "approved_validation_command",
                 "full_regression_command", "attempt_limit", "evidence_output",
                 "escalation_conditions", "failure_asset", "freeze"]


def load(path, problems):
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        problems.append(f"missing file: {path}")
    except json.JSONDecodeError as e:
        problems.append(f"invalid JSON in {path}: {e}")
    return None


def check_contract(root, unit_id, state, problems):
    path = root / "docs" / "work-units" / f"{unit_id}.json"
    c = load(path, problems)
    if c is None:
        return
    for k in CONTRACT_KEYS:
        if k not in c:
            problems.append(f"{path.name}: missing field '{k}'")
    if c.get("id") != unit_id:
        problems.append(f"{path.name}: id '{c.get('id')}' does not match filename")
    if isinstance(c.get("attempt_limit"), int) and not 1 <= c["attempt_limit"] <= 3:
        problems.append(f"{path.name}: attempt_limit must be 1..3")
    overlap = set(c.get("allowed_files", [])) & set(c.get("acceptance_artifacts", []))
    if overlap:
        problems.append(f"{path.name}: acceptance artifacts inside allowed_files: {sorted(overlap)}")
    if state in ("ACTIVE", "READY"):
        if not c.get("acceptance_artifacts"):
            problems.append(f"{path.name}: {state} unit has no acceptance_artifacts (do acceptance preparation first)")
        if not c.get("approved_validation_command"):
            problems.append(f"{path.name}: {state} unit has no approved_validation_command")
        if "REPLACE" in c.get("full_regression_command", []):
            problems.append(f"{path.name}: full_regression_command still says REPLACE")


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    problems = []
    ledger = load(root / "ENGINEERING_LEDGER.json", problems)
    if ledger is not None:
        for k in LEDGER_KEYS:
            if k not in ledger:
                problems.append(f"ledger: missing key '{k}'")
        queues = ledger.get("queues", {})
        seen = {}
        for name, required in QUEUE_REQUIRED.items():
            if name not in queues:
                problems.append(f"ledger: missing queue '{name}'")
                continue
            for item in queues[name]:
                for k in required:
                    if not item.get(k):
                        problems.append(f"ledger: {name} item {item.get('id', '?')} missing '{k}'")
                uid = item.get("id")
                if uid in seen:
                    problems.append(f"ledger: '{uid}' appears in both {seen[uid]} and {name}")
                seen[uid] = name
                if name in ("ACTIVE", "READY") and uid:
                    check_contract(root, uid, name, problems)
        owners = [i.get("owner") for i in queues.get("ACTIVE", []) if i.get("owner")]
        if len(owners) != len(set(owners)):
            problems.append("ledger: one owner is writing more than one ACTIVE unit")
    if problems:
        print("\n".join(problems))
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
