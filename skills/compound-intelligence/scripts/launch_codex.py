#!/usr/bin/env python3
"""User-run Codex launcher: optional hidden TypeSafe key entry, no key files or API calls."""
from __future__ import annotations

import argparse
import getpass
import os
from pathlib import Path
import shutil
import subprocess
import sys
import warnings

SKILL_ROOT = Path(__file__).resolve().parents[1]


def launch(*, jev=False, environment=None):
    env = dict(os.environ if environment is None else environment)
    host = shutil.which('codex',path=env.get('PATH'))
    if not host:
        raise ValueError('Install and sign in to Codex CLI first: https://developers.openai.com/codex/cli/')
    # A new launcher session grants no standing permission to send cases.
    env.pop('CI_ALLOW_TYPESAFE',None)
    if jev:
        if not env.get('TYPESAFE_API_KEY','').strip():
            if not sys.stdin.isatty() or not sys.stderr.isatty():
                raise ValueError('Run this yourself in an interactive terminal; never provide a key through chat or agent tools.')
            with warnings.catch_warnings():
                warnings.simplefilter('error',getpass.GetPassWarning)
                key = getpass.getpass('TypeSafe API key (hidden): ')
            if not key.strip():
                raise ValueError('No key supplied. Use --local to start without Jev.')
            env['TYPESAFE_API_KEY'] = key.strip()
        mode = 'Use Jev-assisted selection for eligible substantive cases after approval. If staying local, explain the reason; do not silently skip requested Jev. Check doctor in the actual tool environment first. Ask before any TypeSafe call; a key is not sending permission.'
        print('Key available to the new Codex process; connection remains unverified. No key file was written. Approve each outgoing request separately.')
    else:
        env.pop('TYPESAFE_API_KEY',None)
        mode = 'Use local coaching only. Do not make TypeSafe calls.'
        print('Starting local coaching without a TypeSafe key.')
    prompt = f'Use $compound-intelligence from {SKILL_ROOT / "SKILL.md"}. {mode} Help me start with one leadership situation; no case save is authorized yet.'
    # The secret exists only in the child's environment, never in argv/prompt.
    # Host environment/sandbox policy is preserved; in-host doctor confirms access.
    return subprocess.call([host,'--no-daemon',prompt],env=env)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--jev',action='store_true',help='Use your environment key or ask you for hidden terminal entry')
    mode.add_argument('--local',action='store_true',help='Start without a TypeSafe key')
    args = parser.parse_args(argv)
    try:
        return launch(jev=args.jev)
    except ValueError as error:
        print(str(error),file=sys.stderr)
    except (getpass.GetPassWarning,EOFError,KeyboardInterrupt,OSError):
        print('Setup stopped. No key was saved or displayed; Codex was not started successfully.',file=sys.stderr)
    return 1


if __name__ == '__main__':
    sys.exit(main())
