# AI Engineering Foundation

A portable set of engineering standards, approval boundaries, Codex skills, and review templates for software projects. It is a **starting point**, not an application, security product, legal compliance certification, or a guarantee that an agent obeys instructions. Use CI, repository permissions, sandboxing, human approvals, and independent review to enforce consequential controls.

## Adopt in a project

Requires Python 3.9+ and a local checkout of this foundation. From the foundation directory:

```sh
python3 scripts/install.py /path/to/project --profile baseline
```

Choose `baseline`, `web-saas`, or `regulated`; see [profiles](profiles/README.md). The installer copies standards into `.ai-foundation/`, installs skills under `.agents/skills/`, and creates `AGENTS.md` and `.ai-governance.md` only if absent. It reports existing instruction files and refuses managed-file collisions or locally modified managed files. It never merges or replaces an existing `AGENTS.md`; if one exists, **add this line to the active instruction file after review**:

> Read `.ai-governance.md`, then the foundation workflow, selected profile and standards it references; follow them for relevant work.

Complete `.ai-governance.md`: select the profile, name source-of-truth documents and actual project commands, and reconcile contradictions. Review all reported root and nested instruction files, as well as global instructions; the installer inventories filenames but cannot detect semantic conflicts or enforce inclusion. Do not adopt until conflicts are resolved. A root `AGENTS.override.md` takes precedence over root `AGENTS.md`, so edit the active one. Start a new Codex session and ask it to identify the loaded instructions and selected profile. Inspect [installation details](docs/agent-governance/adoption.md) before updating or handling an interrupted installation.

Codex discovers `AGENTS.md` along the project path; closer instructions are later in its chain, `AGENTS.override.md` wins in the same directory, and instruction-size limits apply. Files referenced by an instruction are not automatically loaded as native instruction files: the agent must follow the instruction to read them. Skills are discovered from `.agents/skills/` and can be chosen automatically or requested explicitly, e.g. `$foundation-planning`, `$foundation-implementation`, `$foundation-code-review`, or `$foundation-ui-review`. Restart Codex if newly installed skills do not appear. See [official Codex sources](docs/agent-governance/codex-compatibility.md).

## Operate

Follow [request → inspect → plan → approve when required → implement → test → review → report → merge](docs/agent-governance/workflow.md). Small, low-risk work can use a short inline plan. Have a separate reviewer inspect the actual diff and evidence; a fresh review pass is useful, but is not independent human approval. Use the [task](templates/tasks/task.md) and [review](templates/reviews/review.md) templates when useful or when the profile requires a record. [Agent operations](docs/security/agent-operations.md) governs the agent's own tool surface, session credentials, untrusted content and automated runs; [instruction hygiene](docs/agent-governance/instruction-hygiene.md) governs keeping the loaded instruction set canonical, budgeted and reconciled.

To request a review, ask: “Use `$foundation-code-review` to inspect the actual diff against the task and checks; report actionable findings first.” For UI work use `$foundation-ui-review`, provide the design source and relevant viewports, and request rendered inspection. The [worked example](examples/sample-project/worked-example.md) follows a feature through the whole lifecycle, including reviewer findings; the [blocked example](examples/sample-project/blocked-example.md) shows a destructive request and an instruction conflict stopping work, with the failing responses named.

For project-specific rules edit `.ai-governance.md` and project instructions, not managed files. A proposed exception uses the [exception record](templates/decisions/exception.md): record scope, owner, reason, compensating control, approval, and expiry. Do not override a security or approval boundary without the required authority; resolve conflicts before proceeding.

## Update and validate

Check out a reviewed newer foundation revision, review its changes, then rerun the same installer command. It verifies previously managed file hashes before writing and updates only managed files; it does not change your configuration, profile, or instruction files. Review the resulting diff and reconcile new requirements: an update can add managed documents, change which documents your configuration must point to, and add entries it must record. Run `git diff HEAD -- .ai-foundation/templates/project/ai-governance.md` (against `HEAD`, so staged installer output is still reported) and apply both the entries that template gained and the lines it changed, including its `All work` and `When relevant` reading tiers. Your configuration is never overwritten, which also means it is never updated for you. Trace the installed content by `.ai-foundation/manifest.json` (source Git revision when available plus a content digest). If locally modified managed files block an update, preserve them, reconcile the changes into project-owned rules or an exception, restore the installed version, then retry. See [adoption](docs/agent-governance/adoption.md).

In this repository:

```sh
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
```

These validate this foundation only. Application checks are defined by each project; see [quality gates](docs/testing/quality-gates.md) and [CI starter](templates/ci/README.md). No app tests are represented as passing here.
