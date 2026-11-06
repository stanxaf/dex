# Codex compatibility and assumptions

Checked against official OpenAI documentation on 2026-11-06:

- [AGENTS.md discovery and precedence](https://developers.openai.com/codex/guides/agents-md): one instruction file per directory, override before regular, root-to-current path, and size limit.
- [Agent skills](https://developers.openai.com/codex/skills/create-skill): repo `.agents/skills/<name>/SKILL.md`, `name` and `description` frontmatter, explicit `$skill-name` and implicit discovery. Skill selection is not guaranteed and duplicate names can coexist.
- [Sandbox and approvals](https://developers.openai.com/codex/sandbox): permission boundaries and approvals are independent; `.agents` can be protected even inside a writable workspace.
- [Configuration](https://developers.openai.com/codex/config-basic): project config layers require a trusted project and have their own precedence; this foundation does not change them.
- [Non-interactive workflows](https://developers.openai.com/codex/noninteractive): `codex exec` can be used in CI with appropriate permissions; this foundation does not require it.

Assumptions: users launch Codex within the consuming Git repository and explicitly link existing instructions to the configuration. Discovery is verified by the user in their Codex environment; this repository's checks cannot prove runtime selection, model compliance, or organization's approval settings. Product behavior and protected paths may vary with version and environment; consult current documentation when upgrading. The framework deliberately avoids undocumented hooks or custom agent orchestration.
