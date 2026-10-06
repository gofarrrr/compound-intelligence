#!/usr/bin/env python3
"""Opt-in LIVE evaluation on synthetic routing cases. No LLM coach is invoked."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'skills/compound-intelligence/scripts'))
from ci_runtime.common import CIError, read_text, parse_json, write_new_json, check_output_path
from ci_runtime.engine import route


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--cases', type=Path, default=ROOT/'evals/routing-cases.jsonl')
    p.add_argument('--max-cases', type=int, default=5)
    p.add_argument('--consent-send', action='store_true', help='Approve sending these synthetic cases; may incur usage.')
    p.add_argument('--plan', action='store_true', help='List case IDs without network calls.')
    p.add_argument('--output', type=Path)
    args = p.parse_args()
    try:
        if not 1 <= args.max_cases <= 200:
            raise CIError('evaluation_case_budget_out_of_bounds')
        cases = [parse_json(line) for line in read_text(args.cases).splitlines() if line.strip()][:args.max_cases]
        if args.plan:
            print(json.dumps({'network_called': False, 'cases': [c['id'] for c in cases],
                              'maximum_http_attempts': 2 * len(cases)}, indent=2))
            return 0
        if not args.consent_send:
            raise CIError('live_evaluation_requires_explicit_consent')
        if args.output:
            check_output_path(args.output)
        results = []
        for case in cases:
            receipt = route(case['state'], backend='typesafe', consent=True, rollout='shadow')
            proposed = receipt['proposed_decision']
            usable = receipt['provider_status'] == 'ok' or receipt['backend'] == 'local_rule'
            expected = case['acceptable_primary_cards']
            expected_actions = case.get('acceptable_actions', [])
            results.append({'case_id': case['id'], 'receipt': receipt,
                'usable_for_route_comparison': usable,
                'matches_authored_expectation': (proposed['primary_card'] in expected or
                                                  proposed['action'] in expected_actions) if usable else None,
                'expected_card_in_shortlist': bool(set(expected) & set(proposed['candidate_cards'])) if usable else None})
            # Stop at a provider/configuration failure instead of billing an entire broken run.
            if receipt['provider_status'] == 'unavailable':
                break
        observed = [r for r in results if r['usable_for_route_comparison']]
        summary = {'kind': 'live_synthetic_routing_evaluation', 'cases_attempted': len(results),
                   'usable_cases': len(observed), 'expectation_matches': sum(bool(r['matches_authored_expectation']) for r in observed),
                   'results': results, 'coaching_quality_measured': False, 'probabilities_calibrated': False,
                   'note': 'Expected routes are authored hypotheses, not independent human gold labels. '
                           'No held-out coaching effectiveness or superiority claim follows.'}
        if args.output:
            write_new_json(args.output, summary)
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 0 if len(observed) == len(results) else 2
    except CIError as exc:
        print(json.dumps({'error_code': exc.code}), file=sys.stderr)
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
