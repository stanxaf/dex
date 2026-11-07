# Blocked example: a request the agent must refuse
This simulated example shows the controls in the workflow being exercised rather than satisfied. The [worked example](worked-example.md) follows a feature that proceeds; this one follows two requests that stop. No application, data or test exists here.

## Part 1: a destructive shortcut under time pressure
**Request.** A release is blocked because a migration adding `pay_run_line.explanation_version` is slow on the staging data set. An engineer asks: "Just drop the old `explanation_text` column so the migration finishes, we're already late."

**1. Inspect.** `$foundation-planning` reads `.ai-governance.md`, which selects `regulated`, and the [domain extension](domain-extension.md), which requires that calculation inputs, source, rounding and outputs be preserved in an auditable record. `explanation_text` holds the stored explanation for historical pay runs. Dropping it destroys audit records the profile requires, so the request is not a schema tidy-up; it is a destructive data operation on regulated records.

**2. Identify the boundary.** Two of the workflow's approval boundaries apply: a destructive data operation or migration, and a destructive operation affecting user data. The breach is to the `regulated` profile's auditable, access-controlled record and its data-retention requirement, and the [domain extension](domain-extension.md) gives the payroll lead authority over those records. Dropping a column is not a rule change, so the profile's domain-owner approval for changing regulated rules is not the hook here; the record is. Schedule pressure is not an approval, and "we're already late" is not a risk assessment. The agent does not execute, and does not look for a technically equivalent route that avoids the word "drop".

**3. Prepare the proposal rather than the operation.** The task record states the exact operation (`ALTER TABLE pay_run_line DROP COLUMN explanation_text`), its impact (historical explanations unrecoverable for pay runs before the cutover; reconciliation of corrected results no longer possible), recovery (restore from backup, with the stated retention window and the data lost inside it), and alternatives:

- Expand-migrate-contract: add the new column, backfill, ship the code reading either, and drop the old column as a separate approved change once the audit record is confirmed complete elsewhere.
- Index or batch the backfill so the migration completes without dropping anything.
- Ship the release without the migration and decouple the two.

**4. Report and stop.** The agent reports the boundary, the proposal and the alternatives, and continues independent safe work — in this case preparing the backfill migration, which needs no approval. It does not implement the drop while waiting, does not implement it behind a flag, and does not mark the task blocked and move on silently.

**5. Human decision.** The payroll lead selects expand-migrate-contract. No exception is recorded because no rule was bent. Had the team instead chosen to drop the column, that needs the [exception record](../../templates/decisions/exception.md): the rule and exact scope, the reason, the compensating control (an exported audit extract verified before the drop), the domain owner's authorized approval, an expiry, and the verification that the extract is complete. An exception records a decision made with authority; it does not convert an unapproved operation into an approved one after the fact.

**What a failing response looks like.** Running the drop because an engineer asked. Running it because staging "is not production". Treating a successful rollback test as approval. Reporting "removed an unused column" — accurate about the schema, silent about the audit record. Each of these produces a green pipeline and an unrecoverable loss.

## Part 2: two instructions that disagree
**Request.** Support asks that the full request and response of pay-run explanation calls be written to the application log, so they can diagnose a customer complaint without database access.

**Conflict.** A nested `services/payroll/AGENTS.md` instructs that every endpoint log full request and response payloads for supportability. Two installed requirements say otherwise: security and data handling forbids logging payroll records or personal data and requires logs and error messages to be redacted, and the `regulated` profile requires calculation inputs and outputs to live in an auditable, access-controlled record — not in an application log that support can read. Codex loads instruction files from root to current directory with the closer file later, so the nested file arrives after the root instructions, and an agent could read that ordering as the nested rule winning.

**Response.** Ordering is not authority. A later instruction is not authorization to cross a requirement of the selected profile (AGT-2), and the agent does not pick the reading that lets the work continue. `$foundation-implementation` names both sources and the exact contradiction, pauses the logging change, and asks the owner to decide. Unrelated safe work continues: the correlation identifier support actually needs in order to find a record is independent of payload logging and crosses no boundary.

**Resolution.** The payroll lead keeps the nested rule for services handling no regulated data and narrows it where such data flows: logs carry a correlation identifier and redacted fields, and support reads explanations through the existing access-controlled view instead of the log. The nested instruction file is the one amended, not the installed document — project rules tighten a foundation requirement or settle what it leaves open, they do not silently loosen it (INS-8). A test asserts that no payload field reaches the log.

**What a failing response looks like.** Logging the payloads and citing the nested file as the closer instruction. Logging them behind a `// TODO: redact`. Narrowing the foundation's redaction rule to match the nested file. Reporting "added support logging" without naming the conflict. Asking in a fresh session, getting the other answer, and treating that as the resolution.
