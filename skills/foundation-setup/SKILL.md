---
name: foundation-setup
description: Set up or finish setting up the AI engineering foundation in a project, connecting it to existing instructions and separating evidence-based configuration from decisions a human must make.
---
# Setup

Input: the project. A reviewed foundation checkout path is needed only to install or to update; if `.ai-foundation/manifest.json` is already present and no update was asked for, run from the installed copy and ask for no path. Follow `.ai-foundation/docs/agent-governance/setup.md`, which is the canonical procedure; this skill is the entry point to it, not a second copy.

Works for a fresh project and for one already installed or partly configured. Establish the state read-only first. Reconcile contradictions between existing and nested instructions and the foundation before activating it, since activating into a conflict leaves two competing authorities. Treat a mention of `.ai-governance.md` as evidence to review rather than proof of activation: read the surrounding text, and if it does not actually instruct the agent to follow the configuration, report it rather than assuming either state. Then fill every `.ai-governance.md` entry the repository evidences and group the rest into the procedure's four handoff groups.

Never invent an owner, approver, permission, credential scope, approval mode, egress rule, readable data class or branch-protection setting. Never edit an existing project rule or a nested instruction file, never delete a directory that still holds files, and never commit, stage or push unless asked. Report against the procedure's six-condition completion test and name what fails. Presenting a decision is not obtaining one: while any handoff entry is unanswered the status is files installed with setup outstanding, not complete.
