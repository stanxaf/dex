#!/usr/bin/env python3
"""Check local documentation links and the portable foundation structure."""
from pathlib import Path
import datetime
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
errors = []
required = [
    'README.md', 'AGENTS.md', 'CONTRIBUTING.md',
    'docs/agent-governance/workflow.md', 'docs/agent-governance/adoption.md',
    'docs/agent-governance/instruction-hygiene.md',
    'docs/engineering/standards.md', 'docs/design/design-system.md',
    'docs/security/security.md', 'docs/security/agent-operations.md',
    'docs/security/deployment-gate.md',
    'docs/testing/quality-gates.md',
    'profiles/baseline/PROFILE.md', 'profiles/web-saas/PROFILE.md',
    'profiles/regulated/PROFILE.md', 'templates/project/AGENTS.md',
    'templates/project/ai-governance.md', 'templates/ci/node-starter.yml',
    'examples/sample-project/worked-example.md',
    'examples/sample-project/blocked-example.md', '.github/workflows/validate.yml',
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

# Every document a reading tier names must exist, so a tier cannot point at nothing.
# This checks the template's own lists; a project's completed config is not inspected here.
template = ROOT / 'templates' / 'project' / 'ai-governance.md'
if template.is_file():
    config = template.read_text(encoding='utf-8')
    for tier in ('All work', 'When relevant'):
        line = re.search(r'^- ' + tier + r':\s*(.+)$', config, re.M)
        if not line:
            errors.append('missing reading tier in ai-governance template: ' + tier)
            continue
        named = re.findall(r'`\.ai-foundation/([^`]+\.md)`', line.group(1))
        if not named:
            errors.append('reading tier names no document: ' + tier)
        for doc in named:
            if not (ROOT / doc).is_file():
                errors.append('reading tier {} names missing document: {}'.format(tier, doc))

    # The profile line must name every profile by its complete installed path, because a
    # bare fragment like `web-saas/PROFILE.md` does not resolve from the project root.
    line = re.search(r'^- Selected profile:\s*(.+)$', config, re.M)
    if not line:
        errors.append('missing selected profile line in ai-governance template')
    else:
        named = re.findall(r'`\.ai-foundation/(profiles/[^`]+\.md)`', line.group(1))
        for profile in ('baseline', 'web-saas', 'regulated'):
            expected = 'profiles/{}/PROFILE.md'.format(profile)
            if expected not in named:
                errors.append('selected profile line omits the complete installed path'
                              ' for {}: expected .ai-foundation/{}'.format(profile, expected))
        for doc in named:
            if not (ROOT / doc).is_file():
                errors.append('selected profile line names missing profile: ' + doc)

# INS-1: one canonical location per rule. Splitting a rule document must not duplicate an id.
defined = {}
for path in markdown:
    if '.git' in path.parts:
        continue
    text = path.read_text(encoding='utf-8')
    for rule in re.findall(r'^- \*\*((?:AGT|INS)-\d+)\*\*', text, re.M):
        defined.setdefault(rule, []).append(str(path.relative_to(ROOT)))
for rule in sorted(defined):
    if len(defined[rule]) > 1:
        errors.append('rule {} defined in more than one place: {}'.format(
            rule, ', '.join(sorted(set(defined[rule])))))

# Every rule id cited anywhere must resolve to a definition, so moving or renumbering
# a rule cannot leave a dangling citation in a template, profile or decision record.
for path in markdown:
    if '.git' in path.parts:
        continue
    text = path.read_text(encoding='utf-8')
    for cited in sorted(set(re.findall(r'\b((?:AGT|INS)-\d+)\b', text))):
        if cited not in defined:
            errors.append('{} cites undefined rule {}'.format(
                path.relative_to(ROOT), cited))

# The workflow requires every decision record to carry an explicit expiry and say what
# an overdue one changes. Each date is its own labelled field rather than prose matched
# by proximity, because proximity let one date answer both questions: "expires once
# review concludes; review by 2027-05-07" satisfied a search for an expiry date using
# the review date. Fields are parsed, so an impossible date is rejected rather than
# accepted for looking like one.
decisions = sorted((ROOT / 'docs' / 'decisions').glob('*.md'))
if not decisions:
    errors.append('no decision records found under docs/decisions')
for path in decisions:
    name = str(path.relative_to(ROOT))
    text = path.read_text(encoding='utf-8')
    dates = {}
    for field in ('Expiry date', 'Review by'):
        found = re.search(r'^' + field + r':[ \t]*(\S+)[ \t]*$', text, re.M)
        if not found:
            errors.append('decision record has no "{}: YYYY-MM-DD" field: {}'.format(
                field, name))
            continue
        value = found.group(1).strip('*`')
        try:
            dates[field] = datetime.date.fromisoformat(value)
        except ValueError:
            errors.append('decision record has an invalid {} "{}", expected a real'
                          ' calendar date as YYYY-MM-DD: {}'.format(field, value, name))
    if len(dates) == 2 and dates['Review by'] > dates['Expiry date']:
        errors.append('decision record is reviewed only after it expires: ' + name)
    section = re.search(r'^Expiry and review handling:(.*)\Z', text, re.M | re.S)
    if not section:
        errors.append('decision record missing expiry and review handling: ' + name)
        continue
    body = section.group(1).strip()
    # The rule is about what an overdue record changes, so that case must be addressed.
    if not re.search(r'overdue|lapse|lapsed|expire[sd]|expiry', body, re.I):
        errors.append('decision record does not say what an overdue or expired record'
                      ' changes: ' + name)
    if len(body.split()) < 20:
        errors.append('decision record states no overdue handling: ' + name)

# Reported, not enforced: a record whose owner is still a placeholder is valid
# structure but not yet an audit record, and AGT-11 requires a named human.
pending = sorted(
    str(path.relative_to(ROOT)) for path in decisions
    if 'OWNER NAME PENDING' in path.read_text(encoding='utf-8')
)

if errors:
    for error in errors:
        print('FAIL:', error)
    sys.exit(1)
for path in pending:
    print('NOTE: unfilled owner placeholder (fill before merge):', path)
print('PASS: required structure, eight skill entrypoints, local Markdown links,'
      ' reading-tier targets, unique rule ids, and resolvable rule citations')
print('Note: this does not verify agent compliance, external URLs, or application checks.')
