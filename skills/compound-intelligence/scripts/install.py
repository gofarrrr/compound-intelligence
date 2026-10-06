#!/usr/bin/env python3
"""Install this complete local skill for Codex without replacing an existing copy."""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys

SKILL_ROOT = Path(__file__).resolve().parents[1]


def install(destination=None, *, source=SKILL_ROOT):
    source = Path(source).resolve()
    target = Path(destination or Path.home()/'.agents/skills/compound-intelligence').expanduser().absolute()
    if target.name != 'compound-intelligence':
        raise ValueError('Destination must end in compound-intelligence.')
    if target.exists() or target.is_symlink():
        raise ValueError('An installation already exists. Back it up or disable it before installing; nothing was overwritten.')
    if any(p.is_symlink() for p in target.parents):
        raise ValueError('Destination has a symlink parent. Choose its actual location explicitly.')
    target = target.resolve()
    if target == source or source in target.parents:
        raise ValueError('Destination must be outside the downloaded source folder.')
    for name in ('SKILL.md','VERSION','LICENSE','NOTICE.md','scripts/ci.py','references/onboarding.md'):
        if not (source/name).is_file():
            raise ValueError('Incomplete download. Keep the entire portable skill folder together.')
    if any(p.is_symlink() for p in source.rglob('*')):
        raise ValueError('Source contains symlinks. Use a fresh release download.')
    target.parent.mkdir(parents=True, exist_ok=True)
    # copytree creates the destination exclusively. Failure leaves a partial copy,
    # never a successful installation or permission to replace it on a retry.
    shutil.copytree(source, target, ignore=shutil.ignore_patterns(
        '__pycache__','*.pyc','.DS_Store','.git','.env','.env.*','*.pem','*.key'))
    return target


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination',type=Path,help='Optional repository-local .agents/skills/compound-intelligence path')
    args = parser.parse_args(argv)
    try:
        target = install(args.destination)
    except ValueError as error:
        print(str(error),file=sys.stderr)
        return 1
    except OSError:
        # Avoid printing arbitrary filesystem errors that could disclose contents.
        print('Installation not completed. Keep the full download; choose a new, non-symlink destination and preserve any existing copy.',file=sys.stderr)
        return 1
    print(f'Installed Compound Intelligence at {target}')
    print('Restart Codex and invoke $compound-intelligence, or follow README for Jev setup.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
