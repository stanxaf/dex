# Quality gates

Projects MUST record actual commands and required status checks in `.ai-governance.md`; configure branch protection or equivalent so a missing, failing, or unrun required check blocks merge. The repository owner decides any exception, recorded as the workflow requires. A required check that is unavailable is not a pass.

Apply checks at the [workflow checkpoints](../agent-governance/workflow.md#exploration-and-checkpoints); project and profile rules may require them earlier.

| Area | Minimum decision |
| --- | --- |
| Formatting/lint and type checks | Run configured checks for affected code; baseline may omit unsupported type tooling with rationale. |
| Unit/integration | Cover changed behavior and trust boundaries; use representative data and isolate external services. |
| End-to-end | Select critical journeys where integration risk warrants; SaaS profiles define required journeys. |
| Accessibility and visual regression | Test relevant interactive UI and viewports; automate where configured, review screenshots and baseline changes. |
| Dependencies and secrets | Scan supported dependency manifests and all changes for credentials; investigate findings. |
| Database migration | For schema/data changes validate migration on realistic disposable data, integrity, compatibility and recovery. |
| Review/approval | Review actual diff and evidence; obtain the workflow's and the profile's approvals. |

Set required checks in Git hosting; a workflow file alone does not enforce branch protection. The [application CI starter](../../templates/ci/README.md) is opt-in and needs real project scripts. The workflow's evidence rules govern weakening checks and classifying failures.
