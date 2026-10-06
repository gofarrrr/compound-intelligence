#!/usr/bin/env python3
"""Compound Intelligence local CLI. Python 3.10+, standard library only."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import sys

from ci_runtime import __version__
from ci_runtime.client import TypeSafeClient, DEFAULT_MODEL, ENDPOINT
from ci_runtime.common import (CIError, SKILL_ROOT, ASSETS, read_json, read_text,
                               parse_json, load_registry, load_policy, write_new_json, check_output_path)
from ci_runtime.engine import route, review, reflection_record
from ci_runtime.metrics import reliability_report
from ci_runtime.policy import compose
from ci_runtime.questions import preflight
from ci_runtime.state import normalize_state, outbound_state


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--version', action='version', version=__version__)
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor', help='Check local files and key presence, without printing the key or calling an API.')
    sub.add_parser('demo', help='Run an explicitly synthetic offline policy fixture, not Jev inference.')
    for name in ('preview', 'route', 'review'):
        s = sub.add_parser(name)
        s.add_argument('--state', type=Path, required=True)
        s.add_argument('--policy', type=Path)
        s.add_argument('--output', type=Path, help='New explicit output path outside the installed package; never overwritten.')
        if name != 'preview':
            s.add_argument('--backend', choices=('auto', 'offline', 'typesafe'), default='auto')
            s.add_argument('--consent-send', action='store_true', help='Approve this minimized packet for TypeSafe.')
        if name == 'route':
            s.add_argument('--rollout', choices=('assist', 'shadow'), default='assist')
        if name == 'review':
            s.add_argument('--draft', type=Path, required=True)
            s.add_argument('--routing-receipt', type=Path, required=True)
            s.add_argument('--cards', nargs='+', help='Actual source-card IDs used by the host; at most two.')
            s.add_argument('--attempt', type=int, choices=(0, 1), default=0)
    s = sub.add_parser('smoke', help='One small LIVE request using synthetic, nonpersonal input; may incur usage.')
    s.add_argument('--consent-send', action='store_true')
    s = sub.add_parser('reflect', help='Save an explicitly approved, provisional user-reported lesson locally.')
    s.add_argument('--routing-receipt', type=Path, required=True)
    s.add_argument('--note', type=Path, required=True)
    s.add_argument('--output', type=Path, required=True)
    s.add_argument('--approve-save', action='store_true')
    s = sub.add_parser('evaluate', help='Offline metrics from externally supplied human-labeled Noul rows.')
    s.add_argument('--labels', type=Path, required=True)
    s.add_argument('--output', type=Path)
    return p


def main(argv=None) -> int:
    args = parser().parse_args(argv)
    try:
        if getattr(args, 'output', None):
            check_output_path(args.output)
        registry = load_registry()
        consent = getattr(args, 'consent_send', False) or os.environ.get('CI_ALLOW_TYPESAFE') == '1'
        if args.command == 'doctor':
            policy = load_policy()
            result = {'version': __version__, 'python': sys.version.split()[0],
                      'skill_root': str(SKILL_ROOT), 'cards_validated': len(registry),
                      'discoverable_skills_in_this_bundle': 1,
                      'typesafe_key_present': bool(os.environ.get('TYPESAFE_API_KEY', '').strip()),
                      'typesafe_egress_approved_for_session': consent,
                      'model_requested': os.environ.get('CI_JEV_MODEL', DEFAULT_MODEL),
                      'endpoint': ENDPOINT, 'calibration_status': policy['calibration_status'],
                      'network_called': False}
        elif args.command == 'demo':
            fixture = read_json(ASSETS / 'offline-demo.json')
            state = normalize_state(fixture['state'], registry)
            result = {'kind': 'OFFLINE_CANNED_POLICY_DEMO_NOT_MODEL_INFERENCE',
                      'network_called': False, 'scores_source': 'invented_test_fixture',
                      'decision': compose(state, fixture['answers'], registry, load_policy()),
                      'note': 'This demonstrates code paths only; it does not test Jev accuracy.'}
        elif args.command == 'smoke':
            if not consent:
                raise CIError('typesafe_egress_not_approved')
            questions = {
                'topic': {'type': 'choice', 'instructions': 'Which topic is explicitly requested?',
                          'criteria': {'feedback': 'Giving workplace feedback',
                                       'coding': 'Writing a computer program', 'other': 'Neither topic'}},
                'learning': {'type': 'noul', 'instructions': 'Does the request explicitly ask to learn a technique?'},
                'specificity': {'type': 'score', 'instructions': 'How specifically is the learning objective stated?',
                                'criteria': ['No learning objective', 'Broad learning topic', 'Named method and practice requested']}}
            response = TypeSafeClient().evaluate(
                'Teach me Factual Feedback and give me one small practice.', questions)
            result = {'kind': 'live_synthetic_api_smoke_test', 'network_called': True,
                      'model': response['model'], 'answers': response['answers'],
                      'usage': response['usage'], 'transport': response['transport'],
                      'note': 'Validates this API exchange, not coaching quality or calibration.'}
        elif args.command == 'preview':
            state = normalize_state(read_json(args.state), registry)
            load_policy(args.policy)
            result = {'kind': 'local_outbound_preview', 'network_called': False,
                      'data_class': state['data_class'],
                      'warning': 'Names, phone numbers, and identifying stories require manual minimization. '
                                 'This is not an anonymization guarantee.',
                      'payload': {'model': os.environ.get('CI_JEV_MODEL', DEFAULT_MODEL),
                                  'state': outbound_state(state), 'questions': preflight(registry)}}
        elif args.command == 'route':
            result = route(read_json(args.state), backend=args.backend, consent=consent,
                           rollout=args.rollout, policy=load_policy(args.policy))
        elif args.command == 'review':
            result = review(read_json(args.state), read_text(args.draft), read_json(args.routing_receipt),
                            cards=args.cards, backend=args.backend, consent=consent,
                            attempt=args.attempt, policy=load_policy(args.policy))
        elif args.command == 'reflect':
            result = reflection_record(read_json(args.routing_receipt), read_json(args.note), args.approve_save)
        elif args.command == 'evaluate':
            rows = [parse_json(line) for line in read_text(args.labels).splitlines() if line.strip()]
            result = reliability_report(rows)
        else:
            raise CIError('unknown_command')
        if getattr(args, 'output', None):
            write_new_json(args.output, result)
        print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
        return 0
    except CIError as exc:
        print(json.dumps({'error_code': exc.code, 'completed': False}), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print(json.dumps({'error_code': 'cancelled', 'completed': False}), file=sys.stderr)
        return 130

if __name__ == '__main__':
    raise SystemExit(main())
