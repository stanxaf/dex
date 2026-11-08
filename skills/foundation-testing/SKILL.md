---
name: foundation-testing
description: Select and run proportionate software tests, investigate failures, and record verification evidence for a change.
---
# Testing

Input: task, acceptance criteria, diff, project instructions and configured checks in `.ai-governance.md`. Read `.ai-foundation/docs/testing/quality-gates.md` and the workflow checkpoints it references. Identify changed behaviors, negative paths, trust boundaries and regression risks. Choose meaningful unit, integration, end-to-end, accessibility, visual or migration checks as applicable; add focused tests where needed and within scope. Run configured checks at their required checkpoint and investigate failures.

Report commands, actual outcomes, coverage limits, deferred or skipped checks and whether failures are related, proven pre-existing, or unknown. Escalate checks unavailable at a required checkpoint and any proposal to weaken coverage or change a baseline. Complete verification only when required checks pass; an unrun test is never a pass.
