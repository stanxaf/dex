import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.source = self.root / 'source'
        self.project = self.root / 'project'
        # The installer reports global instruction files from the home directory, so
        # an isolated HOME keeps these tests independent of the developer's machine.
        self.home = self.root / 'home'
        # None means "let the installer default to ~/.codex under the isolated HOME".
        self.codex_home = None
        self.source.mkdir()
        self.project.mkdir()
        self.home.mkdir()
        for name in ('docs', 'profiles', 'skills', 'templates', 'scripts'):
            shutil.copytree(ROOT / name, self.source / name)

    def tearDown(self):
        self.temp.cleanup()

    def env(self):
        environment = dict(os.environ)
        environment['HOME'] = str(self.home)
        environment.pop('USERPROFILE', None)
        # Drop any inherited CODEX_HOME so a developer's own setting cannot leak in.
        environment.pop('CODEX_HOME', None)
        if self.codex_home is not None:
            environment['CODEX_HOME'] = str(self.codex_home)
        return environment

    def install_into(self, project, *args, success=True):
        cmd = [sys.executable, str(self.source / 'scripts/install.py'), str(project), *args]
        result = subprocess.run(cmd, text=True, capture_output=True, env=self.env())
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        return result

    def run_install(self, *args, success=True):
        return self.install_into(self.project, *args, success=success)

    def write_global_instruction(self, text, name='AGENTS.md'):
        base = self.codex_home if self.codex_home is not None else self.home / '.codex'
        path = base / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def manifest(self):
        return json.loads((self.project / '.ai-foundation/manifest.json').read_text())

    def test_fresh_install_and_profile(self):
        self.run_install('--profile', 'regulated')
        self.assertIn('Selected profile: regulated', (self.project / '.ai-governance.md').read_text())
        self.assertIn('.ai-governance.md', (self.project / 'AGENTS.md').read_text())
        self.assertTrue((self.project / '.agents/skills/foundation-planning/SKILL.md').is_file())
        self.assertIn('.agents/skills/foundation-planning/SKILL.md', self.manifest()['files'])
        self.assertIn('.ai-foundation/docs/engineering/standards.md', self.manifest()['files'])

    def test_fresh_install_names_complete_installed_profile_paths(self):
        # The config must name every profile by a path that resolves from the project
        # root. An abbreviated fragment such as `web-saas/PROFILE.md` reads fine but
        # points nowhere, so a regulated adopter silently loses two of three profiles.
        for profile in ('baseline', 'web-saas', 'regulated'):
            with self.subTest(profile=profile):
                project = self.root / ('project-' + profile)
                project.mkdir()
                result = self.install_into(project, '--profile', profile)
                config = (project / '.ai-governance.md').read_text()
                self.assertIn('Selected profile: ' + profile, config)
                named = re.findall(r'`\.ai-foundation/(profiles/[^`]+\.md)`', config)
                for expected in ('profiles/baseline/PROFILE.md',
                                 'profiles/web-saas/PROFILE.md',
                                 'profiles/regulated/PROFILE.md'):
                    self.assertIn(expected, named, config)
                for relative in named:
                    self.assertTrue((project / '.ai-foundation' / relative).is_file(),
                                    'config names an uninstalled profile: ' + relative)

    def test_fresh_install_reports_setup_is_not_complete(self):
        result = self.run_install('--profile', 'baseline')
        self.assertIn('FILES INSTALLED - SETUP IS NOT COMPLETE', result.stdout)
        # The installer created AGENTS.md from the template, which is the one case it
        # can settle itself rather than sending the agent to review the text.
        self.assertIn('Active instruction file: AGENTS.md', result.stdout)
        self.assertIn('Foundation link: present (file is the unmodified template)',
                      result.stdout)
        self.assertIn('setup.md', result.stdout)
        self.assertIn('commit when you decide to', result.stdout)
        self.assertTrue((self.project / '.agents/skills/foundation-setup/SKILL.md').is_file())

    def test_existing_agents_file_without_link_is_reported_and_untouched(self):
        original = '# House rules\n\nUse tabs. Ask before touching the parser.\n'
        (self.project / 'AGENTS.md').write_text(original)
        result = self.run_install('--profile', 'baseline')
        self.assertIn('Active instruction file: AGENTS.md', result.stdout)
        self.assertIn('Mentions .ai-governance.md: no - not connected.', result.stdout)
        # The installer reports; it never edits a project-owned instruction file.
        self.assertEqual((self.project / 'AGENTS.md').read_text(), original)

    def test_mention_of_the_config_is_reported_for_review_not_as_connected(self):
        # A mention is not proof of activation. This file names the configuration in
        # order to forbid it, which must not be reported as the foundation being live.
        (self.project / 'AGENTS.md').write_text(
            '# House rules\n\nIgnore `.ai-governance.md`; it is left over from a trial.\n')
        result = self.run_install('--profile', 'baseline')
        self.assertIn('Mentions .ai-governance.md: yes', result.stdout)
        self.assertIn('REVIEW the surrounding text', result.stdout)
        self.assertNotIn('do not add a second one', result.stdout)
        # Nothing in the output may claim the project is connected or set up.
        self.assertIn('SETUP IS NOT COMPLETE', result.stdout)

    def test_absent_mention_is_reported_as_not_connected(self):
        (self.project / 'AGENTS.md').write_text('# House rules\n\nUse tabs.\n')
        result = self.run_install('--profile', 'baseline')
        self.assertIn('Mentions .ai-governance.md: no - not connected.', result.stdout)

    def test_nested_instructions_and_no_root_file_defers_activation(self):
        # Creating the root file from the template also activates the foundation. With
        # a conflicting nested instruction file and no root file, activating would put
        # the foundation live beside a rule nobody reconciled, so nothing is created.
        (self.project / 'pkg').mkdir()
        (self.project / 'pkg/AGENTS.md').write_text(
            '# Package rules\n\nSkip code review for changes under this directory.\n')
        result = self.run_install('--profile', 'baseline')
        self.assertFalse((self.project / 'AGENTS.md').exists(),
                         'root AGENTS.md must not be created while a nested file is unreconciled')
        self.assertIn('NOT ACTIVATED ON PURPOSE', result.stdout)
        self.assertIn('pkg/AGENTS.md', result.stdout)
        self.assertIn('SETUP IS NOT COMPLETE', result.stdout)
        # The managed files still install, and the nested file is left alone.
        self.assertTrue((self.project / '.ai-foundation/manifest.json').is_file())
        self.assertEqual((self.project / 'pkg/AGENTS.md').read_text(),
                         '# Package rules\n\nSkip code review for changes under this directory.\n')

    def test_ancestor_git_root_instructions_defer_activation(self):
        # The project is a subdirectory of a Git repository whose root carries an
        # AGENTS.md. Codex loads that file before the project's own, so it binds here
        # and is not reachable by walking the project. Activating without reconciling
        # it is the same defect as activating beside a nested file.
        repo = self.root / 'monorepo'
        (repo / '.git').mkdir(parents=True)
        (repo / 'AGENTS.md').write_text(
            '# Monorepo rules\n\nDeploy straight to production from any branch.\n')
        package = repo / 'packages' / 'orders'
        package.mkdir(parents=True)
        result = self.install_into(package, '--profile', 'baseline')
        self.assertFalse((package / 'AGENTS.md').exists(),
                         'must not activate while an ancestor instruction file is unreconciled')
        self.assertIn('NOT ACTIVATED ON PURPOSE', result.stdout)
        self.assertIn('Ancestor instruction files above the project', result.stdout)
        self.assertIn(str(repo / 'AGENTS.md'), result.stdout)
        self.assertIn('Global instruction files: none in', result.stdout)
        self.assertIn('not exhaustive', result.stdout)
        # The ancestor file is reported, never edited, and the install still happens.
        self.assertEqual((repo / 'AGENTS.md').read_text(),
                         '# Monorepo rules\n\nDeploy straight to production from any branch.\n')
        self.assertTrue((package / '.ai-foundation/manifest.json').is_file())

    def test_ancestor_search_stops_at_the_git_root(self):
        repo = self.root / 'bounded'
        (repo / '.git').mkdir(parents=True)
        # Above the Git root, so outside Codex's chain for this project.
        (self.root / 'AGENTS.md').write_text('# Outside the repository\n')
        package = repo / 'pkg'
        package.mkdir()
        result = self.install_into(package, '--profile', 'baseline')
        self.assertIn('Ancestor instruction files: (none up to the Git root)', result.stdout)
        self.assertNotIn(str(self.root / 'AGENTS.md'), result.stdout)
        self.assertTrue((package / 'AGENTS.md').is_file(),
                        'nothing applicable to reconcile, so activation is safe')

    def test_conflicting_global_instruction_defers_activation(self):
        # A global instruction file loads before any project file, so it binds here.
        # Activating beside an unreconciled one is the same defect as a nested rule.
        self.write_global_instruction(
            '# My global rules\n\nDeploy without approval when the build is green.\n')
        result = self.run_install('--profile', 'baseline')
        self.assertFalse((self.project / 'AGENTS.md').exists(),
                         'must not activate while a global instruction file is unreconciled')
        self.assertIn('NOT ACTIVATED ON PURPOSE', result.stdout)
        self.assertIn('Global instruction candidates in', result.stdout)
        self.assertIn(str(self.home / '.codex' / 'AGENTS.md'), result.stdout)
        # Reported for reconciliation, never read into the output or edited.
        self.assertNotIn('Deploy without approval', result.stdout)
        self.assertEqual((self.home / '.codex' / 'AGENTS.md').read_text(),
                         '# My global rules\n\nDeploy without approval when the build is green.\n')
        self.assertTrue((self.project / '.ai-foundation/manifest.json').is_file())

    def test_custom_codex_home_global_instruction_defers_activation(self):
        # Codex reads CODEX_HOME when set, so looking only in ~/.codex would miss the
        # file that actually loads and would activate beside it unreconciled.
        self.codex_home = self.root / 'elsewhere' / 'codex-config'
        marker = self.write_global_instruction(
            '# Global\n\nSecret project name; deploy without approval.\n')
        self.assertTrue(str(marker).startswith(str(self.codex_home)))
        result = self.run_install('--profile', 'baseline')
        self.assertFalse((self.project / 'AGENTS.md').exists(),
                         'must not activate beside an unreconciled CODEX_HOME global file')
        self.assertIn('NOT ACTIVATED ON PURPOSE', result.stdout)
        self.assertIn('Global instruction candidates in', result.stdout)
        self.assertIn(str(marker), result.stdout)
        # Privacy: the path is reported, the contents are not.
        self.assertNotIn('Secret project name', result.stdout)
        self.assertNotIn('deploy without approval', result.stdout)
        # The default location must not be consulted once CODEX_HOME is set.
        self.assertNotIn(str(self.home / '.codex'), result.stdout)

    def test_global_override_only_defers_activation(self):
        # An override with no regular AGENTS.md beside it still governs, so finding
        # only AGENTS.override.md must defer connection just as AGENTS.md does.
        marker = self.write_global_instruction(
            '# Global override\n\nPrivate notes.\n', name='AGENTS.override.md')
        self.assertFalse((self.home / '.codex' / 'AGENTS.md').exists())
        result = self.run_install('--profile', 'baseline')
        self.assertFalse((self.project / 'AGENTS.md').exists(),
                         'must not activate beside an unreconciled global override')
        self.assertIn('NOT ACTIVATED ON PURPOSE', result.stdout)
        self.assertIn('AGENTS.override.md', result.stdout)
        self.assertIn(str(marker), result.stdout)
        self.assertNotIn('Private notes', result.stdout)

    def test_no_global_instruction_names_the_searched_location(self):
        self.codex_home = self.root / 'empty-codex'
        self.codex_home.mkdir()
        result = self.run_install('--profile', 'baseline')
        self.assertIn('Global instruction files: none in {}'.format(self.codex_home),
                      result.stdout)
        self.assertIn('not exhaustive', result.stdout)
        self.assertTrue((self.project / 'AGENTS.md').is_file())

    def write_codex_config(self, body):
        base = self.codex_home if self.codex_home is not None else self.home / '.codex'
        base.mkdir(parents=True, exist_ok=True)
        (base / 'config.toml').write_text(body)

    def test_configured_fallback_file_is_not_displaced_by_a_new_agents_md(self):
        # Codex reads project_doc_fallback_filenames when AGENTS.md is absent, so this
        # project's rules live in NOTES.md. Creating AGENTS.md would take precedence
        # and stop NOTES.md loading at all, silently dropping those rules.
        self.write_codex_config('project_doc_fallback_filenames = ["NOTES.md"]\n')
        rules = '# House rules\n\nNever touch the parser without review.\n'
        (self.project / 'NOTES.md').write_text(rules)
        result = self.run_install('--profile', 'baseline')
        self.assertFalse((self.project / 'AGENTS.md').exists(),
                         'creating AGENTS.md would stop the active fallback file loading')
        self.assertIn('Active instruction file: NOTES.md', result.stdout)
        self.assertIn('project_doc_fallback_filenames', result.stdout)
        self.assertIn('AGENTS.md was NOT created', result.stdout)
        self.assertIn('Add the link to NOTES.md instead', result.stdout)
        # The project's rules are untouched and still the active instruction file.
        self.assertEqual((self.project / 'NOTES.md').read_text(), rules)
        self.assertTrue((self.project / '.ai-foundation/manifest.json').is_file())

    def test_fallback_name_absent_from_project_still_allows_creation(self):
        self.write_codex_config('project_doc_fallback_filenames = ["NOTES.md"]\n')
        result = self.run_install('--profile', 'baseline')
        self.assertTrue((self.project / 'AGENTS.md').is_file())
        self.assertIn('Configured fallback instruction filenames: NOTES.md', result.stdout)
        self.assertIn('At the project root: (none)', result.stdout)

    def test_project_config_fallback_is_treated_as_possibly_effective(self):
        # A project .codex/config.toml applies only to a trusted project, and trust
        # cannot be read from here, so its names must not be assumed inert.
        config = self.project / '.codex'
        config.mkdir()
        (config / 'config.toml').write_text('project_doc_fallback_filenames = ["RULES.md"]\n')
        rules = '# Project rules\n\nKeep migrations reversible.\n'
        (self.project / 'RULES.md').write_text(rules)
        result = self.run_install('--profile', 'baseline')
        self.assertFalse((self.project / 'AGENTS.md').exists())
        self.assertIn('Active instruction file: RULES.md', result.stdout)
        self.assertIn('treated as possibly in', result.stdout)
        self.assertEqual((self.project / 'RULES.md').read_text(), rules)

    def test_nested_and_ancestor_fallback_files_are_reported(self):
        repo = self.root / 'mono'
        (repo / '.git').mkdir(parents=True)
        (repo / 'NOTES.md').write_text('# Ancestor fallback\n')
        package = repo / 'pkg'
        (package / 'sub').mkdir(parents=True)
        (package / 'sub' / 'NOTES.md').write_text('# Nested fallback\n')
        (self.home / '.codex').mkdir(parents=True, exist_ok=True)
        (self.home / '.codex' / 'config.toml').write_text(
            'project_doc_fallback_filenames = ["NOTES.md"]\n')
        result = self.install_into(package, '--profile', 'baseline')
        self.assertFalse((package / 'AGENTS.md').exists())
        self.assertIn('Elsewhere, where they also load:', result.stdout)
        self.assertIn(str(package / 'sub' / 'NOTES.md'), result.stdout)
        self.assertIn(str(repo / 'NOTES.md'), result.stdout)

    def test_ancestor_project_config_fallback_preserves_instructions(self):
        # A trusted ancestor project config can declare the fallback name, so the
        # file it names is the active instruction file for a package beneath it.
        repo = self.root / 'mono'
        (repo / '.git').mkdir(parents=True)
        (repo / '.codex').mkdir()
        (repo / '.codex' / 'config.toml').write_text(
            'project_doc_fallback_filenames = ["TEAM.md"]\n')
        package = repo / 'pkg'
        package.mkdir()
        rules = '# Team rules\n\nReview migrations together.\n'
        (package / 'TEAM.md').write_text(rules)
        result = self.install_into(package, '--profile', 'baseline')
        self.assertFalse((package / 'AGENTS.md').exists(),
                         'an ancestor project config still names a live instruction file')
        self.assertIn('Active instruction file: TEAM.md', result.stdout)
        self.assertEqual((package / 'TEAM.md').read_text(), rules)

    def write_profile_config(self, profile, body):
        """`codex -p <profile>` layers $CODEX_HOME/<profile>.config.toml."""
        base = self.codex_home if self.codex_home is not None else self.home / '.codex'
        base.mkdir(parents=True, exist_ok=True)
        path = base / '{}.config.toml'.format(profile)
        path.write_text(body)
        return path

    def test_profile_config_file_fallback_preserves_the_file_it_names(self):
        # `-p work` layers work.config.toml over the base config, so a fallback
        # declared there is live whenever that profile is selected. Missing it means
        # creating an AGENTS.md that stops the real instruction file loading.
        source = self.write_profile_config(
            'work', 'project_doc_fallback_filenames = ["NOTES.md"]\n')
        rules = '# Project rules\n\nNever rewrite migrations.\n'
        (self.project / 'NOTES.md').write_text(rules)
        result = self.run_install('--profile', 'baseline')
        self.assertFalse((self.project / 'AGENTS.md').exists(),
                         'a profile config file still names a live instruction file')
        self.assertIn('Active instruction file: NOTES.md', result.stdout)
        self.assertIn('Declared only by a profile: NOTES.md', result.stdout)
        self.assertIn(str(source), result.stdout)
        self.assertEqual((self.project / 'NOTES.md').read_text(), rules)

    def test_profile_config_file_without_a_matching_file_allows_creation(self):
        self.write_profile_config('work', 'project_doc_fallback_filenames = ["NOTES.md"]\n')
        result = self.run_install('--profile', 'baseline')
        self.assertTrue((self.project / 'AGENTS.md').is_file(),
                        'nothing is displaced when no such file exists')
        self.assertIn('At the project root: (none)', result.stdout)

    def test_base_config_names_are_not_reported_as_profile_scoped(self):
        self.write_codex_config('project_doc_fallback_filenames = ["BASE.md"]\n')
        self.write_profile_config('work', 'project_doc_fallback_filenames = ["WORK.md"]\n')
        (self.project / 'BASE.md').write_text('# base\n')
        result = self.run_install('--profile', 'baseline')
        self.assertIn('Active instruction file: BASE.md', result.stdout)
        # BASE.md always applies; WORK.md only under that profile.
        self.assertIn('Declared only by a profile: WORK.md', result.stdout)
        self.assertNotIn('Declared only by a profile: BASE.md', result.stdout)

    def test_base_config_is_not_mistaken_for_a_profile_file(self):
        self.write_codex_config('project_doc_fallback_filenames = ["NOTES.md"]\n')
        (self.project / 'NOTES.md').write_text('# notes\n')
        result = self.run_install('--profile', 'baseline')
        self.assertIn('Active instruction file: NOTES.md', result.stdout)
        self.assertNotIn('Declared only by a profile', result.stdout)

    def test_profile_scoped_fallback_preserves_the_file_it_names(self):
        self.write_codex_config(
            'profile = "work"\n\n[profiles.work]\n'
            'project_doc_fallback_filenames = ["NOTES.md"]\n')
        rules = '# Notes\n\nProject rules live here.\n'
        (self.project / 'NOTES.md').write_text(rules)
        result = self.run_install('--profile', 'baseline')
        self.assertFalse((self.project / 'AGENTS.md').exists())
        self.assertIn('Declared only by a profile: NOTES.md', result.stdout)
        self.assertIn('cannot determine', result.stdout)
        self.assertEqual((self.project / 'NOTES.md').read_text(), rules)

    def test_fallback_above_the_git_boundary_does_not_defer_activation(self):
        # An unrelated file of the same name outside the repository is not in this
        # project's chain, so it must not block the clean-install path.
        self.write_codex_config('project_doc_fallback_filenames = ["NOTES.md"]\n')
        outside = self.root / 'outside'
        outside.mkdir()
        (outside / 'NOTES.md').write_text('# Unrelated\n')
        repo = outside / 'repo'
        (repo / '.git').mkdir(parents=True)
        result = self.install_into(repo, '--profile', 'baseline')
        self.assertTrue((repo / 'AGENTS.md').is_file(),
                        'a file above the Git root must not defer activation')
        self.assertNotIn(str(outside / 'NOTES.md'), result.stdout)
        self.assertEqual((outside / 'NOTES.md').read_text(), '# Unrelated\n')

    def test_regular_file_at_skills_path_refuses_before_any_write(self):
        (self.project / '.agents').mkdir()
        (self.project / '.agents' / 'skills').write_text('not a directory')
        result = self.run_install('--profile', 'baseline', success=False)
        self.assertIn('parent path is not a directory: .agents/skills', result.stderr)
        self.assertFalse((self.project / '.ai-foundation').exists(),
                         'refusal must leave no partial installation')
        self.assertEqual((self.project / '.agents' / 'skills').read_text(),
                         'not a directory')
        # Removing the obstruction must allow a clean retry.
        (self.project / '.agents' / 'skills').unlink()
        self.run_install('--profile', 'baseline')
        self.assertTrue((self.project / '.ai-foundation/manifest.json').is_file())
        self.assertTrue((self.project / '.agents/skills/foundation-setup/SKILL.md').is_file())

    def test_regular_file_inside_the_foundation_path_refuses_before_any_write(self):
        # An obstruction under .ai-foundation is caught by the ownership guard, which
        # fires earlier than the parent-component check. Either way the requirement
        # is the same: refuse, touch nothing, and stay recoverable.
        (self.project / '.ai-foundation').mkdir()
        (self.project / '.ai-foundation' / 'docs').write_text('not a directory')
        result = self.run_install('--profile', 'baseline', success=False)
        self.assertIn('refusing to take ownership', result.stderr)
        self.assertEqual((self.project / '.ai-foundation' / 'docs').read_text(),
                         'not a directory')
        self.assertFalse((self.project / '.ai-foundation' / 'manifest.json').exists())
        self.assertFalse((self.project / '.agents').exists())
        self.assertFalse((self.project / '.ai-governance.md').exists())

    def test_unreadable_fallback_config_defers_instead_of_assuming_none(self):
        # Exercises the no-tomllib branch: the key is present but the pattern cannot
        # read it. Treating that as "no fallbacks" is what creates a displacing
        # AGENTS.md, so the installer defers instead.
        self.write_codex_config(
            'project_doc_fallback_filenames = [\n  CONFIG_BUILT_ELSEWHERE,\n]\n')
        result = self.run_install('--profile', 'baseline')
        self.assertIn('UNCERTAIN', result.stdout)
        self.assertIn('rather', result.stdout)
        self.assertFalse((self.project / 'AGENTS.md').exists(),
                         'uncertain configuration must defer, not activate')
        self.assertIn('NOT ACTIVATED ON PURPOSE', result.stdout)
        self.assertTrue((self.project / '.ai-foundation/manifest.json').is_file())

    def test_dangling_config_symlink_leaves_no_partial_installation(self):
        link = self.project / '.ai-governance.md'
        link.symlink_to(self.root / 'absent.md')
        result = self.run_install('--profile', 'baseline', success=False)
        self.assertIn('not a regular file', result.stderr)
        self.assertFalse((self.project / '.ai-foundation').exists(),
                         'refusal must leave nothing behind')
        self.assertEqual(list(self.project.glob('.agents')), [])
        # With the cause removed the install proceeds, so the refusal blocks nothing.
        link.unlink()
        self.run_install('--profile', 'baseline')
        self.assertTrue((self.project / '.ai-foundation/manifest.json').is_file())

    def test_agents_directory_leaves_no_partial_installation(self):
        (self.project / 'AGENTS.md').mkdir()
        result = self.run_install('--profile', 'baseline', success=False)
        self.assertIn('not a regular file', result.stderr)
        self.assertFalse((self.project / '.ai-foundation').exists())
        (self.project / 'AGENTS.md').rmdir()
        self.run_install('--profile', 'baseline')
        self.assertTrue((self.project / '.ai-foundation/manifest.json').is_file())

    def test_symlinked_global_instruction_is_detected(self):
        # A symlinked instruction file still loads, so skipping symlinks hid it.
        target = self.root / 'dotfiles' / 'codex-rules.md'
        target.parent.mkdir(parents=True)
        target.write_text('# Global\n\nPrivate dotfile rules.\n')
        link = self.home / '.codex' / 'AGENTS.md'
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(target)
        result = self.run_install('--profile', 'baseline')
        self.assertFalse((self.project / 'AGENTS.md').exists())
        self.assertIn('NOT ACTIVATED ON PURPOSE', result.stdout)
        self.assertIn(str(link), result.stdout)
        self.assertIn('(symlink)', result.stdout)
        self.assertNotIn('Private dotfile rules', result.stdout)
        self.assertEqual(target.read_text(), '# Global\n\nPrivate dotfile rules.\n')

    def test_symlinked_ancestor_instruction_is_detected(self):
        repo = self.root / 'repo'
        (repo / '.git').mkdir(parents=True)
        target = self.root / 'shared' / 'team-rules.md'
        target.parent.mkdir(parents=True)
        target.write_text('# Team\n\nShared rules.\n')
        (repo / 'AGENTS.md').symlink_to(target)
        package = repo / 'pkg'
        package.mkdir()
        result = self.install_into(package, '--profile', 'baseline')
        self.assertFalse((package / 'AGENTS.md').exists())
        self.assertIn('NOT ACTIVATED ON PURPOSE', result.stdout)
        self.assertIn(str(repo / 'AGENTS.md'), result.stdout)
        self.assertIn('(symlink)', result.stdout)
        self.assertEqual(target.read_text(), '# Team\n\nShared rules.\n')

    def test_global_override_is_reported_as_superseding_the_regular_file(self):
        # Codex loads only the override when both exist, so listing both as loaded
        # would misreport what actually governs.
        self.write_global_instruction('# Override\n', name='AGENTS.override.md')
        self.write_global_instruction('# Regular\n', name='AGENTS.md')
        result = self.run_install('--profile', 'baseline')
        self.assertIn('override: the one Codex loads', result.stdout)
        self.assertIn('likely NOT loaded, superseded by the override', result.stdout)
        self.assertIn('Codex may load only the override', result.stdout)

    def test_empty_project_still_gets_a_root_instruction_file(self):
        # With nothing to reconcile, the convenience of creating it is safe to keep.
        result = self.run_install('--profile', 'baseline')
        self.assertTrue((self.project / 'AGENTS.md').is_file())
        self.assertIn('Created project-owned AGENTS.md.', result.stdout)
        self.assertNotIn('NOT ACTIVATED ON PURPOSE', result.stdout)

    def test_output_requires_reconciliation_before_activation(self):
        (self.project / 'AGENTS.md').write_text('# House rules\n\nUse tabs.\n')
        (self.project / 'pkg').mkdir()
        (self.project / 'pkg/AGENTS.md').write_text('# Nested\n\nSkip code review.\n')
        result = self.run_install('--profile', 'baseline')
        self.assertIn('pkg/AGENTS.md', result.stdout.split('In-project instruction files to reconcile')[1])
        self.assertIn('BEFORE', result.stdout)

    def test_commit_guidance_names_foundation_skills_and_does_not_commit(self):
        # .agents/skills/ may hold skills the project owns, so the whole directory
        # must not be swept into a governance commit.
        result = self.run_install('--profile', 'baseline')
        self.assertIn('.agents/skills/foundation-*/', result.stdout)
        self.assertIn('this does not commit for you', result.stdout)
        self.assertNotRegex(result.stdout, r'Commit: .*\.agents/skills/ ')

    def test_resumed_setup_needs_no_checkout_when_installed(self):
        # The procedure must let a resumed run work from the installed copy alone, so
        # the documents and the setup skill have to be present after installing.
        self.run_install('--profile', 'baseline')
        for name in ('.ai-foundation/docs/agent-governance/setup.md',
                     '.agents/skills/foundation-setup/SKILL.md',
                     '.ai-foundation/manifest.json'):
            self.assertTrue((self.project / name).is_file(), name)
        installed = (self.project / '.ai-foundation/docs/agent-governance/setup.md').read_text()
        self.assertIn('you need no checkout and no installer run', installed)

    def test_installer_refuses_a_foundation_directory_it_does_not_own(self):
        # Migoy's failure mode: a part-deleted install leaves directories with no
        # manifest. The installer must refuse rather than adopt or clear them.
        (self.project / '.ai-foundation/docs').mkdir(parents=True)
        (self.project / '.ai-foundation/docs/leftover.md').write_text('keep me')
        result = self.run_install(success=False)
        self.assertIn('no manifest', result.stderr)
        self.assertEqual((self.project / '.ai-foundation/docs/leftover.md').read_text(),
                         'keep me')

    def test_root_override_is_reported_as_the_active_instruction_file(self):
        (self.project / 'AGENTS.override.md').write_text('# Override\n\nOverride rules.\n')
        (self.project / 'AGENTS.md').write_text('# Stale\n\nOlder rules.\n')
        result = self.run_install('--profile', 'baseline')
        self.assertIn('Active instruction file: AGENTS.override.md', result.stdout)
        self.assertIn('Mentions .ai-governance.md: no - not connected.', result.stdout)
        # The non-active root file is surfaced so a human can judge whether it is stale.
        self.assertIn('AGENTS.md', result.stdout.split('In-project instruction files to reconcile')[1])
        self.assertEqual((self.project / 'AGENTS.override.md').read_text(),
                         '# Override\n\nOverride rules.\n')

    def test_repeated_setup_is_idempotent_for_instructions_and_config(self):
        self.run_install('--profile', 'baseline')
        agents = (self.project / 'AGENTS.md').read_bytes()
        config = (self.project / '.ai-governance.md').read_bytes()
        result = self.run_install()
        self.assertEqual((self.project / 'AGENTS.md').read_bytes(), agents)
        self.assertEqual((self.project / '.ai-governance.md').read_bytes(), config)
        self.assertEqual((self.project / 'AGENTS.md').read_text().count('.ai-governance.md'), 1)
        self.assertIn('Foundation link: present (file is the unmodified template)',
                      result.stdout)

    def test_partially_configured_project_keeps_its_answers_on_update(self):
        # The pilot's shape: baseline already installed, an existing AGENTS.md with its
        # own rules, and a .ai-governance.md whose decisions are only partly filled.
        self.run_install('--profile', 'baseline')
        agents = self.project / 'AGENTS.md'
        agents.write_text(agents.read_text() + '\nProject rule: ask before schema edits.\n')
        config = self.project / '.ai-governance.md'
        config.write_text(config.read_text().replace(
            '- Project owner and approvers: **set before adoption**.',
            '- Project owner and approvers: Dana owns; Lee approves.'))
        agents_before, config_before = agents.read_bytes(), config.read_bytes()
        result = self.run_install()
        self.assertEqual(agents.read_bytes(), agents_before)
        self.assertEqual(config.read_bytes(), config_before)
        self.assertIn('Dana owns; Lee approves', config.read_text())
        self.assertIn('Project rule: ask before schema edits.', agents.read_text())
        self.assertIn('Preserved existing .ai-governance.md', result.stdout)
        self.assertIn('FILES INSTALLED - SETUP IS NOT COMPLETE', result.stdout)

    def test_existing_instructions_config_and_override_are_preserved(self):
        (self.project / 'AGENTS.override.md').write_text('custom override')
        (self.project / '.ai-governance.md').write_text('custom config')
        (self.project / 'sub').mkdir()
        (self.project / 'sub/AGENTS.md').write_text('nested')
        result = self.run_install('--profile', 'regulated')
        self.assertEqual((self.project / 'AGENTS.override.md').read_text(), 'custom override')
        self.assertEqual((self.project / '.ai-governance.md').read_text(), 'custom config')
        self.assertFalse((self.project / 'AGENTS.md').exists())
        self.assertIn('sub/AGENTS.md', result.stdout)
        self.assertIn('AGENTS.override.md', result.stdout)

    def test_update_tracks_content_and_preserves_project_files(self):
        self.run_install()
        before = self.manifest()
        (self.project / '.ai-governance.md').write_text('project config')
        source_doc = self.source / 'docs/engineering/standards.md'
        source_doc.write_text(source_doc.read_text() + '\nNew rule.\n')
        self.run_install('--profile', 'regulated')
        self.assertNotEqual(before['content_sha256'], self.manifest()['content_sha256'])
        self.assertIn('New rule.', (self.project / '.ai-foundation/docs/engineering/standards.md').read_text())
        self.assertEqual((self.project / '.ai-governance.md').read_text(), 'project config')

    def test_modified_managed_file_blocks_all_updates(self):
        self.run_install()
        doc = self.project / '.ai-foundation/docs/engineering/standards.md'
        doc.write_text('custom')
        before = (self.project / '.ai-foundation/manifest.json').read_bytes()
        result = self.run_install(success=False)
        self.assertIn('missing or modified', result.stderr)
        self.assertEqual(doc.read_text(), 'custom')
        self.assertEqual((self.project / '.ai-foundation/manifest.json').read_bytes(), before)

    def test_unmanaged_skill_collision_is_not_overwritten(self):
        skill = self.project / '.agents/skills/foundation-planning'
        skill.mkdir(parents=True)
        (skill / 'other.txt').write_text('keep')
        self.run_install(success=False)
        self.assertEqual((skill / 'other.txt').read_text(), 'keep')
        self.assertFalse((self.project / '.ai-foundation').exists())

    def test_existing_unmanaged_foundation_is_not_taken_over(self):
        (self.project / '.ai-foundation').mkdir()
        self.run_install(success=False)
        self.assertFalse((self.project / 'AGENTS.md').exists())

    def test_symlink_destination_is_rejected(self):
        external = self.root / 'external'
        external.mkdir()
        (self.project / '.agents').symlink_to(external, target_is_directory=True)
        self.run_install(success=False)
        self.assertEqual(list(external.iterdir()), [])
        self.assertFalse((self.project / '.ai-foundation').exists())

    def test_tampered_manifest_path_is_rejected(self):
        self.run_install()
        path = self.project / '.ai-foundation/manifest.json'
        data = self.manifest()
        data['files']['../../outside'] = '0' * 64
        path.write_text(json.dumps(data))
        result = self.run_install(success=False)
        self.assertIn('invalid managed path', result.stderr)

    def test_malformed_manifest_is_rejected_without_traceback(self):
        self.run_install()
        (self.project / '.ai-foundation/manifest.json').write_text('[]')
        result = self.run_install(success=False)
        self.assertIn('invalid or unsupported manifest', result.stderr)
        self.assertNotIn('Traceback', result.stderr)

    def test_explicit_profile_conflict_is_reported_and_config_preserved(self):
        self.run_install('--profile', 'baseline')
        config = (self.project / '.ai-governance.md').read_text()
        result = self.run_install('--profile', 'regulated')
        self.assertIn('PROFILE CONFLICT', result.stdout)
        self.assertEqual((self.project / '.ai-governance.md').read_text(), config)

    def test_removed_upstream_file_is_removed_only_if_unchanged(self):
        self.run_install()
        old_file = self.project / '.ai-foundation/templates/stacks/react.md'
        (self.source / 'templates/stacks/react.md').unlink()
        self.run_install()
        self.assertFalse(old_file.exists())
        self.assertNotIn('.ai-foundation/templates/stacks/react.md', self.manifest()['files'])

    def test_update_adds_new_docs_and_template_entries_without_touching_config(self):
        # Backs the reconciliation guidance in docs/agent-governance/adoption.md: an update may add
        # managed documents and newly required configuration entries. The documents and the updated
        # template must land so the adopter can diff them, and the project-owned configuration must
        # be left exactly as it was, because it is reconciled by hand rather than updated for them.
        self.run_install('--profile', 'web-saas')
        config_before = (self.project / '.ai-governance.md').read_bytes()
        (self.source / 'docs/security/new-requirement.md').write_text('# New requirement\nRecord it.\n')
        template = self.source / 'templates/project/ai-governance.md'
        template.write_text(template.read_text() + '- New required entry: **set before adoption**.\n')
        self.run_install()
        self.assertTrue((self.project / '.ai-foundation/docs/security/new-requirement.md').is_file())
        self.assertIn('.ai-foundation/docs/security/new-requirement.md', self.manifest()['files'])
        self.assertEqual((self.project / '.ai-governance.md').read_bytes(), config_before)
        installed_template = self.project / '.ai-foundation/templates/project/ai-governance.md'
        self.assertIn('- New required entry:', installed_template.read_text())


