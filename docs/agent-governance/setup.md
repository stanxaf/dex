# AI-guided setup

This is the procedure an agent follows to set this foundation up in a project. A human should not have to run the installer or work through a checklist: they ask once, the agent does the mechanical work, and the agent comes back with a short list of decisions only a human can make.

**Starting instruction.** The human says this, naming a reviewed foundation checkout:

> Set up the DEX AI Foundation in this project. The checkout is at `<path>`; read `docs/agent-governance/setup.md` there and follow it.

That works before anything is installed, because it names a file path rather than a skill. [AGT-22](../security/agent-operations.md) is what permits following it: an agent may read an instruction set read-only before it knows the rules in it. After setup, `$foundation-setup` reaches this same procedure from the installed copy at `.ai-foundation/docs/agent-governance/setup.md`, so re-running setup or finishing an interrupted one needs no path.

## What this procedure must never do

- **Never invent an owner, approver, permission, credential scope, approval mode, egress rule, readable data class, or branch-protection setting.** A repository cannot evidence these; they are decisions with consequences. A plausible guess in a governance file is worse than a blank, because the blank is visible and the guess is not. Record what you observed, and hand the decision over.
- **Never remove, rewrite or reorder an existing project rule** to make room for the foundation. Existing instructions are project-owned and may encode decisions you cannot see. You add a pointer; you do not edit their content.
- **Never claim setup is complete because files were installed.** Those are different states, defined below.
- **Never edit a nested instruction file.** List it for human review.

Work through the whole procedure in one pass and report once, as the [workflow](workflow.md) expects. Stop early only for the reasons it names: an approval boundary, a contradiction you cannot resolve, or verification you cannot run. Do not return after each step for confirmation that the evidence already provides.

## 1. Establish the state before changing anything

Read, do not write. Record:

- Is `.ai-foundation/manifest.json` present? If yes the project is already installed — note its `content_sha256` and `source_revision`, and treat this run as an update or a resumed setup. If no, this is a fresh project.
- Which instruction files exist, across all four scopes? In the project, check the root and every directory that is not `.git`, `.ai-foundation`, `node_modules`, `vendor` or `.venv`, for `AGENTS.md`, `AGENTS.override.md` and any configured fallback filename. Above the project, search up to the Git root. Globally, check the effective Codex home — `CODEX_HOME` when set, otherwise `~/.codex`. Count a symlink as present, and record paths rather than copying contents out of files that are not the project's.
- Does `.ai-governance.md` exist, and which of its entries are already filled? A partially completed configuration is the normal case for a resumed setup; keep every answer already there.
- What does the project actually contain: package manifests, scripts, CI workflows, test and lint configuration, architecture or design documentation, existing decision records.

## 2. Install, update, or neither

Decide which of the three applies before running anything.

**Already installed and no update wanted.** If `.ai-foundation/manifest.json` is present and intact and nobody asked for an update, you need no checkout and no installer run. The procedure, the documents and the skills are already in the project; continue from step 3 using `.ai-foundation/`. A resumed or repeated setup is the normal case here, and `$foundation-setup` reaches this file without a path.

**Installing or updating.** Both need a **reviewed** foundation checkout — reviewed because the installer copies whatever that checkout contains into the project, so its contents are the thing being trusted. Never install from an unreviewed or unknown checkout to save a step. Then run:

```sh
python3 scripts/install.py /path/to/project --profile <baseline|web-saas|regulated>
```

`--profile` is used only when creating `.ai-governance.md`; it never rewrites an existing one. Updating uses the same command: the installer verifies every previously managed file against its recorded hash and refuses to proceed if one was modified locally.

**If the installer refuses, stop and report.** Do not delete files or directories to force it through. Two refusals are common and each means something specific:

