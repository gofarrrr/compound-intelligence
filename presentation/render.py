#!/usr/bin/env python3
"""Render a supplied final coaching packet; no coaching or runtime imports."""
from __future__ import annotations

import argparse
import base64
import hashlib
from html import escape
import json
import os
from pathlib import Path
import re
from string import Template
import sys

HERE = Path(__file__).resolve().parent
VERSION = 'ci.presentation.v1'
KINDS = {'advice': 'Advice', 'clarification': 'Clarification',
         'no_fit': 'No method selected', 'manual_review': 'Manual review needed'}
MAX_BYTES = 262_144


def text(value, field):
    if (not isinstance(value, str) or not value.strip() or len(value) > 20_000
            or any(ord(c) < 32 and c not in '\n\r\t' for c in value)):
        raise ValueError(f'Invalid text field: {field}')
    value.encode('utf-8')
    return value


def fields(value, required, optional=()):
    if (not isinstance(value, dict) or not set(required) <= set(value)
            or set(value) - set(required) - set(optional)):
        raise ValueError('Invalid or incomplete presentation fields')


def validate(packet):
    fields(packet, {'schema_version', 'kind', 'title', 'goal', 'notice', 'next_move'},
           {'why', 'principle', 'facts', 'unknowns', 'sources', 'practice', 'reflection'})
    if (packet['schema_version'] != VERSION or not isinstance(packet['kind'], str)
            or packet['kind'] not in KINDS):
        raise ValueError('Unsupported presentation version or kind')
    for key in ('title', 'goal', 'notice', 'next_move', 'why', 'principle'):
        if key in packet:
            text(packet[key], key)
    for key in ('facts', 'unknowns', 'sources'):
        if key in packet:
            if not isinstance(packet[key], list) or len(packet[key]) > 30:
                raise ValueError(f'Invalid list field: {key}')
            for value in packet[key]:
                text(value, key)
    if 'practice' in packet:
        practice = packet['practice']
        fields(practice, {'prompt', 'observe'}, {'example'})
        for key, value in practice.items():
            text(value, 'practice.' + key)
    if 'reflection' in packet:
        reflection = packet['reflection']
        fields(reflection, {'prompt', 'adjustment_prompt'})
        for key, value in reflection.items():
            text(value, 'reflection.' + key)


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON field')
        result[key] = value
    return result


def read_packet(path):
    with path.open('rb') as file:
        raw = file.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError('Presentation input exceeds 256 KiB')
    packet = json.loads(raw.decode('utf-8'), object_pairs_hook=unique_pairs)
    validate(packet)
    return packet


def paragraph(value):
    return '<p class="text">' + escape(value) + '</p>'


def items(values):
    return '<ul>' + ''.join('<li class="text">' + escape(v) + '</li>' for v in values) + '</ul>'


