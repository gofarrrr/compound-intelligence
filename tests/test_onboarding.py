"""Offline installation and launcher tests using synthetic keys and a mocked host."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT/'skills/compound-intelligence'


def module(name):
    spec=importlib.util.spec_from_file_location(name,SKILL/'scripts'/f'{name}.py')
    result=importlib.util.module_from_spec(spec); spec.loader.exec_module(result)
    return result


class OnboardingTests(unittest.TestCase):
    def test_install_complete_and_refuse_existing_copy(self):
        installer=module('install')
        with tempfile.TemporaryDirectory() as tmp:
            destination=Path(tmp).resolve()/'skills/compound-intelligence'
            installer.install(destination)
            self.assertEqual((destination/'SKILL.md').read_bytes(),(SKILL/'SKILL.md').read_bytes())
            self.assertEqual(len(list((destination/'references/cards').glob('*.md'))),21)
            (destination/'README.md').write_text('user edit')
            with self.assertRaises(ValueError): installer.install(destination)
            self.assertEqual((destination/'README.md').read_text(),'user edit')

    def test_install_rejects_symlink_destination_and_nested_source(self):
        installer=module('install')
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp).resolve(); actual=base/'actual'; actual.mkdir()
            link=base/'linked'; link.symlink_to(actual,target_is_directory=True)
            with self.assertRaises(ValueError): installer.install(link/'compound-intelligence')
            self.assertEqual(list(actual.iterdir()),[])
            with self.assertRaises(ValueError): installer.install(SKILL/'nested/compound-intelligence')

    def test_install_excludes_credential_files(self):
        installer=module('install')
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp).resolve(); source=base/'source'
            installer.install(source/'compound-intelligence')
            source=source/'compound-intelligence'
            (source/'.env.local').write_text('synthetic fixture only')
            (source/'example.key').write_text('synthetic fixture only')
            target=base/'target/compound-intelligence'
            installer.install(target,source=source)
            self.assertFalse((target/'.env.local').exists())
            self.assertFalse((target/'example.key').exists())

    def test_jev_key_is_child_environment_only_and_consent_not_inherited(self):
        launcher=module('launch_codex'); env={'PATH':'synthetic','CI_ALLOW_TYPESAFE':'1'}
        output=io.StringIO()
        with patch.object(launcher.shutil,'which',return_value='/fake/codex'), \
             patch.object(launcher.sys.stdin,'isatty',return_value=True), \
             patch.object(launcher.sys.stderr,'isatty',return_value=True), \
             patch.object(launcher.getpass,'getpass',return_value='synthetic-not-a-real-key'), \
             patch.object(launcher.subprocess,'call',return_value=0) as call, \
             contextlib.redirect_stdout(output):
            self.assertEqual(launcher.launch(jev=True,environment=env),0)
        argv=call.call_args.args[0]; child=call.call_args.kwargs['env']
        self.assertEqual(child['TYPESAFE_API_KEY'],'synthetic-not-a-real-key')
        self.assertNotIn('synthetic-not-a-real-key',str(argv)+output.getvalue())
        self.assertNotIn('CI_ALLOW_TYPESAFE',child)
        self.assertEqual(env,{'PATH':'synthetic','CI_ALLOW_TYPESAFE':'1'})

    def test_no_tty_does_not_prompt_or_launch(self):
        launcher=module('launch_codex')
        with patch.object(launcher.shutil,'which',return_value='/fake/codex'), \
             patch.object(launcher.sys.stdin,'isatty',return_value=False), \
             patch.object(launcher.getpass,'getpass') as prompt, \
             patch.object(launcher.subprocess,'call') as call:
            with self.assertRaises(ValueError): launcher.launch(jev=True,environment={'PATH':'synthetic'})
        prompt.assert_not_called(); call.assert_not_called()

    def test_local_mode_removes_key_without_mutating_parent(self):
        launcher=module('launch_codex')
        env={'PATH':'synthetic','TYPESAFE_API_KEY':'synthetic-not-a-real-key','CI_ALLOW_TYPESAFE':'1'}
        with patch.object(launcher.shutil,'which',return_value='/fake/codex'), \
             patch.object(launcher.subprocess,'call',return_value=0) as call, \
             contextlib.redirect_stdout(io.StringIO()):
            launcher.launch(environment=env)
        child=call.call_args.kwargs['env']
        self.assertNotIn('TYPESAFE_API_KEY',child); self.assertNotIn('CI_ALLOW_TYPESAFE',child)
        self.assertIn('TYPESAFE_API_KEY',env)

    def test_missing_codex_does_not_request_a_key(self):
        launcher=module('launch_codex')
        with patch.object(launcher.shutil,'which',return_value=None), \
             patch.object(launcher.getpass,'getpass') as prompt:
            with self.assertRaises(ValueError): launcher.launch(jev=True,environment={'PATH':'synthetic'})
        prompt.assert_not_called()

    def test_package_version_matches_all_installed_surfaces(self):
        version=(ROOT/'VERSION').read_text().strip()
        self.assertEqual(version,(SKILL/'VERSION').read_text().strip())
        for path in ['plugin.json','.codex-plugin/plugin.json','.claude-plugin/plugin.json']:
            self.assertEqual(json.loads((ROOT/path).read_text())['version'],version)
        self.assertIn(f'__version__ = "{version}"',(SKILL/'scripts/ci_runtime/__init__.py').read_text())


if __name__=='__main__': unittest.main()
