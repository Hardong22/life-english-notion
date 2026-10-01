"""Check release files and optionally reachable Git history; not a complete audit."""
import argparse
from pathlib import Path
import re
import subprocess
import sys

FILES = (
    '.github/workflows/check.yml', '.gitignore', 'LICENSE', 'README.md', 'README.en.md',
    'SKILL.md', 'agents/openai.yaml', 'preferences.example.md',
    'references/conversation.md', 'references/review.md', 'references/notion.md',
    'docs/DESIGN.md', 'docs/DESIGN.en.md', 'docs/BEHAVIOR.md', 'docs/BEHAVIOR.en.md',
    'scripts/check_project.py', 'tests/test_check_project.py',
)
SKILL_NAME = 'life-english-notion'
# Front matter fields defined by the Agent Skills format and their length limits.
FRONT_MATTER_KEYS = ('name', 'description', 'license', 'compatibility', 'metadata', 'allowed-tools')
FRONT_MATTER_LIMITS = {'description': 1024, 'compatibility': 500}


def private_content(content):
    patterns = (
        r'/(?:Users|home)/[^\s/]+/',
        r'https://[^\s)]*notion\.(?:so|site)/',
        r'gh[pousr]_[A-Za-z0-9]{30,}', r'github_pat_[A-Za-z0-9_]{30,}',
        r'(?:sk|secret|ntn)[_-][A-Za-z0-9_-]{24,}',
        r'-----BEGIN [A-Z ]*PRIVATE KEY-----',
    )
    if any(re.search(pattern, content) for pattern in patterns):
        return True
    for email in re.findall(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', content):
        if not safe_email(email):
            return True
    return False


def safe_email(email):
    """GitHub privacy addresses and no-reply bot addresses carry no personal data."""
    return bool(re.fullmatch(r'[\w.+-]+@users\.noreply\.github\.com|no-?reply@[\w.-]+',
                             email, re.IGNORECASE))


def check_skill(content):
    """Validate SKILL.md front matter: required name/description, known fields, limits."""
    match = re.match(r'\A---\n(.*?)\n---\n', content, re.DOTALL)
    if not match:
        return ['SKILL.md: missing front matter metadata']
    errors = []
    fields = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line[0] in ' \t#':
            continue  # nested values of metadata and comments
        key, sep, value = line.partition(':')
        if not sep or key not in FRONT_MATTER_KEYS:
            errors.append(f'SKILL.md: unexpected front matter line {line!r}')
            continue
        value = value.strip()
        if len(value) > 1 and value[0] == value[-1] and value[0] in '"\'':
            value = value[1:-1]
        fields[key] = value
    if fields.get('name') != SKILL_NAME:
        errors.append(f'SKILL.md: name must be {SKILL_NAME}')
    if not fields.get('description'):
        errors.append('SKILL.md: description is required')
    for key, limit in FRONT_MATTER_LIMITS.items():
        if len(fields.get(key, '')) > limit:
            errors.append(f'SKILL.md: {key} exceeds {limit} characters')
    return errors


def git(root, *args):
    return subprocess.run(['git', '-C', str(root), *args], check=True,
                          capture_output=True).stdout


def check_history(root):
    errors = []
    commits = git(root, 'rev-list', '--branches', '--tags').decode().splitlines()
    seen = set()
    for commit in commits:
        identities = git(root, 'show', '-s', '--format=%ae%n%ce', commit).decode().splitlines()
        if any(not safe_email(email) for email in identities):
            errors.append(f'{commit[:8]}: commit identity is not a GitHub privacy address')
        message = git(root, 'show', '-s', '--format=%B', commit).decode()
        if private_content(message):
            errors.append(f'{commit[:8]}: possible private data in commit message')
        for item in git(root, 'ls-tree', '-rz', commit).split(b'\0'):
            if not item:
                continue
            meta, name = item.split(b'\t', 1)
            mode, kind, sha = meta.split()
            path = name.decode()
            if path not in FILES or mode != b'100644':
                errors.append(f'{commit[:8]}: historical file outside release policy')
            if kind == b'blob' and sha not in seen:
                seen.add(sha)
                content = git(root, 'cat-file', 'blob', sha.decode()).decode('utf-8', errors='replace')
                if private_content(content):
                    errors.append(f'{commit[:8]}: possible private data in historical file')
    return errors


def check(root, history=False):
    root = Path(root).resolve()
    errors = []
    for name in FILES:
        path = root / name
        if not path.resolve().is_relative_to(root) or path.is_symlink() or not path.is_file():
            errors.append(f'{name}: missing file or symlink')
            continue
        content = path.read_text(encoding='utf-8')
        if private_content(content):
            errors.append(f'{name}: possible private data')
        if name.endswith('.md'):
            for target in re.findall(r'\[[^\]]*\]\(([^\s)]+)\)', content):
                if re.match(r'https?://|#', target):
                    continue
                linked = (path.parent / target.split('#')[0]).resolve()
                if not linked.is_relative_to(root) or not linked.exists():
                    errors.append(f'{name}: invalid local link {target}')
    skill = root / 'SKILL.md'
    if skill.is_file() and not skill.is_symlink():
        errors.extend(check_skill(skill.read_text(encoding='utf-8')))
    if (root / '.git').exists():
        tracked = git(root, 'ls-files', '-z').decode().split('\0')
        if any(name and name not in FILES for name in tracked):
            errors.append('Git tracks files outside the release manifest')
        if history:
            errors.extend(check_history(root))
    elif history:
        errors.append('History check requires a Git checkout at the project root')
    return errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--history', action='store_true')
    args = parser.parse_args()
    problems = check(Path(__file__).resolve().parents[1], history=args.history)
    print('\n'.join(problems) if problems else f'OK: {len(FILES)} public files checked')
    sys.exit(bool(problems))
