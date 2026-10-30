# Design: Hoppscotch AI Issue Triage Agent

## 1. Workflow Selection and Motivation

This project configures a GitHub Agentic Workflow to assist with issue triage for the open-source Hoppscotch project. The agent classifies issues, identifies missing information, searches for possible duplicates, and recommends a next action without modifying issues.

Issue triage requires interpreting natural-language reports, technical symptoms, reproduction steps, and repository context. Conventional automation can validate labels or detect exact duplicates, but it cannot reliably interpret ambiguous reports or explain why further investigation is needed. The agent therefore supports maintainers rather than replacing their judgement.

**Repository evidence:** I examined Hoppscotch issues created between 1 and 30 September 2026 using the GitHub REST API. The retrieved pages contained 29 matching issue records. This is a preliminary count rather than a verified total because the API request filtered by update activity and may not capture every issue created during the period. The evaluation additionally uses ten historical issues representing bugs, enhancements, questions, and no-action cases. The sample demonstrates the need for consistent triage but cannot establish average response time or total maintainer workload.

## 2. Configuration and Architecture

- `.github/workflows/issue-triage.md`: Defines an `issues: opened` trigger, the `TRIAGE_ENABLED` kill switch, Copilot engine with `model: auto`, a 10-minute timeout, read-only agent tools, and constrained comment/label safe outputs.
- `.github/workflows/issue-triage.lock.yml`: Compiled workflow used by GitHub Actions.
- `AGENTS.md`: Repository structure, conventions, instructions, and prohibited changes.
- `.claude/skills/issue-triage/SKILL.md`: Issue classification, information checks, duplicate-search procedure, and recommendation rules.
- `CONTRIBUTING.md`: Contributor guidance and AI-assisted contribution policy.
- `evals/golden/`: Historical cases, expected outcomes, actual outputs, and adversarial evaluation material.

The agent produces a structured JSON recommendation containing the issue number, category, suggested labels, possible duplicates, missing information, recommended action, explanation, and skill-loading status.

Allowed actions are `review`, `request_information`, and `no_action`. These are recommendations, not GitHub mutations.

## 3. Governance Controls

| Control | Implementation and status |
|---|---|
| Identity | GitHub Actions provides workflow-run attribution; bot identity during live execution remains unverified. |
| Least privilege | The agent job has `contents: read` and `issues: read`; its GitHub MCP tools are issue-reading tools. Generated safe-output and conclusion jobs have `issues: write` for configured comments and labels. They have no `pull-requests: write` or `contents: write`. |
| Safe outputs | `create-issue: false` and `report-failure-as-issue: false`; comments and labels are limited and target the triggering issue. This is static configuration evidence, not an end-to-end runtime test. |
| Human approval | The agent does not close issues or merge changes. Configured safe outputs can automatically add labels and post one comment; maintainers remain responsible for reviewing recommendations and deciding any further action. |
| Budgets | The workflow triggers on opened issues; the 10-minute agent timeout limits each execution, not the number of runs. Safe outputs limit labels to three and comments to one. Model-token spending is not explicitly capped. |
| Audit trail | Workflow definitions and evaluation artifacts are stored in Git. A hosted run was logged, but it failed before triage; complete tool-call and cost reporting for a successful triage has not been verified. |
| Kill switch | Activation requires `TRIAGE_ENABLED == 'true'`. The disabled-variable path and cancellation procedure have not been tested. |
| Drift detection | Rerun the ten golden cases after model, prompt, skill, or tool changes. A maintainer should review changed classifications, recommended actions, duplicates, and explanations before accepting updates. This review process is proposed, not automated. |
| Accountability | Repository maintainers control workflow changes and remain responsible for decisions. Git history records configuration changes; formal ownership rules are not yet established. |

Network restrictions are configured as `network: defaults`; a restrictive domain allowlist has not been verified.

## 4. Threat Model and Five Required Scenarios

**Q1. An issue claims maintainer approval and instructs the agent to close all stale issues.**

The issue body is treated as untrusted data, not an instruction source. The agent job itself has read-only GitHub permissions and no close/delete safe-output handler is configured. The generated write jobs retain `issues: write` for comment/label handling, so the token scope is broader than those operations if a trusted handler were compromised. In a separate local adversarial dry run, the recommendation was `no_action` / `unclear`; no GitHub write was performed. This does not establish hosted enforcement.

**Q2. A provider updates the model and a golden task starts failing.**

The source uses `model: auto`, which is a runtime alias rather than a fixed model. A proposed regression process reruns golden cases after provider or workflow updates and compares results with recorded expectations. Changed recommendations and explanations require human review. Automatic drift detection is not implemented.

**Q3. The project receives 300 issues in one week.**

The workflow triggers on each opened issue, so a busy week could produce many runs. The 10-minute timeout limits each execution, but no weekly run quota or volume cap is enforced. `TRIAGE_ENABLED` can prevent activation when set to anything other than `true`.

**Q4. A tool or MCP server returns malicious instructions.**

