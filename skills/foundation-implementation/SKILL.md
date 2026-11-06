---
name: foundation-implementation
description: Implement an approved software task within project conventions, with appropriate tests, evidence, and approval boundaries.
---
# Implementation

Input: request or accepted plan, project instructions, `.ai-governance.md`, relevant standards and existing code. Read `.ai-foundation/docs/agent-governance/workflow.md` and `.ai-foundation/docs/engineering/standards.md`. Inspect existing components, contracts, tests and worktree before changing anything. Reuse patterns and keep the diff in scope.

Implement the approved task, validate inputs and error states, add proportionate regression tests and update relevant docs. Run configured checks and inspect the diff. Stop for unresolved consequential decisions or approval boundaries, including auth, destructive data operations and regulated rules. Never weaken checks merely to pass. Report changed files, actual commands/results, skipped or failing checks, approvals and residual risk. Complete only when acceptance criteria and required checks pass or a specific blocker is honestly reported; completion never implies independent review.
