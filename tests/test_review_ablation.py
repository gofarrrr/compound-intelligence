"""Offline intervention boundaries and bounded failures; no collected model evidence."""
from copy import deepcopy
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('review_ablation', ROOT / 'evals/run_review_ablation.py')
ablation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ablation)


class ReviewAblationTests(unittest.TestCase):
    def test_promoted_contract_matches_evaluated_G_and_preserves_frozen_A(self):
        from ci_runtime.questions import POSTFLIGHT_VERSION, postflight
        frozen = ablation.frozen_postflight()
        promoted = postflight()
        expected = deepcopy(frozen)
        expected['unsupported_assertions']['instructions'] += ablation.CLARIFICATION
        self.assertEqual(POSTFLIGHT_VERSION, 'ci.postflight.v2.1.0')
        self.assertEqual(promoted, expected)
        self.assertEqual(ablation.digest(promoted),
                         'aafdc55c31551ada8d9c40d7fa18a14d6338a6e1876b40ab26ba48cb8e411dd0')
        self.assertEqual(ablation.digest(frozen),
                         'cfe7583e66ad259cc4fab55ed1da6394bbae2538532836b6b941d0fb7d475b09')
        self.assertEqual(ablation.digest(ablation.load_policy()),
                         '5fb4e7a81e47f49b1d08e74bf86e1204847081d50060211341e5f187f3e741b9')

    def test_frozen_variants_repeat_schedule_and_failure_stop(self):
        registry, policy = ablation.load_registry(), ablation.load_policy()
        original_questions = ablation.frozen_postflight()
        experiment = ablation.prepare(['A', 'F', 'G'], 5, registry, policy)
        self.assertEqual(len(experiment['schedule']), 60)
        self.assertEqual(experiment['unsupported_assertions_cutoff'], .25)
        self.assertEqual(experiment, ablation.prepare(['A', 'F', 'G'], 5, registry, policy))
        archived = ablation.read_json(ROOT / 'docs/validation/review-ablation-afg-2026-10-02.json')
        self.assertEqual(experiment, archived['experiment'])
        self.assertEqual(len({(i['case_id'], i['condition'], i['repeat']) for i in experiment['schedule']}), 60)
        for case_id in ablation.CASE_IDS:
            a = experiment['packets'][case_id + ':A']['state']
            f = experiment['packets'][case_id + ':F']['state']
            self.assertEqual(set(a), {'case', 'draft', 'source_cards'})
            self.assertEqual(a, {k: v for k, v in f.items() if k != 'sentence_types'})
            self.assertEqual(len(f['sentence_types']['annotations']), len(a['draft'].splitlines()))
            self.assertEqual(a, experiment['packets'][case_id + ':G']['state'])
        variants = experiment['conditions']
        self.assertEqual(variants['A']['questions'], original_questions)
        self.assertEqual(variants['F']['questions'], original_questions)
        expected_g = deepcopy(original_questions)
        expected_g['unsupported_assertions']['instructions'] += ablation.CLARIFICATION
        self.assertEqual(variants['G']['questions'], expected_g)
        h = ablation.prepare(['A', 'H'], 5, registry, policy)
        expected_h = deepcopy(original_questions)
        expected_h['framework_load']['criteria'] = ablation.PROPORTIONALITY
        self.assertEqual(h['conditions']['H']['questions'], expected_h)
        self.assertEqual(ablation.frozen_postflight(), original_questions)
        positive = ablation.prepare(['A', 'G'], 5, registry, policy, positive_controls=True)
        self.assertEqual(positive['case_ids'], list(ablation.POSITIVE_CASE_IDS))
        self.assertEqual(len(positive['schedule']), 70)
        self.assertEqual(len({(i['case_id'], i['condition'], i['repeat']) for i in positive['schedule']}), 70)
        self.assertEqual(positive['conditions']['G'], variants['G'])
        for case_id in ablation.POSITIVE_CASE_IDS:
            self.assertEqual(positive['packets'][case_id + ':A']['state'],
                             positive['packets'][case_id + ':G']['state'])
        for conditions in (['A', 'F'], ['A', 'H'], ['A'], ['A', 'F', 'G']):
            with self.assertRaisesRegex(ablation.CIError, 'positive_controls_require_only_A_and_G'):
                ablation.prepare(conditions, 5, registry, policy, positive_controls=True)
        stdout = io.StringIO()
        with patch.object(ablation, 'TypeSafeClient') as unused_client, contextlib.redirect_stdout(stdout):
            self.assertEqual(ablation.main(['--positive-controls', '--plan']), 0)
        unused_client.assert_not_called()
        self.assertEqual(json.loads(stdout.getvalue())['requests'], 70)
        remaining = ablation.prepare(['G'], 5, registry, policy, remaining_grounded=True)
        self.assertEqual(remaining['case_ids'], list(ablation.REMAINING_GROUNDED_CASE_IDS))
        self.assertEqual(len(remaining['schedule']), 25)
        self.assertEqual(remaining['conditions']['G'], variants['G'])
        self.assertEqual(set(remaining['case_ids']) | set(experiment['case_ids']) | set(positive['case_ids']),
                         {row['case_id'] for row in ablation.read_json(ablation.BASELINE)['results']})
        boundaries_path = ROOT / 'evals/review-boundary-cases.jsonl'
        boundaries = ablation.prepare(['A', 'G'], 5, registry, policy, cases_path=boundaries_path)
        self.assertEqual(len(boundaries['schedule']), 60)
        self.assertEqual(boundaries['conditions']['G'], variants['G'])
        self.assertEqual(boundaries['baseline_case_set_digest'], experiment['case_set_digest'])
        self.assertNotEqual(boundaries['case_set_digest'], experiment['case_set_digest'])
        for grounded, unsupported in zip(boundaries['cases'][::2], boundaries['cases'][1::2]):
            self.assertEqual({k: v for k, v in grounded['state'].items() if k != 'case_id'},
                             {k: v for k, v in unsupported['state'].items() if k != 'case_id'})
            self.assertEqual(grounded['cards'], unsupported['cards'])
            self.assertEqual([i for i, (a, b) in enumerate(zip(grounded['sentences'], unsupported['sentences']), 1)
                              if a != b], [4])
        for case_id in boundaries['case_ids']:
            a = boundaries['packets'][case_id + ':A']['state']
            self.assertEqual(a, boundaries['packets'][case_id + ':G']['state'])
            self.assertNotIn('scenario_family', json.dumps(a))
        balanced_h = ablation.prepare(['A', 'H'], 5, registry, policy,
                                     cases_path=ROOT / 'evals/review-framework-cases.jsonl')
        self.assertEqual(len(balanced_h['schedule']), 40)
        self.assertEqual(balanced_h['conditions']['H'], h['conditions']['H'])
        for cli, expected_requests in [(['--remaining-grounded'], 25),
            (['--cases', str(boundaries_path)], 60),
            (['--cases', str(ROOT / 'evals/review-framework-cases.jsonl'), '--conditions', 'A', 'H'], 40)]:
            stdout = io.StringIO()
            with patch.object(ablation, 'TypeSafeClient') as unused_client, contextlib.redirect_stdout(stdout):
                self.assertEqual(ablation.main(cli + ['--plan']), 0)
            unused_client.assert_not_called()
            self.assertEqual(json.loads(stdout.getvalue())['requests'], expected_requests)
        for kwargs in ({'positive_controls': True, 'remaining_grounded': True},
                       {'remaining_grounded': True, 'cases_path': boundaries_path}):
            with self.assertRaises(ablation.CIError):
                ablation.prepare(['A', 'G'], 5, registry, policy, **kwargs)
        with self.assertRaisesRegex(ablation.CIError, 'followup_cases_require_A_and_G_or_A_and_H'):
            ablation.prepare(['A', 'G', 'H'], 5, registry, policy, cases_path=boundaries_path)
        with self.assertRaisesRegex(ablation.CIError, 'remaining_grounded_requires_G_or_A_and_G'):
            ablation.prepare(['A', 'H'], 5, registry, policy, remaining_grounded=True)
        with patch.object(ablation, 'read_text', return_value='{}\n' * 21):
            with self.assertRaisesRegex(ablation.CIError, 'followup_case_budget_exceeded'):
                ablation.prepare(['A', 'G'], 5, registry, policy, cases_path=boundaries_path)
        changed_policy = deepcopy(policy)
        changed_policy['thresholds']['review_negative_max'] = .6
        with self.assertRaisesRegex(ablation.CIError, 'ablation_baseline_changed'):
            ablation.prepare(['A', 'G'], 5, registry, changed_policy)
        for conditions, repeats in [(['G'], 5), (['A', 'A'], 5), (['A', 'G'], 6)]:
            with self.assertRaises(ablation.CIError):
                ablation.prepare(conditions, repeats, registry, policy)

        calls = []
        def transport(payload, key, timeout):
            calls.append(payload)
            self.assertNotIn('human_label', json.dumps(payload))
            self.assertNotIn('unsupported_assertion_present', json.dumps(payload))
            if len(calls) == 3:
                return 401, {}, b''
            answers = {qid: {'type': 'noul', 'noul': .9} for qid in payload['questions'] if qid != 'framework_load'}
            answers['unsupported_assertions']['noul'] = .27 if len(calls) == 1 else .3
            answers['framework_load'] = {'type': 'score', 'score': .64, 'confidence': .04,
                'probabilities': {'0': .5, '1': .36, '2': .14},
                'legend': {str(i): level for i, level in enumerate(payload['questions']['framework_load']['criteria'])}}
            return 200, {}, json.dumps({'model': payload['model'], 'answers': answers,
                                       'usage': {'input_tokens': 10, 'output_tokens': 10}}).encode()

        # Exercise the same provider path with the newly selected positive corpus.
        with patch.dict(os.environ, {'TYPESAFE_API_KEY': 'offline-unit-test-placeholder'}):
            client = ablation.TypeSafeClient(model=positive['model_requested'], transport=transport)
            with self.assertRaises(ablation.CIError):
                ablation.run(positive, registry, client, False)
            positive['cases'][-1]['state']['data_class'] = 'restricted'
            with self.assertRaises(ablation.CIError):
                ablation.run(positive, registry, client, True)
            self.assertEqual(calls, [])
            positive['cases'][-1]['state']['data_class'] = 'anonymized'
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                report = ablation.run(positive, registry, client, True)
        self.assertEqual(len(calls), 3)
        self.assertIn('unavailable (provider_authentication_or_permission_error)', stderr.getvalue())
        self.assertEqual(report['summary']['usable_requests'], 2)
        self.assertEqual(report['results'][-1]['provider_error_code'], 'provider_authentication_or_permission_error')
        self.assertIsNone(report['results'][-1]['jev'])
        self.assertEqual(report['results'][0]['jev']['answers']['framework_load']['probabilities'],
                         {'0': .5, '1': .36, '2': .14})
        self.assertEqual(sum(g['unsupported_assertions']['n'] for g in report['summary']['groups']), 2)
        self.assertFalse(report['thresholds_fitted'])
        self.assertFalse(report['production_questions_modified'])
        self.assertFalse(report['policy_modified'])
        self.assertIn('seven AI-authored positive controls', report['note'])
        self.assertNotIn('No positive controls are included', report['note'])
        with patch.dict(os.environ, {}, clear=True):
            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                missing = ablation.run(remaining, registry, client, True)
        self.assertEqual(len(calls), 3)
        self.assertEqual(missing['summary']['usable_requests'], 0)
        self.assertEqual(missing['results'][0]['provider_error_code'], 'typesafe_key_missing')
        self.assertIn('unavailable (typesafe_key_missing)', stderr.getvalue())


if __name__ == '__main__':
    unittest.main()
