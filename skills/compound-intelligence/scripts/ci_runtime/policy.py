"""Deterministic, advisory selection. Model values never authorize an action."""
from __future__ import annotations

BASE_CONTEXT = ['references/context-contract.md', 'references/coaching-contract.md',
                'references/safety.md', 'references/routing.md']


def decision(action: str, reasons: list[str], *, candidates=None,
             primary: str | None = None, support: str | None = None,
             checks=None) -> dict:
    return {'action': action, 'reason_codes': reasons,
            'candidate_cards': candidates or [], 'primary_card': primary,
            'support_card': support, 'host_checks': checks or [],
            'requires_llm_fit_check': True, 'authorizes_external_action': False}


def local_rule(state: dict) -> dict | None:
    if state['requested_action'] == 'personnel_decision':
        return decision('human_review', ['consequential_personnel_decision_not_automated'])
    requested = state['requested_card']
    if requested == '20-exits' and state['mode'] != 'learn':
        if not (state['confirmed_process'] and
                state['requested_action'] == 'communicate_confirmed_process'):
            return decision('human_review', ['exit_process_not_established'])
    if state['mode'] == 'learn' and requested:
        return decision('teach_requested_method', ['explicit_learning_goal_no_classifier_needed'],
                        candidates=[requested], primary=requested)
    if state['mode'] == 'reflect' and not state['observations']:
        return decision('clarify', ['reflection_needs_an_actual_attempt'],
                        checks=['Ask what the user tried and what actually happened.'])
    return None


def compose(state: dict, answers: dict, registry: list[dict], policy: dict) -> dict:
    """Independent fits are not an exclusive distribution or success probabilities."""
    t = policy['thresholds']
    p = lambda key: answers[key]['noul']
    high = lambda key: p(key) >= t['signal_high']
    if p('immediate_harm') >= t['risk_review']:
        return decision('human_support', ['harm_or_abuse_signal'], checks=[
            'Use appropriate human support or incident processes; do not use ordinary conflict advice.',
            'A low model value would not prove that harm is absent.'])
    if p('consequential_action') >= t['risk_review']:
        return decision('human_review', ['consequential_personnel_decision_not_automated'])
    if p('leadership_relevance') <= t['irrelevance_max']:
        return decision('no_book_fit', ['outside_leadership_scope'])
    if state['mode'] == 'reflect' and not high('completed_attempt'):
        return decision('clarify', ['reflection_attempt_or_outcome_unclear'])

    checks, reasons = [], ['uncalibrated_advisory_policy']
    if high('motive_attribution'):
        checks.append('Separate observed events from claims about motives; do not endorse the latter.')
    if high('missing_perspective'):
        checks.append('Keep the missing perspective visible; ask about it only when it changes the next move.')
    if high('structural_overload'):
        checks.append('Address capacity and work design; a personal reset cannot substitute for resources.')
    if high('colleague_struggle'):
        checks.append('Consider a supportive inquiry without diagnosing the colleague or assuming low motivation.')
    if high('self_reported_pressure'):
        checks.append('A brief reset may support the next move; do not infer a mental-health diagnosis.')

    eligible = [row for row in registry if row['automatic_candidate']]
    # A user report of a settled process permits communication coaching, not adjudication.
    if (state['confirmed_process'] and state['requested_action'] == 'communicate_confirmed_process'):
        eligible.extend(row for row in registry if row['id'] == '20-exits')
    ranked = sorted(eligible, key=lambda row: (-p('fit_' + row['id'][:2]), row['id']))
    fits = {row['id']: p('fit_' + row['id'][:2]) for row in eligible}
    candidates = [row['id'] for row in ranked if fits[row['id']] >= t['fit_min']]
    candidates = candidates[:policy['max_candidate_cards']]

    # A user's explicitly requested tool is visible, not silently overridden.
    requested = state['requested_card']
    if requested:
        if requested not in fits or fits[requested] < t['fit_min']:
            return decision('clarify', reasons + ['requested_method_fit_uncertain'],
                            candidates=candidates, checks=checks + [
                                'Explain the requested method\'s possible mismatch before suggesting another.'])
        candidates = [requested] + [c for c in candidates if c != requested]
        candidates = candidates[:policy['max_candidate_cards']]
        return decision('suggest', reasons + ['explicit_method_candidate'], candidates=candidates,
                        primary=requested, checks=checks)

    if not candidates:
        return decision('clarify', reasons + ['no_candidate_clears_starting_policy'], checks=checks + [
            'Ask one discriminating question or use qualified general coaching; do not force a chapter.'])

    # These rules expose evidence conflicts; they do not manufacture a root cause.
    if (state['mode'] not in {'learn'} and answers['evidence_quality']['score'] < 0.75):
        return decision('clarify', reasons + ['evidence_too_thin'], candidates=candidates, checks=checks)
    if (state['mode'] != 'learn' and high('motive_attribution') and high('missing_perspective')):
        exploratory = [c for c in ['01-understand', '18-support'] if fits.get(c, 0) >= t['fit_min']]
        candidates = list(dict.fromkeys(exploratory + candidates))[:policy['max_candidate_cards']]
        return decision('clarify', reasons + ['unsupported_motive_and_missing_perspective'],
                        candidates=candidates, checks=checks)

    first = candidates[0]
    if high('structural_overload') and fits.get('21-team-resilience', 0) >= t['fit_min']:
        first = '21-team-resilience'
        candidates = [first] + [c for c in candidates if c != first]
        candidates = candidates[:policy['max_candidate_cards']]
        reasons.append('capacity_signal_before_mindset')
    elif len(candidates) > 1 and fits[first] - fits[candidates[1]] < t['fit_margin']:
        return decision('clarify', reasons + ['several_methods_plausible'],
                        candidates=candidates, checks=checks + [
                            'Compare the candidate cards; several high fits may be complementary, not model uncertainty.',
                            'Ask only the question that distinguishes the next useful move.'])

    support = None
    if (state['mode'] != 'learn' and first != '15-reset' and high('self_reported_pressure')
            and fits.get('15-reset', 0) >= t['fit_min']):
        support = '15-reset'
        # Keep the actual loaded source within the three-card retrieval budget.
        candidates = list(dict.fromkeys([first, support] + candidates))[:policy['max_candidate_cards']]
        reasons.append('optional_reset_support_not_a_root_cause')
    return decision('suggest', reasons, candidates=candidates, primary=first, support=support, checks=checks)


def review_decision(answers: dict, policy: dict, attempt: int) -> dict:
    t = policy['thresholds']
    failures = []
    for name in ('addresses_goal', 'concrete_next_move', 'teaches_selection',
                 'practice_or_observation', 'source_fidelity'):
        if answers[name]['noul'] < t['review_positive_min']:
            failures.append(name)
    for name in ('unsupported_assertions', 'oversteps_agency'):
        if answers[name]['noul'] > t['review_negative_max']:
            failures.append(name)
    if answers['framework_load']['score'] > 0.75:
        failures.append('framework_load')
    if not failures:
        action = 'advisory_pass'
    elif attempt < policy['max_revision_attempts']:
        action = 'revise_once'
    else:
        action = 'human_review_or_narrow'
    return {'action': action, 'failed_checks': failures,
            'authorizes_external_action': False, 'certifies_correctness': False,
            'revision_attempt': attempt}