- *`existing .ai-foundation has no manifest`* — the directory exists but the installer cannot prove it owns the contents. Inspect what is actually there. If files are present, they are not yours to remove; report them. If only empty directories remain, a previous install was partly deleted, and removing **verified-empty** directories is the repair. Count the files before removing anything, and never delete a directory that still holds one.
- *`managed file missing or modified`* — someone edited an installed file. That is either a mistake to revert deliberately or a rule that belongs in a project-owned file; both are human decisions.
- *`project-owned path is not a regular file`* or *`destination exists and is not a regular file`* — something stands where an instruction file or the configuration belongs: a directory named `AGENTS.md`, or a symlink whose target is gone. Every destination this run could create is validated before the first file is written, so a refusal here means nothing was installed and nothing is left to clean up. Fix the path and run it again.

The installer prints `FILES INSTALLED - SETUP IS NOT COMPLETE` with the active instruction file, what it mentions, what to reconcile, and what you may commit. Treat that as input to the next steps, not as a result to relay.

## 3. Reconcile the existing instructions, then connect

Codex reads the file closest to the work, and in the same directory an override file wins. So the **active instruction file** is the repository root's `AGENTS.override.md` if it exists, otherwise the root `AGENTS.md` — and otherwise a **configured fallback filename**.

Fallbacks matter more than they look. `project_doc_fallback_filenames` lets a project keep its instructions under another name, and that file loads only while no `AGENTS.md` is present. **Creating `AGENTS.md` beside it takes precedence and stops it loading at all**, so the project's rules disappear from discovery while still sitting in the repository looking authoritative. Add the link to *that* file instead; the installer refuses to create `AGENTS.md` in this case and names the file.

Three details decide whether you find those files at all:

- **Several config sources, and profiles are separate files.** `codex -p <name>` layers `$CODEX_HOME/<name>.config.toml` over the base `$CODEX_HOME/config.toml`, so a fallback declared in a profile file is live whenever that profile is selected. The installer reads the base config, every `*.config.toml` profile file beside it, the project's `.codex/config.toml`, and any ancestor project config up to the Git root. Measured against codex-cli 0.155.1: the base top-level key is effective; a profile **file** is effective under `-p <name>`; a project `.codex/config.toml` is effective **when the project is trusted**, both at the Git root and in a nested directory, and a root declaration applies while working under it; and a `[profiles.<name>]` **table** inside a config was *not* applied even with that profile selected. Trust is required — `trust_level = "untrusted"`, or no entry at all, and the declaration is ignored — and the `[projects."..."]` key must be the **canonical** path. An entry written against a symlinked form, such as `/var/...` where the real path is `/private/var/...` on macOS, silently fails to match; mistaking that for project configs being ignored altogether is exactly the error an earlier revision of this document made. Everything found is still reported, and a file any of it names is never displaced, because the installer cannot know which profile will be selected or how layering changes between versions. Preserving a file costs nothing; displacing a live instruction file costs the project its rules. Confirm your own version with `codex debug prompt-input`, adding `-p <name>` to check a profile.
- **Three locations.** A configured name loads from the project root, from nested directories, and from ancestors up to the Git root. Checking only the root misses the rest.
- **Uncertainty is not absence.** On Python 3.9 and 3.10 there is no TOML parser available, so the installer reads that one key with a narrow pattern. If a config declares the key in a form it cannot read, it reports `UNCERTAIN` and defers activation rather than reporting no fallbacks. Read the config yourself and connect by hand, or run the installer on 3.11 or newer. A silent "none" here is the failure mode worth avoiding.

Two more discovery details, both verifiable with `codex debug prompt-input`:

- **A symlinked instruction file still loads.** Treat it as present and reconcile it; the target is a real rule set. Never write *through* the symlink, and never edit the target to make room for the foundation.
- **Among global files, only the override loads when both exist.** `AGENTS.override.md` in the Codex home supersedes `AGENTS.md` there, so reconcile the override first and do not assume both are in effect. Confirm which the environment actually loads rather than inferring from what is on disk.

### 3a. Reconcile before activating

Read the active file in full, and every nested instruction file, before changing anything. Activation is what gives the foundation authority in this project, so a contradiction that exists at that moment becomes two authorities the agent must choose between — which is the situation the workflow forbids it from resolving silently.

