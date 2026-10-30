#!/usr/bin/env bash
# After runs finish: save each run's log and the agent's comment/labels per golden case.
# Usage: bash scripts/collect_results.sh nericensy/hoppscotch-ai-triage
set -euo pipefail
REPO="$1"
mkdir -p evals/golden/actual evals/golden/logs
gh run list -R "$REPO" --workflow issue-triage.lock.yml --limit 50 \
  --json databaseId,createdAt,conclusion,event > evals/golden/logs/runs.json
for id in $(jq -r '.[].databaseId' evals/golden/logs/runs.json); do
  gh run view "$id" -R "$REPO" --log > "evals/golden/logs/run-$id.log" || true
done
while read -r case url; do
  num=${url##*/}
  gh issue view "$num" -R "$REPO" --json number,labels,comments \
    > "evals/golden/actual/$case.json"
done < evals/golden/runs/issue-map.txt
