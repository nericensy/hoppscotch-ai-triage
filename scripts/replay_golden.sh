#!/usr/bin/env bash
# Replay each golden input as a NEW issue in the sandbox so the workflow fires on issues:opened.
# Usage: bash scripts/replay_golden.sh nericensy/hoppscotch-ai-triage
set -euo pipefail
REPO="$1"
mkdir -p evals/golden/runs
for f in evals/golden/inputs/*.json; do
  id=$(basename "$f" .json)
  title=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['title'])" "$f")
  python3 -c "import json,sys;d=json.load(open(sys.argv[1]));print(d['body']);print();print('<!-- golden-cutoff: %s -->' % d.get('createdAt','9999'))" "$f" > /tmp/body.md
  url=$(gh issue create -R "$REPO" --title "$title" --body-file /tmp/body.md)
  echo "$id $url" | tee -a evals/golden/runs/issue-map.txt
  sleep 90   # concurrency group runs one at a time; spacing keeps logs separate
done
