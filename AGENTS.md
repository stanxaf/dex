# Repository instructions

This repository maintains a reusable governance foundation, not an application.
Before changing files, inspect the relevant documentation, existing conventions, and current diff; keep changes scoped. Preserve project-specific material and avoid new dependencies or abstractions without a clear need. Ask for clarification when consequential requirements conflict or cannot safely be inferred. Obtain explicit approval before destructive or irreversible operations, production deployment, material architecture changes, security-control weakening, or changes to authorization or regulated rules.

Use the workflow and approval boundaries in `docs/agent-governance/workflow.md`. Validate changes with `python3 scripts/validate.py` and `python3 -m unittest discover -s tests -v`; report failures and checks not run. Do not weaken checks or silently update baselines to hide failures. Document nontrivial decisions and exceptions with an owner, rationale, scope and expiry. Review actual changes and evidence before calling work complete.
