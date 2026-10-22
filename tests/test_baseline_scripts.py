import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def run(script, *args):
    return subprocess.run([sys.executable, str(ROOT / "scripts" / script), *args],
                          capture_output=True, text=True)


class Admission(unittest.TestCase):
    NOW = 1_000_000

    def s(self, **kw):
        base = {"provider": "p", "window_minutes": 60, "used_percent": 50,
                "observed_at": self.NOW - 10, "resets_at": self.NOW + 1000, "source": "t"}
        base.update(kw)
        return [base]

    def test_admit_below_threshold(self):
        self.assertTrue(load("check_admission").decide(self.s(), self.NOW)[0])

    def test_stop_at_threshold(self):
        self.assertFalse(load("check_admission").decide(self.s(used_percent=85), self.NOW)[0])

    def test_block_unknown_stale_expired_future_invalid(self):
        d = load("check_admission").decide
        self.assertFalse(d([], self.NOW)[0])
        self.assertFalse(d(self.s(observed_at=self.NOW - 601), self.NOW)[0])
        self.assertFalse(d(self.s(resets_at=self.NOW - 1), self.NOW)[0])
        self.assertFalse(d(self.s(observed_at=self.NOW + 5), self.NOW)[0])
        self.assertFalse(d([{"provider": "p"}], self.NOW)[0])

    def test_every_window_must_pass(self):
        two = self.s() + self.s(used_percent=90)
        self.assertFalse(load("check_admission").decide(two, self.NOW)[0])


class LedgerAndFreeze(unittest.TestCase):
    def make_repo(self):
        d = Path(tempfile.mkdtemp())
        (d / "docs" / "work-units").mkdir(parents=True)
        led = json.loads((ROOT / "ENGINEERING_LEDGER.json").read_text())
        (d / "ENGINEERING_LEDGER.json").write_text(json.dumps(led))
        return d, led

    def test_shipped_baseline_validates(self):
        r = run("validate_ledger.py", str(ROOT))
        self.assertEqual(r.returncode, 0, r.stdout)

    def test_ready_unit_needs_acceptance_and_valid_contract(self):
        d, led = self.make_repo()
        led["queues"]["READY"] = [{"id": "U1"}]
        (d / "ENGINEERING_LEDGER.json").write_text(json.dumps(led))
        c = json.loads((ROOT / "docs/work-units/TEMPLATE.json").read_text())
        c["id"] = "U1"
        (d / "docs/work-units/U1.json").write_text(json.dumps(c))
        r = run("validate_ledger.py", str(d))
        self.assertEqual(r.returncode, 1)
        self.assertIn("acceptance_artifacts", r.stdout)

    def test_deferred_needs_reopen_condition(self):
        d, led = self.make_repo()
        led["queues"]["DEFERRED"] = [{"id": "X", "reason": "r"}]
        (d / "ENGINEERING_LEDGER.json").write_text(json.dumps(led))
        r = run("validate_ledger.py", str(d))
        self.assertEqual(r.returncode, 1)
        self.assertIn("reopen_when", r.stdout)

    def test_acceptance_inside_allowlist_rejected(self):
        d, led = self.make_repo()
        led["queues"]["READY"] = [{"id": "U2"}]
        (d / "ENGINEERING_LEDGER.json").write_text(json.dumps(led))
        c = json.loads((ROOT / "docs/work-units/EXAMPLE.json").read_text())
        c["id"] = "U2"
        c["allowed_files"].append(c["acceptance_artifacts"][0])
        (d / "docs/work-units/U2.json").write_text(json.dumps(c))
        r = run("validate_ledger.py", str(d))
        self.assertIn("inside allowed_files", r.stdout)

    def test_freeze_detects_tampering_and_refuses_overwrite(self):
        d, _ = self.make_repo()
        c = json.loads((ROOT / "docs/work-units/EXAMPLE.json").read_text())
        c["id"] = "U3"
        (d / "docs/work-units/U3.json").write_text(json.dumps(c))
        (d / "acceptance").mkdir()
        t = d / "acceptance/test_durations.py"
        t.write_text("assert True\n")
        self.assertEqual(run("freeze_acceptance.py", "freeze", "U3", str(d)).returncode, 0)
        self.assertEqual(run("freeze_acceptance.py", "check", "U3", str(d)).returncode, 0)
        self.assertEqual(run("freeze_acceptance.py", "freeze", "U3", str(d)).returncode, 1)
        t.write_text("assert False\n")
        r = run("freeze_acceptance.py", "check", "U3", str(d))
        self.assertEqual(r.returncode, 1)
        self.assertIn("changed", r.stdout)


if __name__ == "__main__":
    unittest.main()
