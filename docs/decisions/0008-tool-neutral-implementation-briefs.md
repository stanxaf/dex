# ADR 0008: Tool-neutral implementation briefs

Status / owner / date / approving authority: proposed on 2026-11-13 at the user's request to implement tool-neutral briefs and optional coder preferences. Owner and approving authority: **[OWNER NAME PENDING]** — the foundation owner; their name has not been verified. Fill before merge.

Scope and non-goals: clarify planning output, implementer selection and handoff expectations. Preserve direct implementation, required checks, separate review and approval boundaries. Do not change installation, discovery, permissions, integrations, project-owned instructions or global preferences.

Context: the foundation already uses implementer and reviewer roles, but personal instructions can hard-code Kiro and require every plan to become a Kiro prompt. A reusable workflow needs an actionable brief that a person or tool can execute, while allowing a designer to choose a separate coder for a task, chat or project.

Options considered: require a named external coder for all work; reduce plans to informal summaries without acceptance criteria; or keep an actionable, tool-neutral brief and resolve the implementer from explicit preferences. The first imposes one operating model, and the second weakens the handoff.

Decision and rationale: keep the workflow canonical for the brief and coder selection. Prefer an explicit task choice, then a session choice, then a project preference. Save a project preference only on an explicit request; casual “today” or “here” wording stays in the chat. Direct implementation requests remain supported. A handoff carries scope, acceptance criteria, checks and completion evidence regardless of its recipient.

Consequences, migration and recovery: this adds guidance, not a runtime router or automatic tool integration. No new configuration entry or reading tier is required. After a reviewed update, adopters reconcile any conflicting personal or project instructions separately; the installer continues preserving them. Revert this record and the associated workflow, skill, task-template, example, README and adoption edits to recover the previous guidance.

Evidence: the worked example covers an unnamed plan, task and session choices, a saved project default, direct implementation and an unsupported completion claim. Repository validation and tests check structure, links and distribution behavior; they cannot prove an agent follows a preference or another tool loads these instructions.

Expiry date: 2028-11-13
Review by: 2027-05-13
Expiry and review handling: if this decision is overdue or expired, report it and fall back to explicit task-by-task role assignment under the prior workflow until reviewed. Do not infer a new saved preference or erase a project-owned one. Required checks, separate review, permissions and approval boundaries remain in force.
