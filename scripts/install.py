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


def active_instruction(project, fallback_names=()):
    # Override beats regular, and a configured fallback name governs when neither is
    # present. Read-only here: a symlinked file still loads, so it is reported.
    for name in ('AGENTS.override.md', 'AGENTS.md', *fallback_names):
        path = project / name
        if path.is_file():
            return name, path
    return None, None


# Instruction files that load before any project file. Override before regular, the
# same precedence as in a project directory. Existence is checked, never content:
# these are the user's own files, reconciling them is the agent's and the human's
# job, and an installer has no business reading them. The list is not exhaustive and
# the output says so.
GLOBAL_INSTRUCTION_NAMES = ('AGENTS.override.md', 'AGENTS.md', 'instructions.md')


def codex_home():
    """The effective Codex home: CODEX_HOME when set, otherwise ~/.codex."""
    configured = os.environ.get('CODEX_HOME')
    if configured:
        return Path(configured).expanduser()
    try:
        return Path.home() / '.codex'
    except RuntimeError:
        return None


def global_instruction_files():
    # A symlinked instruction file still loads, so it is reported. Writing through a
    # symlink stays forbidden; that protection lives at the write sites.
    home = codex_home()
    if home is None:
        return []
    return [home / name for name in GLOBAL_INSTRUCTION_NAMES
            if (home / name).is_file() or (home / name).is_symlink()]


FALLBACK_KEY = 'project_doc_fallback_filenames'


def strip_toml_comment(line):
    """Drop a trailing TOML comment, honouring quoted strings.

    A comment can contain `]`, so cutting the line at the first bracket silently
    truncates a multi-line list and loses the names after it.
    """
    out, quote = [], None
    for char in line:
        if quote is not None:
            out.append(char)
            if char == quote:
                quote = None
        elif char in '"\'':
            quote = char
            out.append(char)
        elif char == '#':
            break
        else:
            out.append(char)
    return ''.join(out)


def scan_fallback_declarations(text):
    """Find the fallback key per table without a TOML parser.

    Returns (root_names, profile_names, uncertain). Table awareness matters: a
    declaration under `[profiles.<name>]` applies only when that profile is
    selected, which this installer cannot know.
    """
    root, profile, uncertain = [], [], False
    lines = text.splitlines()
    table, index = '', 0
    while index < len(lines):
        line = strip_toml_comment(lines[index])
        header = re.match(r'^\s*\[\[?([^\]]+)\]\]?\s*$', line)
        if header:
            table = header.group(1).strip().strip('"\'')
            index += 1
            continue
        declaration = re.match(r'^\s*' + FALLBACK_KEY + r'\s*=\s*(.*)$', line)
        if declaration is None:
            index += 1
            continue
        buffer = declaration.group(1)
        # A list may span lines; accumulate until its brackets balance.
        while buffer.count('[') > buffer.count(']') and index + 1 < len(lines):
            index += 1
            buffer += ' ' + strip_toml_comment(lines[index])
        target = profile if table.startswith('profiles.') or table == 'profiles' else root
        if '[' in buffer and buffer.count('[') == buffer.count(']'):
            found = [a or b for a, b in re.findall(r'"([^"]*)"|\'([^\']*)\'', buffer)]
            inner = buffer[buffer.index('[') + 1:buffer.rindex(']')]
            if not found and inner.strip():
                uncertain = True
            target.extend(found)
        else:
            # Unterminated, or not a list literal: say so rather than guess.
            uncertain = True
        index += 1
    return root, profile, uncertain


def read_fallback_key(config):
    """Read the fallback key from a TOML file.

    Returns (root_names, profile_names, uncertain). `uncertain` means the file may
    declare names that could not be read with confidence; treating that as "no
    fallbacks" is the dangerous reading, because it leads to creating an AGENTS.md
    that stops the real instruction file loading.
    """
    if not config.is_file():
        return [], [], False
    try:
        text = config.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return [], [], True
    try:
        import tomllib
    except ModuleNotFoundError:
        # Python 3.9 and 3.10 ship no TOML parser and this project adds no
        # dependency, so the key is scanned with table awareness instead.
        return scan_fallback_declarations(text)
    try:
        data = tomllib.loads(text)
    except ValueError:
        return [], [], FALLBACK_KEY in text
    uncertain = False

    def names_from(value):
        nonlocal uncertain
        if value is None:
            return []
        if not isinstance(value, list):
            uncertain = True
            return []
        return [n for n in value if isinstance(n, str)]

    root = names_from(data.get(FALLBACK_KEY))
    profile = []
    profiles = data.get('profiles')
    if isinstance(profiles, dict):
        for body in profiles.values():
            if isinstance(body, dict):
                profile.extend(names_from(body.get(FALLBACK_KEY)))
    return root, profile, uncertain


