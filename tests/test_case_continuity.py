"""Offline case-record/persistence transitions, not tests of model interpretation.

Authored reports and decision deltas pass through real temporary Markdown files.
These checks establish representation, consent and I/O behavior; no model judges
whether a natural-language detail is material or a recommendation is effective.
"""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT/'skills/compound-intelligence'
spec = importlib.util.spec_from_file_location('case_file',SKILL/'scripts/case_file.py')
store = importlib.util.module_from_spec(spec)
spec.loader.exec_module(store)


def section(text, name, body):
    pattern = r'(?ms)(^## '+re.escape(name)+r'\n).*?(?=^## |\Z)'
    result, count = re.subn(pattern, lambda m: m[1]+body+'\n\n', text)
    assert count == 1
    return result


class ContinuityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.path = self.base/'case.md'
        text = (SKILL/'assets/case-record-template.md').read_text()
        text = text.replace('[short problem title]','Next handoff').replace('[case identifier]','handoff')
        text = section(text,'Goal','Understand the missed handoffs and agree the next one.')
        text = section(text,'Current evidence','User reports two missed handoffs; testing was postponed.')
        text = section(text,'Interpretations','User suspects disengagement; cause unknown.')
        text = section(text,'Unknowns and constraints','Colleague account unknown. Authority to reassign not supplied.')
        text = section(text,'Before the latest attempt','Proposed move: describe two reported missed handoffs and invite the account.\nUser-agreed plan: user says they will try that opening.')
        text = section(text,'Current next move','Prepare a factual opening and invite the colleague account.')
        text = section(text,'Persistence scope','Synthetic test user approved this case at this destination; no general lesson or reminder.')
        text = section(text,'User notes','Do not overwrite my notes.')
        self.text = text

    def create(self, **kwargs):
        return store.write_case(self.path,self.text,case_id='handoff',approved=True,
                                authorized_path=self.path,**kwargs)

    def update(self, text, *, snapshot=None, scope=('New information',), **kwargs):
        snapshot = store.read_case(self.path) if snapshot is None else snapshot
        return store.write_case(self.path,text,case_id='handoff',approved=True,
                                permission='ongoing',authorized_path=self.path,
                                allowed_sections=scope,expected_sha256=snapshot['sha256'],**kwargs)

    def test_plan_is_not_attempt_after_save_and_reopen(self):
        self.create()
        reopened = store.read_case(self.path)
        self.assertIn('will try',reopened['sections']['Before the latest attempt'])
        self.assertIn('Not supplied',reopened['sections']['Attempt'])
        self.assertNotIn('will try',reopened['sections']['Attempt'])
        self.assertIn('Not supplied',reopened['sections']['Outcome'])

    def test_secondhand_report_keeps_attribution(self):
        self.create()
        report = 'User reports that colleague says they requested a priority change; receipt and approval unverified.'
        revised = section(self.text,'New information',report)
        self.update(revised)
        reopened = store.read_case(self.path)
        self.assertEqual(reopened['sections']['New information'],'## New information\n'+report+'\n\n')
        self.assertEqual(reopened['sections']['Current evidence'],store._parse(self.text)['sections']['Current evidence'])
        self.assertIn('cause unknown',reopened['sections']['Interpretations'])

    def test_correction_supersedes_current_evidence_retains_prior_position(self):
        self.create()
        revised = section(self.text,'Current evidence','User corrects the account: one missed handoff; the other was rescheduled.')
        revised = section(revised,'Interpretations','Earlier disengagement interpretation is superseded; cause remains unknown.')
        self.update(revised,scope=('Current evidence','Interpretations'))
        reopened = store.read_case(self.path)
        self.assertIn('one missed handoff',reopened['sections']['Current evidence'])
        self.assertNotIn('two missed',reopened['sections']['Current evidence'])
        self.assertIn('two reported missed',reopened['sections']['Before the latest attempt'])
        self.assertIn('superseded',reopened['sections']['Interpretations'])

    def test_conflicting_reports_remain_separate(self):
        self.create()
        report = 'User reports colleague says request was sent.\nUser reports project lead says it was not received.\nConflict unresolved.'
        self.update(section(self.text,'New information',report))
        reopened = store.read_case(self.path)['sections']['New information']
        self.assertIn('colleague says request was sent',reopened)
        self.assertIn('project lead says it was not received',reopened)
        self.assertIn('Conflict unresolved',reopened)

    def test_immaterial_report_update_keeps_move_and_blocks_out_of_scope_change(self):
        self.create()
        old = store.read_case(self.path)
        revised = section(self.text,'New information','User reports a different room; no material effect on the opening.')
        self.update(revised)
        current = store.read_case(self.path)
        self.assertEqual(current['sections']['Current next move'],old['sections']['Current next move'])
        unwanted = section(revised,'Current next move','Use an unrelated new method.')
        with self.assertRaisesRegex(store.CaseError,'sections_outside_consent'):
            self.update(unwanted)
        self.assertEqual(self.path.read_text(),revised)

    def test_no_attempt_return_preserves_unknown_outcome_and_preparation(self):
        self.create()
        revised = section(self.text,'Attempt','User reports: not tried.')
        revised = section(revised,'Current next move','Continue preparing the opening; no outcome is established.')
        self.update(revised,scope=('Attempt','Current next move'))
        current = store.read_case(self.path)
        self.assertIn('not tried',current['sections']['Attempt'])
        self.assertIn('Not supplied',current['sections']['Outcome'])
        self.assertIn('Continue preparing',current['sections']['Current next move'])

    def test_snapshot_only_cannot_overwrite_even_with_approve_flag(self):
        self.create()
        revised = section(self.text,'New information','User returned.')
        with self.assertRaisesRegex(store.CaseError,'snapshot_only'):
            store.write_case(self.path,revised,case_id='handoff',approved=True,
                             authorized_path=self.path,permission='snapshot_only',
                             expected_sha256=store.read_case(self.path)['sha256'],
                             allowed_sections=('New information',))
        self.assertEqual(self.path.read_text(),self.text)
        # A fresh specific update is a separate legitimate approval.
        result = store.write_case(self.path,revised,case_id='handoff',approved=True,
                                  authorized_path=self.path,permission='update_once',
                                  expected_sha256=store.read_case(self.path)['sha256'],
                                  allowed_sections=('New information',))
        self.assertTrue(result['saved'])

    def test_ongoing_consent_requires_same_case_path_scope_and_actual_approval(self):
        self.create()
        revised = section(self.text,'New information','User returned.')
        params = dict(case_id='handoff',approved=True,permission='ongoing',
                      authorized_path=self.path,allowed_sections=('New information',),
                      expected_sha256=store.read_case(self.path)['sha256'])
        for change in [{'case_id':'other'},{'authorized_path':self.base/'other.md'},
                       {'allowed_sections':('Outcome',)},{'approved':False}]:
            with self.subTest(change=change),self.assertRaises(store.CaseError):
                store.write_case(self.path,revised,**dict(params,**change))
            self.assertEqual(self.path.read_text(),self.text)
        self.assertTrue(store.write_case(self.path,revised,**params)['saved'])

    def test_stale_file_must_be_reread_and_reconciled_preserving_user_edits(self):
        self.create()
        old = store.read_case(self.path)
        user_edit = section(self.text,'User notes','Keep my revised note and constraint.')
        self.path.write_text(user_edit)
        stale_draft = section(self.text,'New information','User reports an earlier priority request.')
        with self.assertRaisesRegex(store.CaseError,'stale_case_read'):
            self.update(stale_draft,snapshot=old)
        self.assertEqual(self.path.read_text(),user_edit)
        fresh = store.read_case(self.path)
        reconciled = section(fresh['text'],'New information','User reports an earlier priority request.')
        self.update(reconciled,snapshot=fresh)
        self.assertIn('Keep my revised note',store.read_case(self.path)['sections']['User notes'])

    def test_write_truth_failure_reports_not_saved_and_keeps_original(self):
        self.create()
        revised = section(self.text,'New information','User returned.')
        draft = self.base/'draft.md';draft.write_text(revised)
        output = io.StringIO()
        with patch.object(store.os,'replace',side_effect=OSError('synthetic write failure')),contextlib.redirect_stdout(output):
            code = store.main(['write','--destination',str(self.path),'--draft',str(draft),
                               '--case-id','handoff','--approve-write','--permission','ongoing',
                               '--scope','New information','--expected-sha256',store.read_case(self.path)['sha256']])
        self.assertEqual(code,1)
        self.assertFalse(json.loads(output.getvalue())['saved'])
        self.assertEqual(self.path.read_text(),self.text)
        self.assertFalse(list(self.base.glob('.ci-case-*.tmp')))

    def test_no_op_does_not_claim_new_save_and_files_are_private(self):
        self.create()
        self.assertEqual(stat.S_IMODE(self.path.stat().st_mode),0o600)
        result = self.update(self.text)
        self.assertFalse(result['saved'])
        self.assertEqual(result['status'],'unchanged')

    def test_exclusive_creation_and_protected_or_symlink_destinations(self):
        self.create()
        with self.assertRaises(FileExistsError):self.create()
        link = self.base/'link.md';link.symlink_to(self.path)
        for path in [link,SKILL/'private-case.md',ROOT/'private-case.md']:
            with self.subTest(path=path),self.assertRaises(store.CaseError):
                store.write_case(path,self.text,case_id='handoff',approved=True,authorized_path=path)

    def test_external_section_edit_during_temporary_write_is_detected(self):
        self.create()
        original_read = store.read_case
        count = 0
        user_edit = section(self.text,'User notes','Edited while a draft was being written.')
        def read_with_edit(path):
            nonlocal count
            count += 1
            if count == 2:self.path.write_text(user_edit)
            return original_read(path)
        revised = section(self.text,'New information','User returned.')
        current = store.read_case(self.path)
        with patch.object(store,'read_case',side_effect=read_with_edit),self.assertRaisesRegex(store.CaseError,'stale_case_read'):
            self.update(revised,snapshot=current)
        self.assertEqual(self.path.read_text(),user_edit)

    def test_different_actual_attempt_and_no_automatic_lessons(self):
        self.create()
        before = store.read_case(self.path)
        revised = section(self.text,'Attempt','User reports sending a demand instead of trying the planned opening.')
        revised = section(revised,'Outcome','User reports no reply yet; cause unknown.')
        self.update(revised,scope=('Attempt','Outcome'))
        current = store.read_case(self.path)
        self.assertEqual(current['sections']['Before the latest attempt'],before['sections']['Before the latest attempt'])
        self.assertIn('instead',current['sections']['Attempt'])
        self.assertEqual(current['sections']['Provisional lesson'],before['sections']['Provisional lesson'])

    def test_cli_save_read_and_scoped_return_using_real_processes(self):
        draft = self.base/'draft.md';draft.write_text(self.text)
        def run(*args, expected=0):
            result = subprocess.run([sys.executable,str(SKILL/'scripts/case_file.py'),*args],
                                    capture_output=True,text=True,check=False,cwd=self.base)
            self.assertEqual(result.returncode,expected,result.stdout+result.stderr)
            return json.loads(result.stdout)
        write_args = ('write','--destination',str(self.path),'--draft',str(draft),'--case-id','handoff')
        self.assertFalse(run(*write_args,expected=1)['saved'])
        self.assertFalse(self.path.exists())
        self.assertTrue(run(*write_args,'--approve-write')['saved'])
        before = run('read',str(self.path))
        revised = section(before['text'],'Attempt','User reports trying the factual opening.')
        revised = section(revised,'New information','User reports colleague described an earlier priority request; approval unknown.')
        draft.write_text(revised)
        result = run(*write_args,'--approve-write','--permission','update_once',
                     '--scope','Attempt','New information','--expected-sha256',before['sha256'])
        self.assertTrue(result['saved'])
        after = run('read',str(self.path))
        self.assertEqual(after['sha256'],result['sha256'])
        self.assertIn('approval unknown',after['sections']['New information'])
        self.assertEqual(after['sections']['Before the latest attempt'],before['sections']['Before the latest attempt'])

    def test_malformed_record_refused_without_overwriting_existing_file(self):
        self.create()
        malformed = [self.text+'\n## Attempt\nDuplicate\n',
                     self.text.replace('## Outcome\n','### Outcome\n'),
                     self.text.replace('Case ID: handoff','Case ID: different case'),
                     self.text+'\x00', self.text+('x'*store.MAX_BYTES)]
        before = store.read_case(self.path)
        for text in malformed:
            with self.subTest(size=len(text)),self.assertRaises(store.CaseError):
                self.update(text,snapshot=before)
            self.assertEqual(self.path.read_text(),self.text)

    def test_scoped_update_rejects_reordered_sections_including_user_sections(self):
        cases = [
            (False, 'Goal', 'Current evidence'),
            (True, 'Goal', 'Current evidence'),
            (True, 'Current evidence', 'Supporting notes'),
        ]
        for index, (extra, first, second) in enumerate(cases):
            with self.subTest(extra=extra, swapped=(first,second)):
                path = self.base/f'ordered-{index}.md'
                original = self.text
                if extra:
                    original += '\n## Supporting notes\nKeep this user-authored section.\n\n'
                store.write_case(path,original,case_id='handoff',approved=True,
                                 authorized_path=path)
                before = store.read_case(path)
                revised = section(original,'Goal','Prepare the next handoff conversation.')
                record = store._parse(revised)
                order = list(record['sections'])
                i, j = order.index(first), order.index(second)
                order[i], order[j] = order[j], order[i]
                reordered = record['preamble']+''.join(record['sections'][s] for s in order)
                with self.assertRaisesRegex(store.CaseError,'^case_header_or_sections_changed$'):
                    store.write_case(path,reordered,case_id='handoff',approved=True,
                                     permission='update_once',authorized_path=path,
                                     allowed_sections=('Goal',),expected_sha256=before['sha256'])
                self.assertEqual(path.read_bytes(),original.encode('utf-8'))


if __name__ == '__main__':
    unittest.main()
