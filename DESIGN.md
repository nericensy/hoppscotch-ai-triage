# Design: Hoppscotch AI Issue Triage Agent

## 1. Workflow Selection and Motivation

This project configures a GitHub Agentic Workflow to assist with issue triage for the open-source Hoppscotch project. The agent classifies issues, identifies missing information, searches for possible duplicates, and recommends a next action without modifying issues.

Issue triage requires interpreting natural-language reports, technical symptoms, reproduction steps, and repository context. Conventional automation can validate labels or detect exact duplicates, but it cannot reliably interpret ambiguous reports or explain why further investigation is needed. The agent therefore supports maintainers rather than replacing their judgement.

**Repository evidence:** I examined Hoppscotch issues created between 1 and 30 September 2026 using the GitHub REST API. The retrieved pages contained 29 matching issue records. This is a preliminary count rather than a verified total because the API request filtered by update activity and may not capture every issue created during the period. The evaluation additionally uses ten historical issues representing bugs, enhancements, questions, and no-action cases. The sample demonstrates the need for consistent triage but cannot establish average response time or total maintainer workload.

## 2. Configuration and Architecture

- `.github/workflows/issue-triage.md`: Defines manual `workflow_dispatch` triggering, issue-number input, read-only GitHub permissions, Copilot engine, a 10-minute timeout, concurrency configuration, and tool access.
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
| Least privilege | Agent job uses `contents: read` and `issues: read`; GitHub MCP issue-reading tools are allowlisted. Compiled permissions were inspected. |
| Safe outputs | `create-issue: false` and `report-failure-as-issue: false` were added. The workflow was recompiled and the previously exposed `create_issue` tool was no longer found in the checked configuration. |
| Human approval | The agent recommends actions only. Maintainers decide whether to apply labels, request information, or close issues. |
| Budgets | Manual triggering limits automatic invocation. Runtime is capped at 10 minutes. JSON output limits labels, duplicates, and missing-information entries to three each, and explanations to 100 words. Model-token spending is not explicitly capped. |
| Audit trail | Workflow definitions and evaluation artifacts are stored in Git. GitHub Actions logs can provide execution evidence when a hosted run is completed. Complete tool-call and cost logs have not been verified. |
| Kill switch | Maintainers can disable the workflow through GitHub Actions and cancel running executions. This procedure has not been tested. |
| Drift detection | Rerun the ten golden cases after model, prompt, skill, or tool changes. A maintainer should review changed classifications, recommended actions, duplicates, and explanations before accepting updates. This review process is proposed, not automated. |
| Accountability | Repository maintainers control workflow changes and remain responsible for decisions. Git history records configuration changes; formal ownership rules are not yet established. |

Network restrictions are configured as `network: defaults`; a restrictive domain allowlist has not been verified.

## 4. Threat Model and Five Required Scenarios

**Q1. An issue claims maintainer approval and instructs the agent to close all stale issues.**

The issue body is treated as untrusted data, not an instruction source. The workflow prohibits closing issues and does not grant the agent issue-write tools. In the adversarial dry run, the agent recommended `no_action`, classified the fabricated issue as `unclear`, and did not perform GitHub writes. This demonstrates resistance in the tested dry run, not a complete hosted-execution security guarantee.

**Q2. A provider updates the model and a golden task starts failing.**

The model version is not explicitly pinned in the source configuration. A proposed regression process reruns golden cases after provider or workflow updates and compares results with the recorded expectations. Changed recommendations and explanations require human review. Automatic drift detection is not implemented.

**Q3. The project receives 300 issues in one week.**

The workflow uses manual triggering rather than automatic execution on every new issue. Therefore, 300 incoming issues do not automatically generate 300 agent runs. Maintainers select which issues to process. The 10-minute timeout limits each execution, but a weekly run quota is not enforced.

**Q4. A tool or MCP server returns malicious instructions.**

Tool results are untrusted. The agent is instructed to ignore embedded commands and use results only as evidence. Its allowlisted GitHub issue tools provide read operations; the checked safe-output configuration removes issue creation. Malicious tool content could still influence the model's recommendation, so human review and adversarial testing remain necessary.

**Q5. A maintainer needs to stop the agent using only a phone.**

The maintainer opens the repository on GitHub in a mobile browser, selects **Actions**, opens the issue-triage workflow, and disables it to prevent new runs. They must also open any running workflow execution and select **Cancel workflow**. Repository permissions are required. This procedure is proposed and has not been tested on mobile.

## 5. Historical Evaluation and Findings

The evaluation uses ten historical Hoppscotch issues: #6756, #6753, #6750, #6742, #6738, #6720, #6701, #6686, #6680, and #6676. The cases include bugs, enhancements, questions, missing-information reports, and no-action situations.

A Copilot coding-assistant dry run produced recommendations for all ten cases. Compared with the previously recorded expected outcomes, category agreement was 8/10 and recommended-action agreement was 8/10.

Four cases had disagreements: #6680 was classified as an enhancement rather than a bug; #6701 was classified as unclear rather than a question; #6720 received `review` instead of `no_action`; and #6753 received `request_information` instead of `review`. These demonstrate ambiguity in issue classification and differences in interpreting when further information or maintainer action is necessary.

The dry-run output omitted the required `skill_loaded` field. The assistant separately reported loading the skill, but output-schema compliance was incomplete. The suggested duplicates #3901 and #3905 for issue #6756 were not independently verified.

The previously saved actual JSON files produced 10/10 category and action agreement, but some were manually prepared and are not treated as independent agent evaluation results.

The original Copilot output is preserved in `evals/golden/dry-run-transcript.md`. Hosted GitHub Actions execution remains untested; therefore, hosted permissions, tool enforcement, and execution logs have not been verified end-to-end.

## 6. Alternatives, Trade-offs, and Unresolved Issues

A fully automated issue-management bot was rejected because automatically changing labels or closing issues would increase the risk of incorrect decisions and prompt-injection attacks.

A read-only recommendation agent provides useful analysis while retaining maintainer control. The trade-off is that human review remains necessary and triage decisions are not automatically applied.

Remaining limitations include incomplete end-to-end validation, unverified network restrictions, uncertain historical expectation chronology, incomplete evaluation transcripts, and the absence of automated drift monitoring.

## 7. Agent Bill of Materials

- **Model:** GitHub Copilot workflow engine; exact underlying model/version and pinning are not verified.
- **Instructions:** `AGENTS.md`, `.claude/skills/issue-triage/SKILL.md`, and workflow prompt.
- **Tools/MCP:** GitHub MCP issue-reading tools (`issue_read`, `list_issue_types`, `list_issues`, `search_issues`); compiled workflow infrastructure.
- **Permissions:** `contents: read`, `issues: read` for the agent job; generated support-job permissions require separate interpretation.
- **Data sources:** Sandbox GitHub issues, historical Hoppscotch issue records, comments, labels, and preserved evaluation context.
- **Logs:** Saved evaluation artifacts and coding-assistant dry-run records where available; hosted GitHub Actions logs not yet collected.
- **Evaluations:** Ten historical cases and one adversarial prompt-injection case.
- **Responsible humans:** Repository owner and authorised maintainers; they review recommendations and approve configuration changes.

## 8. AI-Use Statement

AI assistance was used to develop and refine the workflow instructions, skill, evaluation materials, and documentation. I reviewed the generated configuration, inspected the compiled workflow, checked JSON validity, compared saved evaluation outcomes, and conducted coding-assistant dry runs. I distinguish those checks from unperformed hosted tests and remain responsible for the submitted work.