"""Small stdlib HTTPS adapter for the documented TypeSafe HTTP API.

No SDK installation, key files, dynamic endpoint, redirects, or remote error-body logs.
Transport injection supports offline tests. This is not a hard realtime deadline.
"""
from __future__ import annotations
import email.utils
import math
import os
import random
import socket
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Callable
from .common import CIError, bounded_number, canonical, parse_json

ENDPOINT = 'https://api.typesafe.ai/v1/systemone'
DEFAULT_MODEL = 'jev-1.13.0'  # Verified in official docs on 2026-10-02; override deliberately.
MAX_RESPONSE_BYTES = 1_048_576
RETRY_STATUSES = {429, 500, 502, 503, 504, 529}

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def http_transport(payload: dict, key: str, timeout: float) -> tuple[int, dict, bytes]:
    request = urllib.request.Request(
        ENDPOINT, data=canonical(payload), method='POST',
        headers={'Authorization': 'Bearer ' + key, 'Content-Type': 'application/json',
                 'Accept': 'application/json', 'User-Agent': 'compound-intelligence/0.2.0'})
    opener = urllib.request.build_opener(NoRedirect())
    try:
        with opener.open(request, timeout=timeout) as response:
            body = response.read(MAX_RESPONSE_BYTES + 1)
            if len(body) > MAX_RESPONSE_BYTES:
                raise CIError('provider_response_too_large')
            return response.status, dict(response.headers), body
    except urllib.error.HTTPError as exc:
        # A response body can echo private state. Do not read or expose it.
        headers = dict(exc.headers or {})
        exc.close()
        return exc.code, headers, b''
    except (urllib.error.URLError, TimeoutError, socket.timeout, OSError) as exc:
        raise CIError('provider_network_error') from exc

def _distribution(answer: dict, keys: set[str]) -> dict:
    probabilities = answer.get('probabilities')
    if not isinstance(probabilities, dict) or set(probabilities) != keys:
        raise CIError('provider_distribution_keys_mismatch')
    for probability in probabilities.values():
        bounded_number(probability)
    if not math.isclose(sum(probabilities.values()), 1.0, abs_tol=0.015):
        raise CIError('provider_probabilities_do_not_sum_to_one')
    bounded_number(answer.get('confidence'))
    return probabilities

def validate_response(raw: dict, questions: dict, requested_model: str | None = None) -> dict:
    if not isinstance(raw, dict) or not isinstance(raw.get('answers'), dict):
        raise CIError('provider_invalid_response')
    model = raw.get('model')
    if not isinstance(model, str) or not model or len(model) > 96:
        raise CIError('provider_missing_model')
    if requested_model and requested_model not in {'jev-latest', 'jev-preview'} and model != requested_model:
        raise CIError('provider_model_pin_mismatch')
    if set(raw['answers']) != set(questions):
        raise CIError('provider_answer_keys_mismatch')
    for qid, question in questions.items():
        answer = raw['answers'][qid]
        if not isinstance(answer, dict) or answer.get('type') != question['type']:
            raise CIError('provider_answer_type_mismatch')
        if question['type'] == 'noul':
            bounded_number(answer.get('noul'))
        elif question['type'] == 'choice':
            probs = _distribution(answer, set(question['criteria']))
            chosen = answer.get('choice')
            if chosen not in probs or probs[chosen] + 0.015 < max(probs.values()):
                raise CIError('provider_invalid_choice')
        elif question['type'] == 'score':
            levels = question['criteria']
            keys = {str(i) for i in range(len(levels))}
            probs = _distribution(answer, keys)
            legend = answer.get('legend')
            if legend != {str(i): level for i, level in enumerate(levels)}:
                raise CIError('provider_score_legend_mismatch')
            score = bounded_number(answer.get('score'), 0, len(levels) - 1)
            expected = sum(int(i) * p for i, p in probs.items())
            if not math.isclose(score, expected, abs_tol=0.025):
                raise CIError('provider_score_distribution_mismatch')
        else:
            raise CIError('unknown_question_type')
    usage = raw.get('usage')
    if not isinstance(usage, dict):
        raise CIError('provider_missing_usage')
    for key in ('input_tokens', 'output_tokens'):
        if type(usage.get(key)) is not int or usage[key] < 0:
            raise CIError('provider_invalid_usage')
    # Whitelist fields; unexpected provider metadata never enters receipts.
    cleaned = {}
    for qid, answer in raw['answers'].items():
        allowed = {'noul': {'type', 'noul'},
                   'choice': {'type', 'choice', 'probabilities', 'confidence'},
                   'score': {'type', 'score', 'probabilities', 'confidence', 'legend'}}[answer['type']]
        cleaned[qid] = {k: answer[k] for k in allowed}
    return {'model': model, 'answers': cleaned,
            'usage': {k: usage[k] for k in ('input_tokens', 'output_tokens')}}

