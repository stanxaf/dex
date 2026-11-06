# ADR 0001: Local, versioned copy distribution

Status: accepted. Use a standard-library installer to copy a reviewed checkout's canonical docs, profiles and native Codex skills into a project. Store exact hashes and a content digest; leave project-owned instructions and configuration untouched. This works offline, avoids a central runtime and supports review and rollback in Git. Tradeoffs: copies need explicit updates; semantic rule conflicts require human review; interrupted multi-file updates need recovery. Do not use undocumented Codex orchestration or claim instructions enforce policy.
