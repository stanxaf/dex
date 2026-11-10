# ADR 0007: Efficient agent use

Status / owner / date / approving authority: proposed on 2026-11-10 at the user's request. Owner and approving authority: **[OWNER NAME PENDING]** — the foundation owner; their name has not been verified. Fill before merge.

Scope and non-goals: add portable guidance for selecting agent effort, delegating independent work and evaluating efficiency. Preserve the existing verification, review, approval and security requirements. Do not prescribe a vendor, model, project-specific operating model or mandatory metrics collection.

Context: unnecessary delegation, oversized reasoning effort and repeated coordination can consume time without improving an outcome. The workflow already selects checks by risk and permits reuse of relevant evidence, but does not guide agent allocation. The effect on time, cost and quality is not established.

Decision and rationale: default to one implementer and a focused batch; scale agent and reasoning effort to the work and delegate parallel tasks when their expected benefit justifies coordination. Evaluate comparable tasks using evidence available to the project and disclose gaps. This permits a lightweight starting point without making assumptions about tool availability or relaxing quality gates.

Alternatives: prescribe model tiers for task categories, which would depend on a particular platform and age quickly; require parallel agents by default, which adds coordination to small work; or leave allocation entirely implicit. The chosen guidance supplies a default while preserving project and user choices.

Consequences, migration and recovery: adopters receive this guidance only through a reviewed foundation update. Existing project-owned instructions remain in place. Revert the workflow's efficient agent use section and this decision record to return allocation to the prior task-by-task role selection.

Evidence: the guidance was reviewed against a small edit, independent parallel investigation and a change requiring separate review. The workflow grows from 1,408 to 1,510 words, measured by whitespace splitting. Repository checks validate document structure, not agent adherence, time saved or quality; actual outcomes require measurement.

Expiry date: 2028-11-09
Review by: 2027-05-09
Expiry and review handling: if this decision is overdue or expired, report it and stop applying its allocation default until reviewed; use the prior task-by-task role selection. Required checks, approvals and separate review remain in force.
