import json
import os
from pathlib import Path
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
        self.source.mkdir()
        self.project.mkdir()
        for name in ('docs', 'profiles', 'skills', 'templates', 'scripts'):
            shutil.copytree(ROOT / name, self.source / name)

    def tearDown(self):
        self.temp.cleanup()

    def run_install(self, *args, success=True):
        cmd = [sys.executable, str(self.source / 'scripts/install.py'), str(self.project), *args]
        result = subprocess.run(cmd, text=True, capture_output=True)
        self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
        return result

    def manifest(self):
        return json.loads((self.project / '.ai-foundation/manifest.json').read_text())

    def test_fresh_install_and_profile(self):
        self.run_install('--profile', 'regulated')
        self.assertIn('Selected profile: regulated', (self.project / '.ai-governance.md').read_text())
        self.assertIn('.ai-governance.md', (self.project / 'AGENTS.md').read_text())
        self.assertTrue((self.project / '.agents/skills/foundation-planning/SKILL.md').is_file())
        self.assertIn('.agents/skills/foundation-planning/SKILL.md', self.manifest()['files'])
        self.assertIn('.ai-foundation/docs/engineering/standards.md', self.manifest()['files'])

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


if __name__ == '__main__':
    unittest.main()
