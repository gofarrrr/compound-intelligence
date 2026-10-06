#!/usr/bin/env python3
"""Exploratory review disagreements, with declared reviewer provenance."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/compound-intelligence/scripts'))
from ci_runtime.client import TypeSafeClient
from ci_runtime.common import (CIError, SKILL_ROOT, check_output_path, digest, load_policy,
                               load_registry, parse_json, read_json, read_text, safe_id,
                               write_new_json)
from ci_runtime.policy import review_decision
from ci_runtime.questions import POSTFLIGHT_VERSION, postflight
from ci_runtime.state import ensure_egress, normalize_state, outbound_state, redact


def load_cases(path: Path, maximum: int, registry: list[dict]) -> list[dict]:
    if not 1 <= maximum <= 20:
        raise CIError('diagnostic_case_budget_out_of_bounds')
    cases = [parse_json(line) for line in read_text(path).splitlines() if line.strip()]
    seen, known = set(), {r['id'] for r in registry}
    for case in cases:
        if not isinstance(case, dict) or set(case) != {'case_id', 'scenario_family', 'state', 'cards', 'sentences'}:
            raise CIError('invalid_diagnostic_case')
        safe_id(case['case_id'])
        safe_id(case['scenario_family'])
        state = normalize_state(case['state'], registry)
        if case['case_id'] in seen or state['case_id'] != case['case_id']:
            raise CIError('duplicate_or_mismatched_diagnostic_case')
        seen.add(case['case_id'])
        cards, sentences = case['cards'], case['sentences']
        if (not isinstance(cards, list) or len(cards) > 2 or
                any(not isinstance(c, str) or c not in known for c in cards) or len(set(cards)) != len(cards)):
            raise CIError('invalid_diagnostic_cards')
        if (not isinstance(sentences, list) or not sentences or
                any(not isinstance(s, str) or not s.strip() or '\x00' in s for s in sentences) or
                len('\n'.join(sentences).encode('utf-8')) > 24_000):
            raise CIError('invalid_diagnostic_sentences')
    if not cases:
        raise CIError('diagnostic_cases_empty')
    return cases[:maximum]


def reference_cards(case: dict, registry: list[dict]) -> list[dict]:
    by_id = {r['id']: r for r in registry}
    return [{'id': c, 'content': read_text(SKILL_ROOT / by_id[c]['path'])} for c in case['cards']]


def label_packet(cases: list[dict], registry: list[dict]) -> dict:
    return {'kind': 'exploratory_label_packet', 'case_set_digest': digest(cases),
            'reviewer': None, 'reviewer_kind': None, 'labels': [case | {
                'sentences': [{'id': i, 'text': s} for i, s in enumerate(case['sentences'], 1)],
                'source_cards': reference_cards(case, registry),
                'human_label': {'unsupported_assertion_present': None, 'sentence_ids': [], 'rationale': '',
                    'framework_load': {'level': None, 'sentence_ids': [], 'rationale': ''}}
            } for case in cases]}


def validate_labels(packet: dict, cases: list[dict], registry: list[dict]) -> dict:
    expected = label_packet(cases, registry)
    if (not isinstance(packet, dict) or set(packet) != set(expected) or
            packet['kind'] != expected['kind'] or packet['case_set_digest'] != expected['case_set_digest'] or
            not isinstance(packet['labels'], list) or len(packet['labels']) != len(cases)):
        raise CIError('invalid_or_incomplete_label_packet')
    if not isinstance(packet['reviewer'], str) or not packet['reviewer'].strip():
        raise CIError('human_reviewer_required')
    if packet['reviewer_kind'] not in ('human', 'ai'):
        raise CIError('reviewer_kind_required')
    labels = {}
    for row, original in zip(packet['labels'], expected['labels']):
        if (not isinstance(row, dict) or set(row) != set(original) or
                any(row[k] != original[k] for k in original if k != 'human_label')):
            raise CIError('labels_do_not_match_case_and_sources')
        label = row['human_label']
        if not isinstance(label, dict) or set(label) != set(original['human_label']):
            raise CIError('invalid_human_label')
        if type(label['unsupported_assertion_present']) is not bool:
            raise CIError('human_labels_must_be_completed')
        load = label['framework_load']
        if (not isinstance(load, dict) or set(load) != {'level', 'sentence_ids', 'rationale'} or
                type(load['level']) is not int or load['level'] not in {0, 1, 2}):
            raise CIError('human_framework_label_must_be_completed')
        for judgment in (label, load):
            ids = judgment['sentence_ids']
            if (not isinstance(ids, list) or any(type(i) is not int or not 1 <= i <= len(row['sentences']) for i in ids) or
                    len(set(ids)) != len(ids) or not isinstance(judgment['rationale'], str) or
                    not judgment['rationale'].strip()):
                raise CIError('human_labels_need_valid_sentence_ids_and_rationale')
        if label['unsupported_assertion_present'] != bool(label['sentence_ids']):
            raise CIError('unsupported_label_and_sentence_ids_disagree')
        if load['level'] > 0 and not load['sentence_ids']:
            raise CIError('framework_overload_label_needs_sentence_ids')
        labels[row['case_id']] = label
    return labels


def run(cases: list[dict], labels: dict, registry: list[dict], policy: dict,
        client: TypeSafeClient, consent: bool) -> dict:
    states = [normalize_state(c['state'], registry) for c in cases]
    # Preflight every case before any paid request.
    for state in states:
        ensure_egress(state, consent)
    questions, results, interrupted = postflight(), [], False
    try:
        for case, state in zip(cases, states):
            draft = '\n'.join(case['sentences'])
            outgoing = {'case': outbound_state(state), 'draft': redact(draft),
                        'source_cards': reference_cards(case, registry)}
            row = case | {'draft': draft,
                          'sentences': [{'id': i, 'text': s} for i, s in enumerate(case['sentences'], 1)],
                          'human_label': labels[case['case_id']], 'outbound_state_digest': digest(outgoing),
                          'provider_status': 'unavailable', 'provider_error_code': None, 'jev': None}
            try:
                response = client.evaluate(outgoing, questions)
                answers = response['answers']
                row.update(provider_status='ok', jev=response | {
                    'unsupported_assertions': answers['unsupported_assertions']['noul'],
                    'framework_load': answers['framework_load'],
                    'decision': review_decision(answers, policy, 0)})
            except CIError as exc:
                row['provider_error_code'] = exc.code
            results.append(row)
            print(f"{case['case_id']}: {row['provider_status']}", file=sys.stderr)
            if row['provider_status'] != 'ok':
                break
    except KeyboardInterrupt:
        interrupted = True
    observed = [r for r in results if r['provider_status'] == 'ok']
    cutoff = policy['thresholds']['review_negative_max']
    disagreement = lambda r: (r['jev']['unsupported_assertions'] > cutoff) != r['human_label']['unsupported_assertion_present']
    return {'kind': 'exploratory_review_diagnostics', 'created_at': datetime.now(timezone.utc).isoformat(),
        'case_set_digest': digest(cases), 'registry_digest': digest(registry),
        'question_version': POSTFLIGHT_VERSION, 'question_digest': digest(questions),
        'policy_version': policy['version'], 'policy_digest': digest(policy),
        'model_requested': client.model, 'labels_digest': digest(labels),
        'thresholds_fitted': False, 'policy_modified': False, 'coaching_effectiveness_measured': False,
        'summary': {'cases_planned': len(cases), 'cases_attempted': len(results), 'usable_cases': len(observed),
            'interrupted': interrupted,
            'unsupported_assertions': {'cutoff': cutoff,
                'disagreement_case_ids': [r['case_id'] for r in observed if disagreement(r)],
                'flagged_reviewer_negative_case_ids': [r['case_id'] for r in observed if disagreement(r) and not r['human_label']['unsupported_assertion_present']],
                'unflagged_reviewer_positive_case_ids': [r['case_id'] for r in observed if disagreement(r) and r['human_label']['unsupported_assertion_present']]},
            'framework_load': {'score_cutoff': 0.75,
                'disagreement_case_ids': [r['case_id'] for r in observed if
                    (r['jev']['framework_load']['score'] > 0.75) != (r['human_label']['framework_load']['level'] > 0)]}},
        'results': results,
        'note': 'Exploratory disagreements with supplied reviewer labels, not gold truth or calibration. '
                'Framework Score, confidence and distribution remain separate; no threshold search. '
                'This isolates postflight judgments without preflight routing or revision attempts.'}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cases', type=Path, default=ROOT / 'evals/review-diagnostic-cases.jsonl')
    p.add_argument('--max-cases', type=int, default=16)
    mode = p.add_mutually_exclusive_group()
    mode.add_argument('--plan', action='store_true')
    mode.add_argument('--label-template', type=Path, help='New external path for reviewer labeling; no network.')
    mode.add_argument('--check-labels', action='store_true', help='Validate completed labels locally; no network.')
    p.add_argument('--labels', type=Path, help='Completed label packet; never sent to Jev.')
    p.add_argument('--consent-send', action='store_true')
    p.add_argument('--output', type=Path, help='New external result file; never overwritten.')
    args = p.parse_args(argv)
    try:
        registry, policy = load_registry(), load_policy()
        cases = load_cases(args.cases, args.max_cases, registry)
        if args.plan:
            print(json.dumps({'network_called': False, 'case_ids': [c['case_id'] for c in cases],
                              'maximum_http_attempts': 2 * len(cases)}, indent=2))
            return 0
        if args.label_template:
            write_new_json(args.label_template, label_packet(cases, registry))
            print(json.dumps({'network_called': False, 'label_template': str(args.label_template)}))
            return 0
        if not args.labels:
            raise CIError('diagnostics_require_labels')
        packet = read_json(args.labels)
        labels = validate_labels(packet, cases, registry)
        if args.check_labels:
            print(json.dumps({'network_called': False, 'labels_validated': len(labels),
                              'reviewer_kind': packet['reviewer_kind']}))
            return 0
        if not args.consent_send:
            raise CIError('live_diagnostics_require_explicit_consent')
        if not args.output:
            raise CIError('live_diagnostics_require_labels_and_output')
        check_output_path(args.output)
        report = run(cases, labels, registry, policy, TypeSafeClient(), args.consent_send)
        report['reviewer'] = packet['reviewer']
        report['reviewer_kind'] = packet['reviewer_kind']
        write_new_json(args.output, report)
        print(json.dumps({'output': str(args.output), **report['summary']}, indent=2))
        return 130 if report['summary']['interrupted'] else (0 if report['summary']['usable_cases'] == len(cases) else 2)
    except CIError as exc:
        error = {'error_code': exc.code}
        label_help = {
            'human_reviewer_required': 'Set reviewer to the reviewer name or identifier, then complete all human_label fields before rerunning.',
            'reviewer_kind_required': 'Set reviewer_kind to human or ai to record who authored the labels.',
            'human_labels_must_be_completed': 'Complete unsupported_assertion_present, sentence_ids, and rationale for every case; do not leave null labels.',
            'human_framework_label_must_be_completed': 'Complete framework_load.level (0, 1, or 2), sentence_ids, and rationale for every case.'}
        if exc.code in label_help:
            error.update(message=label_help[exc.code], network_called=False)
        print(json.dumps(error), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