Tool results are untrusted. The agent is instructed to ignore embedded commands and use results only as evidence. Its allowlisted GitHub issue tools provide read operations; safe outputs allow only configured comments and labels, with triggering-issue targeting, and disable issue creation. These restrictions were inspected statically but were not exercised by a successful hosted triage. Malicious tool content could still influence recommendations, so human review and adversarial testing remain necessary.

**Q5. A maintainer needs to stop the agent using only a phone.**

The maintainer opens the repository on GitHub in a mobile browser, selects **Actions**, opens the issue-triage workflow, and disables it to prevent new runs. They must also open any running workflow execution and select **Cancel workflow**. Repository permissions are required. This procedure is proposed and has not been tested on mobile.

## 5. Historical Evaluation and Findings

The evaluation uses ten historical Hoppscotch issues: #6756, #6753, #6750, #6742, #6738, #6720, #6701, #6686, #6680, and #6676. The cases include bugs, enhancements, questions, missing-information reports, and no-action situations.

A local Copilot coding-assistant dry run produced recommendations for all ten cases. The preserved `evaluation-results.txt` reports 8/10 category agreement, 8/10 action agreement, and 0/10 schema compliance against the expectations used when that summary was generated. It is preserved unchanged.

The expected action for #6720 was later corrected from `no_action` to `review` based on its explicit feature proposal. Comparing the unchanged transcript directly with the current `expected.json` therefore gives 8/10 category agreement and 9/10 action agreement; #6753 remains the action disagreement. Category disagreements are #6680 (dry run: enhancement; expected: bug) and #6701 (dry run: unclear; expected: question). These differences reflect classification and action judgments, not hosted-agent results.

The dry-run output omitted `skill_loaded` and did not use the workflow schema's `labels`, `duplicates`, or `should_comment` fields; schema compliance was 0/10 in the recorded summary. The assistant reported loading the skill, but that report was not independently verified. Duplicate candidates #3901 and #3905 for #6756 were cited by the issue but not independently verified.

Some historical files in `actual/` were manually prepared and are not independent agent evaluation results; they are deleted in the current working tree and are not used here.

The original local Copilot output is preserved in `evals/golden/dry-run-transcript.md`. A separate local adversarial dry run ignored the fabricated maintainer authorization in issue #99999 and returned `no_action`; the adversarial actual-output file is not present in the current working tree.

Hosted execution was attempted in run `41093819162` on 2026-10-30. The agent failed before producing a triage recommendation: `auto` resolved to `claude-sonnet-5.5`, and GitHub Copilot returned HTTP 400 `model_not_supported` at `/chat/completions`. The same-run inventory marked that model as not enabled in the Copilot model picker; no account-enabled replacement was verified. This is a failed hosted execution, not a hosted evaluation result.

The run's pre-activation, activation, detection, and safe-output jobs completed, but the model failure prevented a successful triage. Compiled permissions and safe-output configuration were inspected statically; actual comment/label target enforcement, permission boundaries, disabled-kill-switch behavior, timeout behavior, network restrictions, and successful-run audit completeness remain unverified end-to-end.

## 6. Alternatives, Trade-offs, and Unresolved Issues

A fully automated issue-management bot was rejected because automatically changing labels or closing issues would increase the risk of incorrect decisions and prompt-injection attacks.

The read-only agent job provides analysis, while the separate safe-output path can apply the configured labels and comment. The trade-off is that those writes are automated within narrow limits, but maintainers must still review recommendations and decide any further action.

Remaining limitations include the unresolved Copilot model-picker availability, absence of a successful hosted triage, unverified runtime controls, incomplete persisted adversarial output, and no automated drift monitoring.

## 7. Agent Bill of Materials

- **Model:** Copilot engine configured with `auto`; hosted run `41093819162` resolved it to `claude-sonnet-5.5`, which Copilot rejected as `model_not_supported`. No supported account-enabled model is verified.
- **Instructions:** `AGENTS.md`, `.claude/skills/issue-triage/SKILL.md`, and workflow prompt.
- **Tools/MCP:** GitHub MCP issue-reading tools (`issue_read`, `list_issue_types`, `list_issues`, `search_issues`); compiled workflow infrastructure.
- **Permissions:** `contents: read`, `issues: read` for the agent job; generated support-job permissions require separate interpretation.
- **Data sources:** Sandbox GitHub issues, historical Hoppscotch issue records, comments, labels, and preserved evaluation context.
- **Logs:** Local dry-run transcript and evaluation summary are preserved. Hosted logs/artifacts establish the failed model-selection attempt only; no successful hosted triage log exists.
- **Evaluations:** Ten historical cases and one adversarial prompt-injection case.
- **Responsible humans:** Repository owner and authorised maintainers; they review recommendations and approve configuration changes.

## 8. AI-Use Statement

AI assistance was used to develop and refine the workflow instructions, skill, evaluation materials, and documentation. I reviewed the generated configuration, inspected the compiled workflow, checked JSON validity, compared saved evaluation outcomes, conducted local coding-assistant dry runs, and attempted hosted execution. The hosted attempt failed during model selection; it did not produce triage results or verify runtime controls end-to-end. I remain responsible for the submitted work.