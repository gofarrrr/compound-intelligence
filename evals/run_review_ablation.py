#!/usr/bin/env python3
"""Frozen review-state/question pilot; experimental variants never change the runtime."""
from __future__ import annotations
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import random
from statistics import mean, stdev
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_review_diagnostics import (CIError, ROOT, TypeSafeClient, check_output_path,
    digest, ensure_egress, load_cases, load_policy, load_registry, normalize_state,
    outbound_state, read_json, read_text, redact, reference_cards, write_new_json)
from ci_runtime.common import canonical, file_digest

BASELINE = ROOT / 'docs/validation/review-diagnostics-2026-10-02.json'
FROZEN_QUESTIONS = ROOT / 'docs/validation/review-ablation-afg-2026-10-02.json'
CASE_IDS = ('ua-001', 'ua-004', 'ua-010', 'ua-012')
POSITIVE_CASE_IDS = ('ua-002', 'ua-003', 'ua-005', 'ua-006', 'ua-007', 'ua-009', 'ua-013')
REMAINING_GROUNDED_CASE_IDS = ('ua-008', 'ua-011', 'ua-014', 'ua-015', 'ua-016')
SEED = 20261002
DESCRIPTIONS = {
    'A': 'Unchanged diagnostic packet and all eight production questions.',
    'F': 'Only add AI-authored sentence-type annotations to state; keep draft and questions unchanged.',
    'G': 'Only clarify the assertion question: advice/questions do not assert that an event occurred.',
    'H': 'Only replace framework-load criteria with the experimental proportionality rubric.'}
CLARIFICATION = (
    ' A recommendation, imperative, question, or suggested practice is not a factual assertion '
    'merely because the case does not state that it already happened. If advice also asserts '
    'an unsupported event, cause, permission, or promised outcome, judge that assertion.')
PROPORTIONALITY = [
    "Framework use is proportionate to the user's objective. Multiple methods may be appropriate "
    'when they address distinct requested subgoals.',
    'Some method steps or terminology do not materially serve the requested objective.',
    'The draft imposes substantial unrequested framework work, curriculum, or process.']
# Several types can coexist within a sentence. These are intervention hints, not gold labels.
TYPES = {
    'ua-001': [('attribution',), ('attribution',), ('recommendation', 'framework_statement'),
               ('recommendation', 'question'), ('recommendation',)],
    'ua-004': [('attribution',), ('attribution',), ('hypothesis', 'recommendation'),
               ('recommendation', 'framework_statement'), ('recommendation', 'question'), ('recommendation',)],
    'ua-010': [('attribution',), ('attribution',)] +
              [('recommendation', 'framework_statement')] * 10 + [('recommendation',)] * 2,
    'ua-012': [('attribution',), ('attribution',), ('framework_statement', 'recommendation')] +
              [('recommendation',)] * 3}


def frozen_postflight() -> dict:
    """Use the archived v2.0.0 A contract even after the live runtime changes."""
    return read_json(FROZEN_QUESTIONS)['experiment']['conditions']['A']['questions']


