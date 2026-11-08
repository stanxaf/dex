---
name: foundation-code-review
description: Review an actual code diff for actionable correctness, regression, maintainability, test, and security risks with evidence.
---
# Code review

Input: request, acceptance criteria, actual diff, project instructions, `.ai-governance.md`, selected profile and available test results. Read `.ai-foundation/docs/agent-governance/workflow.md` and relevant standards. Inspect changed code and callers; do not rely on an implementer's summary. Check behavior, edge cases, types, errors, duplication, compatibility, security and meaningful regression coverage. Use current, relevant test evidence; run targeted checks when required, when evidence is missing or stale, or to investigate a risk.

Output actionable findings first, with severity, file/line, trigger, impact and remedy; then residual risks and checks not run. Escalate approval-boundary changes or missing evidence. Complete when the diff and evidence have been independently inspected or limitations are explicit. A separate agent review does not replace any required independent human approval.
