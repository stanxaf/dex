# AI Engineering Foundation

A portable set of engineering standards, approval boundaries, Codex skills, and review templates for software projects. It is a **starting point**, not an application, security product, legal compliance certification, or a guarantee that an agent obeys instructions. Use CI, repository permissions, sandboxing, human approvals, and independent review to enforce consequential controls.

## Adopt in a project

Requires Python 3.9+ and a local checkout of this foundation. **Ask an AI agent to do it** — say this in the project, naming the checkout:

> Set up the DEX AI Foundation in this project. The checkout is at `<path>`; read `docs/agent-governance/setup.md` there and follow it.

That names a file rather than a skill, so it works before anything is installed. The agent then follows [AI-guided setup](docs/agent-governance/setup.md): it inspects your existing instructions, installs the managed files, reconciles contradictions with your rules before connecting anything, connects the foundation to your active instruction file without editing your rules, fills every configuration entry the repository evidences, and hands back the decisions only you can make. Once installed, `$foundation-setup` reaches the same procedure, so a resumed or repeated setup needs no path.

To run the installer yourself instead:

```sh
python3 scripts/install.py /path/to/project --profile baseline
```

Choose `baseline`, `web-saas`, or `regulated`; see [profiles](profiles/README.md). The installer copies standards into `.ai-foundation/`, installs skills under `.agents/skills/`, and creates `AGENTS.md` and `.ai-governance.md` only if absent. It reports existing instruction files and refuses managed-file collisions or locally modified managed files. It never merges or replaces an existing `AGENTS.md`, and it creates a root one only when no instruction file that applies to the project exists — in the project, above it up to the Git root, or at the known global locations. Creating it would otherwise activate the foundation beside rules nobody has read. It reports all of those, and says the global list is not exhaustive.

To connect it by hand: reconcile every applicable instruction file first — global, ancestor, root and nested — then check whether the active file already instructs the agent to follow `.ai-governance.md`. A project rule that is stricter than the foundation is not a conflict and needs no decision; only a genuinely looser or contradictory rule does. **A mention is not proof of connection** — the text may forbid the file, quote it, or point at a path that moved — so read the sentence before deciding. If it genuinely activates the foundation, add nothing. If it does not, **append this line, keeping everything already there**:

> Read `.ai-governance.md`, then the foundation workflow, selected profile and standards they reference, and follow them.

**Installing files is not finishing setup.** The installer says so, and prints which conditions remain. Setup is complete only when the managed files are installed and verified, contradictions with existing instructions are resolved, the active instruction file instructs the agent to follow `.ai-governance.md` exactly once, every evidence-backed entry is filled, **every handoff decision has been answered by a human and recorded**, and the result is reviewed and committed. Asking a question is not getting an answer: while any decision is outstanding the status is *files installed, setup outstanding*. An unset entry is not a passed check.

**Commit `.ai-foundation/`, `.agents/skills/foundation-*/`, your active instruction file and `.ai-governance.md`** — the foundation skills by name, not the whole `.agents/skills/` directory, which may hold skills your project owns. Distribution is a local copy ([ADR 0001](docs/decisions/0001-distribution.md)), so the committed copy is the installed version: versioning it makes each update a reviewable diff, lets the hash check tell a local edit from an upstream change, makes a bad revision revertible, and means a deleted installation can be restored. An uncommitted one cannot. Do not `.gitignore` it. The agent proposes the commit and does not make it for you.

Review all reported root and nested instruction files, as well as global instructions; the installer inventories filenames but cannot detect semantic conflicts or enforce inclusion. A root `AGENTS.override.md` takes precedence over root `AGENTS.md`, so the override is the active file when both exist. Start a new Codex session and ask it to identify the loaded instructions and selected profile. Inspect [installation details](docs/agent-governance/adoption.md) before updating or handling an interrupted installation.

Codex discovers `AGENTS.md` along the project path; closer instructions are later in its chain, `AGENTS.override.md` wins in the same directory, and instruction-size limits apply. Files referenced by an instruction are not automatically loaded as native instruction files: the agent must follow the instruction to read them. Skills are discovered from `.agents/skills/` and can be chosen automatically or requested explicitly, e.g. `$foundation-setup`, `$foundation-planning`, `$foundation-implementation`, `$foundation-code-review`, or `$foundation-ui-review`. Restart Codex if newly installed skills do not appear. See [official Codex sources](docs/agent-governance/codex-compatibility.md).

## Operate

Follow [request → inspect → plan → approve when required → implement → test → review → report → merge](docs/agent-governance/workflow.md). Small, low-risk work can use a short inline plan. Have a separate reviewer inspect the actual diff and evidence; a fresh review pass is useful, but is not independent human approval. Use the [task](templates/tasks/task.md) and [review](templates/reviews/review.md) templates when useful or when the profile requires a record. [Agent operations](docs/security/agent-operations.md) governs the agent's own tool surface, session credentials, untrusted content and automated runs, and is read for all work; the [deployment gate](docs/security/deployment-gate.md) adds the conditions an automated deployment must meet and is read only before one. [Instruction hygiene](docs/agent-governance/instruction-hygiene.md) governs keeping the loaded instruction set canonical, budgeted and reconciled.

Say “try this layout” for an exploratory feedback checkpoint, or “make this ready for consumers” when the full applicable checks and review are needed. The [checkpoint guidance](docs/agent-governance/workflow.md#exploration-and-checkpoints) explains what may be deferred and what still binds; project and profile rules may require checks earlier.

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
