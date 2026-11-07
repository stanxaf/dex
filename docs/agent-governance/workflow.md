# Workflow and authority

## Quick reference

**Request → Inspect → Plan → Approve when required → Implement → Test → Review → Report → Merge.**

Each stage is specified below, and the applicable profile may add to it. Obtain human approval before crossing an [approval boundary](#approval-boundaries), and continue independent safe work while waiting.

## Plan and inspect

Before planning, inspect the applicable instructions, profile, architecture, existing components and changes, and how the work will be verified; surface material uncertainties and risks rather than assuming them away. Then state scope, non-goals, steps, verification and any approval boundary. For small, reversible, low-risk work a short inline plan and proportionate checks are enough. For larger or high-risk work, record the task and acceptance criteria; the [task template](../../templates/tasks/task.md) sets out the fields. Assess complexity and risk rather than file count alone. Merge only when required checks and review pass and approvals are recorded, and use repository protection to enforce it.

## One verified batch

Carry agreed work through to a verified result and report once, rather than returning after each step for confirmation the evidence already supplies. Within the agreed scope, settle what the repository, the instructions and the checks can settle: a question the project already answers spends the reviewer's attention for nothing and buries the decisions that need it. This applies to any implementer, person or tool.

Stop before the work is finished for one of three reasons, and say which:

- **An approval boundary is reached.** Prepare the proposal and wait; continue independent safe work meanwhile.
- **A conflict cannot be resolved in scope** — contradictory instructions, an unreconciled rule, a requirement that cannot be met as specified. Report the conflicting sources instead of choosing between them.
- **Required verification is unavailable** — a check that does not exist, cannot run in this environment, or needs access you do not have. Finish the independent safe work first, then report the check by name as unrun and say why. An unavailable check is not a pass, and work whose verification did not run is not reported as passing, working or done, however complete the edits look.

Stopping for one of these completes the batch rather than abandoning it: report what was done, what was verified, and what remains. Batching means not fragmenting the work, never proceeding past a boundary to keep momentum.

## Approval boundaries

Before acting, obtain explicit approval from the authorized human for significant architecture or dependency strategy changes, destructive data operations or migrations, auth/authz changes, production deployment, financial or regulated business rules, weakening security controls, and destructive operations affecting user data. An instruction to investigate or implement does not imply approval to deploy or destroy data, and a destructive migration requires approval even if rollback or recovery is possible.

Prepare a reviewable proposal first: impact, alternatives, rollback/recovery, evidence, and the exact operation. Continue independent safe work while approval is pending. Actual tool or infrastructure permission is separate and can be stricter.

## Roles

Assign roles according to the task; an appropriate person or tool may implement or review.

- **Implementer:** Follow the approved scope and test relevant behavior, reporting under the evidence rules below.
- **Reviewer:** Before merge, a separate reviewer must inspect the actual diff, requirements, and evidence; check regressions, tests, accessibility, and security as applicable; and report actionable findings in the form the [review template](../../templates/reviews/review.md) sets out, which it requires when the profile does.
- **Human approver:** Approve operations at the stated boundaries and any approval required by the selected profile. When independent human approval is required, a separate person is needed; another agent or fresh session is not a substitute.

A separate reviewer may be another person, agent, or fresh session that did not implement the change, subject to project and profile requirements. If the required review is unavailable, report it as a blocker to merge.

## Evidence rules

Use the actual changes and relevant results to assess acceptance criteria. Evidence can include diffs, command outputs, test results, and rendered inspection where applicable; report what was checked, what was not, and any remaining risks. An implementer's completion claim or an expectation that something should work is not verification.

Do not weaken tests, disable gates, suppress findings, or update visual snapshots solely to obtain green checks. Explain root cause and obtain appropriate review for intentional changes. Classify broad failures as related, pre-existing (with evidence), or unknown; do not claim unknown failures are unrelated.

## Instruction precedence, conflicts, and exceptions

Platform and tool restrictions and applicable law constrain all other instructions; the authorized human's instructions come before repository guidance. Closer project instruction files come later in the chain and an override file wins over a regular one in the same directory; [Codex compatibility](codex-compatibility.md) records the platform's actual discovery rules. The project configuration selects a profile and identifies local sources; the selected profile adds to the baseline. Project rules may tighten the foundation or specify choices it leaves open.

Do not silently resolve a substantive contradiction or treat a later instruction as authorization to bypass an approval boundary: identify the conflicting sources, pause affected work, and ask the authorized owner to decide and record any exception. Continue unrelated safe work, and escalate an unverifiable assumption the same way. Use the [exception template](../../templates/decisions/exception.md) to record scope, reason, risk, compensating control, owner, authorized approval, expiry, and exit plan.

Every decision and exception record must carry an explicit expiry and state what an overdue one changes. An overdue or expired record never widens permission: fall back to the requirement it modified, treat what it authorized as unreconciled, and report the lapse. Where it permitted an automated path, the fallback is the ordinary approval boundary with a human in the session — work continues, automation stops.

The practices this workflow adapts are listed under [external sources](codex-compatibility.md#sources-this-foundation-adapts); they do not imply certification or compliance.
