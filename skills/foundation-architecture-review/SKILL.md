---
name: foundation-architecture-review
description: Review proposed or changed software architecture for boundary, dependency, data-flow, contract, and decision-record risks.
---
# Architecture review

Input: proposal or actual diff, `.ai-governance.md`, project architecture and ADRs. Read `.ai-foundation/docs/architecture/architecture.md` and workflow. Trace module ownership, dependency direction, public interfaces, data flow, migrations, operational impacts and compatibility. Compare against existing decisions; check meaningful evidence and alternatives.

Report prioritized findings with concrete paths, risk, affected contracts and recommended remedy, plus uncertainty and checks not run. Escalate significant architecture changes and unresolved decisions for approval. Complete when relevant boundaries and evidence were inspected or limitations are stated; never claim a proposed design is approved without recorded authority.
