# Project governance configuration

- Selected profile: {{PROFILE}}. Read `.ai-foundation/profiles/baseline/PROFILE.md`; for `web-saas` or `regulated` also `.ai-foundation/profiles/web-saas/PROFILE.md`; for `regulated` also `.ai-foundation/profiles/regulated/PROFILE.md`.
- All work: `.ai-foundation/docs/agent-governance/workflow.md`, `.ai-foundation/docs/engineering/standards.md`, `.ai-foundation/docs/testing/quality-gates.md`, `.ai-foundation/docs/security/agent-operations.md`.
- When relevant: `.ai-foundation/docs/security/deployment-gate.md` (before any automated deployment), `.ai-foundation/docs/design/design-system.md`, `.ai-foundation/docs/security/security.md`, `.ai-foundation/docs/architecture/architecture.md`, `.ai-foundation/docs/agent-governance/instruction-hygiene.md`.
- Project owner and approvers: **set before adoption**.
- Project architecture and existing instructions: **link or state none**.
- Design system: **link the tokens, components, baselines and owner; or state none established**.
- Domain requirements, decision records and exceptions: **link or state none; note each record's expiry and review date**.
- Applicable stack extensions: **list project-owned rules or state none**.
- Required checks and exact commands: **name each required check with its command; identify any unavailable**.
- Branch protection, reviewers, release and recovery owners: **document actual project settings**.
- Permitted agent tools and MCP servers (AGT-4): **inventory each with owner, purpose, readable data and writes; or none, plus who approves an addition**.
- Approval mode and sandbox posture (AGT-6): **name both, who may relax either, and how that is recorded**.
- Permitted network egress (AGT-7): **list destinations and who approves an addition; or state none recorded**.
- Data classes an agent session may read (AGT-9): **name the readable real-data classes and any restricted class, whose restriction also covers de-identified extracts of it; note fictional fixtures explicitly permitted in a restricted domain**.
- Non-interactive or CI agent runs (AGT-12): **state whether permitted, with scope and credentials; or none**.
- Automated deployment gate (AGT-15 to AGT-21): **if permitted, record the gate, the release approver, what the release identity pins, how it is verified and applied, credential scope and lifetime, and the evidence location; else none, the default**.
- Reading tiers and reconciliation (INS-5 to INS-7): **record each document's tier, the always-loaded budget, and the last reconciliation date and author**.

Do not treat an unset entry as evidence that a check passed or a requirement does not apply. Reconcile existing global, nested and fallback instruction files before work, under the workflow's precedence rules.
