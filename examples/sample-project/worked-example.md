# Worked example: explain a fictional bonus calculation

This simulated example describes the workflow; it does not claim an application or tests exist here.

1. **Request / inspect:** A payroll lead asks to show a calculation explanation on a pay-run detail screen. The project uses `regulated`; inspect its design system, calculation contract, authorization and `bonus-v1` domain record. The existing API returns explanation data only to authorized pay-run viewers.
2. **Plan:** `$foundation-planning` proposes reuse of the existing details component, no calculation changes, an accessible disclosure, and tests for authorized access, keyboard behavior, loading and error states. The feature's acceptance criteria require the displayed explanation to match the version returned by the server. No new rule is introduced; if the API or permissions must change, stop for the required approval.
3. **Implement:** `$foundation-implementation` works against the accepted task and project-owned rules. Reuse the component and localization pattern. The fictional fixture input `5` and output `10` test display only; the application domain owner independently verifies any real fixture.
4. **Test:** Run the project-configured unit and integration commands, keyboard/accessibility checks and rendered desktop/mobile inspection. Record commands and outcomes; missing infrastructure blocks any required gate.
5. **Review:** A separate `$foundation-code-review` pass reads the actual diff and evidence. Example finding: the disclosure lost focus when refreshed; fix and rerun the keyboard regression test. `$foundation-ui-review` checks states and screenshots. An independent human validates regulated evidence and approves release.
6. **Report / merge:** Record changed files, test evidence, remaining risks and human approvals on the PR; merge only when required checks and branch protection pass. Obtain production deployment approval separately.

## Checkpoint examples

These are fictional illustrations; actual project, profile and host rules determine the checks.

- **Explore:** A designer or developer asks to try a layout. Inspect its rendered view and affected interactions, report it as ready for feedback, and name permitted deferred checks. Do not present the change as consumer-ready.
- **Stricter local rule:** A project requires a documentation check whenever a component page changes. Run it at that checkpoint even during exploration.
- **Work in progress:** The user requests a commit to a known work-in-progress branch. Apply that destination's rules and report permitted deferrals; do not assume an unknown branch is safe or that a commit is a release.
- **Prepare for consumers:** Complete applicable tests and documentation. A separate reviewer inspects the actual diff and current evidence before merge; rerun checks if required or if the evidence is insufficient. Meet merge gates and obtain any required release approval.
