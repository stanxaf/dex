#!/usr/bin/env python3
"""Install reviewed foundation content without overwriting project-owned files."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = '.ai-foundation/manifest.json'
PROFILES = ('baseline', 'web-saas', 'regulated')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_name(name):
    path = PurePosixPath(name)
    if (not isinstance(name, str) or path.is_absolute() or
            any(part in ('', '.', '..') for part in name.split('/'))):
        raise ValueError('invalid managed path: ' + repr(name))
    parts = path.parts
    if (len(parts) >= 3 and parts[:2] in (('.ai-foundation', 'docs'),
                                           ('.ai-foundation', 'profiles'),
                                           ('.ai-foundation', 'templates'))):
        return name
    if (len(parts) >= 4 and parts[:2] == ('.agents', 'skills') and
            re.fullmatch(r'foundation-[a-z0-9-]+', parts[2])):
        return name
    raise ValueError('path outside managed scope: ' + repr(name))


def checked_path(project, name):
    # Never follow symlinks in any component of a managed or project-owned path.
    current = project
    for part in PurePosixPath(name).parts:
        current = current / part
        if current.is_symlink():
            raise ValueError('symlink in destination path: ' + str(current))
    return current


def sources():
    files = {}
    for group in ('docs', 'profiles', 'templates'):
        for path in sorted((ROOT / group).rglob('*')):
            if path.is_symlink():
                raise ValueError('source symlink is not supported: ' + str(path))
            if path.is_file():
                name = '.ai-foundation/' + path.relative_to(ROOT).as_posix()
                files[safe_name(name)] = path.read_bytes()
    for skill in sorted((ROOT / 'skills').iterdir()):
        if skill.is_symlink() or not skill.is_dir():
            raise ValueError('unexpected skill entry: ' + str(skill))
        for path in sorted(skill.rglob('*')):
            if path.is_symlink():
                raise ValueError('source symlink is not supported: ' + str(path))
            if path.is_file():
                name = '.agents/skills/' + path.relative_to(ROOT / 'skills').as_posix()
                files[safe_name(name)] = path.read_bytes()
    if not files:
        raise ValueError('no foundation sources found')
    return files


def read_manifest(project):
    path = checked_path(project, MANIFEST)
    if not path.exists():
        if (project / '.ai-foundation').exists():
            raise ValueError('existing .ai-foundation has no manifest; refusing to take ownership')
        return {}
    data = json.loads(path.read_text(encoding='utf-8'))
    if (not isinstance(data, dict) or data.get('schema') != 1 or
            not isinstance(data.get('files'), dict) or not data['files']):
        raise ValueError('invalid or unsupported manifest')
    result = data['files']
    for name, file_hash in result.items():
        safe_name(name)
        if not isinstance(file_hash, str) or not re.fullmatch(r'[a-f0-9]{64}', file_hash):
            raise ValueError('invalid manifest hash: ' + name)
    return result


def revision():
    try:
        commit = subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'],
                                         stderr=subprocess.DEVNULL, text=True).strip()
        return commit
    except (OSError, subprocess.CalledProcessError):
        return None


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
            tmp = Path(handle.name)
            handle.write(data)
        os.replace(tmp, path)
    finally:
        if tmp is not None and tmp.exists():
            tmp.unlink()


def instruction_files(project):
    found = []
    for directory, dirs, names in os.walk(project, followlinks=False):
        dirs[:] = [d for d in dirs if d not in ('.git', '.ai-foundation', 'node_modules', 'vendor', '.venv')
                   and not (Path(directory) / d).is_symlink()]
        for name in names:
            if name in ('AGENTS.md', 'AGENTS.override.md'):
                found.append(str((Path(directory) / name).relative_to(project)))
    return sorted(found)


def install(project, profile):
    project = project.resolve()
    if not project.is_dir():
        raise ValueError('project directory must already exist')
    files = sources()
    old = read_manifest(project)
    existing_instructions = instruction_files(project)
    # Validate every affected path before the first write.
    for name, old_hash in old.items():
        path = checked_path(project, name)
        if not path.is_file() or digest(path.read_bytes()) != old_hash:
            raise ValueError('managed file missing or modified: ' + name)
    old_skill_dirs = {PurePosixPath(name).parts[2] for name in old if name.startswith('.agents/skills/')}
    for name in files:
        path = checked_path(project, name)
        if name not in old and path.exists():
            raise ValueError('unmanaged destination already exists: ' + name)
        parts = PurePosixPath(name).parts
        if parts[:2] == ('.agents', 'skills') and parts[2] not in old_skill_dirs:
            skill_dir = checked_path(project, '/'.join(parts[:3]))
            if skill_dir.exists():
                raise ValueError('unmanaged skill directory already exists: ' + str(skill_dir))
    for name in ('AGENTS.md', '.ai-governance.md', MANIFEST):
        checked_path(project, name)
    config_path = project / '.ai-governance.md'
    existing_config = config_path.read_text(encoding='utf-8') if config_path.exists() else None
    hashes = {name: digest(data) for name, data in sorted(files.items())}
    content_id = digest(json.dumps(hashes, sort_keys=True, separators=(',', ':')).encode())
    manifest = {'schema': 1, 'source_revision': revision(), 'content_sha256': content_id, 'files': hashes}
    for name, data in files.items():
        if old.get(name) != hashes[name]:
            atomic_write(checked_path(project, name), data)
    for name in old.keys() - files.keys():
        checked_path(project, name).unlink()
    if not (project / 'AGENTS.md').exists() and not (project / 'AGENTS.override.md').exists():
        atomic_write(project / 'AGENTS.md', (ROOT / 'templates/project/AGENTS.md').read_bytes())
        print('Created project-owned AGENTS.md.')
    if existing_config is None:
        config = (ROOT / 'templates/project/ai-governance.md').read_text(encoding='utf-8')
        selected = profile or 'baseline'
        atomic_write(project / '.ai-governance.md', config.replace('{{PROFILE}}', selected).encode())
        print('Created project-owned .ai-governance.md with profile:', selected)
    else:
        match = re.search(r'^- Selected profile:\s*(baseline|web-saas|regulated)\b', existing_config, re.M)
        if profile and match and profile != match.group(1):
            print('PROFILE CONFLICT: requested {}, but existing configuration selects {}; '
                  'reconcile manually.'.format(profile, match.group(1)))
        else:
            print('Preserved existing .ai-governance.md; --profile did not change it.')
    atomic_write(checked_path(project, MANIFEST), (json.dumps(manifest, indent=2, sort_keys=True) + '\n').encode())
    print('Installed content SHA-256:', content_id)
    print('Existing instruction files to review:', ', '.join(existing_instructions) or '(none)')
    print('Review active and nested instructions, resolve conflicts, and complete .ai-governance.md.')
    if existing_instructions:
        print('If the active instruction file lacks the foundation link, add the line from README.md manually.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project', type=Path)
    parser.add_argument('--profile', choices=PROFILES)
    args = parser.parse_args()
    try:
        install(args.project, args.profile)
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print('Installation stopped:', exc, file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
