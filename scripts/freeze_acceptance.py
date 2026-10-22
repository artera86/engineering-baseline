#!/usr/bin/env python3
"""Freeze and verify acceptance artifacts for a work unit.

  python scripts/freeze_acceptance.py freeze <unit> [repo_root]
  python scripts/freeze_acceptance.py check  <unit> [repo_root]

freeze: hashes every file in the contract's acceptance_artifacts (plus the
        contract itself) into evidence/<unit>/freeze.json. Refuses to overwrite.
check:  recomputes the hashes; exit 1 on any change or missing file.
"""
import hashlib
import json
import sys
from pathlib import Path


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("freeze", "check"):
        print(__doc__)
        return 2
    mode, unit = sys.argv[1], sys.argv[2]
    root = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(".")
    contract_path = root / "docs" / "work-units" / f"{unit}.json"
    contract = json.loads(contract_path.read_text())
    files = [str(contract_path.relative_to(root))] + list(contract.get("acceptance_artifacts", []))
    freeze_path = root / "evidence" / unit / "freeze.json"

    if mode == "freeze":
        if freeze_path.exists():
            print(f"refusing to overwrite {freeze_path}; supersede with a new contract version instead")
            return 1
        hashes = {}
        for f in files:
            p = root / f
            if not p.is_file():
                print(f"missing acceptance artifact: {f}")
                return 1
            hashes[f] = sha256(p)
        freeze_path.parent.mkdir(parents=True, exist_ok=True)
        freeze_path.write_text(json.dumps({"unit": unit, "sha256": hashes}, indent=2) + "\n")
        print(f"froze {len(hashes)} file(s) -> {freeze_path}")
        return 0

    if not freeze_path.is_file():
        print(f"no freeze record at {freeze_path}")
        return 1
    recorded = json.loads(freeze_path.read_text())["sha256"]
    bad = []
    for f, h in recorded.items():
        p = root / f
        if not p.is_file():
            bad.append(f"missing: {f}")
        elif sha256(p) != h:
            bad.append(f"changed: {f}")
    if bad:
        print("\n".join(bad))
        return 1
    print("OK: acceptance unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
