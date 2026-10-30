#!/usr/bin/env python3
"""Deterministic label check: no model judgement needed.

Usage: python3 validate_labels.py "bug" "need testing"
Prints JSON {"valid": [...], "rejected": [...]} and exits 1 if any label is rejected.
"""
import json
import sys
from pathlib import Path

ALLOWED_FILE = Path(__file__).with_name("allowed-labels.txt")


def load_allowed():
    lines = ALLOWED_FILE.read_text(encoding="utf-8").splitlines()
    return {l.strip() for l in lines if l.strip() and not l.startswith("#")}


def main(argv):
    allowed = load_allowed()
    proposed = [a.strip() for a in argv if a.strip()]
    valid = [l for l in proposed if l in allowed]
    rejected = [l for l in proposed if l not in allowed]
    if len(valid) > 3:
        rejected += valid[3:]
        valid = valid[:3]
    print(json.dumps({"valid": valid, "rejected": rejected, "allowed": sorted(allowed)}))
    return 1 if rejected else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