def fallback_config_sources(project, repo_root):
    """Config files that may declare fallback names, as (path, profile_scoped).

    `codex -p <name>` layers `$CODEX_HOME/<name>.config.toml` over the base user
    config, so each of those files belongs to a profile that may or may not be the
    one selected at runtime. The base config applies always. Project and ancestor
    `.codex/config.toml` are read too; see setup.md for what was measured about them.
    """
    sources = []
    home = codex_home()
    if home is not None:
        sources.append((home / 'config.toml', False))
        try:
            profile_files = sorted(home.glob('*.config.toml'))
        except OSError:
            profile_files = []
        for path in profile_files:
            sources.append((path, True))
    sources.append((project / '.codex' / 'config.toml', False))
    if repo_root is not None and repo_root != project:
        for parent in project.parents:
            sources.append((parent / '.codex' / 'config.toml', False))
            if parent == repo_root:
                break
    return sources


def fallback_instruction_names(project, repo_root):
    """Fallback instruction filenames. Returns (names, profile_only, uncertain).

    Codex reads these when no AGENTS.md is present, so a project can have an active
    instruction file under another name; creating AGENTS.md then stops it loading at
    all. `profile_only` names come from a `[profiles.*]` table and apply only when
    that profile is selected, which this installer cannot determine.
    """
    root_names, profile_names, uncertain = [], [], False
    profile_sources = []
    for config, profile_scoped in fallback_config_sources(project, repo_root):
        found, scoped, unsure = read_fallback_key(config)
        uncertain = uncertain or unsure
        # A key at the top of a profile config file is profile-scoped: it applies
        # only while that profile is the selected one.
        (profile_names if profile_scoped else root_names).extend(found)
        profile_names.extend(scoped)
        if profile_scoped and (found or scoped):
            profile_sources.append(config)

    def clean(values):
        return [n for n in dict.fromkeys(values)
                if n and '/' not in n and n not in ('.', '..')]

    root_names = clean(root_names)
    profile_only = [n for n in clean(profile_names) if n not in root_names]
    return root_names + profile_only, profile_only, uncertain, profile_sources


def git_root(project):
    for candidate in (project, *project.parents):
        if (candidate / '.git').exists():
            return candidate
    return None


def ancestor_instruction_files(project):
    """Instruction files above the project that load before the project's own.

    Codex reads instruction files along the path down to the work, so a file at the
    Git root of a repository that contains this project applies to it. Those are not
    reachable by walking the project, and an unreconciled one is exactly as binding
    as a nested file. Returns the files and the boundary used, or None when no Git
    root was found and the boundary cannot be established.
    """
    root = git_root(project)
    found = []
    if root is None or root == project:
        return found, root
    for parent in project.parents:
        for name in ('AGENTS.override.md', 'AGENTS.md'):
            path = parent / name
            # A symlinked ancestor file still loads, so report it rather than skip it.
            if path.is_file() or path.is_symlink():
                found.append(path)
        if parent == root:
            break
    return found, root


def fallback_instruction_locations(project, names, repo_root):
    """Configured fallback files anywhere they would load: nested and ancestors."""
    found = []
    if not names:
        return found
    for directory, dirs, filenames in os.walk(project, followlinks=False):
        dirs[:] = [d for d in dirs
                   if d not in ('.git', '.ai-foundation', 'node_modules', 'vendor', '.venv')
                   and not (Path(directory) / d).is_symlink()]
        if Path(directory) == project:
            continue
        for name in names:
            if name in filenames:
                found.append(Path(directory) / name)
    # Ancestors are searched only inside the Git boundary. Without one, or when the
    # project is itself the root, there is no applicable ancestor: walking further
    # would let an unrelated file above the repository defer activation here.
    if repo_root is not None and repo_root != project:
        for parent in project.parents:
            for name in names:
                path = parent / name
                if path.is_file() or path.is_symlink():
                    found.append(path)
            if parent == repo_root:
                break
    return found


