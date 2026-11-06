# Engineering standards

**MUST** = baseline requirement; **SHOULD** = recommendation with documented rationale for departure; **CONTEXT** = decide per project and record when material. Profile additions may be stricter.

- MUST inspect and reuse established architecture, dependencies, components and utilities; keep modules cohesive, responsibilities separate, dependencies directed through documented public interfaces, and changes within scope. Ask before material architecture or dependency strategy changes. SHOULD prefer the smallest maintainable extension.
- MUST validate external input and enforce data invariants at trust boundaries; use the language's type system where available, do not bypass type checks to conceal invalid data, and make null/invalid/error paths explicit. CONTEXT: choose schema tooling and type strictness per stack.
- MUST define stable, versioned API contracts as appropriate, validate requests and responses, document compatibility and errors, and prevent internal details or sensitive data leaking through errors. SHOULD use structured, actionable logs with safe correlation identifiers.
- MUST preserve data integrity across migrations with constraints, tested transitions, compatibility during rollout, backup/recovery and rollback or forward-repair plans. Destructive migrations require prior approval. CONTEXT: availability and data-volume strategy depend on deployment.
- MUST use least privilege, server-side authorization at each protected boundary, safe secret handling and data minimization; see [security](../security/security.md).
- MUST add proportionate tests for changed behavior and document public behavior, migration steps and material decisions. Follow [quality gates](../testing/quality-gates.md). SHOULD automate repetitive checks.
- MUST review dependency purpose, provenance, maintenance, security and license before adding it; use lockfiles when supported and obtain approval when a dependency changes architecture or risk materially. Avoid unnecessary packages.
- MUST use a project-defined Git/PR workflow, protect review and CI on the merge target, and avoid committing credentials, generated secrets or private data. SHOULD use short-lived branches, focused PRs and a reviewable diff. Record exceptions using the project-owned exception template; do not silently override requirements.

Optional stack-specific starter rules are in `templates/stacks/`; select and adapt them rather than treating them as universal.
