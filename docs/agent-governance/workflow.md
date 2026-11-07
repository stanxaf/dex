# Workflow and authority

## Quick reference

**Request → Inspect → Plan → Approve when required → Implement → Test → Review → Report → Merge.**

- **Plan:** Small, reversible, low-risk work can use an inline plan; larger or high-risk work needs a recorded task. [Details](#inline-plan-or-recorded-task).
- **Approve:** Obtain human approval before crossing an [approval boundary](#approval-boundaries) or when the profile requires it. Continue independent safe work while waiting.
- **Review:** A separate reviewer inspects the actual diff and evidence before merge. Self-review does not replace separate review or required human approval. [Details](#roles).
- **Evidence:** Report actual checks, results, and gaps. A missing, failing, or unrun required check blocks merge. [Details](#evidence-rules).
- **Templates:** [Task](../../templates/tasks/task.md) · [Review](../../templates/reviews/review.md) · [Exception](../../templates/decisions/exception.md).

Consult the full workflow and applicable profile for requirements.

## Core loop

- **Request and inspect:** Capture the desired outcome and constraints; inspect applicable instructions, profiles, architecture, components, existing changes, and verification. Surface material uncertainties and risks.
- **Plan and approve:** Define scope, non-goals, steps, verification, and any approval boundaries. Prepare the proposal described below when approval is required.
- **Implement and test:** Stay within scope, reuse established patterns, and run the relevant checks. Record actual commands, results, and unrun checks.
- **Review and report:** Review the actual changes and evidence. Report findings, verification, remaining risks, blockers, and relevant task or exception records.
- **Merge:** Merge only when required checks and review pass and approvals are recorded; use repository protection to enforce this.

## Inline plan or recorded task

For small, reversible, low-risk work, use a short inline plan and proportionate checks. For larger or high-risk work, record the task and acceptance criteria; the [task template](../../templates/tasks/task.md) can be used. Assess complexity and risk rather than file count alone.

## Approval boundaries

Before acting, obtain explicit approval from the authorized human for significant architecture or dependency strategy changes, destructive data operations or migrations, auth/authz changes, production deployment, financial or regulated business rules, weakening security controls, and destructive operations affecting user data. An instruction to investigate or implement does not imply approval to deploy or destroy data.

Examples include changes to permission models, production releases, disabling protections, and bulk deletion. A destructive migration requires approval even if rollback or recovery is possible.

Prepare a reviewable proposal first: impact, alternatives, rollback/recovery, evidence, and the exact operation. Continue independent safe work while approval is pending. Actual tool or infrastructure permission is separate and can be stricter.

## Roles

Assign roles according to the task; an appropriate person or tool may implement or review.

- **Implementer:** Follow the approved scope, test relevant behavior, and report actual commands and outcomes, missing checks, risks, and blockers.
- **Reviewer:** Before merge, a separate reviewer must inspect the actual diff, requirements, and evidence; check regressions, tests, accessibility, and security as applicable; and report actionable findings with severity, location, trigger, impact, and remedy. Use the [review template](../../templates/reviews/review.md) when useful or required.
- **Human approver:** Approve operations at the stated boundaries and any approval required by the selected profile. When independent human approval is required, a separate person is needed; another agent or fresh session is not a substitute.

A separate reviewer may be another person, agent, or fresh session that did not implement the change, subject to project and profile requirements. A review of one's own implementation is a self-review and does not replace that separate review. If the required review is unavailable, report it as a blocker to merge.

## Evidence rules

Use the actual changes and relevant results to assess acceptance criteria. Evidence can include diffs, command outputs, test results, and rendered inspection where applicable; report what was checked, what was not, and any remaining risks. An implementer's completion claim or an expectation that something should work is not verification. A missing, failing, or unrun required check is not a pass.

Do not weaken tests, disable gates, suppress findings, or update visual snapshots solely to obtain green checks. Explain root cause and obtain appropriate review for intentional changes. Classify broad failures as related, pre-existing (with evidence), or unknown; do not claim unknown failures are unrelated.

## Instruction precedence, conflicts, and exceptions

Platform and tool restrictions and applicable law constrain all other instructions; the authorized human's instructions come before repository guidance. Codex loads global and then project instruction files in path order, with closer files later and `AGENTS.override.md` taking precedence over `AGENTS.md` in the same directory. The project configuration selects a profile and identifies local sources; the selected profile adds to the baseline. Project rules may tighten the foundation or specify choices it leaves open.

Do not silently resolve a substantive contradiction or treat a later instruction as authorization to bypass an approval boundary: identify the conflicting sources, pause affected work, and ask the authorized owner to decide and record any exception. Continue unrelated safe work. Escalate unresolved contradictions, unverifiable assumptions, or any change crossing an approval boundary. Use the [exception template](../../templates/decisions/exception.md) to record scope, reason, risk, compensating control, owner, authorized approval, expiry, and exit plan.

## Based on

This workflow adapts selected practices; these references do not imply certification or compliance:

- [NIST Secure Software Development Framework](https://csrc.nist.gov/pubs/sp/800/218/final): secure development and verification practices.
- [GitHub protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches): enforcement of required reviews and status checks.
- [Codex instruction discovery](https://developers.openai.com/codex/guides/agents-md): project instruction precedence for Codex; other tools may differ.