def preflight_destination(project, name):
    """Validate a destination this run may create, before anything is written.

    `checked_path` refuses a symlink in any component, including a dangling one. Two
    further states would otherwise fail only at write time, after earlier files had
    landed: the destination existing as something that is not a regular file, and a
    parent component existing as a regular file so no directory can be made there.
    """
    path = checked_path(project, name)
    parts = PurePosixPath(name).parts
    for depth in range(1, len(parts)):
        parent = project / Path(*parts[:depth])
        if parent.exists() and not parent.is_dir():
            raise ValueError('parent path is not a directory: ' + '/'.join(parts[:depth]))
    if (path.exists() or path.is_symlink()) and not path.is_file():
        raise ValueError('destination exists and is not a regular file: ' + name)
    return path


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
    ancestors, repo_root = ancestor_instruction_files(project)
    globals_found = global_instruction_files()
    (fallback_names, fallback_profile_only, fallback_uncertain,
     fallback_profile_sources) = fallback_instruction_names(project, repo_root)
    # A configured fallback is an active instruction file under another name, and it
    # loads from the project tree and from ancestors, not only the root. Creating
    # AGENTS.md beside one would stop it loading entirely.
    active_fallbacks = [name for name in fallback_names
                        if (project / name).is_file()]
    # The ancestor search depends on the repository boundary, not on whether any
    # ancestor AGENTS.md happened to be found.
    fallback_elsewhere = fallback_instruction_locations(project, fallback_names, repo_root)
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
    # Decide here what this run may create, then validate every one of those
    # destinations before the first managed file is written. Checking at the write
    # sites instead leaves a partial installation when one of them is unusable.
    root_file_present = any((project / name).is_file() or (project / name).is_symlink()
                            for name in ('AGENTS.md', 'AGENTS.override.md'))
    deferred_activation = not root_file_present and bool(
        existing_instructions or ancestors or globals_found or active_fallbacks
        or fallback_elsewhere or fallback_uncertain)
    create_agents = not root_file_present and not deferred_activation
    config_path = project / '.ai-governance.md'
    existing_config = (config_path.read_text(encoding='utf-8')
                       if config_path.is_file() else None)
    destinations = [MANIFEST]
    if create_agents:
        destinations.append('AGENTS.md')
    if existing_config is None:
        destinations.append('.ai-governance.md')
    # Any project-owned instruction path that exists as something other than a file
    # is refused even when this run would not write it: discovery cannot read it,
    # so proceeding would report a state that is not the real one.
    for name in ('AGENTS.md', 'AGENTS.override.md', '.ai-governance.md'):
        path = project / name
        if (path.exists() or path.is_symlink()) and not path.is_file():
            raise ValueError('project-owned path is not a regular file: ' + name)
    # Every managed destination, not only the project-owned ones: a regular file at
    # .agents/skills or .ai-foundation/docs makes its directory impossible to create
    # and would otherwise surface partway through writing.
    for name in list(files) + destinations:
        preflight_destination(project, name)
    hashes = {name: digest(data) for name, data in sorted(files.items())}
    content_id = digest(json.dumps(hashes, sort_keys=True, separators=(',', ':')).encode())
    manifest = {'schema': 1, 'source_revision': revision(), 'content_sha256': content_id, 'files': hashes}
    for name, data in files.items():
        if old.get(name) != hashes[name]:
            atomic_write(checked_path(project, name), data)
    for name in old.keys() - files.keys():
        checked_path(project, name).unlink()
    # Creating the root instruction file from the template also activates the
    # foundation, because the template carries the link. Only do that when there is
    # nothing to reconcile: activating alongside an unreviewed instruction file would
    # leave the agent holding two authorities, which is the one thing setup must not
    # decide on its own.
    if create_agents:
        atomic_write(checked_path(project, 'AGENTS.md'),
                     (ROOT / 'templates/project/AGENTS.md').read_bytes())
        print('Created project-owned AGENTS.md.')
    if existing_config is None:
        config = (ROOT / 'templates/project/ai-governance.md').read_text(encoding='utf-8')
        selected = profile or 'baseline'
        atomic_write(checked_path(project, '.ai-governance.md'),
                     config.replace('{{PROFILE}}', selected).encode())
        print('Created project-owned .ai-governance.md with profile:', selected)
    else:
        match = re.search(r'^- Selected profile:\s*(baseline|web-saas|regulated)\b', existing_config, re.M)
        if profile and match and profile != match.group(1):
            print('PROFILE CONFLICT: requested {}, but existing configuration selects {}; '
                  'reconcile manually.'.format(profile, match.group(1)))
        else:
            print('Preserved existing .ai-governance.md; --profile did not change it.')
    atomic_write(checked_path(project, MANIFEST), (json.dumps(manifest, indent=2, sort_keys=True) + '\n').encode())
    print('Installed {} managed files; content SHA-256: {}'.format(len(files), content_id))
    print()
    print('FILES INSTALLED - SETUP IS NOT COMPLETE.')
    active, active_path = active_instruction(project, active_fallbacks)
    if active in active_fallbacks:
        print('Active instruction file: {} (configured project_doc_fallback_filenames)'
              .format(active))
        print('  AGENTS.md was NOT created: it would take precedence and stop this')
        print('    file loading at all, silently dropping the rules in it.')
        print('    Add the link to {} instead, after reconciling.'.format(active))
    elif active is None:
        print('Active instruction file: (none at the repository root)')
        if deferred_activation:
            print('  NOT ACTIVATED ON PURPOSE: no root instruction file was created,')
            print('    because instructions that apply to this project are unreconciled')
            print('    - in the project, above it, globally, or under a configured')
            print('    fallback name. Reconcile them first, then create the root file')
            print('    and add the link - see setup.md step 3.')
        else:
            print('  Not connected: no root instruction file to carry the link.')
    else:
        print('Active instruction file:', active)
        active_text = active_path.read_text(encoding='utf-8')
        template_agents = (ROOT / 'templates/project/AGENTS.md').read_text(encoding='utf-8')
        # A mention is evidence to read, not proof of activation: the text may forbid
        # it, quote it, or be a stale note. Only a human reading it can tell. The one
        # case this tool can settle is a file that is still the template it installed.
        if active_text == template_agents:
            print('  Foundation link: present (file is the unmodified template).')
        elif '.ai-governance.md' in active_text:
            print('  Mentions .ai-governance.md: yes - REVIEW the surrounding text.')
            print('    A mention is not proof the foundation is active; confirm it')
            print('    instructs the agent to follow the configuration.')
        else:
            print('  Mentions .ai-governance.md: no - not connected.')
    others = [name for name in existing_instructions if name != active]
    print('In-project instruction files to reconcile:',
          ', '.join(others) or '(none besides the active file)')
    if fallback_names or fallback_uncertain:
        print('Configured fallback instruction filenames:',
              ', '.join(fallback_names) or '(none could be read)')
        print('  At the project root:', ', '.join(active_fallbacks) or '(none)')
        if fallback_profile_only:
            print('  Declared only by a profile:', ', '.join(fallback_profile_only))
            for path in fallback_profile_sources:
                print('    from', path)
            print('    A profile applies only while it is the selected one, which this')
            print('    installer cannot determine, so these are treated as possibly in')
            print('    effect and no AGENTS.md is created beside a file they name.')
        if fallback_elsewhere:
            print('  Elsewhere, where they also load:')
            for path in fallback_elsewhere:
                print('    {}{}'.format(path, '  (symlink)' if path.is_symlink() else ''))
        if fallback_uncertain:
            print('  UNCERTAIN: a Codex config declares this key but it could not be')
            print('    read with confidence here, so activation is deferred rather')
            print('    than assuming there are no fallback names. Read the config and')
            print('    connect by hand, or run the installer on Python 3.11 or newer.')
        print('  Sources read: the base config, each *.config.toml profile beside it,')
        print('    and project and ancestor .codex/config.toml. Which of these your')
        print('    Codex version layers, and which profile is selected, cannot be')
        print('    determined here, so every name found is treated as possibly in')
        print('    effect and none is used to displace an existing file.')
    if ancestors:
        print('Ancestor instruction files above the project (they load first):')
        for path in ancestors:
            print('    {}{}'.format(path, '  (symlink)' if path.is_symlink() else ''))
    elif repo_root is None:
        print('Ancestor instruction files: not determined - no Git root found above')
        print('    this directory, so the boundary to search could not be established.')
    else:
        print('Ancestor instruction files: (none up to the Git root)')
    if globals_found:
        print('Global instruction candidates in {} (they load before any project file):'
              .format(codex_home()))
        has_override = any(path.name == 'AGENTS.override.md' for path in globals_found)
        for path in globals_found:
            marks = []
            if path.is_symlink():
                marks.append('symlink')
            if path.name == 'AGENTS.override.md':
                marks.append('override: the one Codex loads')
            elif has_override:
                marks.append('likely NOT loaded, superseded by the override')
            print('    {}{}'.format(path, '  ({})'.format('; '.join(marks)) if marks else ''))
        if has_override and len(globals_found) > 1:
            print('  Codex may load only the override, so reconcile that one first and')
            print('    confirm which the environment actually loads before relying on either.')
    else:
        print('Global instruction files: none in {}'.format(
            codex_home() or '(no Codex home could be determined)'))
    print('  Paths only; contents are not read here. Other tool-level instructions may')
    print('  load from elsewhere, so this list is not exhaustive - confirm what your')
    print('  environment actually loads.')
    print('  Reconcile all of the above against the foundation BEFORE activating it;')
    print('  activating into a conflict gives the agent two authorities.')
    print()
    print('Next: follow .ai-foundation/docs/agent-governance/setup.md, or run')
    print('  $foundation-setup, which needs no checkout path once installed.')
    print()
    print('Review, then commit when you decide to - this does not commit for you:')
    print('  .ai-foundation/  .agents/skills/foundation-*/  {}  .ai-governance.md'.format(
        active or 'AGENTS.md'))
    print('  Name the foundation skills, not all of .agents/skills/, which may hold')
    print('  skills this project owns. Committing pins the installed version, so the')
    print('  next update is a reviewable diff, the hash check can tell a local edit')
    print('  from an upstream change, and a lost install is recoverable from Git.')


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
