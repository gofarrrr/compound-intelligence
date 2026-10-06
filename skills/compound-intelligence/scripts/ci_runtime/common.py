"""Strict local contracts, bounded file I/O, and consent-based receipts."""
from __future__ import annotations
import hashlib
import json
import math
import os
import re
from pathlib import Path
from typing import Any

SKILL_ROOT = Path(__file__).resolve().parents[2]
ASSETS = SKILL_ROOT / 'assets' / 'decision'
MAX_FILE_BYTES = 1_048_576

class CIError(Exception):
    """Public errors carry a fixed code, never provider bodies or credentials."""
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)

def canonical(value: Any) -> bytes:
    try:
        return json.dumps(value, sort_keys=True, ensure_ascii=False,
                          separators=(',', ':'), allow_nan=False).encode('utf-8')
    except (ValueError, TypeError, UnicodeError) as exc:
        raise CIError('invalid_json_value') from exc

def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()

def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def _unique_pairs(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise CIError('duplicate_json_key')
        obj[key] = value
    return obj

def parse_json(raw: bytes | str) -> Any:
    def reject_constant(_):
        raise CIError('nonfinite_json_number')
    try:
        return json.loads(raw, object_pairs_hook=_unique_pairs,
                          parse_constant=reject_constant)
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise CIError('malformed_json') from exc

def read_json(path: Path) -> Any:
    return parse_json(read_text(path))

def read_text(path: Path, limit: int = MAX_FILE_BYTES) -> str:
    try:
        with path.expanduser().open('rb') as f:
            content = f.read(limit + 1)
        if len(content) > limit:
            raise CIError('file_too_large')
        return content.decode('utf-8')
    except (OSError, UnicodeError) as exc:
        raise CIError('file_unreadable') from exc

def bounded_number(value: Any, low: float = 0, high: float = 1) -> float:
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not math.isfinite(value) or not low <= value <= high):
        raise CIError('invalid_numeric_value')
    return float(value)

def safe_id(value: Any, code: str = 'invalid_identifier') -> str:
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,95}', value):
        raise CIError(code)
    return value

def load_registry() -> list[dict]:
    rows = read_json(ASSETS / 'cards.json')
    if not isinstance(rows, list) or len(rows) != 21:
        raise CIError('invalid_card_registry')
    ids = set()
    for row in rows:
        safe_id(row['id'])
        if row['id'] in ids:
            raise CIError('duplicate_card')
        ids.add(row['id'])
        path = (SKILL_ROOT / row['path']).resolve()
        if not path.is_relative_to(SKILL_ROOT) or not path.is_file():
            raise CIError('invalid_card_path')
        if file_digest(path) != row['sha256']:
            raise CIError('card_changed_update_registry_and_evals')
    return rows

def load_policy(path: Path | None = None) -> dict:
    data = read_json(path or ASSETS / 'policy.json')
    default = read_json(ASSETS / 'policy.json')
    if not isinstance(data, dict) or set(data) != set(default):
        raise CIError('invalid_policy')
    safe_id(data['version'])
    # This release has no empirical calibration. Editing a JSON flag cannot create it.
    if data['calibration_status'] != 'uncalibrated_starting_policy':
        raise CIError('unsupported_calibration_claim')
    if set(data.get('thresholds', {})) != set(default['thresholds']):
        raise CIError('invalid_policy_thresholds')
    for value in data['thresholds'].values():
        bounded_number(value)
    if not (0 < data['thresholds']['fit_min'] <= 1 and
            0 < data['thresholds']['signal_high'] <= 1 and
            0 < data['thresholds']['risk_review'] <= 1):
        raise CIError('invalid_policy_thresholds')
    for key in ['max_candidate_cards', 'max_applied_cards', 'max_revision_attempts']:
        if type(data[key]) is not int or data[key] != default[key]:
            raise CIError('unsupported_policy_budget')
    return data

def protected_roots() -> list[Path]:
    roots = [SKILL_ROOT]
    # In the full distribution protect the package, not only the skill folder.
    if SKILL_ROOT.parent.name == 'skills':
        roots.append(SKILL_ROOT.parent.parent)
    return roots

def check_output_path(path: Path) -> Path:
    """Preflight an explicit new output destination without a write."""
    path = path.expanduser().absolute()
    if any(p.is_symlink() for p in [path, *path.parents]):
        raise CIError("symlink_destination_refused")
    if any(path.resolve().is_relative_to(root) for root in protected_roots()):
        raise CIError("installed_package_is_read_only")
    if not path.parent.is_dir():
        raise CIError("receipt_parent_missing")
    if path.exists():
        raise CIError("destination_exists")
    return path

def write_new_json(path: Path, data: Any) -> None:
    """Explicit destination only; never overwrite, follow symlinks, or write into install.

    Parent directories must exist. Symlink checks reduce accidental misdirection;
    this is a local utility, not a defense against a concurrent hostile filesystem.
    """
    path = check_output_path(path)
    payload = json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + '\n'
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0)
    try:
        fd = os.open(path, flags, 0o600)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(payload)
    except FileExistsError as exc:
        raise CIError('destination_exists') from exc
    except OSError as exc:
        raise CIError('destination_unwritable') from exc
