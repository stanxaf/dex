import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class ValidatorTests(unittest.TestCase):
    """Checks that the structural gates in scripts/validate.py actually fail.

    A check nobody has seen fail is not known to work, so each test breaks one
    invariant in a throwaway copy of the tree and asserts the reported message.
    """

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.tree = Path(self.temp.name) / 'tree'
        shutil.copytree(ROOT, self.tree, ignore=shutil.ignore_patterns('.git'))

    def tearDown(self):
        self.temp.cleanup()

    def validate(self):
        return subprocess.run(
            [sys.executable, str(self.tree / 'scripts/validate.py')],
            text=True, capture_output=True)

    def path(self, relative):
        return self.tree / relative

    def edit(self, relative, old, new):
        target = self.path(relative)
        text = target.read_text()
        self.assertIn(old, text, 'fixture text not found in ' + relative)
        target.write_text(text.replace(old, new, 1))

    def test_unmodified_tree_passes(self):
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('PASS:', result.stdout)

    def test_handling_that_ignores_the_overdue_case_is_rejected(self):
        # Valid dates are not sufficient on their own: the workflow rule is about what
        # an overdue record changes, so a section that never addresses it fails.
        self.write_record(**{'Expiry and review handling':
                             'this decision was taken after weighing the alternatives'
                             ' and it reflects how the system should behave from now'
                             ' on, with no further qualification recorded here by'
                             ' anyone involved in making the original choice.'})
        result = self.validate()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('does not say what an overdue or expired record changes',
                      result.stdout)

    def test_empty_expiry_section_is_rejected(self):
        record = self.path('docs/decisions/0003-instruction-reading-tiers.md')
        body = re.sub(r'^Expiry and review handling:.*\Z', '', record.read_text(),
                      flags=re.M | re.S)
        record.write_text(body + 'Expiry and review handling:\n')
        result = self.validate()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('states no overdue handling', result.stdout)

    def test_missing_expiry_section_is_rejected(self):
        record = self.path('docs/decisions/0001-distribution.md')
        record.write_text(re.sub(r'^Expiry and review handling:.*\Z', '',
                                 record.read_text(), flags=re.M | re.S))
        result = self.validate()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('missing expiry and review handling', result.stdout)

    HANDLING = ('the underlying requirement holds regardless of either date. An'
                ' overdue review falls back to that requirement, is reported, and'
                ' never widens permission or drops a protection.')

    def write_record(self, drop=(), **overrides):
        """Write docs/decisions/0004-example.md by filling the shipped ADR template.

        Built from templates/decisions/adr.md rather than a hand-written copy, so the
        test fails if the template and the validator drift apart again. `overrides`
        replaces a field's value by label; `drop` omits a field entirely.
        """
        values = {'Expiry date': '2028-11-07', 'Review by': '2027-05-07',
                  'Expiry and review handling': self.HANDLING}
        values.update(overrides)
        lines = ['# ADR 0004: Example decision', '']
        for line in self.path('templates/decisions/adr.md').read_text().splitlines():
            if not line.strip() or line.startswith('#'):
                continue
            label = line.split(':', 1)[0]
            if label in drop:
                continue
            lines.append('{}: {}'.format(
                label, values.get(label, 'a recorded answer for this field.')))
        self.path('docs/decisions/0004-example.md').write_text('\n'.join(lines) + '\n')

    def test_completed_template_record_passes(self):
        self.write_record()
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_template_provides_the_fields_the_validator_requires(self):
        # The template's labels must be exactly what the validator looks for; a
        # parenthetical before a colon silently exempts every record built from it.
        template = self.path('templates/decisions/adr.md').read_text()
        for field in ('Expiry date', 'Review by', 'Expiry and review handling'):
            self.assertRegex(template, r'(?m)^' + field + ':')

    def test_review_date_alone_does_not_satisfy_a_missing_expiry(self):
        # The defect this replaced: prose matched by proximity let one date answer
        # both questions, so a record with only a review date passed as if it had
        # an expiry. The expiry field is now required on its own.
        self.write_record(
            drop=('Expiry date',),
            **{'Expiry and review handling':
               'this record expires once the review concludes; review by 2027-05-07. '
               + self.HANDLING})
        result = self.validate()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('has no "Expiry date: YYYY-MM-DD" field', result.stdout)

    def test_unrelated_dates_without_an_expiry_are_rejected(self):
        self.write_record(
            drop=('Expiry date', 'Review by'),
            **{'Expiry and review handling':
               'we adopted the 2024-01-01 approach and revisited it after the'
               ' 2024-06-01 migration. ' + self.HANDLING})
        result = self.validate()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('has no "Expiry date: YYYY-MM-DD" field', result.stdout)
        self.assertIn('has no "Review by: YYYY-MM-DD" field', result.stdout)

    def test_invalid_calendar_date_is_rejected(self):
        for value in ('2027-02-30', '2027-13-01', '07-05-2027', 'soon'):
            with self.subTest(value=value):
                self.write_record(**{'Review by': value})
                result = self.validate()
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertIn('invalid Review by', result.stdout)
                self.assertIn('expected a real calendar date', result.stdout)

    def test_review_after_expiry_is_rejected(self):
        self.write_record(**{'Review by': '2029-01-01'})
        result = self.validate()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('reviewed only after it expires', result.stdout)

    def test_abbreviated_profile_path_is_rejected(self):
        # A bare `web-saas/PROFILE.md` does not resolve from the project root.
        self.edit('templates/project/ai-governance.md',
                  '`.ai-foundation/profiles/web-saas/PROFILE.md`',
                  '`web-saas/PROFILE.md`')
        result = self.validate()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('omits the complete installed path for web-saas', result.stdout)

    def test_reading_tier_naming_missing_document_is_rejected(self):
        self.edit('templates/project/ai-governance.md',
                  '`.ai-foundation/docs/security/deployment-gate.md`',
                  '`.ai-foundation/docs/security/gone.md`')
        result = self.validate()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('names missing document', result.stdout)

    def test_duplicate_rule_definition_is_rejected(self):
        target = self.path('docs/security/deployment-gate.md')
        target.write_text(target.read_text() + '\n- **AGT-9** Duplicated elsewhere.\n')
        result = self.validate()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('defined in more than one place', result.stdout)

    def test_undefined_rule_citation_is_rejected(self):
        target = self.path('templates/project/ai-governance.md')
        target.write_text(target.read_text() + '\n- Bogus entry citing AGT-99.\n')
        result = self.validate()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('cites undefined rule AGT-99', result.stdout)


if __name__ == '__main__':
    unittest.main()
