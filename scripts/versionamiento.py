#!/usr/bin/env python3
"""Versionado por commits, adaptado de Patrick750/versionamiento."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from zoneinfo import ZoneInfo

FORMAT = re.compile(r'^\w[\w-]*(?:\([\w.-]+\))?:\s+(high|low|parch|patch)\s+\[(\d+\.\d+\.\d+)\]\s+\S.*$', re.I)
SUSPICIOUS = re.compile(r'\b(?:high|low|parch|patch)\b|\[\d+(?:\.\d+)*\]', re.I)
SEMVER = re.compile(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)')
EXPECTED = {'high': '1.0.0', 'low': '0.1.0', 'parch': '0.0.1', 'patch': '0.0.1'}


def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()


def keyword(subject):
    if subject.startswith('chore(version-bump):'):
        return None
    match = FORMAT.fullmatch(subject)
    if match:
        kind = match[1].lower()
        if match[2] != EXPECTED[kind]:
            raise ValueError(f'{kind} requiere [{EXPECTED[kind]}], no [{match[2]}]')
        return kind
    if SUSPICIOUS.search(subject):
        raise ValueError('Declaración de versión inválida: tipo(modulo): high|low|parch [X.Y.Z] descripción')
    return None


def read_version(path=Path('VERSION')):
    value = path.read_text().strip() if path.exists() else '0.0.0'
    if not SEMVER.fullmatch(value):
        raise ValueError('VERSION debe contener MAJOR.MINOR.PATCH, sin espacios internos ni ceros iniciales')
    return value


def increment(value, kind):
    major, minor, patch = map(int, value.split('.'))
    if kind == 'high':
        return f'{major + 1}.0.0'
    if kind == 'low':
        return f'{major}.{minor + 1}.0'
    return f'{major}.{minor}.{patch + 1}'


def commits(before, after, for_pr=False):
    for sha in (before, after):
        if not re.fullmatch(r'[0-9a-fA-F]{40}', sha):
            raise ValueError('Los extremos del rango deben ser SHA completos')
    if set(before) == {'0'}:
        return git('rev-list', '--reverse', '--topo-order', after).splitlines()
    if for_pr:
        # Un PR puede divergir de main. Excluir los commits que ya están en la base.
        if subprocess.run(['git', 'merge-base', before, after], capture_output=True).returncode:
            raise ValueError('Las ramas del PR no tienen un ancestro común')
    elif subprocess.run(['git', 'merge-base', '--is-ancestor', before, after], capture_output=True).returncode:
        raise ValueError('before no es ancestro de after; revisar force-push antes de versionar')
    return git('rev-list', '--reverse', '--topo-order', f'{before}..{after}').splitlines()


def sync_version(value, sha, subject):
    paths = ['VERSION']
    Path('VERSION').write_text(value + '\n')
    for name in ('frontend_project/package.json', 'frontend_project/package-lock.json'):
        path = Path(name)
        if not path.exists():
            continue
        data = json.loads(path.read_text())
        data['version'] = value
        if 'packages' in data:
            data['packages']['']['version'] = value
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
        paths.append(name)
    readme = Path('README.md')
    if readme.exists():
        text, count = re.subn(r'(Versión(?: actual)?: \*\*)\d+\.\d+\.\d+(\*\*)', rf'\g<1>{value}\2', readme.read_text(), count=1)
        if count:
            readme.write_text(text)
            paths.append('README.md')
    changelog = Path('CHANGELOG.md')
    date = datetime.now(ZoneInfo('America/Bogota')).date().isoformat()
    # Una entrada por origen. Se conserva el changelog detallado previo.
    title = subject.replace('<', '&lt;').replace('>', '&gt;')
    author = git('show', '-s', '--format=%an', sha).replace('<', '&lt;').replace('>', '&gt;')
    actor = os.environ.get('VERSION_ACTOR', '').strip()
    github_user = f'@{actor}' if actor else 'No disponible (ejecución local)'
    github_user = github_user.replace('<', '&lt;').replace('>', '&gt;')
    entry = f'### {value} — {date} — {title}\n\n- Autor del commit: {author}.\n- Usuario de GitHub que inició el versionamiento: {github_user}.\n- Commit de origen: `{sha}`. Versión calculada automáticamente desde VERSION.\n\n'
    text = changelog.read_text() if changelog.exists() else '# Changelog\n\n'
    position = re.search(r'^### ', text, re.M)
    index = position.start() if position else len(text)
    changelog.write_text(text[:index] + entry + text[index:])
    paths.append('CHANGELOG.md')
    return paths


def process(before, after, branch, push=False, initial_version=None):
    if branch not in ('main', 'master'):
        raise ValueError('Solo se permite versionar main o master')
    if git('status', '--porcelain'):
        raise ValueError('El checkout debe estar limpio antes de versionar')
    if subprocess.run(['git', 'merge-base', '--is-ancestor', after, 'HEAD'], capture_output=True).returncode:
        raise ValueError('El checkout no contiene el push solicitado')
    value = read_version()
    initial_tag = None
    if initial_version is not None:
        if not SEMVER.fullmatch(initial_version):
            raise ValueError('La versión inicial debe ser MAJOR.MINOR.PATCH')
        candidate = f'v{initial_version}'
        if subprocess.run(['git', 'show-ref', '--verify', '--quiet', f'refs/tags/{candidate}']).returncode:
            if value != initial_version:
                raise ValueError(f'Falta el tag inicial {candidate}, pero VERSION ya es {value}')
            initial_tag = candidate
    subjects = [(sha, git('show', '-s', '--format=%s', sha)) for sha in commits(before, after)]
    # Validar el lote completo antes de generar commits o tags.
    kinds = [(sha, subject, keyword(subject)) for sha, subject in subjects]
    completed = set(re.findall(r'^Version-Origin: ([0-9a-f]{40})$', git('log', '--format=%B', 'HEAD'), re.M))
    plan = []
    for sha, subject, kind in kinds:
        if not kind or sha in completed:
            continue
        value = increment(value, kind)
        tag = f'v{value}'
        if subprocess.run(['git', 'show-ref', '--verify', '--quiet', f'refs/tags/{tag}']).returncode == 0:
            raise ValueError(f'El tag {tag} ya existe sin un origen procesado; no se sobrescribe')
        plan.append((sha, subject, value, tag))
    tags = []
    if initial_tag:
        subprocess.run(['git', 'tag', '-a', initial_tag, '-m', f'Release inicial {initial_tag}'], check=True)
        tags.append(initial_tag)
    for sha, subject, value, tag in plan:
        paths = sync_version(value, sha, subject)
        subprocess.run(['git', 'add', '--', *paths], check=True)
        message = f'chore(version-bump): {value} (origen: {sha[:7]} - {subject})\n\nVersion-Origin: {sha}'
        subprocess.run(['git', 'commit', '-m', message], check=True)
        subprocess.run(['git', 'tag', '-a', tag, '-m', f'Release {tag} (origen: {sha[:7]} - {subject})'], check=True)
        tags.append(tag)
    if push and tags:
        # Solo estos tags, junto con la rama; no se publican tags ajenos.
        subprocess.run(['git', 'push', '--atomic', 'origin', f'HEAD:refs/heads/{branch}',
                        *[f'refs/tags/{tag}:refs/tags/{tag}' for tag in tags]], check=True)
    return tags


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['lint', 'bump', 'check'])
    parser.add_argument('--before')
    parser.add_argument('--after')
    parser.add_argument('--branch', default='main')
    parser.add_argument('--push', action='store_true')
    parser.add_argument('--initial-version', help='Registrar la versión existente antes del primer incremento')
    args = parser.parse_args()
    try:
        if args.mode == 'check':
            value = read_version()
            for name in ('frontend_project/package.json', 'frontend_project/package-lock.json'):
                data = json.loads(Path(name).read_text())
                if data['version'] != value or ('packages' in data and data['packages']['']['version'] != value):
                    raise ValueError(f'{name} no coincide con VERSION={value}')
            readme = Path('README.md')
            if readme.exists():
                match = re.search(r'Versión(?: actual)?: \*\*(\d+\.\d+\.\d+)\*\*', readme.read_text())
                if not match or match[1] != value:
                    raise ValueError('La versión del README no coincide con VERSION')
            print(f'Versión consistente: {value}')
        elif args.mode == 'lint':
            errors = []
            for sha in commits(args.before or '', args.after or '', for_pr=True):
                try:
                    keyword(git('show', '-s', '--format=%s', sha))
                except ValueError as exc:
                    errors.append(f'{sha[:7]}: {exc}')
            if errors:
                raise ValueError('; '.join(errors))
            print('Commits del PR válidos')
        else:
            tags = process(args.before or '', args.after or '', args.branch, args.push, args.initial_version)
            print(f'Versiones generadas: {", ".join(tags) or "ninguna"}')
            if os.environ.get('GITHUB_OUTPUT'):
                with open(os.environ['GITHUB_OUTPUT'], 'a') as output:
                    output.write(f'sha={git("rev-parse", "HEAD")}\n')
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        message = str(exc).replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A')
        print(f'::error::{message}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
