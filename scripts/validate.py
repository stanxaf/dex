#!/usr/bin/env python3
"""Check local documentation links and the portable foundation structure."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
errors = []
required = [
    'README.md', 'AGENTS.md', 'CONTRIBUTING.md',
    'docs/agent-governance/workflow.md', 'docs/agent-governance/adoption.md',
    'docs/engineering/standards.md', 'docs/design/design-system.md',
    'docs/security/security.md', 'docs/testing/quality-gates.md',
    'profiles/baseline/PROFILE.md', 'profiles/web-saas/PROFILE.md',
    'profiles/regulated/PROFILE.md', 'templates/project/AGENTS.md',
    'templates/project/ai-governance.md', 'templates/ci/node-starter.yml',
    'examples/sample-project/worked-example.md', '.github/workflows/validate.yml',
]
for name in required:
    if not (ROOT / name).is_file():
        errors.append('missing required file: ' + name)

skills = ('planning', 'implementation', 'code-review', 'architecture-review',
          'ui-review', 'testing', 'security-review', 'documentation')
for skill in skills:
    path = ROOT / 'skills' / ('foundation-' + skill) / 'SKILL.md'
    if not path.is_file():
        errors.append('missing skill: ' + str(path.relative_to(ROOT)))
        continue
    text = path.read_text(encoding='utf-8')
    front = re.match(r'\A---\n(.*?)\n---\n', text, re.S)
    if not front:
        errors.append('missing skill frontmatter: ' + str(path.relative_to(ROOT)))
        continue
    fields = dict(re.findall(r'^([a-z][a-z-]*):\s*(.+)$', front.group(1), re.M))
    if fields.get('name') != 'foundation-' + skill or not fields.get('description'):
        errors.append('invalid skill name or description: ' + str(path.relative_to(ROOT)))
    if '{{' in text or '[TODO]' in text:
        errors.append('unfilled skill placeholder: ' + str(path.relative_to(ROOT)))

markdown = list(ROOT.rglob('*.md'))
for path in markdown:
    if '.git' in path.parts:
        continue
    text = path.read_text(encoding='utf-8')
    # Check ordinary relative links; external URLs and fragment-only links are not fetched.
    for link in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)', text):
        target = link.split('#', 1)[0]
        if not target or '://' in target or target.startswith(('mailto:', '/')):
            continue
        if not (path.parent / target).exists():
            errors.append('broken link in {}: {}'.format(path.relative_to(ROOT), link))

if errors:
    for error in errors:
        print('FAIL:', error)
    sys.exit(1)
print('PASS: required structure, eight skill entrypoints, and local Markdown links')
print('Note: this does not verify agent compliance, external URLs, or application checks.')
