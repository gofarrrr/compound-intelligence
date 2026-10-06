#!/usr/bin/env python3
"""Explicit local Markdown case persistence, with scoped consent and stale-read checks.

No inference, discovery, network, scheduler or learning. The host supplies the
already-decided content and actual authorization. Ordinary local filesystem use;
the digest recheck is not an atomic CAS against hostile concurrent writers.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile

SKILL_ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 65_536
SECTIONS = (
    'Goal', 'Current evidence', 'Interpretations', 'Unknowns and constraints',
    'Before the latest attempt', 'Attempt', 'Outcome', 'New information',
    'Current next move', 'Provisional lesson', 'Persistence scope', 'User notes',
)


class CaseError(ValueError):
    """Fixed errors do not echo case content."""


def _sha(payload):
    return hashlib.sha256(payload).hexdigest()


def _path(value):
    path = Path(value).expanduser().absolute()
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise CaseError('symlink_case_path')
    path = path.resolve(strict=False)
    roots = [SKILL_ROOT]
    if SKILL_ROOT.parent.name == 'skills':
        roots.append(SKILL_ROOT.parent.parent)
    if any(path == r or r in path.parents for r in roots):
        raise CaseError('case_inside_installed_package')
    if path.suffix.lower() != '.md':
        raise CaseError('case_requires_markdown')
    return path


def _parse(text):
    if not isinstance(text, str) or len(text.encode('utf-8')) > MAX_BYTES or '\x00' in text:
        raise CaseError('invalid_case_text')
    ids = re.findall(r'^Case ID: ([A-Za-z0-9][A-Za-z0-9_-]{0,95})\s*$', text, re.M)
    if len(ids) != 1:
        raise CaseError('missing_or_duplicate_case_id')
    heads = list(re.finditer(r'^## ([^\n\r]+)\r?\n', text, re.M))
    sections = {}
    for i, head in enumerate(heads):
        name = head[1]
        if name in sections:
            raise CaseError('duplicate_case_section')
        end = heads[i+1].start() if i+1 < len(heads) else len(text)
        sections[name] = text[head.start():end]
    if not set(SECTIONS) <= sections.keys():
        raise CaseError('incomplete_case_record_use_existing_tools')
    preamble = text[:heads[0].start()]
    if not re.search(r'^Case ID: '+re.escape(ids[0])+r'\s*$', preamble, re.M):
        raise CaseError('case_id_must_be_in_header')
    return {'case_id':ids[0], 'preamble':preamble, 'sections':sections}


def read_case(value):
    path = _path(value)
    with path.open('rb') as handle:
        payload = handle.read(MAX_BYTES+1)
    if len(payload) > MAX_BYTES:
        raise CaseError('case_too_large')
    text = payload.decode('utf-8')
    record = _parse(text)
    return dict(record, path=str(path), text=text, sha256=_sha(payload))


def write_case(value, text, *, case_id, approved=False, permission='snapshot_only',
               authorized_path=None, allowed_sections=(), expected_sha256=None):
    """Create once or update explicit sections against an actual read snapshot.

    `approved` comes from the real user instruction, never a flag inferred from
    the Markdown file. Ongoing consent must name this path, case and section scope.
    Snapshot-only consent cannot overwrite an existing file. Fresh narrow update
    approval uses update_once. The returned saved flag follows a completed write.
    """
    if approved is not True:
        raise CaseError('case_write_not_approved')
    if permission not in {'snapshot_only','update_once','ongoing'}:
        raise CaseError('invalid_case_permission')
    path = _path(value)
    if authorized_path is None or _path(authorized_path) != path:
        raise CaseError('case_destination_outside_consent')
    proposed = _parse(text)
    if proposed['case_id'] != case_id:
        raise CaseError('case_id_outside_consent')
    payload = text.encode('utf-8')
    if expected_sha256 is None:
        if permission == 'update_once':
            raise CaseError('update_requires_read_snapshot')
        if not path.parent.is_dir():
            raise CaseError('case_parent_missing')
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os,'O_NOFOLLOW',0)
        with os.fdopen(os.open(path,flags,0o600),'wb') as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        changed = list(proposed['sections'])
    else:
        if permission == 'snapshot_only':
            raise CaseError('snapshot_only_does_not_authorize_update')
        current = read_case(path)
        if current['case_id'] != case_id:
            raise CaseError('case_id_outside_consent')
        if current['sha256'] != expected_sha256:
            raise CaseError('stale_case_read_reconcile_before_write')
        if proposed['preamble'] != current['preamble'] or list(proposed['sections']) != list(current['sections']):
            raise CaseError('case_header_or_sections_changed')
        changed = [s for s in current['sections'] if current['sections'][s] != proposed['sections'][s]]
        scope = set(allowed_sections)
        if not scope or not scope <= set(SECTIONS) or not set(changed) <= scope:
            raise CaseError('case_sections_outside_consent')
        if not changed:
            return {'saved':False,'status':'unchanged','path':str(path),'case_id':case_id,'sha256':current['sha256'],'changed_sections':[]}
        # Write a private temporary file in the same directory, then replace.
        # Re-read immediately before replacement to catch ordinary editor changes.
        fd, name = tempfile.mkstemp(prefix='.ci-case-', suffix='.tmp', dir=path.parent)
        temp = Path(name)
        try:
            with os.fdopen(fd,'wb') as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            if read_case(path)['sha256'] != expected_sha256:
                raise CaseError('stale_case_read_reconcile_before_write')
            os.replace(temp,path)
        finally:
            temp.unlink(missing_ok=True)
    return {'saved':True,'status':'saved','path':str(path),'case_id':case_id,
            'sha256':_sha(payload),'changed_sections':changed}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command',required=True)
    read = sub.add_parser('read',help='Read only the explicitly named Markdown case.')
    read.add_argument('path',type=Path)
    write = sub.add_parser('write',help='Write already-decided content with actual user approval.')
    write.add_argument('--destination',type=Path,required=True)
    write.add_argument('--draft',type=Path,required=True)
    write.add_argument('--case-id',required=True)
    write.add_argument('--approve-write',action='store_true')
    write.add_argument('--permission',choices=['snapshot_only','update_once','ongoing'],default='snapshot_only')
    write.add_argument('--scope',nargs='+',default=[])
    write.add_argument('--expected-sha256')
    args = parser.parse_args(argv)
    try:
        if args.command == 'read':
            result = read_case(args.path)
        else:
            with args.draft.open('rb') as handle:
                payload = handle.read(MAX_BYTES+1)
            if len(payload) > MAX_BYTES:
                raise CaseError('case_too_large')
            result = write_case(args.destination,payload.decode('utf-8'),case_id=args.case_id,
                                approved=args.approve_write,permission=args.permission,
                                authorized_path=args.destination,allowed_sections=args.scope,
                                expected_sha256=args.expected_sha256)
        print(json.dumps(result,ensure_ascii=False))
        return 0
    except (CaseError,OSError,UnicodeError) as exc:
        error = str(exc) if isinstance(exc,CaseError) else 'case_io_failed_not_saved'
        print(json.dumps({'saved':False,'error':error}))
        return 1


if __name__ == '__main__':
    sys.exit(main())
