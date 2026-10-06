"""Receipts bind inputs, contracts and source snapshots, not model reasoning traces."""
from __future__ import annotations
import copy
import os
import uuid
from datetime import datetime, timezone
from .common import (CIError, SKILL_ROOT, digest, read_text,
                     load_registry, load_policy, file_digest)
from .client import TypeSafeClient
from .questions import preflight, postflight, PREFLIGHT_VERSION, POSTFLIGHT_VERSION
from .state import normalize_state, outbound_state, ensure_egress, redact
from .policy import BASE_CONTEXT, local_rule, compose, decision, review_decision

RECEIPT_VERSION = 'ci.receipt.v2'


def seal(receipt: dict) -> dict:
    receipt = copy.deepcopy(receipt)
    receipt.pop('integrity_sha256', None)
    receipt['integrity_sha256'] = digest(receipt)
    return receipt


def verify_integrity(receipt: dict) -> None:
    if not isinstance(receipt, dict):
        raise CIError('invalid_receipt')
    expected = receipt.get('integrity_sha256')
    body = {k: v for k, v in receipt.items() if k != 'integrity_sha256'}
    if expected != digest(body):
        raise CIError('receipt_integrity_mismatch')


def _base(state: dict, registry: list[dict], policy: dict) -> dict:
    return {'schema_version': RECEIPT_VERSION, 'kind': 'routing',
            'receipt_id': str(uuid.uuid4()), 'case_id': state['case_id'],
            'created_at': datetime.now(timezone.utc).isoformat(),
            'state_schema_version': state['schema_version'], 'state_digest': digest(state),
            'registry_digest': digest(registry), 'policy_version': policy['version'],
            'policy_digest': digest(policy), 'calibration_status': policy['calibration_status'],
            'model_requested': None, 'model_returned': None, 'provider_status': 'not_called',
            'question_version': PREFLIGHT_VERSION, 'question_digest': digest(preflight(registry)),
            'answers': None, 'usage': None, 'transport': None,
            'outbound_state_digest': None, 'provider_error_code': None,
            'numbers_are_not_outcome_probabilities': True,
            'sources': [], 'context_paths': list(BASE_CONTEXT),
            'authorizes_external_action': False,
            'privacy_note': 'No raw case or draft is stored; signals themselves may still be sensitive.'}


def _finish(receipt: dict, state: dict, registry: list[dict], proposal: dict,
            rollout: str) -> dict:
    receipt['rollout'] = rollout
    receipt['proposed_decision'] = proposal
    if rollout == 'shadow' and receipt['provider_status'] == 'ok':
        effective = decision('llm_only', ['shadow_mode_does_not_change_the_coaching_route'])
    else:
        effective = proposal
    receipt['effective_decision'] = effective
    selected = effective['candidate_cards']
    source_by_id = {row['id']: row for row in registry}
    receipt['sources'] = [{k: source_by_id[c][k] for k in
                          ('id', 'path', 'sha256', 'chapter', 'printed_pages', 'framework')}
                         for c in selected]
    receipt['context_paths'] += [source_by_id[c]['path'] for c in selected]
    workflow = {'learn': 'learn', 'rehearse': 'rehearse', 'reflect': 'reflect'}.get(state['mode'])
    if workflow:
        receipt['context_paths'].append(f'references/workflows/{workflow}.md')
    return seal(receipt)


def route(raw_state: dict, *, backend='auto', consent=False, rollout='assist',
          client=None, policy=None, registry=None) -> dict:
    if backend not in {'auto', 'offline', 'typesafe'} or rollout not in {'assist', 'shadow'}:
        raise CIError('invalid_runtime_mode')
    registry = registry or load_registry()
    policy = policy or load_policy()
    state = normalize_state(raw_state, registry)
    receipt = _base(state, registry, policy)
    local = local_rule(state)
    if local:
        receipt['backend'] = 'local_rule'
        return _finish(receipt, state, registry, local, rollout)
    if backend == 'auto':
        backend = 'typesafe' if consent and os.environ.get('TYPESAFE_API_KEY') else 'offline'
    receipt['backend'] = backend
    if backend == 'offline':
        proposal = decision('llm_only', ['typed_router_not_enabled_use_source_routing_guide'])
        return _finish(receipt, state, registry, proposal, rollout)
    try:
        # Restriction/consent checks happen before state or key reaches transport.
        ensure_egress(state, consent)
        outgoing = outbound_state(state)
        receipt['outbound_state_digest'] = digest(outgoing)
        client = client or TypeSafeClient()
        receipt['model_requested'] = client.model
        response = client.evaluate(outgoing, preflight(registry))
        receipt.update({'provider_status': 'ok', 'model_returned': response['model'],
                        'answers': response['answers'], 'usage': response['usage'],
                        'transport': response.get('transport')})
        proposal = compose(state, response['answers'], registry, policy)
    except CIError as exc:
        receipt['provider_status'] = 'unavailable'
        receipt['provider_error_code'] = exc.code
        proposal = decision('llm_only', ['typed_router_unavailable_no_model_scores_invented'],
                            checks=['Use the original source-grounded routing and safety checks locally.'])
    return _finish(receipt, state, registry, proposal, rollout)


