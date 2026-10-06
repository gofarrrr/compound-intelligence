"""Offline preparation/contamination checks. No host, provider or real secrets."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('host_prepare', ROOT/'evals/prepare_host_comparison.py')
prep = importlib.util.module_from_spec(spec); spec.loader.exec_module(prep)


class HostPreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name); self.pm = self.root/'pm'; self.pm.mkdir()
        self.skill = self.root/'skill'; self.skill.mkdir()
        payloads = {'SKILL.md':b'Synthetic enriched guidance', 'references/cards/01.md':b'Synthetic unchanged source'}
        old = {**payloads, 'SKILL.md':b'Synthetic baseline guidance'}
        for name,data in payloads.items():
            p = self.skill/name; p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(data)
        baseline = self.root/'B.zip'
        with zipfile.ZipFile(baseline,'x') as z:
            for name,data in old.items():z.writestr('compound-intelligence/'+name,data)
        self.record = self.root/'record.json'
        self.record.write_text(json.dumps({'pre_change_skill_snapshot':{'path':str(baseline),
            'sha256':prep.sha(baseline.read_bytes()),'files':[{'path':n,'sha256':prep.sha(d)} for n,d in old.items()]},
            'enriched_skill_snapshot':{'files':[{'path':n,'sha256':prep.sha(d)} for n,d in payloads.items()]}}))
        self.corpus = self.root/'cases.jsonl'
        cases = [{'id':f'CASE-{n:02}','prompt':f'Synthetic request number {n}.','must_include':['Do not leak this expected answer.']} for n in range(15)]
        self.corpus.write_text(''.join(json.dumps(c)+'\n' for c in cases))
        manifest = {'acceptance_contract':'ci.release.host-enrichment.v1','source_member_sha256':prep.sha(self.corpus.read_bytes()),
                    'cases':[{'id':c['id'],'prompt':c['prompt'],'prompt_sha256':prep.sha(c['prompt'].encode())} for c in cases]}
        (self.pm/'case-manifest.json').write_text(json.dumps(manifest))
        (self.pm/'PM-RELEASE-ACCEPTANCE-2026-10-04.md').write_text('Synthetic frozen criteria')

    def run_prepare(self,name='prepared'):
        return prep.prepare(self.pm,self.corpus,self.record,self.skill,self.root/name)

    def test_45_isolated_slots_hide_labels_and_remain_unexecuted(self):
        plan = self.run_prepare()
        self.assertEqual(len(plan['slots']),45)
        self.assertEqual(plan['generation_calls_performed'],0)
        self.assertEqual(plan['reviewer_calls_performed'],0)
        self.assertEqual(len({s['review_alias'] for s in plan['slots']}),45)
        for n in range(15):
            self.assertEqual({s['condition'] for s in plan['slots'] if s['case_id']==f'CASE-{n:02}'},{'P','B','E'})
        for slot in plan['slots']:
            packet = (self.root/'prepared'/slot['request_path']).read_text()
            self.assertNotIn(slot['case_id'],packet)
            self.assertNotIn('expected answer',packet)
            self.assertTrue(packet.startswith(prep.WRAPPER+'\n\n'))
        results = list((self.root/'prepared/coordinator/results').glob('*.json'))
        self.assertEqual(len(results),45)
        self.assertTrue(all(json.loads(p.read_text())['status']=='not_run' for p in results))
        self.assertFalse(list((self.root/'prepared').rglob('SKILL.md')))

    def test_order_aliases_and_snapshots_are_reproducible(self):
        a = self.run_prepare('one');b = self.run_prepare('two')
        self.assertEqual(a['slots'],b['slots']);self.assertEqual(a['snapshots'],b['snapshots'])
        with self.assertRaises(FileExistsError):self.run_prepare('one')

    def test_changed_prompt_and_skill_are_rejected_before_preparing(self):
        self.corpus.write_text(self.corpus.read_text()+'\n')
        with self.assertRaises(ValueError):self.run_prepare()
        self.assertFalse((self.root/'prepared').exists())
        manifest = json.loads((self.pm/'case-manifest.json').read_text())
        manifest['source_member_sha256']=prep.sha(self.corpus.read_bytes())
        (self.pm/'case-manifest.json').write_text(json.dumps(manifest))
        (self.skill/'SKILL.md').write_text('Unexpected new guidance')
        with self.assertRaises(ValueError):self.run_prepare()

    def test_wrong_baseline_cannot_be_substituted(self):
        record=json.loads(self.record.read_text());record['pre_change_skill_snapshot']['sha256']='0'*64
        self.record.write_text(json.dumps(record))
        with self.assertRaises(ValueError):self.run_prepare()
