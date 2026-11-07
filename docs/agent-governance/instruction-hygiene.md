# Instruction hygiene
An adopted foundation fails quietly when its rules are duplicated, contradictory, unread or unverifiable. This document governs how a project writes and maintains the instruction set agents actually load. [Adoption](adoption.md) covers installing it; this covers keeping it worth loading. Requirements are numbered so a review finding can cite one.

## Structure
- **INS-1** One canonical location per rule. A rule copied into a second instruction file drifts from the first, and an agent then holds two authorities and resolves the conflict itself.
- **INS-2** Project files point to foundation documents rather than restating them. Restating is the most common adoption error: the copy looks like agreement and becomes a contradiction at the first upstream change. Put project-specific additions in project-owned files, as `.ai-governance.md` directs.
- **INS-3** Each rule is one testable requirement. A requirement a reviewer cannot cite and check is not operational; a sentence carrying four requirements cannot be cited at all. Number rules where they are referenced in findings.
- **INS-4** A prohibition states the permitted alternative. "Do not do X" without "do Y instead" produces invention, which is usually worse than the thing prohibited.

## Size and reading tiers
- **INS-5** Record the reading tier of every document the configuration names: read for all work, read when relevant, or reference only. Everything in the first tier competes with the task for the agent's attention on every request, so the tier is a cost decision, not a formality.
- **INS-6** Keep always-loaded instructions within a recorded budget. Codex enforces an instruction-size limit; exceeding it drops guidance you believe is loaded, without saying so. A document referenced by an instruction is not automatically loaded either — the agent must follow the instruction to read it, so a reference is a weaker control than inclusion.

## Maintenance
- **INS-7** Reconcile the full instruction set on a schedule, not only at adoption. Global, root, nested, override and fallback instruction files accumulate independently. Record the date of the last reconciliation and who performed it.
- **INS-8** Project rules may tighten a foundation requirement or settle a choice it leaves open. Loosening one requires the [exception record](../../templates/decisions/exception.md) with owner, scope, compensating control and expiry; a project file that contradicts a foundation requirement without that record is a defect, not a local preference.
- **INS-9** A rule nothing can verify is converted into a check or removed. Unenforceable prose accumulates, and every line of it dilutes the rules that do carry weight.
- **INS-10** Changing instructions is a reviewable change. Diff it, state the intended effect on agent behavior, and do not bundle it with the work it governs.

A reconciled instruction set still proves nothing about compliance: discovery, selection and adherence happen at runtime in the agent's environment and must be verified there. See [Codex compatibility](codex-compatibility.md) for what the platform guarantees and what it does not.
