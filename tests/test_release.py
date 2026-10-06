"""Offline release packaging checks; no network and no user data."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('ci_release_builder', ROOT / 'scripts/build_releases.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

class ReleaseTests(unittest.TestCase):
    def test_secret_private_and_cache_paths_excluded(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            for name in ('SKILL.md', '.env', '.env.local', '.env.production', 'key.pem', 'key.key',
                         'private/case.json', 'receipts/case.json', 'learning-home/CONTEXT.md', '__pycache__/x.pyc',
                         '.venv/pkg.py', 'references/card.md', 'book.epub', '.aws/credentials',
                         '.ssh/id_ed25519', '.DS_Store', '__MACOSX/x', 'docs/research/internal.md',
                         'docs/internal/pm.md', 'credentials.json', 'secrets.json'):
                path = source / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('synthetic')
            self.assertEqual({str(r) for _, r in builder.files_under(source)},
                             {'SKILL.md', 'references/card.md'})

    def test_allowlist_excludes_unknown_reports_and_accepts_curated_technical_doc(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            for name in ['README.md', 'docs/PUBLIC-VALIDATION.md', 'docs/new-private-notes.md', '.env.local']:
                path = source / name; path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('synthetic')
            selected = list(builder.files_under(source, allowed=['README.md', 'docs/PUBLIC-VALIDATION.md']))
            self.assertEqual({str(r) for _, r in selected}, {'README.md', 'docs/PUBLIC-VALIDATION.md'})
            for bad in ['.env.local', 'docs/research/internal.md', 'docs/internal/pm.md', '.aws/credentials', '../outside.md']:
                with self.assertRaises(ValueError):
                    list(builder.files_under(source, allowed=[bad]))

    def test_missing_public_file_and_broken_public_link_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            with self.assertRaises(ValueError):
                list(builder.files_under(source, allowed=['missing.md']))
            (source / 'README.md').write_text('[internal](docs/research/private.md)')
            with self.assertRaises(ValueError):
                builder.archive(source, source.parent / 'invalid-ci-archive.zip', allowed=['README.md'])

    def test_parent_symlink_in_allowlisted_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'source'; source.mkdir()
            outside = Path(tmp) / 'outside'; outside.mkdir()
            (outside / 'x.md').write_text('synthetic')
            (source / 'docs').symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ValueError):
                list(builder.files_under(source, allowed=['docs/x.md']))

    def test_real_public_inventories_have_complete_cards_and_valid_links(self):
        for source in (ROOT, builder.MAIN):
            selected = list(builder.files_under(source))
            builder.check_links(selected)
            names = {relative.as_posix() for _, relative in selected}
            self.assertFalse(any('research/' in n or 'internal/' in n or '.env' in n for n in names))
            self.assertEqual(sum('/cards/' in n and n.endswith('.md') for n in names), 21)
            self.assertEqual(sum(n.endswith('SKILL.md') for n in names), 1)
            self.assertTrue(any(n.endswith('assets/decision/state.schema.json') for n in names))
            if source == builder.MAIN:
                self.assertIn('presentation/render.py',names)
                self.assertIn('presentation/workspace.html',names)
                self.assertEqual(next(p for p,n in selected if n.as_posix()=='presentation/render.py'),ROOT/'presentation/render.py')

    def test_reproducible_archives_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / 'src'
            source.mkdir()
            (source / 'SKILL.md').write_text('synthetic skill')
            a = builder.archive(source, base / 'a.zip')
            b = builder.archive(source, base / 'b.zip')
            self.assertEqual(a['sha256'], b['sha256'])
            with zipfile.ZipFile(base / 'a.zip') as z:
                self.assertIsNone(z.testzip())
                self.assertEqual(z.namelist(), ['compound-intelligence/SKILL.md'])
            with self.assertRaises(FileExistsError):
                builder.archive(source, base / 'a.zip')

    def test_setup_templates_in_both_release_formats(self):
        templates = set((builder.MAIN / 'assets/home-templates').rglob('*.md'))
        self.assertEqual(len(templates), 5)
        for source in (ROOT, builder.MAIN):
            self.assertTrue(templates <= {p for p, _ in builder.files_under(source)})

    def test_symlink_payload_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / 'src'
            source.mkdir()
            outside = base / 'outside.txt'
            outside.write_text('synthetic')
            (source / 'leak.txt').symlink_to(outside)
            with self.assertRaises(ValueError):
                list(builder.files_under(source))

if __name__ == '__main__':
    unittest.main()
