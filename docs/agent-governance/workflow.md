# Workflow and authority

## Quick reference

**Request → Inspect → Plan → Approve when required → Implement → Test → Review → Report → Merge.**

Each stage is specified below, and the applicable profile may add to it. Obtain human approval before crossing an [approval boundary](#approval-boundaries), and continue independent safe work while waiting.

## Plan and inspect

Before planning, inspect the applicable instructions, profile, architecture, existing components and changes, and how the work will be verified; surface material uncertainties and risks rather than assuming them away. Summarize the intended outcome, planned changes and likely files, scope and non-goals, acceptance criteria, checks to run and any approval boundary as a concise implementation brief. For small, reversible, low-risk work a short inline list and proportionate checks are enough. For larger or high-risk work, record the task; the [task template](../../templates/tasks/task.md) sets out the fields. Assess complexity and risk rather than file count alone. Merge only when required checks and review pass and approvals are recorded, and use repository protection to enforce it.

## Coder selection and handoffs

Use a tool-neutral implementation brief by default; DEX does not assign a particular coder or require a separate coding tool. A planning or handoff request ends with the brief. A direct implementation request proceeds through the workflow using the current agent when the user's operating model permits it.

Resolve the implementer from an explicit task choice, then an active session choice, then a project preference. With no choice, leave a handoff unnamed. “Ask Kiro” selects Kiro for that task; “today we use Kiro” or “we use Kiro here” selects Kiro for the current chat until changed. An explicit request for the current agent to implement selects it for that task. Naming a coder alone does not start implementation or authorize installing tools, granting access or sending messages.

Keep session choices in the conversation. Persist a project default only when the user explicitly asks to save it, in project-owned instructions or `.ai-governance.md`; a session choice never edits project or global instructions. A coder preference changes the implementer, not the required checks, separate review or approval boundaries.

Title the default output “Implementation brief”; tailor a named handoff to the selected coder and any requested format. Include a completion-report requirement: files changed, what changed, checks run with pass/fail results, checks not run, and remaining blockers or unrelated failures with evidence. Include “Do not call complete unless…” with the acceptance criteria and required verification for the intended checkpoint. A finished brief completes planning only; implementation still requires any outstanding decisions or approvals and its own evidence.

## Efficient agent use

Default to one implementer and a focused batch. Select available agents and reasoning effort for the task's complexity and risk. Delegate parallel work only when tasks are independent, bounded and likely to save more effort than coordination costs; avoid conflicting edits. Respect the user's operating model and platform permissions.

When evaluating efficiency across tasks, compare similar work using available evidence such as elapsed time, agent calls, token use or cost, rework and defects found. Record missing data and do not claim savings or quality improvements without evidence. This guidance does not change required verification, approvals or separate review.

## Exploration and checkpoints

Choose checks by outcome, affected behavior, risk and destination, not persona or agent. “Try this layout” can end at a feedback checkpoint. State the interpretation when it matters and retain it across iteration. Ask about consequential uncertainty; do not assume an unknown destination is safe.

During exploration, check the idea and relevant risks using the selection below. Report checks and deferrals: an exploration can be ready for feedback without being a verified, consumer-ready change.

For each checkpoint, select the applicable items: diff and scope; behavior and tests; rendered UI and accessibility; documentation and generated output; security, destination rules, review and approvals. Record results and any permitted deferrals.

At wrap-up, apply checks for the intended outcome, review the diff, and report evidence, deferrals and risks. Before commit or push, apply the project's rules for the destination; work in progress is not automatically a release. Before presenting a change as complete or ready for consumers, merging or releasing, complete applicable checks, documentation, review and approvals. Project, profile and host-enforced requirements bind at their stated checkpoints. Exploration does not authorize a commit, push, deployment, restricted-data access or another approval-boundary operation.

## Selecting verification

Start with the actual diff and acceptance criteria. Identify what changed, affected contexts and consumers, consequences of failure, uncertainty, and the evidence already available. Choose the least costly checks that address those risks at the current checkpoint; a change's category or file count alone does not determine the checks. Explain material choices and gaps briefly. Required project, profile, host and user checks still apply at their stated checkpoints.

Inspect rendered UI when needed to assess the requested visual outcome or a realistic risk, such as unfamiliar placement or styling, responsive reflow, or uncertain contrast in a theme. Select viewports, themes and states according to that risk rather than a fixed matrix. Check keyboard and other interactions when their behavior or accessibility may be affected; a screenshot alone does not prove an interaction. For shared contracts or components, assess affected consumers and use targeted tests or broader journeys when their integration risk warrants them.

Run checks when useful or required, not automatically after every edit. Reuse a recorded result only for the risks and context it actually covers, while its relevant inputs, including code, configuration, dependencies and environment, remain unchanged. Combine it with the current diff and other evidence to assess the change; obtain missing evidence or rerun affected checks when needed. An unchanged token does not establish contrast or appearance in a new context. Review the actual diff and evidence, and repeat checks when needed to resolve uncertainty.

## One verified batch

Carry agreed work through to the verification required for its checkpoint and report once, rather than returning after each step for confirmation the evidence already supplies. Within the agreed scope, settle what the repository, the instructions and the checks can settle: a question the project already answers spends the reviewer's attention for nothing and buries the decisions that need it. This applies to any implementer, person or tool.

Stop before the work is finished for one of three reasons, and say which:

- **An approval boundary is reached.** Prepare the proposal and wait; continue independent safe work meanwhile.
- **A conflict cannot be resolved in scope** — contradictory instructions, an unreconciled rule, a requirement that cannot be met as specified. Report the conflicting sources instead of choosing between them.
- **Verification required for the current checkpoint is unavailable** — a check that does not exist, cannot run in this environment, or needs access you do not have. Finish the independent safe work first, then report the check by name as unrun and say why. An unavailable check is not a pass; do not claim that checkpoint was met. Checks deferred to a later checkpoint remain unverified, not unavailable passes.

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
