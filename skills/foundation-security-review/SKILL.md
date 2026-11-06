---
name: foundation-security-review
description: Review software changes for trust boundaries, authorization, secrets, data protection, dependencies, and tenant isolation when applicable.
---
# Security review

Input: actual diff, request, threat context, `.ai-governance.md`, selected profile, data flow and available scan/test results. Read `.ai-foundation/docs/security/security.md` and workflow. Trace identity and server-side authorization to data access, tenant boundaries where applicable, input validation, secrets, logging, privilege and dependency changes. Inspect relevant denial tests and scans without exposing sensitive data.

Report concrete findings, impact, location and remediation, plus evidence and unverified assumptions. Escalate auth/authz changes, security-control weakening, production access and destructive data operations before execution. Complete when relevant boundaries and evidence have been reviewed or limitations are explicit; do not represent this pass as a security certification.
