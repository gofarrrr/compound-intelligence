"""Deterministic structure and filesystem tests, not model-behavior evaluations."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import re
import shutil
import stat
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'skills' / 'compound-intelligence'
REF = MAIN / 'references'
WORKFLOWS = {'learn','rehearse','review','panel','debate','compose','reflect','save','setup'}

def load_creator(path=MAIN/'scripts'/'create_home.py'):
    spec=importlib.util.spec_from_file_location('ci_home_'+str(id(path)),path)
    module=importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module

class StructureTests(unittest.TestCase):
    def test_manifest_identity_and_paths(self):
        manifests=[json.loads((ROOT/p).read_text()) for p in ['plugin.json','.claude-plugin/plugin.json','.codex-plugin/plugin.json']]
        for field in ['name','version','description']:
            self.assertEqual(len({m[field] for m in manifests}),1)
        self.assertEqual(manifests[0]['name'],'compound-intelligence')
        self.assertEqual(manifests[2]['skills'],'./skills/')
        self.assertTrue((ROOT/manifests[2]['skills']).is_dir())
        for m in manifests:
            self.assertNotIn('repository',m)  # No invented published repository.

    def test_skill_frontmatter_and_names(self):
        paths=list((ROOT/'skills').glob('*/SKILL.md'))
        self.assertEqual(len(paths),1)
        for path in paths:
            text=path.read_text()
            self.assertTrue(text.startswith('---\n'),path)
            front=text.split('---\n',2)[1]
            fields={line.split(':',1)[0]:line.split(':',1)[1].strip() for line in front.splitlines() if ':' in line}
            self.assertEqual(set(fields),{'name','description'},path)
            self.assertEqual(fields['name'],path.parent.name,path)
            self.assertRegex(fields['name'],r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
            description=json.loads(fields['description'])
            self.assertTrue(20<=len(description)<=1024,path)
            self.assertLess(len(text.splitlines()),500,path)

    def test_all_local_markdown_links_resolve(self):
        pattern=re.compile(r'\[[^\]\n]*\]\(([^)]+)\)')
        for path in ROOT.rglob('*.md'):
            for raw in pattern.findall(path.read_text()):
                if raw.startswith(('http://','https://','mailto:','#')):
                    continue
                relative=raw.split('#')[0]
                target=(path.parent/relative).resolve()
                self.assertTrue(target==ROOT or ROOT in target.parents,(path,raw,'outside package'))
                self.assertTrue(target.exists(),(path,raw,'missing'))

    def test_portable_skill_self_contained(self):
        pattern=re.compile(r'\[[^\]\n]*\]\(([^)]+)\)')
        for path in MAIN.rglob('*.md'):
            for raw in pattern.findall(path.read_text()):
                if raw.startswith(('http://','https://','mailto:','#')):
                    continue
                target=(path.parent/raw.split('#')[0]).resolve()
                self.assertTrue(target==MAIN or MAIN in target.parents,(path,raw))
        self.assertTrue((MAIN/'scripts/create_home.py').is_file())

    def test_source_coverage_and_card_sections(self):
        index=json.loads((REF/'source-index.json').read_text())
        self.assertEqual([c['chapter'] for c in index['chapters']],list(range(1,22)))
        self.assertEqual(len(list((REF/'cards').glob('*.md'))),21)
        for c in index['chapters']:
            card=REF/c['card']; text=card.read_text()
            self.assertIn(c['framework'],text)
            self.assertIn(c['printed_pages'],text)
            for section in ['## Select this when','## Route elsewhere when','## Coaching explanation','## Useful output','## Original coaching question','## Small practice','## Observe and adjust','## Common misuse']:
                self.assertIn(section,text,card)
            self.assertTrue(any(r['legacy_alias']==c['skill'] for r in json.loads((MAIN/'assets/decision/cards.json').read_text())))
            self.assertTrue(c['primary_epub_spine_path'].startswith('OEBPS/xhtml/'))

    def test_workflow_adapters_point_to_canonical_files(self):
        for name in WORKFLOWS:
            path=REF/'workflows'/f'{name}.md'
            self.assertTrue(path.is_file())
            self.assertTrue(path.read_text().strip())

    def test_no_legacy_components_or_book_payload(self):
        for path in ROOT.rglob('*'):
            self.assertFalse(path.name.startswith('cw-'),path)
            self.assertNotIn(path.suffix.lower(),{'.epub','.pdf','.png','.jpg','.jpeg'},path)
            self.assertNotIn(path.name,{'VOICE.md','STYLE.md','TASTE.md','AUDIENCE.md'},path)
        self.assertFalse((ROOT/'hooks').exists())
        self.assertFalse((ROOT/'.mcp.json').exists())
        self.assertFalse((ROOT/'learning-home').exists())

    def test_learning_record_schema(self):
        schema=json.loads((MAIN/'assets/practice-record.schema.json').read_text())
        self.assertFalse(schema['additionalProperties'])
        for field in ['scope','source','observations','limits','status','user_approved','updated','review_trigger']:
            self.assertIn(field,schema['required'])
        self.assertIn('provisional',schema['properties']['status']['enum'])
        self.assertIn('retired',schema['properties']['status']['enum'])

    def test_evaluation_set_is_well_formed_and_unclaimed(self):
        cases=[json.loads(line) for line in (ROOT/'evals/cases.jsonl').read_text().splitlines() if line.strip()]
        self.assertGreaterEqual(len(cases),40)
        self.assertEqual(len({c['id'] for c in cases}),len(cases))
        self.assertEqual({c['source_chapters'][0] for c in cases if c['category']=='chapter-fit'},set(range(1,22)))
        skills={p.parent.name for p in (ROOT/'skills').glob('*/SKILL.md')}
        skills.update(r['legacy_alias'] for r in json.loads((MAIN/'assets/decision/cards.json').read_text()))
        skills.update('ci-'+name for name in WORKFLOWS|{'help'})
        for c in cases:
            self.assertTrue(c['prompt'] and c['must_include'] and c['must_not'])
            for route in c['expected_routes']:
                self.assertIn(route,skills|{'clarify','out-of-scope','safety-first'})
        self.assertEqual(json.loads((ROOT/'evals/result-template.json').read_text())['status'],'not_run')

class SetupTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.base=Path(self.tmp.name).resolve()
        self.creator=load_creator()
    def tearDown(self):
        self.tmp.cleanup()

    def test_create_new_home(self):
        target=self.base/'home'
        result=self.creator.create_home(target)
        self.assertEqual(len(result['created']),5)
        self.assertEqual(result['preserved'],[])
        for name in ['CONTEXT.md','PRINCIPLES.md','PRACTICE.md','examples/README.md','cases/README.md']:
            self.assertTrue((target/name).is_file())

    def test_dry_run_has_no_side_effects(self):
        target=self.base/'nested'/'home'
        result=self.creator.create_home(target,dry_run=True)
        self.assertEqual(len(result['would_create']),5)
        self.assertFalse((self.base/'nested').exists())
        self.assertEqual(result['created'],[])

    def test_nonempty_requires_explicit_add_missing(self):
        target=self.base/'home';target.mkdir();(target/'existing.txt').write_text('preserve')
        with self.assertRaises(ValueError):self.creator.create_home(target)
        self.assertEqual(list(target.iterdir()),[target/'existing.txt'])

    def test_existing_file_never_overwritten(self):
        target=self.base/'home';target.mkdir();(target/'CONTEXT.md').write_text('USER CONTENT')
        result=self.creator.create_home(target,add_missing=True)
        self.assertEqual((target/'CONTEXT.md').read_text(),'USER CONTENT')
        self.assertIn(str(target/'CONTEXT.md'),result['preserved'])
        self.assertEqual(len(result['created']),4)

    def test_add_missing_is_idempotent(self):
        target=self.base/'home';self.creator.create_home(target)
        result=self.creator.create_home(target,add_missing=True)
        self.assertEqual(result['created'],[])
        self.assertEqual(len(result['preserved']),5)

    def test_target_file_is_rejected(self):
        target=self.base/'home';target.write_text('x')
        with self.assertRaises(ValueError):self.creator.create_home(target)
        self.assertEqual(target.read_text(),'x')

    def test_symlink_target_is_rejected(self):
        actual=self.base/'actual';actual.mkdir();link=self.base/'linked';link.symlink_to(actual,target_is_directory=True)
        with self.assertRaises(ValueError):self.creator.create_home(link)
        self.assertEqual(list(actual.iterdir()),[])

    def test_nested_symlink_rejected_before_any_write(self):
        target=self.base/'home';target.mkdir();outside=self.base/'outside';outside.mkdir()
        (target/'cases').symlink_to(outside,target_is_directory=True)
        with self.assertRaises(ValueError):self.creator.create_home(target,add_missing=True)
        self.assertFalse((target/'CONTEXT.md').exists())
        self.assertEqual(list(outside.iterdir()),[])

    def test_dangling_symlink_file_is_rejected(self):
        target=self.base/'home';target.mkdir();(target/'PRACTICE.md').symlink_to(self.base/'missing')
        with self.assertRaises(ValueError):self.creator.create_home(target,add_missing=True)
        self.assertFalse((target/'CONTEXT.md').exists())

    def test_directory_collision_preflight(self):
        target=self.base/'home';target.mkdir();(target/'examples').write_text('not a directory')
        with self.assertRaises(ValueError):self.creator.create_home(target,add_missing=True)
        self.assertFalse((target/'CONTEXT.md').exists())

    def test_package_directory_is_protected(self):
        with self.assertRaises(ValueError):self.creator.create_home(ROOT/'never-create')
        self.assertFalse((ROOT/'never-create').exists())
        with self.assertRaises(ValueError):self.creator.create_home(MAIN/'never-create')

    def test_filesystem_root_is_rejected(self):
        with self.assertRaises(ValueError):self.creator.create_home(Path('/'),add_missing=True)

    def test_portable_copy_runs_and_protects_itself(self):
        portable=self.base/'portable-skill'
        shutil.copytree(MAIN,portable,ignore=shutil.ignore_patterns('__pycache__'))
        creator=load_creator(portable/'scripts/create_home.py')
        with self.assertRaises(ValueError):creator.create_home(portable/'never-create')
        result=creator.create_home(self.base/'portable-home')
        self.assertEqual(len(result['created']),5)

    def test_new_files_owner_only(self):
        target=self.base/'home';self.creator.create_home(target)
        for path in target.rglob('*.md'):
            self.assertEqual(stat.S_IMODE(path.stat().st_mode),0o600)

if __name__=='__main__':
    unittest.main(verbosity=2)
