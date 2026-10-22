#!/usr/bin/env python3
"""Decide whether new work may be admitted from a usage meter snapshot.

  python scripts/check_admission.py evidence/usage-latest.json [--threshold 85] [--max-age 600]

Exit 0 = ADMIT; exit 1 = STOP/BLOCK (reason printed). Only a fresh sample for
every active window below the threshold admits work; everything else blocks.
"""
import argparse
import json
import sys
import time


def decide(samples, now, threshold=85, max_age=600):
    if not isinstance(samples, list) or not samples:
        return False, "BLOCK: no samples (unknown usage blocks admission)"
    for s in samples:
        name = f"{s.get('provider', '?')}/{s.get('window_minutes', '?')}m"
        try:
            used = float(s["used_percent"])
            observed = float(s["observed_at"])
            resets = float(s["resets_at"])
        except (KeyError, TypeError, ValueError):
            return False, f"BLOCK: invalid sample for {name}"
        if not 0 <= used <= 100:
            return False, f"BLOCK: used_percent out of range for {name}"
        if observed > now:
            return False, f"BLOCK: future-dated sample for {name}"
        if now - observed > max_age:
            return False, f"BLOCK: stale sample for {name} ({int(now - observed)}s old)"
        if resets <= now:
            return False, f"BLOCK: expired window for {name}; take a fresh reading"
        if used >= threshold:
            return False, f"STOP: {name} at {used:g}% used (>= {threshold}%)"
    return True, f"ADMIT: all {len(samples)} active window(s) below {threshold}%"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--threshold", type=float, default=85)
    ap.add_argument("--max-age", type=float, default=600)
    a = ap.parse_args()
    try:
        samples = json.load(open(a.path))
    except (OSError, json.JSONDecodeError) as e:
        print(f"BLOCK: cannot read {a.path}: {e}")
        return 1
    ok, msg = decide(samples, time.time(), a.threshold, a.max_age)
    print(msg)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