Read everything that applies, not only what is inside the project: the active root file, every nested instruction file, instruction files above the project up to the Git root, and the global or tool-level instructions your environment loads. The installer lists the first three and the known global locations; confirm the last against your own environment, because that list cannot be exhaustive. An unreconciled instruction above the project binds exactly as firmly as one inside it.

Then sort what you find, and **only escalate what actually needs a human**:

- **Compatible or stricter project rule** — nothing to do. A project may tighten the foundation freely, so a stricter convention, an extra check or a narrower permission is not a conflict and is not worth a question.
- **Genuine contradiction** — a rule permitting what the foundation prohibits, an approval the project waives, a conflicting owner or reviewer. These need a human: **do not activate while one is unresolved**, and do not resolve one by editing the project's rule. A looser rule needs the exception record the workflow requires, or withdrawal, and either is the human's call.

Resolve the routine parts yourself and say what you did. Asking a human to confirm something the repository already answers wastes the thing that is scarce, and a handoff padded with non-questions buries the decisions that matter.

Note whether the active file is generated or managed by another tool, and **do not assume what that means — verify it.** Many tools write a delimited block and preserve everything around it, in which case appending outside the block is perfectly durable. Others rewrite the whole file, in which case appending is not connecting at all. The difference is testable, so test it rather than guessing in either direction:

- If the file has start and end markers, read the generator's upsert logic, or run it against a *copy* of the file with your line appended and compare. Preserved means `before + block + after`, with your text in `before` or `after`.
- If additions genuinely do not survive, use the most durable location that tool supports — a sibling instruction file the tool does not own, or the location its documentation designates — and report what you chose and why.
- Record the evidence either way. "The framework manages this file" is not a finding; "the framework replaces only the text between its markers, verified by running its writer on a copy" is.

### 3b. Connect

A mention of `.ai-governance.md` is **evidence to review, not proof of activation**. The text may forbid reading it, quote it as an example, describe it in a changelog, or point at a path that no longer exists. Read the surrounding sentence and decide whether it actually instructs the agent to follow the configuration:

- **It does** — the foundation is already connected. Do not add a second link; differently worded pointers to the same file are what INS-1 warns about, because two copies drift.
- **It does not, or it is ambiguous** — treat it as not connected, and say in the handoff what the existing text says and why you read it that way. A human confirms before you add anything.
- **Not mentioned at all** — append this line, leaving every existing rule in place:

  > Read `.ai-governance.md`, then the foundation workflow, selected profile and standards they reference, and follow them.

If the installer created `AGENTS.md` from the template, it already carries the line and there is nothing to add. That only happens in a project with no instruction file anywhere, because creating the root file *is* activation: where any other instruction file exists the installer deliberately creates nothing and reports `NOT ACTIVATED ON PURPOSE`. In that case reconcile under 3a first, then create the root instruction file yourself and add the link — a project with nested rules and no root file is the case most likely to hide a contradiction, since the nested rules were written without a root to defer to.

If both root files exist, the override is active: connect there, and report the other so the human can decide whether it is stale. Never edit a nested instruction file.

## 4. Fill the configuration from evidence

Complete every entry in `.ai-governance.md` that the repository evidences, and cite the evidence in the entry so a reviewer can check it. Leave an existing answer alone unless it is demonstrably wrong, and say so if it is.

| Entry | Fill from | When there is no evidence |
| --- | --- | --- |
| Selected profile | A networked or multi-tenant service suggests `web-saas`; financial, regulated or audited calculations suggest `regulated`; otherwise `baseline` | Propose one with your reasoning and let the human confirm |
| All work / When relevant | Copy the lists from the installed template verbatim | — |
| Project architecture and existing instructions | Architecture docs, README, and the instruction files found in step 1 | State none found |
| Design system | Token files, component library, Storybook, design documentation | State none established |
| Applicable stack extensions | Detected stack against `.ai-foundation/templates/stacks/` | State none |
| Required checks and exact commands | Package scripts, Makefile, CI workflow, lint/type/test configuration | Name the checks that do not exist rather than inventing commands |
| Domain requirements, decision records and exceptions | Decision records already in the repository, with their expiry and review dates | State none |
| Reading tiers and reconciliation | Tiers from the template; today's date for the reconciliation | Leave the reconciling person for the handoff unless the human has given their name |

