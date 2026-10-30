#!/usr/bin/env python3
"""Remove information that did not exist when each issue was opened.

Usage: python3 scripts/strip_future_info.py evals/golden/inputs/*.json
Rewrites each file in place, keeping only: number, title, body, createdAt, url,
and comments created before (createdAt + 0s) i.e. none. State, closedAt and
current labels are dropped because they reflect later maintainer actions.
Labels applied automatically by the issue template at creation can be kept by
listing them in TEMPLATE_LABELS.
"""
import json
import sys
from pathlib import Path

KEEP = ["number", "title", "body", "createdAt", "url"]
TEMPLATE_LABELS = {"bug", "feature"}  # added by hoppscotch issue forms at creation

for path in map(Path, sys.argv[1:]):
    data = json.loads(path.read_text(encoding="utf-8"))
    clean = {k: data[k] for k in KEEP if k in data}
    labels = [l if isinstance(l, str) else l.get("name") for l in data.get("labels", [])]
    clean["labels_at_creation"] = [l for l in labels if l in TEMPLATE_LABELS]
    clean["state"] = "OPEN"
    clean["comments"] = []
    path.write_text(json.dumps(clean, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"cleaned {path}")
