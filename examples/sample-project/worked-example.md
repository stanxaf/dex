# Worked example: explain a fictional bonus calculation

This simulated example describes the workflow; it does not claim an application or tests exist here.

1. **Request / inspect:** A payroll lead asks to show a calculation explanation on a pay-run detail screen. The project uses `regulated`; inspect its design system, calculation contract, authorization and `bonus-v1` domain record. The existing API returns explanation data only to authorized pay-run viewers.
2. **Plan:** `$foundation-planning` proposes reuse of the existing details component, no calculation changes, an accessible disclosure, and tests for authorized access, keyboard behavior, loading and error states. The feature's acceptance criteria require the displayed explanation to match the version returned by the server. No new rule is introduced; if the API or permissions must change, stop for the required approval.
3. **Implement:** `$foundation-implementation` works against the accepted task and project-owned rules. Reuse the component and localization pattern. The fictional fixture input `5` and output `10` test display only; the application domain owner independently verifies any real fixture.
4. **Test:** Run the project-configured unit and integration commands, keyboard/accessibility checks and rendered desktop/mobile inspection. Record commands and outcomes; missing infrastructure blocks any required gate.
5. **Review:** A separate `$foundation-code-review` pass reads the actual diff and evidence. Example finding: the disclosure lost focus when refreshed; fix and rerun the keyboard regression test. `$foundation-ui-review` checks states and screenshots. An independent human validates regulated evidence and approves release.
6. **Report / merge:** Record changed files, test evidence, remaining risks and human approvals on the PR; merge only when required checks and branch protection pass. Obtain production deployment approval separately.