A command you have not run is a claim, not evidence. If you record a check, say whether you ran it.

## 5. Group what is left into a short handoff

Everything below is an authorization, ownership or security decision. Do not fill it. **Presenting a decision is not obtaining one**: an entry stays outstanding until a human answers it and the answer is recorded in `.ai-governance.md`. Asking well is progress, not completion, and the work each unanswered entry governs stays unreconciled meanwhile.

Present it as four groups, with the evidence you gathered attached so the human decides rather than researches:

1. **People.** Project owner and approvers; reviewers; release and recovery owners.
2. **Repository enforcement.** Branch protection and which checks are required to merge. These live in the Git host, not the repository, so you can report the workflow files you found but not the settings in force.
3. **Agent session limits.** Permitted tools and MCP servers (AGT-4); approval mode and sandbox posture (AGT-6); permitted network egress (AGT-7); readable data classes (AGT-9). Where configuration files show what is currently wired up, present that as observation, not as permission.
4. **Automation.** Whether non-interactive or CI agent runs are permitted (AGT-12), and if an automated deployment exists, the deployment gate (AGT-15 to AGT-21).

Keep it to these groups and one question each. An unset entry is not a passed check and not a statement that the requirement does not apply: until it is answered, the work it governs is unreconciled.

## 6. Report status honestly

**Files installed** means the managed files and manifest are in place. That is step 2 of six.

**Setup is complete** only when all of the following hold:

1. Managed files and the manifest are installed and **hash-verified**. The manifest existing is not verification: recompute the SHA-256 of every path in `.ai-foundation/manifest.json` and compare, and say how many matched. Re-running the installer also verifies, because it refuses on a mismatch, but then report that as the evidence rather than claiming a check you did not run.
2. Contradictions between existing instructions and the foundation are resolved, or recorded as approved exceptions.
3. The active instruction file instructs the agent to follow `.ai-governance.md`, once, in a file that is not rewritten by another tool.
4. Every evidence-backed entry in `.ai-governance.md` is filled, with its evidence.
5. Every handoff decision has been **answered by a human and recorded** in `.ai-governance.md`. Having asked is not having an answer.
6. The installed files have been reviewed and committed, when the human chooses to commit.

Report each condition as holding or not, and name what is outstanding. Nothing here lets a presented-but-unanswered decision count as met: while any entry is unanswered the status is *files installed, setup outstanding*, and reporting that plainly is the useful answer. Do not describe setup as complete, done, or ready on the strength of the mechanical steps alone.

## 7. Explain what to commit and why

**Do not commit, stage or push unless the human asks.** Committing is their decision and it is also when the governance change becomes real for everyone else. Review the diff, name the paths below, and stop there.

The paths that belong in one reviewable change:

- `.ai-foundation/` — the managed content and `manifest.json`.
- `.agents/skills/foundation-*/` — **the foundation skills by name, not the whole `.agents/skills/` directory.** A project may keep its own skills alongside them, and sweeping the directory into a governance commit mixes someone else's work into it.
- The active instruction file — project-owned, and now carrying the link.
- `.ai-governance.md` — project-owned, and the record of every decision above.

Why versioning this matters, rather than treating it as generated output: [ADR 0001](../decisions/0001-distribution.md) distributes the foundation as a local copy rather than a runtime dependency, so the committed copy *is* the installed version, and four things follow from it. An update arrives as a reviewable diff instead of an opaque refresh. The hash check can tell a local edit from an upstream change, which is the one thing it exists to do and the one thing it cannot do if the baseline was never recorded. A bad revision is revertible like any other commit. And the installation survives being deleted locally — an uncommitted install that is removed is simply gone, with nothing to restore from.

So do not add these paths to `.gitignore`, and if they are already ignored, say so: an ignored installation looks healthy right up to the point where it cannot be recovered or verified.