class FallbackParserTests(unittest.TestCase):
    """The Python 3.9/3.10 branch of read_fallback_key, with tomllib unavailable.

    Those versions have no TOML parser and this project adds no dependency, so the
    key is read with a narrow pattern. The branch cannot be reached on a newer
    interpreter unless the import is blocked, and the dangerous failure is silently
    reporting "no fallbacks" for a config that declares some.
    """

    class BlockTomllib:
        def find_spec(self, name, path=None, target=None):
            if name == 'tomllib':
                raise ModuleNotFoundError("No module named 'tomllib'")
            return None

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.config = Path(self.temp.name) / 'config.toml'
        spec = importlib.util.spec_from_file_location(
            'dex_install_under_test', ROOT / 'scripts' / 'install.py')
        self.installer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.installer)
        self.blocker = self.BlockTomllib()

    def tearDown(self):
        self.temp.cleanup()

    def read(self, body):
        """Read the key with tomllib blocked, exercising the 3.9/3.10 path."""
        self.config.write_text(body)
        sys.meta_path.insert(0, self.blocker)
        sys.modules.pop('tomllib', None)
        try:
            with self.assertRaises(ModuleNotFoundError):
                importlib.import_module('tomllib')
            return self.installer.read_fallback_key(self.config)
        finally:
            sys.meta_path.remove(self.blocker)
            sys.modules.pop('tomllib', None)

    def read_with_tomllib(self, body):
        """Read the key through the real TOML parser, when one exists."""
        try:
            importlib.import_module('tomllib')
        except ModuleNotFoundError:
            self.skipTest('tomllib is unavailable on this interpreter (Python < 3.11)')
        self.config.write_text(body)
        return self.installer.read_fallback_key(self.config)

    def test_readable_list_is_parsed(self):
        self.assertEqual(self.read('project_doc_fallback_filenames = ["NOTES.md"]\n'),
                         (['NOTES.md'], [], False))

    def test_multiple_names_are_parsed(self):
        self.assertEqual(
            self.read('project_doc_fallback_filenames = ["NOTES.md", "RULES.md"]\n'),
            (['NOTES.md', 'RULES.md'], [], False))

    def test_multiline_list_with_bracket_in_a_comment(self):
        # The comment's `]` must not end the list: cutting there silently drops
        # every name after the first and reports the result as certain.
        body = ('project_doc_fallback_filenames = [\n'
                '  "NOTES.md",  # legacy [deprecated]\n'
                '  "RULES.md",\n'
                ']\n')
        self.assertEqual(self.read(body), (['NOTES.md', 'RULES.md'], [], False))
        self.assertEqual(self.read_with_tomllib(body), (['NOTES.md', 'RULES.md'], [], False))

    def test_hash_inside_a_quoted_name_is_not_a_comment(self):
        self.assertEqual(self.read('project_doc_fallback_filenames = ["a#b.md"]\n'),
                         (['a#b.md'], [], False))

    def test_profile_scoped_declaration_is_attributed_to_the_profile(self):
        body = ('profile = "work"\n\n[profiles.work]\n'
                'project_doc_fallback_filenames = ["NOTES.md"]\n')
        self.assertEqual(self.read(body), ([], ['NOTES.md'], False))
        self.assertEqual(self.read_with_tomllib(body), ([], ['NOTES.md'], False))

    def test_root_and_profile_declarations_are_kept_apart(self):
        body = ('project_doc_fallback_filenames = ["ROOT.md"]\n\n'
                '[profiles.work]\nproject_doc_fallback_filenames = ["WORK.md"]\n')
        self.assertEqual(self.read(body), (['ROOT.md'], ['WORK.md'], False))
        self.assertEqual(self.read_with_tomllib(body), (['ROOT.md'], ['WORK.md'], False))

    def test_declaration_after_an_unrelated_table_is_not_root_scoped(self):
        body = '[profiles.other]\nproject_doc_fallback_filenames = ["X.md"]\n'
        self.assertEqual(self.read(body), ([], ['X.md'], False))

    def test_unterminated_list_is_uncertain(self):
        self.assertEqual(self.read('project_doc_fallback_filenames = [\n  "A.md",\n'),
                         ([], [], True))

    def test_key_present_but_unreadable_is_uncertain_not_empty(self):
        names, profile, uncertain = self.read(
            'project_doc_fallback_filenames = [\n  BUILT_ELSEWHERE,\n]\n')
        self.assertEqual((names, profile), ([], []))
        self.assertTrue(uncertain, 'unreadable declaration must be uncertain')

    def test_non_list_value_is_uncertain(self):
        self.assertEqual(self.read('project_doc_fallback_filenames = "NOTES.md"\n'),
                         ([], [], True))

    def test_key_absent_is_certain_and_empty(self):
        self.assertEqual(self.read('model = "gpt-5"\n'), ([], [], False))
        self.assertEqual(self.read_with_tomllib('model = "gpt-5"\n'), ([], [], False))

    def test_missing_file_is_certain_and_empty(self):
        self.assertFalse(self.config.exists())
        self.assertEqual(self.installer.read_fallback_key(self.config), ([], [], False))


if __name__ == '__main__':
    unittest.main()
