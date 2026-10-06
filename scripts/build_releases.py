#!/usr/bin/env python3
"""Build versioned plugin and portable-skill ZIPs from the canonical tree.

Runs offline tests first; never installs, uploads, or calls a model. Known secret,
private-state and cache paths are excluded, but this is not a secret scanner.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import posixpath
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / 'skills' / 'compound-intelligence'
EXCLUDE = {'.git', '__pycache__', '.pytest_cache', '.dist', '.venv', 'venv',
           'node_modules', '.local', 'private', 'receipts', 'learning-home',
           '__MACOSX', '.DS_Store', '.ssh', '.aws', '.config', '.netrc', '.npmrc',
           'credentials', 'credentials.json', 'secrets.json', 'id_rsa', 'id_ed25519'}
EXCLUDE_SUFFIX = {'.pyc', '.zip', '.epub', '.pdf', '.pem', '.key', '.p12', '.pfx',
                  '.sqlite', '.sqlite3', '.db'}

def prohibited(relative: Path) -> bool:
    return (relative.is_absolute() or '..' in relative.parts
            or any(part in EXCLUDE or part.startswith('.env') for part in relative.parts)
            or relative.suffix.lower() in EXCLUDE_SUFFIX
            or relative.as_posix().startswith(('docs/research/', 'docs/internal/'))
            or relative.as_posix() in {'docs/SESSION-HANDOFF.md', 'docs/VALIDATION.md', 'AGENTS.md'})


def release_paths(source: Path) -> list[str] | None:
    format_name = 'plugin' if source == ROOT else 'skill' if source == MAIN else None
    if format_name is None:
        return None
    policy = json.loads((ROOT / 'scripts/public-release-files.json').read_text())
    if policy['kind'] != 'ci.public-release-files.v1':
        raise ValueError('Unsupported public release manifest')
    return policy['formats'][format_name]


def files_under(source: Path, *, allowed: list[str] | None = None):
    allowed = release_paths(source) if allowed is None else allowed
    if allowed is not None:
        if len(allowed) != len(set(allowed)):
            raise ValueError('Duplicate public release path')
        for name in sorted(allowed):
            relative = Path(name)
            if prohibited(relative):
                raise ValueError(f'Prohibited public release path: {name}')
            # Bundle the separate renderer without maintaining a second source copy.
            payload_source = ROOT if source == MAIN and relative.parts[0] == 'presentation' else source
            if payload_source == ROOT and source == MAIN and name not in release_paths(ROOT):
                raise ValueError(f'Undeclared presentation payload: {name}')
            path = payload_source / relative
            if any(parent.is_symlink() for parent in [path, *(payload_source / p for p in relative.parents)]):
                raise ValueError(f'Refusing symlink in public path: {name}')
            if not path.is_file():
                raise ValueError(f'Missing declared public file: {name}')
            yield path, relative
        return
    for path in sorted(source.rglob('*')):
        relative = path.relative_to(source)
        if prohibited(relative):
            continue
        if path.is_symlink():
            raise ValueError(f'Refusing to package symlink: {path}')
        if not path.is_file() or path.suffix.lower() in EXCLUDE_SUFFIX:
            continue
        yield path, relative

def check_links(payloads) -> None:
    names = {relative.as_posix() for _, relative in payloads}
    for path, relative in payloads:
        if relative.suffix != '.md':
            continue
        for raw in re.findall(r'\[[^\]\n]*\]\(([^)]+)\)', path.read_text()):
            if raw.startswith(('http://', 'https://', 'mailto:', '#')):
                continue
            target = posixpath.normpath(posixpath.join(relative.parent.as_posix(), raw.split('#')[0]))
            if target == '..' or target.startswith('../') or target.startswith('/'):
                raise ValueError(f'Link outside public archive: {relative}: {raw}')
            if target not in names and target != '.' and not any(n.startswith(target + '/') for n in names):
                raise ValueError(f'Missing public link target: {relative}: {raw}')


def archive(source: Path, destination: Path, *, allowed: list[str] | None = None) -> dict:
    payloads = list(files_under(source, allowed=allowed))
    check_links(payloads)
    with zipfile.ZipFile(destination, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for path, relative in payloads:
            name = 'compound-intelligence/' + relative.as_posix()
            info = zipfile.ZipInfo(name, date_time=(2026, 10, 2, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100644 << 16)
            z.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    with zipfile.ZipFile(destination) as z:
        if z.testzip() is not None:
            raise ValueError(f'Archive integrity failure: {destination}')
        for path, relative in payloads:
            if z.read('compound-intelligence/' + relative.as_posix()) != path.read_bytes():
                raise ValueError(f'Archive content mismatch: {path}')
    return {'path': str(destination), 'files': len(payloads), 'bytes': destination.stat().st_size,
            'sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
            'local_markdown_links': 'passed',
            'contents': [{'path': relative.as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
                         for path, relative in payloads]}

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True, help='Output directory outside the source package')
    args = p.parse_args()
    out = args.output.expanduser().resolve()
    if out == ROOT or ROOT in out.parents:
        p.error('Output must be outside the package source tree.')
    version = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
    if not re.fullmatch(r'\d+\.\d+\.\d+', version):
        p.error('VERSION must be a semantic version with three numeric components.')
    prefix = f'compound-intelligence-v{version}'
    names = [prefix + '-plugin.zip', prefix + '-skill.zip', prefix + '-checksums.txt', prefix + '-contents.json']
    if any((out / name).exists() or (out / name).is_symlink() for name in names):
        p.error('Release output already exists; use a new output directory. Files are never overwritten.')
    subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'], cwd=ROOT, check=True)
    out.mkdir(parents=True, exist_ok=True)
    products = [archive(ROOT, out / names[0]), archive(MAIN, out / names[1])]
    with (out / names[2]).open('x', encoding='utf-8') as f:
        f.write(''.join(f'{r["sha256"]}  {Path(r["path"]).name}\n' for r in products))
    with (out / names[3]).open('x', encoding='utf-8') as f:
        json.dump({'publication': 'not performed by builder', 'package_version': version,
                   'public_manifest_sha256': hashlib.sha256((ROOT / 'scripts/public-release-files.json').read_bytes()).hexdigest(),
                   'products': products}, f, indent=2)
        f.write('\n')
    print(json.dumps([{k: v for k, v in product.items() if k != 'contents'} for product in products], indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