def prepare(conditions: list[str], repeats: int, registry: list[dict], policy: dict,
            positive_controls: bool = False, remaining_grounded: bool = False,
            cases_path: Path | None = None) -> dict:
    if (type(positive_controls) is not bool or type(remaining_grounded) is not bool or
            sum((positive_controls, remaining_grounded, cases_path is not None)) > 1):
        raise CIError('ablation_case_modes_must_be_exclusive')
    if (type(repeats) is not int or not 1 <= repeats <= 5 or not conditions or
            ('A' not in conditions and not (remaining_grounded and conditions == ['G'])) or
            len(set(conditions)) != len(conditions) or
            any(c not in DESCRIPTIONS for c in conditions)):
        raise CIError('invalid_ablation_budget_or_conditions')
    if positive_controls and set(conditions) != {'A', 'G'}:
        raise CIError('positive_controls_require_only_A_and_G')
    if remaining_grounded and set(conditions) not in ({'G'}, {'A', 'G'}):
        raise CIError('remaining_grounded_requires_G_or_A_and_G')
    if cases_path is not None and set(conditions) not in ({'A', 'G'}, {'A', 'H'}):
        raise CIError('followup_cases_require_A_and_G_or_A_and_H')
    case_ids = (POSITIVE_CASE_IDS if positive_controls else
                REMAINING_GROUNDED_CASE_IDS if remaining_grounded else CASE_IDS)
    corpus = load_cases(ROOT / 'evals/review-diagnostic-cases.jsonl', 16, registry)
    baseline, questions = read_json(BASELINE), frozen_postflight()
    frozen = {'case_set_digest': digest(corpus), 'registry_digest': digest(registry),
              'question_digest': digest(questions), 'policy_digest': digest(policy)}
    if any(baseline[k] != v for k, v in frozen.items()):
        raise CIError('ablation_baseline_changed')
    archived = {r['case_id']: r for r in baseline['results']}
    if cases_path is not None:
        if sum(bool(line.strip()) for line in read_text(cases_path).splitlines()) > 20:
            raise CIError('followup_case_budget_exceeded')
        corpus = load_cases(cases_path, 20, registry)
        case_ids = tuple(c['case_id'] for c in corpus)
        frozen['baseline_case_set_digest'] = frozen['case_set_digest']
        frozen['case_set_digest'] = digest(corpus)
    cases = [c for c in corpus if c['case_id'] in case_ids]
    if tuple(c['case_id'] for c in cases) != case_ids:
        raise CIError('ablation_cases_missing')
    variants, packets = {}, {}
    for condition in conditions:
        variant = deepcopy(questions)
        if condition == 'G':
            variant['unsupported_assertions']['instructions'] += CLARIFICATION
        elif condition == 'H':
            variant['framework_load']['criteria'] = PROPORTIONALITY.copy()
        description = ('Unchanged follow-up case packet and all eight production questions.'
                       if cases_path is not None and condition == 'A' else DESCRIPTIONS[condition])
        variants[condition] = {'description': description, 'questions': variant,
            'question_digest': digest(variant), 'question_version': baseline['question_version']
            if condition in ('A', 'F') else 'ci.review-ablation.v1.' + condition}
    for case in cases:
        original = {'case': outbound_state(normalize_state(case['state'], registry)),
                    'draft': redact('\n'.join(case['sentences'])), 'source_cards': reference_cards(case, registry)}
        if (case['case_id'] in archived and
                digest(original) != archived[case['case_id']]['outbound_state_digest']):
            raise CIError('ablation_outbound_baseline_changed')
        if 'F' in conditions and len(TYPES[case['case_id']]) != len(case['sentences']):
            raise CIError('ablation_sentence_annotations_mismatch')
        for condition in conditions:
            state = deepcopy(original)
            if condition == 'F':
                state['sentence_types'] = {
                    'provenance': 'AI-authored syntactic annotations; not verified evidence or correctness labels.',
                    'index': 'Sentence IDs refer to draft lines counted from one.',
                    'annotations': [{'sentence_id': i, 'types': list(types)} for i, types in
                                    enumerate(TYPES[case['case_id']], 1)]}
            payload = {'state': state, 'questions': variants[condition]['questions'],
                       'model': baseline['model_requested']}
            if len(canonical(payload)) > 100_000:
                raise CIError('request_byte_budget_exceeded')
            packets[case['case_id'] + ':' + condition] = {
                'state': state, 'outbound_state_digest': digest(state),
                'draft_digest': digest(state['draft']), 'request_digest': digest(payload)}
    rng, schedule = random.Random(SEED), []
    for repeat in range(1, repeats + 1):
        block = [{'case_id': c, 'condition': condition, 'repeat': repeat}
                 for c in case_ids for condition in conditions]
        rng.shuffle(block)
        schedule.extend(block)
    experiment = {'experiment_version': 'ci.review-ablation.v1', 'baseline_sha256': file_digest(BASELINE),
            **frozen, 'model_requested': baseline['model_requested'], 'policy_version': policy['version'],
            'unsupported_assertions_cutoff': policy['thresholds']['review_negative_max'],
            'seed': SEED, 'repeats': repeats, 'case_ids': list(case_ids),
            'conditions': variants, 'cases': cases, 'packets': packets, 'schedule': schedule}
    if positive_controls:
        experiment['purpose'] = 'assertion_sensitivity_preservation'
    elif remaining_grounded:
        experiment['purpose'] = 'assertion_grounded_coverage_completion'
    elif cases_path is not None:
        experiment['purpose'] = 'declared_followup_corpus'
        resolved = cases_path.resolve()
        experiment['corpus_path'] = str(resolved.relative_to(ROOT) if resolved.is_relative_to(ROOT) else resolved)
        experiment['corpus_sha256'] = file_digest(cases_path)
    return experiment


def describe(values: list[float]) -> dict:
    return {'n': len(values), 'values': values, 'mean': mean(values) if values else None,
            'min': min(values) if values else None, 'max': max(values) if values else None,
            'sample_stdev': stdev(values) if len(values) > 1 else None}


