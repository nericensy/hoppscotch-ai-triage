#!/usr/bin/env python3
"""Measure the need for triage automation on hoppscotch/hoppscotch.

Step 1 (run once, needs gh CLI logged in):
  gh issue list -R hoppscotch/hoppscotch --state all --limit 1000 \
    --search "created:2026-07-01..2026-09-30" \
    --json number,createdAt,author,labels,comments,closedAt > data/metrics-issues.json
Step 2:
  python3 scripts/metrics.py data/metrics-issues.json > evals/metrics.txt

Response = first comment by someone other than the issue author and not a bot.
Labels applied by templates are excluded from "labelled by a human" counts only
approximately (gh does not expose who applied a label) - state this limitation.
"""
import json
import statistics
import sys
from datetime import datetime, timedelta

TEMPLATE_LABELS = {"bug", "feature"}
NOW = datetime.fromisoformat("2026-10-30T00:00:00+00:00")


def ts(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


issues = json.load(open(sys.argv[1], encoding="utf-8"))
hours, unanswered, untriaged, answered_7d = [], 0, 0, 0
for i in issues:
    author = (i.get("author") or {}).get("login")
    created = ts(i["createdAt"])
    replies = [c for c in i.get("comments", [])
               if (c.get("author") or {}).get("login") not in (author, None)
               and not (c.get("author") or {}).get("login", "").endswith("[bot]")]
    if replies:
        first = min(ts(c["createdAt"]) for c in replies)
        h = (first - created).total_seconds() / 3600
        hours.append(h)
        answered_7d += h <= 168
    else:
        unanswered += 1
    labels = {l["name"] for l in i.get("labels", [])}
    if not (labels - TEMPLATE_LABELS):
        untriaged += 1

n = len(issues)
print(f"Issues created in period: {n}")
print(f"No non-author response as of {NOW.date()}: {unanswered} ({unanswered/n:.0%})")
if hours:
    q = statistics.quantiles(hours, n=10)
    print(f"Median time to first response: {statistics.median(hours):.1f} h")
    print(f"P90 time to first response:    {q[-1]:.1f} h")
print(f"Answered within 7 days: {answered_7d} ({answered_7d/n:.0%})")
print(f"No label beyond template label: {untriaged} ({untriaged/n:.0%})")
