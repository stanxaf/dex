# Worked example: explain a fictional bonus calculation

This simulated example describes the workflow; it does not claim an application or tests exist here.

1. **Request / inspect:** A payroll lead asks to show a calculation explanation on a pay-run detail screen. The project uses `regulated`; inspect its design system, calculation contract, authorization and `bonus-v1` domain record. The existing API returns explanation data only to authorized pay-run viewers.
2. **Plan:** `$foundation-planning` produces a tool-neutral implementation brief proposing reuse of the existing details component, no calculation changes, an accessible disclosure, and tests for authorized access, keyboard behavior, loading and error states. The feature's acceptance criteria require the displayed explanation to match the version returned by the server. No new rule is introduced; if the API or permissions must change, stop for the required approval.
3. **Implement:** `$foundation-implementation` works against the accepted task and project-owned rules. Reuse the component and localization pattern. The fictional fixture input `5` and output `10` test display only; the application domain owner independently verifies any real fixture.
4. **Test:** Run the project-configured unit and integration commands, keyboard/accessibility checks and rendered desktop/mobile inspection. Record commands and outcomes; missing infrastructure blocks any required gate.
5. **Review:** A separate `$foundation-code-review` pass reads the actual diff and evidence. Example finding: the disclosure lost focus when refreshed; fix and rerun the keyboard regression test. `$foundation-ui-review` checks states and screenshots. An independent human validates regulated evidence and approves release.
6. **Report / merge:** Record changed files, test evidence, remaining risks and human approvals on the PR; merge only when required checks and branch protection pass. Obtain production deployment approval separately.

## Choosing an implementer

These hypothetical requests use the [coder-selection rules](../../docs/agent-governance/workflow.md#coder-selection-and-handoffs). The named tool is a handoff target, not a claimed integration.

| Situation | Expected response |
| --- | --- |
| No coder preference; “plan the explanation disclosure” | An unnamed implementation brief listing the intended changes, likely files, scope, acceptance criteria, checks and completion-report requirements. |
| “Today we use Kiro” | Use Kiro for subsequent handoffs in this chat; leave instruction files untouched. |
| Project default is another coder; “ask Kiro for this task” | Target Kiro for this task; keep the saved project default. |
| Project default is Kiro; “for this chat, you are the coder” | Use the current agent for implementation requests in this chat; keep the saved project default. |
| Session choice is Kiro; “you implement this change” | The current agent implements this task, then later handoffs return to the session choice. |
| “We use Kiro here” | Treat it as a current-chat choice without saving it. |
| “Save Kiro as this project's default coder” | Record the preference in project-owned instructions or configuration; keep the shared foundation neutral. |
| Kiro returns only “complete” | Inspect the diff and obtain the required evidence before accepting the implementation. |

For example, the brief can name the existing pay-run detail component, its disclosure tests and its documentation as likely files, with exact paths determined during inspection. It requests a report of changed files, behavior, checks and results, and blockers. Its completion clause reads: “Do not call complete unless the explanation matches the server's version, authorized access and keyboard behavior are verified, loading and error states are covered, and the project's required checks for this checkpoint pass.” A coder selection does not grant approval to change payroll rules or release to production.

## Checkpoint examples

These are fictional illustrations; actual project, profile and host rules determine the checks.

- **Explore:** A designer or developer asks to try a layout. Inspect its rendered view and affected interactions, report it as ready for feedback, and name permitted deferred checks. Do not present the change as consumer-ready.
- **Stricter local rule:** A project requires a documentation check whenever a component page changes. Run it at that checkpoint even during exploration.
- **Work in progress:** The user requests a commit to a known work-in-progress branch. Apply that destination's rules and report permitted deferrals; do not assume an unknown branch is safe or that a commit is a release.
- **Prepare for consumers:** Complete applicable tests and documentation. A separate reviewer inspects the actual diff and current evidence before merge; rerun checks if required or if the evidence is insufficient. Meet merge gates and obtain any required release approval.

## Selecting checks

These hypothetical examples assume no stricter required check. Each choice depends on the actual context and current evidence.

- **Copy:** Review the diff; inspect the affected layout if the new text could overflow or change responsive behavior.
- **Existing button variant:** Review the prop, component usage and placement. Outline to primary changes appearance even if tokens are unchanged. Current evidence may be enough; check the affected theme, contrast or rendered view if the context or requested outcome makes them uncertain. Do not add dark-mode, viewport or browser checks solely because a UI prop changed.
- **Responsive layout:** Inspect affected widths and states; add interaction checks if behavior also changed.
- **Theme token:** Check affected themes, surfaces and representative consumers, including contrast where relevant.
- **Keyboard or state logic:** Exercise the changed interactions and focus behavior with targeted tests; a screenshot is insufficient.
- **Shared API:** Check affected callers and contracts; test a broader journey if integration risk warrants it.
