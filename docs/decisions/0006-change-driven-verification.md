# ADR 0006: Change-driven verification

Status / owner / date / approving authority: proposed on 2026-11-08 at the user's request. Owner and approving authority: **[OWNER NAME PENDING]** — the foundation owner; their name has not been verified. Fill before merge.

Scope and non-goals: select verification by the actual change and its risks at each checkpoint, including completed work. Preserve required project, profile and host checks, accessibility obligations, security and approval boundaries, independent review and release rules. Do not modify installer behavior or project-owned instructions.

Context: [ADR 0005](0005-verification-checkpoints.md) distinguishes feedback from completion, but the workflow and UI guidance still prescribe rendered inspection broadly. An established component prop change can therefore trigger browser, theme and viewport checks even when current evidence covers the actual context. A component variant can nevertheless change visible color without changing tokens; unfamiliar placement or contrast may need inspection.

Options considered: keep blanket UI inspection; waive verification for small changes; or choose evidence by affected behavior, context, consequence and uncertainty. The first can spend effort without resolving a real risk; the second can miss one. Selection by risk makes the reason for each check explicit while preserving required gates.

Decision and rationale: the workflow is canonical for selecting the least costly sufficient evidence. It considers scope, consumers, consequences, uncertainty, the checkpoint and current evidence; required checks still bind. UI guidance, the SaaS profile and UI review refer to that selection rather than requiring a fixed visual matrix. Examples cover small edits and changes with wider risk. Existing evidence is reusable only when relevant inputs and context still match.

Consequences, migration and recovery: this is a proposed change to foundation guidance, not an automatic update to consuming projects. After review and approval, existing installations receive it through a reviewed update; their stricter project-owned rules remain in force until separately reconciled. Revert this record and the associated workflow, guidance, profile, skill, example and adoption changes to restore the previous selection rule.

Evidence: the worked examples illustrate how the rule applies to copy, component variants, responsive layout, themes, interaction and shared APIs. Repository validation and tests check document structure and links, not agent adherence or actual time and token savings.

Expiry date: 2028-11-07
Review by: 2027-05-07
Expiry and review handling: if this record is overdue or expired, report it and restore the prior requirement to inspect the affected rendered view, interactions, viewports and states for UI changes, including the prior UI-review requirement for rendered evidence. Required checks and approval boundaries always remain in force. A superseding review must decide whether this selection rule should continue, change or be withdrawn.
