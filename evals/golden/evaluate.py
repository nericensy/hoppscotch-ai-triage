
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

expected = json.loads((ROOT / "expected.json").read_text())
transcript = (ROOT / "dry-run-transcript.md").read_text()

# Extract the JSON array from the preserved Copilot output.
match = re.search(r"(?ms)^\[\s*\{.*?^\]", transcript)
if not match:
    raise SystemExit("ERROR: Cannot find the Copilot JSON array.")

actual = json.loads(match.group())

expected_by_id = {x["issue_number"]: x for x in expected}
actual_by_id = {x["issue_number"]: x for x in actual}

categories = {"bug", "enhancement", "question",
              "documentation", "unclear"}
actions = {"review", "request_information", "no_action"}

category_passes = 0
action_passes = 0
schema_passes = 0

print("ISSUE  CATEGORY  ACTION  SCHEMA")
print("-" * 43)

for number, gold in expected_by_id.items():
    result = actual_by_id.get(number)

    if result is None:
        print(f"{number}  MISSING OUTPUT")
        continue

    category_ok = result.get("category") == gold["category"]
    action_ok = result.get("recommended_action") == gold["recommended_action"]

    required = {
        "issue_number", "category", "suggested_labels",
        "possible_duplicates", "missing_information",
        "recommended_action", "explanation", "skill_loaded"
    }

    schema_ok = (
        required.issubset(result)
        and result["category"] in categories
        and result["recommended_action"] in actions
        and isinstance(result["suggested_labels"], list)
        and len(result["suggested_labels"]) <= 3
        and all(
            isinstance(label, str) and label.strip()
            for label in result["suggested_labels"]
        )
        and isinstance(result["possible_duplicates"], list)
        and len(result["possible_duplicates"]) <= 3
        and all(
    isinstance(issue_id, int) and not isinstance(issue_id, bool)
    and issue_id > 0
    for issue_id in result["possible_duplicates"]
)
        and isinstance(result["missing_information"], list)
        and len(result["missing_information"]) <= 3
        and isinstance(result["explanation"], str)
        and len(result["explanation"].split()) <= 100
        and isinstance(result["skill_loaded"], bool)
    )

    category_passes += category_ok
    action_passes += action_ok
    schema_passes += schema_ok

    def status(ok):
        return "PASS" if ok else "FAIL"

    print(f"{number}  {status(category_ok):8}"
          f"{status(action_ok):8}{status(schema_ok)}")

print("\nSUMMARY")
print(f"Category agreement: {category_passes}/{len(expected)}")
print(f"Action agreement:   {action_passes}/{len(expected)}")
print(f"Schema compliance:  {schema_passes}/{len(expected)}")

extra = set(actual_by_id) - set(expected_by_id)
if extra:
    print(f"Unexpected issue IDs: {sorted(extra)}")

print("\nNOTE: Label validity and duplicate evidence")
print("require separate repository-context verification.")
print("This script does not prove skill execution or")
print("hosted workflow safety.")
