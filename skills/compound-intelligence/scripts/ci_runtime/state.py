"""An evidence packet is not a diagnosis, permission grant, or memory dump."""
from __future__ import annotations
import copy
import os
import re
from typing import Any
from .common import CIError, canonical, safe_id

STATE_VERSION = 'ci.state.v2'
MODES = {'advise', 'coach', 'learn', 'rehearse', 'reflect'}
ACTIONS = {'coaching_only', 'personnel_decision', 'communicate_confirmed_process'}
FIELDS = {'schema_version', 'case_id', 'mode', 'request', 'goal', 'observations',
          'interpretations', 'unknowns', 'constraints', 'requested_card',
          'requested_action', 'confirmed_process', 'data_class', 'language'}
MAX_STATE_BYTES = 24_000

# Deliberately limited checks, NOT a PII classifier or anonymization guarantee.
EMAIL = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
TOKEN = re.compile(r'(?i)\b(bearer\s+)[A-Za-z0-9._\-/+=]{8,}|\b(?:sk|ts|tsai)[-_][A-Za-z0-9_-]{16,}\b')
PRIVATE_KEY = re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')

def text(value: Any, maximum: int = 6000, nonempty: bool = False) -> str:
    if not isinstance(value, str) or len(value) > maximum or '\x00' in value:
        raise CIError('invalid_state_text')
    if nonempty and not value.strip():
        raise CIError('missing_state_text')
    return value

def string_list(value: Any) -> list[str]:
    if not isinstance(value, list) or len(value) > 30:
        raise CIError('invalid_state_list')
    return [text(v, 2000, True) for v in value]

def normalize_state(raw: Any, registry: list[dict]) -> dict:
    if not isinstance(raw, dict) or set(raw) - FIELDS:
        raise CIError('unknown_or_invalid_state_fields')
    if raw.get('schema_version', STATE_VERSION) != STATE_VERSION:
        raise CIError('unsupported_state_version')
    mode = raw.get('mode', 'advise')
    action = raw.get('requested_action', 'coaching_only')
    data_class = raw.get('data_class', 'restricted')
    if not isinstance(mode, str) or not isinstance(action, str) or mode not in MODES or action not in ACTIONS:
        raise CIError('invalid_mode_or_action')
    if not isinstance(data_class, str) or data_class not in {'anonymized', 'public', 'restricted'}:
        raise CIError('invalid_data_class')
    if type(raw.get('confirmed_process', False)) is not bool:
        raise CIError('invalid_process_flag')
    aliases = {r['legacy_alias']: r['id'] for r in registry}
    aliases.update({r['id']: r['id'] for r in registry})
    requested = raw.get('requested_card')
    if requested is not None and (not isinstance(requested, str) or requested not in aliases):
        raise CIError('unknown_requested_card')
    observations = raw.get('observations', [])
    if not isinstance(observations, list) or len(observations) > 30:
        raise CIError('invalid_observations')
    entries, ids = [], set()
    for item in observations:
        if not isinstance(item, dict) or set(item) - {'id', 'text', 'kind', 'source', 'observed_at'}:
            raise CIError('invalid_observation_fields')
        oid = safe_id(item.get('id'), 'invalid_observation_id')
        if oid in ids:
            raise CIError('duplicate_observation_id')
        ids.add(oid)
        kind = item.get('kind', 'user_report')
        if kind not in {'user_report', 'attributed_report', 'source_excerpt'}:
            raise CIError('invalid_observation_kind')
        observed = item.get('observed_at')
        if observed is not None:
            text(observed, 80, True)
        entries.append({'id': oid, 'text': text(item.get('text'), 3000, True),
                        'kind': kind, 'source': text(item.get('source', 'user'), 250, True),
                        'observed_at': observed})
    state = {'schema_version': STATE_VERSION,
             'case_id': safe_id(raw.get('case_id'), 'invalid_case_id'),
             'mode': mode, 'request': text(raw.get('request'), 8000, True),
             'goal': text(raw.get('goal', ''), 2000),
             'observations': entries,
             'interpretations': string_list(raw.get('interpretations', [])),
             'unknowns': string_list(raw.get('unknowns', [])),
             'constraints': string_list(raw.get('constraints', [])),
             'requested_card': aliases[requested] if requested else None,
             'requested_action': action, 'confirmed_process': raw.get('confirmed_process', False),
             'data_class': data_class, 'language': text(raw.get('language', 'unknown'), 40, True)}
    if len(canonical(state)) > MAX_STATE_BYTES:
        raise CIError('state_too_large_minimize_context')
    return state

def redact(value: Any) -> Any:
    """Remove common tokens and emails from outbound strings. Names remain manual."""
    if isinstance(value, str):
        key = os.environ.get('TYPESAFE_API_KEY')
        if key and len(key) >= 8:
            value = value.replace(key, '[REDACTED_SECRET]')
        if PRIVATE_KEY.search(value):
            raise CIError('private_key_material_refused')
        value = TOKEN.sub('[REDACTED_SECRET]', value)
        return EMAIL.sub('[REDACTED_EMAIL]', value)
    if isinstance(value, list):
        return [redact(v) for v in value]
    if isinstance(value, dict):
        return {k: redact(v) for k, v in value.items()}
    return value

def outbound_state(state: dict) -> dict:
    # Case IDs are local correlation keys, never sent as evidence to the provider.
    result = copy.deepcopy(state)
    result.pop('case_id', None)
    result.pop('data_class', None)
    return redact(result)

def ensure_egress(state: dict, consent: bool) -> None:
    if not consent:
        raise CIError('typesafe_egress_not_approved')
    if state['data_class'] not in {'anonymized', 'public'}:
        raise CIError('restricted_data_stays_local')
