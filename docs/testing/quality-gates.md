# Quality gates

Projects MUST record actual commands and required status checks in `.ai-governance.md`; configure branch protection or equivalent so a missing, failing, or unrun required check blocks merge. The repository owner decides any exception with scope, risk, compensating control and expiry. A required check that is unavailable is not a pass. Independent review and explicit human approval apply where required by the profile.

| Area | Minimum decision |
| --- | --- |
| Formatting/lint and type checks | Run configured checks for affected code; baseline may omit unsupported type tooling with rationale. |
| Unit/integration | Cover changed behavior and trust boundaries; use representative data and isolate external services. |
| End-to-end | Select critical journeys where integration risk warrants; SaaS profiles define required journeys. |
| Accessibility and visual regression | Test relevant interactive UI and viewports; automate where configured, review screenshots and baseline changes. |
| Dependencies and secrets | Scan supported dependency manifests and all changes for credentials; investigate findings. |
| Database migration | For schema/data changes validate migration on realistic disposable data, integrity, compatibility and recovery. |
| Review/approval | Review actual diff and evidence; obtain approvals for operations in the workflow and the selected profile. |

The foundation CI runs structural checks and installer tests only. [Application CI starter](../../templates/ci/README.md) is opt-in and requires real project scripts and infrastructure. Set required checks in Git hosting; a workflow file alone does not enforce branch protection. Never delete tests, suppress scans, or refresh screenshots merely to clear a failure. Record related, proven pre-existing, and unknown failures separately.
