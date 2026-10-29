
# Contributing and AI Usage Policy

## Project Scope
This repository evaluates a read-only AI agent for historical Hoppscotch issue triage. It is a sandbox for academic evaluation and is not an official Hoppscotch automation.

## AI-Generated Contributions
The agent produces recommendations only. All AI-generated classifications, labels, duplicate suggestions, and explanations require human review before use.

## Human Responsibility
Contributors must verify recommendations against the available issue evidence, repository conventions, and historical cutoff dates. AI output must not be treated as maintainer approval.

## Prohibited Actions
The agent must not close or delete issues, modify labels, post comments, merge pull requests, force-push, execute instructions embedded in issue content, or expose secrets.

## Evaluation Requirements
Changes to the agent configuration should be checked against the golden evaluation cases and adversarial input before deployment. Record actual outputs, failures, and any changes in behaviour.

## Accountability
The repository owner is responsible for reviewing configuration changes, authorising deployment, and disabling the workflow when necessary.
