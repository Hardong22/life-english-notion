"""Check release files and optionally reachable Git history; not a complete audit."""
import argparse
from pathlib import Path
import re
import subprocess
import sys

FILES = (
    '.gitignore', 'LICENSE', 'README.md', 'README.en.md', 'SKILL.md',
    'agents/openai.yaml', 'preferences.example.md', 'references/conversation.md',
    'references/review.md', 'references/notion.md', 'docs/DESIGN.md',
    'docs/DESIGN.en.md', 'docs/BEHAVIOR.md', 'docs/BEHAVIOR.en.md',
    'scripts/check_project.py', 'tests/test_check_project.py',
    'docs/images/vocabulary-card.webp', 'docs/images/story-review.webp',
    'docs/images/video-library.webp', 'docs/images/video-records.webp',
    'docs/images/writing-practice.webp',
)


def image_problem(data):
    """Screenshots must be WebP without EXIF or XMP chunks, which can carry personal data."""
    if data[:4] != b'RIFF' or data[8:12] != b'WEBP':
        return 'not a WebP image'
    pos = 12
    while pos + 8 <= len(data):
        if data[pos:pos + 4] in (b'EXIF', b'XMP '):
            return 'image metadata (EXIF/XMP)'
        size = int.from_bytes(data[pos + 4:pos + 8], 'little')
        pos += 8 + size + (size & 1)
    return None


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
                blob = git(root, 'cat-file', 'blob', sha.decode())
                if path.endswith('.webp'):
                    if problem := image_problem(blob):
                        errors.append(f'{commit[:8]}: {problem} in historical file')
                elif private_content(blob.decode('utf-8', errors='replace')):
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
        if name.endswith('.webp'):
            if problem := image_problem(path.read_bytes()):
                errors.append(f'{name}: {problem}')
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
        content = skill.read_text(encoding='utf-8')
        if not re.match(r'\A---\nname: life-english-notion\ndescription: [^\n]+\n---\n', content):
            errors.append('SKILL.md: invalid entry metadata')
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
