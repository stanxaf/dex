# Workflow and authority

**Request → Inspect → Plan → Approve when required → Implement → Test → Review → Report → Merge.** Inspect relevant specs, instructions, architecture, components, existing changes, and verification before deciding scope. Explain material uncertainties. A small reversible change needs only an inline plan and proportionate checks; larger or high-risk work needs a recorded task and acceptance criteria.

## Instruction precedence and conflicts

Platform and tool restrictions and applicable law constrain all other instructions; the authorized human's instructions come before repository guidance. Codex loads global and then project instruction files in path order, with closer files later and `AGENTS.override.md` taking precedence over `AGENTS.md` in the same directory. The project configuration selects a profile and identifies local sources; the selected profile adds to the baseline. Project rules may tighten the foundation or specify choices it leaves open. Do not silently resolve a substantive contradiction or treat a later instruction as authorization to bypass an approval boundary: identify the conflicting sources, pause affected work, and ask the authorized owner to decide and record any exception. Continue unrelated safe work.

## Approval boundaries

Before acting, obtain explicit approval from the authorized human for significant architecture or dependency strategy changes, destructive data operations or migrations, auth/authz changes, production deployment, financial or regulated business rules, weakening security controls, and destructive operations affecting user data. An instruction to investigate or implement does not imply approval to deploy or destroy data. Prepare a reviewable proposal first: impact, alternatives, rollback/recovery, evidence, and the exact operation. Continue independent safe work while approval is pending. Actual tool or infrastructure permission is separate and can be stricter.

## Responsibilities and evidence

The implementer follows the approved scope, tests relevant behavior, and reports actual commands and outcomes, missing checks, risks and blockers. A reviewer independently reads the actual diff, requirements and evidence, checks for regressions, tests, accessibility and security as applicable, and reports actionable findings with locations and severity. Never accept the implementer's completion claim as evidence. A separate person is needed when the selected profile requires independent approval; another agent or fresh session is not a substitute. Merge only when required checks and review pass and approvals are recorded; use repository protection to enforce this.

Do not weaken tests, disable gates, suppress findings, or update visual snapshots solely to obtain green checks. Explain root cause and obtain appropriate review for intentional changes. Classify broad failures as related, pre-existing (with evidence), or unknown; do not claim unknown failures are unrelated. Escalate unresolved contradictions, unverifiable assumptions, or any change crossing an approval boundary.
