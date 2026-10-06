"""Offline diagnostic checks; fixture labels and answers are not human/model evidence."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('review_diagnostics', ROOT / 'evals/run_review_diagnostics.py')
diagnostic = importlib.util.module_from_spec(spec)
spec.loader.exec_module(diagnostic)


class ReviewDiagnosticTests(unittest.TestCase):
    def test_label_bindings_disagreements_and_failure_stop(self):
        registry, policy = diagnostic.load_registry(), diagnostic.load_policy()
        cases = diagnostic.load_cases(ROOT / 'evals/review-diagnostic-cases.jsonl', 16, registry)
        self.assertEqual(len(cases), 16)
        self.assertEqual(cases[10]['cards'], [])
        self.assertEqual(len(cases[11]['cards']), 2)
        packet = diagnostic.label_packet(cases, registry)
        with self.assertRaisesRegex(diagnostic.CIError, 'human_reviewer_required'):
            diagnostic.validate_labels(packet, cases, registry)
        packet['reviewer'] = 'Offline fixture; not a human judgment'
        with self.assertRaisesRegex(diagnostic.CIError, 'reviewer_kind_required'):
            diagnostic.validate_labels(packet, cases, registry)
        packet['reviewer_kind'] = 'ai'
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp).resolve()
            packet_path = folder / 'labels.json'
            diagnostic.write_new_json(packet_path, packet)
            for reviewer, code in [(None, 'human_reviewer_required'), ('Human test reviewer', 'human_labels_must_be_completed')]:
                packet['reviewer'] = reviewer
                packet_path.write_text(json.dumps(packet))
                stderr = io.StringIO()
                with patch.object(diagnostic, 'TypeSafeClient') as client, contextlib.redirect_stderr(stderr):
                    status = diagnostic.main(['--labels', str(packet_path), '--consent-send',
                                              '--output', str(folder / 'results.json')])
                self.assertEqual(status, 2)
                client.assert_not_called()
                error = json.loads(stderr.getvalue())
                self.assertEqual(error['error_code'], code)
                self.assertIn('message', error)
                self.assertFalse(error['network_called'])
                self.assertFalse((folder / 'results.json').exists())
        packet['reviewer'] = 'Offline fixture; not a human judgment'
        for row in packet['labels']:
            row['human_label'] = {'unsupported_assertion_present': False, 'sentence_ids': [],
                'rationale': 'Synthetic unit-test label.',
                'framework_load': {'level': 0, 'sentence_ids': [], 'rationale': 'Synthetic unit-test label.'}}
        packet['labels'][0]['human_label']['framework_load'].update(level=1, sentence_ids=[3])
        packet['labels'][1]['human_label'].update(unsupported_assertion_present=True, sentence_ids=[3])
        labels = diagnostic.validate_labels(packet, cases, registry)
        packet['labels'][1]['human_label']['sentence_ids'] = [99]
        with self.assertRaises(diagnostic.CIError):
            diagnostic.validate_labels(packet, cases, registry)
        packet['labels'][1]['human_label']['sentence_ids'] = [3]
        packet['labels'][0]['sentences'][0]['text'] = 'Changed draft after labeling.'
        with self.assertRaises(diagnostic.CIError):
            diagnostic.validate_labels(packet, cases, registry)

        calls = []
        def transport(payload, key, timeout):
            calls.append(payload)
            self.assertEqual(set(payload['state']), {'case', 'draft', 'source_cards'})
            self.assertNotIn('human_label', json.dumps(payload))
            if len(calls) == 3:
                return 401, {}, b''
            answers = {qid: {'type': 'noul', 'noul': 0.9} for qid in payload['questions'] if qid != 'framework_load'}
            answers['unsupported_assertions']['noul'] = .3 if len(calls) == 1 else .2
            answers['oversteps_agency']['noul'] = .1
            answers['framework_load'] = {'type': 'score', 'score': .64, 'confidence': .04,
                'probabilities': {'0': .5, '1': .36, '2': .14},
                'legend': {str(i): level for i, level in enumerate(payload['questions']['framework_load']['criteria'])}}
            raw = {'model': payload['model'], 'answers': answers, 'usage': {'input_tokens': 10, 'output_tokens': 10}}
            return 200, {}, json.dumps(raw).encode()

        with patch.dict(os.environ, {'TYPESAFE_API_KEY': 'offline-unit-test-placeholder', 'CI_JEV_MODEL': 'jev-1.13.0'}):
            client = diagnostic.TypeSafeClient(transport=transport)
            with self.assertRaises(diagnostic.CIError):
                diagnostic.run(cases, labels, registry, policy, client, False)
            self.assertEqual(calls, [])
            cases[-1]['state']['data_class'] = 'restricted'
            with self.assertRaises(diagnostic.CIError):
                diagnostic.run(cases, labels, registry, policy, client, True)
            self.assertEqual(calls, [])
            cases[-1]['state']['data_class'] = 'anonymized'
            with contextlib.redirect_stderr(io.StringIO()):
                result = diagnostic.run(cases, labels, registry, policy, client, True)
        self.assertEqual(len(calls), 3)
        self.assertEqual(result['summary']['usable_cases'], 2)
        self.assertEqual(result['results'][-1]['provider_status'], 'unavailable')
        self.assertIsNone(result['results'][-1]['jev'])
        unsupported = result['summary']['unsupported_assertions']
        self.assertEqual(unsupported['flagged_reviewer_negative_case_ids'], ['ua-001'])
        self.assertEqual(unsupported['unflagged_reviewer_positive_case_ids'], ['ua-002'])
        self.assertEqual(result['summary']['framework_load']['disagreement_case_ids'], ['ua-001'])
        self.assertEqual(result['results'][0]['jev']['framework_load']['confidence'], .04)
        self.assertEqual(result['results'][0]['jev']['framework_load']['score'], .64)
        self.assertFalse(result['thresholds_fitted'])
        self.assertFalse(result['policy_modified'])


if __name__ == '__main__':
    unittest.main()