def retry_after(headers: dict) -> float | None:
    value = next((v for k, v in headers.items() if k.lower() == 'retry-after'), None)
    if value is None:
        return None
    try:
        seconds = float(value)
        return max(0.0, seconds) if math.isfinite(seconds) else None
    except (ValueError, TypeError):
        try:
            dt = email.utils.parsedate_to_datetime(value)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return max(0.0, (dt - datetime.now(timezone.utc)).total_seconds())
        except (ValueError, TypeError, OverflowError):
            return None

class TypeSafeClient:
    def __init__(self, *, model: str | None = None,
                 timeout: float = 10.0, budget: float = 22.0,
                 attempts: int = 2, transport: Callable = http_transport,
                 sleep: Callable = time.sleep, clock: Callable = time.monotonic):
        self.model = model or os.environ.get('CI_JEV_MODEL', DEFAULT_MODEL)
        if not isinstance(self.model, str) or not self.model.startswith('jev-') or len(self.model) > 96:
            raise CIError('invalid_model_identifier')
        if type(attempts) is not int or not 1 <= attempts <= 3:
            raise CIError('invalid_retry_budget')
        self.timeout = bounded_number(timeout, 0.1, 30)
        self.budget = bounded_number(budget, 0.1, 90)
        self.attempts, self.transport, self.sleep, self.clock = attempts, transport, sleep, clock

    def evaluate(self, state: dict | str, questions: dict) -> dict:
        key = os.environ.get('TYPESAFE_API_KEY', '')
        if not key.strip():
            raise CIError('typesafe_key_missing')
        if key != key.strip() or '\n' in key or '\r' in key:
            raise CIError('invalid_key_format')
        payload = {'model': self.model, 'state': state, 'questions': questions}
        if len(canonical(payload)) > 100_000:
            raise CIError('request_byte_budget_exceeded')
        start = self.clock()
        for attempt in range(1, self.attempts + 1):
            remaining = self.budget - (self.clock() - start)
            if remaining <= 0:
                raise CIError('provider_budget_exhausted')
            retry_headers = {}
            try:
                status, headers, body = self.transport(payload, key, min(self.timeout, remaining))
                if status == 200:
                    result = validate_response(parse_json(body), questions, self.model)
                    result['transport'] = {'attempts': attempt,
                        'elapsed_ms': round((self.clock() - start) * 1000, 2)}
                    return result
                if status in {401, 403}:
                    raise CIError('provider_authentication_or_permission_error')
                if status == 402:
                    raise CIError('provider_billing_error')
                if status not in RETRY_STATUSES:
                    raise CIError('provider_nonretryable_http_error')
                retry_headers = headers
                error = 'provider_retryable_http_error'
            except CIError as exc:
                if exc.code != 'provider_network_error':
                    raise
                error = exc.code
            if attempt == self.attempts:
                raise CIError(error)
            delay = retry_after(retry_headers)
            if delay is None:
                delay = (0.5 * 2 ** (attempt - 1)) + random.uniform(0, 0.15)
            remaining = self.budget - (self.clock() - start)
            # Never shorten a server's Retry-After and retry too early.
            if delay >= remaining:
                raise CIError('provider_retry_after_exceeds_budget')
            self.sleep(delay)
        raise CIError('provider_unavailable')