def render(packet, template_path=HERE / 'workspace.html'):
    validate(packet)
    canonical = json.dumps(packet, sort_keys=True, ensure_ascii=False,
                           separators=(',', ':'), allow_nan=False).encode('utf-8')
    digest = hashlib.sha256(canonical).hexdigest()
    template = template_path.read_text(encoding='utf-8')
    # Only this developer-owned template can contain code; packet text is escaped.
    scripts = re.findall(r'<script>(.*?)</script>', template, flags=re.S)
    hashes = ' '.join("'sha256-" + base64.b64encode(hashlib.sha256(s.encode()).digest()).decode() + "'"
                      for s in scripts)
    csp = "default-src 'none'; style-src 'unsafe-inline'; script-src " + (hashes or "'none'")
    csp += "; connect-src 'none'; base-uri 'none'; form-action 'none'; object-src 'none'"
    navigation = '<button type="button" data-view="advice" aria-pressed="true">Prepare</button>'
    why = '<section class="card"><h2>Why this fits</h2>' + paragraph(packet['why']) + '</section>' if 'why' in packet else ''
    principle = '<section class="card"><h2>One thing to carry forward</h2>' + paragraph(packet['principle']) + '</section>' if 'principle' in packet else ''
    evidence = ''
    if packet.get('facts') or packet.get('unknowns'):
        evidence = '<details><summary>The evidence and its limits</summary><div class="detail-body two">'
        if packet.get('facts'):
            evidence += '<div><h3>Supplied observations</h3>' + items(packet['facts']) + '</div>'
        if packet.get('unknowns'):
            evidence += '<div><h3>Still unknown</h3>' + items(packet['unknowns']) + '</div>'
        evidence += '</div></details>'
    sources = '<details><summary>Sources behind this response</summary><div class="detail-body">' + items(packet['sources']) + '</div></details>' if packet.get('sources') else ''
    practice = ''
    practice_preview = ''
    if 'practice' in packet:
        navigation += '<button type="button" data-view="practice" aria-pressed="false">Practise</button>'
        p = packet['practice']
        practice_preview = '<section class="card"><h2>Try and notice</h2>' + paragraph(p['prompt']) + '<h3>What to notice</h3>' + paragraph(p['observe']) + '</section>'
        example = '<details><summary>See the prepared example</summary><div class="detail-body">' + paragraph(p['example']) + '<p class="small">A demonstration, not feedback on your answer.</p></div></details>' if 'example' in p else ''
        practice = '<section id="practice" class="view" aria-labelledby="practice-heading"><div class="card"><span class="eyebrow">One small attempt</span><h2 id="practice-heading">Try it in your own words.</h2>' + paragraph(p['prompt'])
        practice += '<label for="practice-note">Your practice attempt</label><textarea id="practice-note" data-note="practice" rows="5" maxlength="12000" autocomplete="off"></textarea>' + example
        practice += '<h3>What to notice</h3>' + paragraph(p['observe']) + '<p class="small">This page offers a prepared self-check. It does not evaluate your text or simulate another person.</p></div></section>'
    reflection = ''
    if 'reflection' in packet:
        navigation += '<button type="button" data-view="reflection" aria-pressed="false">Reflect</button>'
        r = packet['reflection']
        reflection = '<section id="reflection" class="view" aria-labelledby="reflection-heading"><div class="card"><span class="eyebrow">After a real attempt</span><h2 id="reflection-heading">What actually happened?</h2><div class="reflection-fields"><div>' + paragraph(r['prompt'])
        reflection += '<label for="attempt-note">Your account of the attempt</label><textarea id="attempt-note" data-note="attempt" rows="5" maxlength="12000" autocomplete="off"></textarea></div><div>'
        reflection += paragraph(r['adjustment_prompt']) + '<label for="adjustment-note">A possible adjustment</label><textarea id="adjustment-note" data-note="adjustment" rows="4" maxlength="12000" autocomplete="off"></textarea></div></div><p class="small">These are your notes. Exporting them does not approve a general lesson or update the coaching skill\'s learning records.</p></div></section>'
    notes = ''
    if practice or reflection:
        notes = '<aside class="notes" aria-label="Keep your notes"><div><strong>Notes are temporary.</strong><p class="small">Export before closing. No autosave or AI connection.</p></div><div class="note-actions" data-interactive hidden><button type="button" id="export-notes">Export notes</button><label class="file-label" for="import-notes">Load notes</label><input id="import-notes" type="file" accept="application/json,.json"></div><p id="notes-status" class="small" role="status" aria-live="polite">Nothing saved or sent.</p></aside>'
    output = Template(template).substitute(
        csp=escape(csp, quote=True), packet_digest=digest,
        title=escape(packet['title']), goal=paragraph(packet['goal']),
        kind=KINDS[packet['kind']], notice=paragraph(packet['notice']),
        next_move=paragraph(packet['next_move']), navigation=navigation,
        why=why, principle=principle, evidence=evidence, sources=sources,
        practice=practice, practice_preview=practice_preview,
        reflection=reflection, notes=notes)
    content = [packet[key] for key in ('title', 'goal', 'notice', 'next_move', 'why', 'principle')
               if key in packet]
    for key in ('facts', 'unknowns', 'sources'):
        content.extend(packet.get(key, []))
    for key in ('practice', 'reflection'):
        content.extend(packet.get(key, {}).values())
    if any(escape(value) not in output for value in content):
        raise ValueError('Template omitted supplied content')
    return output


def write_new(path, payload):
    path = path.expanduser().absolute()
    skill = HERE.parent / 'skills' / 'compound-intelligence'
    if path.suffix.lower() != '.html' or path.resolve().is_relative_to(skill.resolve()):
        raise ValueError('Output must be an HTML file outside the canonical skill')
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0)
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, 'w', encoding='utf-8') as file:
        file.write(payload)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True, help='New HTML file; never overwritten')
    parser.add_argument('--template', type=Path, default=HERE / 'workspace.html', help='Developer-owned HTML template')
    args = parser.parse_args(argv)
    try:
        output = render(read_packet(args.input.expanduser()), args.template.expanduser())
        write_new(args.output, output)
    except (OSError, ValueError, KeyError, TypeError, RecursionError):
        print('Render failed: check the packet, template and unused output path.', file=sys.stderr)
        return 1
    print(args.output.expanduser().absolute())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