def run(experiment: dict, registry: list[dict], client: TypeSafeClient, consent: bool) -> dict:
    # Check every selected case before the first paid request.
    for case in experiment['cases']:
        ensure_egress(normalize_state(case['state'], registry), consent)
    if client.model != experiment['model_requested'] or client.attempts > 2:
        raise CIError('ablation_model_or_attempt_budget_changed')
    results, interrupted = [], False
    try:
        for sequence, item in enumerate(experiment['schedule'], 1):
            packet = experiment['packets'][item['case_id'] + ':' + item['condition']]
            variant = experiment['conditions'][item['condition']]
            row = item | {'sequence': sequence, 'created_at': datetime.now(timezone.utc).isoformat(),
                'request_digest': packet['request_digest'], 'provider_status': 'unavailable',
                'provider_error_code': None, 'jev': None}
            try:
                row['jev'] = client.evaluate(packet['state'], variant['questions'])
                row['provider_status'] = 'ok'
            except CIError as exc:
                row['provider_error_code'] = exc.code
            results.append(row)
            status = row['provider_status']
            if row['provider_error_code']:
                status += f" ({row['provider_error_code']})"
            print(f"{sequence}/{len(experiment['schedule'])} {item['case_id']} {item['condition']} "
                  f"repeat {item['repeat']}: {status}", file=sys.stderr)
            if row['provider_status'] != 'ok':
                break
    except KeyboardInterrupt:
        interrupted = True
    observed = [r for r in results if r['provider_status'] == 'ok']
    groups = []
    for case_id in experiment['case_ids']:
        for condition in experiment['conditions']:
            answers = [r['jev']['answers'] for r in observed
                       if r['case_id'] == case_id and r['condition'] == condition]
            ua = describe([a['unsupported_assertions']['noul'] for a in answers])
            groups.append({'case_id': case_id, 'condition': condition, 'unsupported_assertions': ua,
                'flagged_at_frozen_cutoff': sum(v > experiment['unsupported_assertions_cutoff'] for v in ua['values']),
                'framework_score': describe([a['framework_load']['score'] for a in answers]),
                'framework_confidence': [a['framework_load']['confidence'] for a in answers]})
    return {'kind': 'exploratory_review_ablation', 'created_at': datetime.now(timezone.utc).isoformat(),
        'experiment': experiment, 'thresholds_fitted': False, 'production_questions_modified': False,
        'policy_modified': False, 'independent_human_validation': False,
        'summary': {'requests_planned': len(experiment['schedule']), 'requests_attempted': len(results),
                    'usable_requests': len(observed), 'interrupted': interrupted, 'groups': groups},
        'results': results,
        'note': ('Descriptive repeats on seven AI-authored positive controls, not accuracy or calibration. '
                 'These cover cause, motive, source claim, trait, authority, count and overgeneralization; '
                 'no promised-outcome control is included. '
                 if experiment.get('purpose') == 'assertion_sensitivity_preservation' else
                 'Descriptive repeats on the five remaining AI-authored grounded drafts. '
                 'ua-011 is an out-of-scope postflight stress test, not an intended coaching flow. '
                 if experiment.get('purpose') == 'assertion_grounded_coverage_completion' else
                 'Descriptive repeats on a separately declared follow-up corpus. '
                 'Intended labels are AI-authored hypotheses, not independent validation. '
                 if experiment.get('purpose') == 'declared_followup_corpus' else
                 'Descriptive repeats on four AI-authored negative examples, not accuracy or calibration. '
                 'No positive controls are included; test preserved detection on unsupported drafts. ') +
                'F contains AI annotation hints, not independent evidence. G/H are experimental contracts. '
                'H Score levels have different meanings; a lower score alone does not prove improvement. '
                'No variant is adopted automatically; consult the dated evaluation protocol and evidence gaps. '
                'Full Score distributions are retained '
                'in results; Score/confidence are never converted into P(yes).'}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--plan', action='store_true', help='Validate frozen inputs and print budget; no network.')
    mode = p.add_mutually_exclusive_group()
    mode.add_argument('--positive-controls', action='store_true', help='Seven frozen unsupported drafts; A/G only.')
    mode.add_argument('--remaining-grounded', action='store_true', help='Five remaining frozen grounded drafts; G by default.')
    mode.add_argument('--cases', type=Path, help='Separate follow-up JSONL corpus, at most 20 cases; A/G or A/H only.')
    p.add_argument('--conditions', nargs='+', choices=tuple(DESCRIPTIONS),
                   help='Defaults to A/F/G, A/G with --positive-controls or --cases, G with --remaining-grounded.')
    p.add_argument('--repeats', type=int, default=5)
    p.add_argument('--consent-send', action='store_true')
    p.add_argument('--output', type=Path, help='New external result file; never overwritten.')
    args = p.parse_args(argv)
    try:
        registry, policy = load_registry(), load_policy()
        conditions = args.conditions or (['G'] if args.remaining_grounded else
            ['A', 'G'] if args.positive_controls or args.cases else ['A', 'F', 'G'])
        experiment = prepare(conditions, args.repeats, registry, policy, args.positive_controls,
                             args.remaining_grounded, args.cases)
        if args.plan:
            print(json.dumps({'network_called': False, 'model': experiment['model_requested'],
                'case_ids': experiment['case_ids'], 'conditions': {k: {'description': v['description'],
                    'question_digest': v['question_digest']} for k, v in experiment['conditions'].items()},
                'repeats': args.repeats, 'requests': len(experiment['schedule']),
                'maximum_http_attempts': 2 * len(experiment['schedule']),
                'unsupported_assertions_cutoff': experiment['unsupported_assertions_cutoff'],
                'experiment_digest': digest(experiment)}, indent=2))
            return 0
        if not args.consent_send or not args.output:
            raise CIError('live_ablation_requires_consent_and_external_output')
        check_output_path(args.output)
        client = TypeSafeClient(model=experiment['model_requested'])
        report = run(experiment, registry, client, args.consent_send)
        write_new_json(args.output, report)
        print(json.dumps({'output': str(args.output), **report['summary']}, indent=2))
        return 130 if report['summary']['interrupted'] else (
            0 if report['summary']['usable_requests'] == len(experiment['schedule']) else 2)
    except CIError as exc:
        print(json.dumps({'error_code': exc.code}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
