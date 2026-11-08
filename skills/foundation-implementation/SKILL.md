---
name: foundation-implementation
description: Implement an approved software task within project conventions, with appropriate tests, evidence, and approval boundaries.
---
# Implementation

Input: request or accepted plan, project instructions, `.ai-governance.md`, relevant standards and existing code. Read `.ai-foundation/docs/agent-governance/workflow.md` and `.ai-foundation/docs/engineering/standards.md`. Inspect existing components, contracts, tests and worktree before changing anything. Reuse patterns and keep the diff in scope.

Implement the approved task and validate inputs and error states as applicable. Add tests and update docs when required by the workflow's checkpoints; an exploration may be ready for feedback with later checks explicitly deferred. Run required checks and inspect the diff. Stop for unresolved consequential decisions or approval boundaries, including auth, destructive data operations and regulated rules. Never weaken checks merely to pass. Report changed files, actual commands/results, deferred or failing checks, approvals and residual risk. Claim a completed change only when its acceptance criteria and required checks pass; completion never implies independent review.