def verify_route_receipt(receipt: dict, state: dict, registry: list[dict], policy: dict) -> None:
    verify_integrity(receipt)
    if receipt.get('schema_version') != RECEIPT_VERSION or receipt.get('kind') != 'routing':
        raise CIError('not_a_routing_receipt')
    expected = {'state_digest': digest(state), 'registry_digest': digest(registry),
                'policy_digest': digest(policy), 'question_digest': digest(preflight(registry))}
    if any(receipt.get(k) != v for k, v in expected.items()):
        raise CIError('stale_receipt_state_or_contract_changed')
    try:
        created = datetime.fromisoformat(receipt['created_at'])
        if created.tzinfo is None:
            raise ValueError('missing timezone')
        age = (datetime.now(timezone.utc) - created).total_seconds()
        if age < -300 or age > 86400:
            raise ValueError('expired')
    except (ValueError, KeyError, TypeError) as exc:
        raise CIError('receipt_expired_or_invalid_timestamp') from exc


def review(raw_state: dict, draft: str, routing_receipt: dict, *, cards=None,
           backend='auto', consent=False, attempt=0, client=None, policy=None) -> dict:
    if type(attempt) is not int or attempt not in {0, 1}:
        raise CIError('revision_attempt_out_of_bounds')
    if backend not in {'auto', 'offline', 'typesafe'}:
        raise CIError('invalid_runtime_mode')
    registry, policy = load_registry(), policy or load_policy()
    state = normalize_state(raw_state, registry)
    verify_route_receipt(routing_receipt, state, registry, policy)
    if not isinstance(draft, str) or not draft.strip() or len(draft.encode('utf-8')) > 24_000:
        raise CIError('invalid_or_oversized_draft')
    if routing_receipt['effective_decision']['action'] in {'human_review', 'human_support'}:
        raise CIError('ordinary_coaching_review_not_appropriate')
    default = [routing_receipt['effective_decision'][k] for k in ('primary_card', 'support_card')
               if routing_receipt['effective_decision'][k]]
    selected = default if cards is None else cards
    by_id = {r['id']: r for r in registry}
    if (not isinstance(selected, list) or not 1 <= len(selected) <= 2
            or any(not isinstance(c, str) or c not in by_id for c in selected)
            or len(set(selected)) != len(selected)):
        raise CIError('review_requires_one_or_two_actual_source_cards')
    if '20-exits' in selected and not (state['mode'] == 'learn' or
            (state['confirmed_process'] and state['requested_action'] == 'communicate_confirmed_process')):
        raise CIError('exit_process_not_established')
    sources = [{'id': c, 'path': by_id[c]['path'], 'sha256': by_id[c]['sha256']} for c in selected]
    result = {'schema_version': RECEIPT_VERSION, 'kind': 'review', 'receipt_id': str(uuid.uuid4()),
              'created_at': datetime.now(timezone.utc).isoformat(), 'case_id': state['case_id'],
              'routing_receipt_sha256': routing_receipt['integrity_sha256'],
              'state_digest': digest(state), 'draft_digest': digest(draft),
              'sources': sources, 'source_selection_changed_from_route': selected != default,
              'question_version': POSTFLIGHT_VERSION, 'question_digest': digest(postflight()),
              'policy_version': policy['version'], 'policy_digest': digest(policy),
              'calibration_status': policy['calibration_status'],
              'provider_status': 'not_called', 'provider_error_code': None, 'backend': backend,
              'model_requested': None, 'model_returned': None, 'answers': None,
              'usage': None, 'transport': None, 'outbound_state_digest': None,
              'authorizes_external_action': False, 'certifies_correctness': False,
              'revision_attempt': attempt}
    if backend == 'auto':
        backend = 'typesafe' if consent and os.environ.get('TYPESAFE_API_KEY') else 'offline'
    result['backend'] = backend
    if backend == 'offline':
        result['decision'] = {'action': 'review_unavailable_use_manual_check', 'failed_checks': []}
        return seal(result)
    try:
        ensure_egress(state, consent)
        outgoing = {'case': outbound_state(state), 'draft': redact(draft),
                    'source_cards': [{'id': c, 'content': read_text(SKILL_ROOT / by_id[c]['path'])}
                                     for c in selected]}
        result['outbound_state_digest'] = digest(outgoing)
        client = client or TypeSafeClient()
        result['model_requested'] = client.model
        response = client.evaluate(outgoing, postflight())
        result.update({'provider_status': 'ok', 'model_returned': response['model'],
                       'answers': response['answers'], 'usage': response['usage'],
                       'transport': response.get('transport'),
                       'decision': review_decision(response['answers'], policy, attempt)})
    except CIError as exc:
        result['provider_status'], result['provider_error_code'] = 'unavailable', exc.code
        result['decision'] = {'action': 'review_unavailable_use_manual_check', 'failed_checks': []}
    return seal(result)


def reflection_record(receipt: dict, note: dict, approved: bool) -> dict:
    if not approved:
        raise CIError('reflection_save_not_approved')
    verify_integrity(receipt)
    if receipt.get('kind') != 'routing':
        raise CIError('reflection_requires_routing_receipt')
    if not isinstance(note, dict) or set(note) != {'observation', 'lesson', 'limitations', 'routing_correction'}:
        raise CIError('invalid_reflection_fields')
    for value in note.values():
        if not isinstance(value, str) or len(value) > 4000:
            raise CIError('invalid_reflection_text')
    if not note['observation'].strip() or not note['limitations'].strip():
        raise CIError('reflection_requires_observation_and_limits')
    return seal({'schema_version': 'ci.reflection.v2', 'kind': 'reflection',
                 'created_at': datetime.now(timezone.utc).isoformat(),
                 'routing_receipt_sha256': receipt['integrity_sha256'],
                 'case_id': receipt['case_id'], 'status': 'user_reported_provisional',
                 'user_approved': True, 'note': redact(note),
                 'updates_model_weights': False, 'updates_installed_skill': False,
                 'is_causal_evidence': False})
