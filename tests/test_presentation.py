"""Offline boundaries for the separate final-response renderer."""
import base64
from copy import deepcopy
import hashlib
from html import escape
import importlib.util
import json
from pathlib import Path
import re
import stat
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('ci_presentation', ROOT / 'presentation/render.py')
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)
EXAMPLE = json.loads((ROOT / 'presentation/examples/handoffs.json').read_text())


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)
    elif isinstance(value, dict):
        for key, item in value.items():
            if key not in {'schema_version', 'kind'}:
                yield from strings(item)


class PresentationTests(unittest.TestCase):
    def test_all_supplied_content_preserved_and_untrusted_markup_escaped(self):
        packet = deepcopy(EXAMPLE)
        packet['title'] = 'An opening <script>alert("case")</script> & a question'
        packet['practice']['example'] = '</textarea><img src=x onerror=alert(1)>'
        html = renderer.render(packet)
        for value in strings(packet):
            self.assertIn(escape(value), html)
        self.assertEqual(len(re.findall(r'<script>', html)), 1)
        self.assertNotIn('<img', html)
        self.assertNotIn('<script>alert', html)
        self.assertEqual(renderer.render(packet), html)
        script = re.search(r'<script>(.*?)</script>', html, flags=re.S).group(1)
        script_hash = base64.b64encode(hashlib.sha256(script.encode()).digest()).decode()
        self.assertIn('sha256-' + script_hash, html)
        self.assertIn("connect-src &#x27;none&#x27;", html)
        self.assertNotRegex(html, r'\b(?:fetch|localStorage|XMLHttpRequest)\s*[(.]')

    def test_all_delivery_branches_preserve_notice_and_do_not_invent_practice(self):
        for kind, label in renderer.KINDS.items():
            with self.subTest(kind=kind):
                packet = {key: EXAMPLE[key] for key in
                          ('schema_version', 'title', 'goal', 'notice', 'next_move')}
                packet['kind'] = kind
                packet['notice'] = 'The host still requires a manual check; no pass is established.'
                html = renderer.render(packet)
                self.assertIn(label, html)
                self.assertIn(escape(packet['notice']), html)
                notice = re.search(r'<aside class="notice".*?</aside>', html, flags=re.S).group()
                self.assertNotIn('hidden', notice)
                self.assertNotIn('data-view="practice"', html)
                self.assertNotIn('data-view="reflection"', html)
                self.assertNotIn('advisory_pass', html)

    def test_invalid_packets_and_duplicate_fields_are_rejected(self):
        for change in ({'unknown_field': 'ignore me'}, {'schema_version': 'ci.state.v2'},
                       {'kind': []}, {'next_move': ''}, {'sources': ['ok', 4]},
                       {'practice': {'prompt': 'incomplete'}}, {'goal': 'x\x00y'},
                       {'reflection': {'prompt': 'ok', 'adjustment_prompt': None}}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                renderer.render(dict(EXAMPLE, **change))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'packet.json'
            path.write_text('{"kind":"advice","kind":"manual_review"}')
            with self.assertRaises(ValueError):
                renderer.read_packet(path)
            path.write_bytes(b' ' * (renderer.MAX_BYTES + 1))
            with self.assertRaises(ValueError):
                renderer.read_packet(path)

    def test_output_is_private_create_only_and_cannot_change_the_skill(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'brief.html'
            renderer.write_new(output, renderer.render(EXAMPLE))
            self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)
            before = output.read_bytes()
            with self.assertRaises(FileExistsError):
                renderer.write_new(output, 'replacement')
            self.assertEqual(output.read_bytes(), before)
            link = Path(directory) / 'link.html'
            link.symlink_to(output)
            with self.assertRaises(OSError):
                renderer.write_new(link, 'replacement')
            self.assertEqual(output.read_bytes(), before)
            with self.assertRaises(ValueError):
                renderer.write_new(ROOT / 'skills/compound-intelligence/test-presentation.html', 'x')

    def test_an_alternate_template_does_not_change_the_packet(self):
        with tempfile.TemporaryDirectory() as directory:
            template = Path(directory) / 'alternate.html'
            template.write_text('<html><head><title>$title</title></head><body>$goal$notice$next_move$why$principle$practice_preview$evidence$sources$practice$reflection</body></html>')
            before = deepcopy(EXAMPLE)
            html = renderer.render(EXAMPLE, template)
            self.assertEqual(EXAMPLE, before)
            for value in strings(EXAMPLE):
                self.assertIn(escape(value), html)
            template.write_text('<html><body>$title$goal$next_move</body></html>')
            with self.assertRaises(ValueError):
                renderer.render(EXAMPLE, template)


if __name__ == '__main__':
    unittest.main()
