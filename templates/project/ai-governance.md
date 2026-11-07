# Project governance configuration

- Selected profile: {{PROFILE}}. Read `.ai-foundation/profiles/baseline/PROFILE.md`; for `web-saas` or `regulated`, also read `.ai-foundation/profiles/web-saas/PROFILE.md`; for `regulated`, also read `.ai-foundation/profiles/regulated/PROFILE.md`.
- All work: `.ai-foundation/docs/agent-governance/workflow.md`, `.ai-foundation/docs/engineering/standards.md`, `.ai-foundation/docs/testing/quality-gates.md`, `.ai-foundation/docs/security/agent-operations.md`.
- When relevant: `.ai-foundation/docs/design/design-system.md`, `.ai-foundation/docs/security/security.md`, `.ai-foundation/docs/architecture/architecture.md`, `.ai-foundation/docs/agent-governance/instruction-hygiene.md`.
- Project owner and approvers: **set before adoption**.
- Project architecture and existing instructions: **link or state none**.
- Design system: **link tokens, component library, usage docs, typography, visual baselines and owner; or state no established system**.
- Domain requirements, decision records and exceptions: **link or state none**.
- Applicable stack extensions: **list actual project-owned rules or state none**.
- Required checks and exact commands: **set formatting, lint, types, tests, security scans and UI/migration checks where applicable; identify unavailable checks**.
- Branch protection, reviewers, release and recovery owners: **document actual project settings**.
- Permitted agent tools and MCP servers (AGT-4): **inventory each one with its owner, purpose, the data it can read and the writes it can perform; or state none, and name who approves an addition**.
- Approval mode and sandbox posture (AGT-6): **name the mode and posture this project expects, rather than relying on client defaults; record who may relax either and how a relaxation is recorded**.
- Data classes an agent session may read (AGT-9): **state them, or state synthetic and de-identified data only**.
- Non-interactive or CI agent runs (AGT-12): **state whether permitted, with scope and credentials; or state none**.
- Reading tiers, instruction budget and last reconciliation (INS-5 to INS-7): **record which documents are read for all work, when relevant, or reference only; record the always-loaded budget, the date instructions were last reconciled, and by whom**.

Do not treat unset entries as evidence that a check passed or a requirement does not apply. Reconcile existing global, root, nested and fallback instructions with these rules and record unresolved conflicts before work. Use project-owned records for exceptions; follow the foundation approval boundary.
