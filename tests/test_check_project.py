"""Synthetic packaging regressions; no private conversations."""
from pathlib import Path
import shutil
import sys
import subprocess
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from check_project import FILES, check

IMAGE = next(name for name in FILES if name.endswith('.webp'))


def webp(*chunks):
    """Build a minimal RIFF/WebP container from (chunk id, payload) pairs."""
    body = b'WEBP' + b''.join(kind + len(data).to_bytes(4, 'little') + data + bytes(len(data) & 1)
                              for kind, data in chunks)
    return b'RIFF' + len(body).to_bytes(4, 'little') + body


class PackageChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        source = Path(__file__).resolve().parents[1]
        for name in FILES:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / name, target)

    def append(self, text):
        with (self.root / 'README.md').open('a', encoding='utf-8') as stream:
            stream.write(text)

    def test_valid_package(self):
        self.assertEqual(check(self.root), [])

    def test_missing_file(self):
        (self.root / 'LICENSE').unlink()
        self.assertTrue(any('missing' in error for error in check(self.root)))

    def test_broken_link(self):
        self.append('\n[missing](missing.md)')
        self.assertTrue(any('invalid local link' in error for error in check(self.root)))

    def test_outside_link(self):
        self.append('\n[outside](../outside.md)')
        self.assertTrue(any('invalid local link' in error for error in check(self.root)))

    def test_private_path(self):
        self.append('\n' + '/Users/' + 'example/private.txt')
        self.assertTrue(any('private data' in error for error in check(self.root)))

    def test_invalid_entry(self):
        (self.root / 'SKILL.md').write_text('not a skill', encoding='utf-8')
        self.assertTrue(any('metadata' in error for error in check(self.root)))

    def test_symlink(self):
        (self.root / 'LICENSE').unlink()
        (self.root / 'LICENSE').symlink_to(self.root / 'README.md')
        self.assertTrue(any('symlink' in error for error in check(self.root)))


    def test_email_in_yaml(self):
        (self.root / 'agents/openai.yaml').write_text('contact: ' + 'person' + '@' + 'example.com')
        self.assertTrue(any('private data' in error for error in check(self.root)))

    def test_token_in_script(self):
        (self.root / 'scripts/check_project.py').write_text('token = ' + 'github_' + 'pat_' + 'x' * 40)
        self.assertTrue(any('private data' in error for error in check(self.root)))

    def test_clean_image(self):
        (self.root / IMAGE).write_bytes(webp((b'VP8X', bytes(10)), (b'ICCP', bytes(3)), (b'VP8 ', bytes(9))))
        self.assertEqual(check(self.root), [])

    def test_image_metadata(self):
        # The odd-sized chunk before EXIF checks that padding keeps the parser aligned.
        (self.root / IMAGE).write_bytes(webp((b'ICCP', bytes(3)), (b'EXIF', b'Exif\0\0synthetic')))
        self.assertTrue(any('metadata' in error for error in check(self.root)))

    def test_image_not_webp(self):
        (self.root / IMAGE).write_text('not an image')
        self.assertTrue(any('not a WebP' in error for error in check(self.root)))

    def run_git(self, *args):
        return subprocess.run(['git', '-C', str(self.root), *args], check=True, capture_output=True)

    def commit(self, email, message='Synthetic fixture'):
        self.run_git('-c', 'user.name=Example', '-c', 'user.email=' + email,
                     '-c', 'commit.gpgsign=false', 'commit', '-m', message)

    def test_tracked_private_file(self):
        self.run_git('init', '-b', 'main')
        (self.root / 'preferences.local.md').write_text('private settings')
        self.run_git('add', '-f', 'preferences.local.md')
        self.assertTrue(any('outside the release' in error for error in check(self.root)))

    def test_commit_email_history(self):
        self.run_git('init', '-b', 'main')
        self.run_git('add', 'README.md')
        self.commit('person' + '@' + 'example.com')
        self.assertTrue(any('commit identity' in error for error in check(self.root, history=True)))

    def test_clean_history(self):
        self.run_git('init', '-b', 'main')
        self.run_git('add', 'README.md')
        self.commit('123+example' + '@users.noreply.github.com')
        self.assertEqual(check(self.root, history=True), [])

    def test_noreply_bot_identity(self):
        self.run_git('init', '-b', 'main')
        self.run_git('add', 'README.md')
        self.commit('noreply@github.com',
                    'Synthetic fixture\n\nCo-Authored-By: Bot <no-reply@example.com>')
        self.assertEqual(check(self.root, history=True), [])

    def test_private_data_in_deleted_file(self):
        self.run_git('init', '-b', 'main')
        (self.root / 'README.md').write_text('person' + '@' + 'example.com')
        self.run_git('add', 'README.md')
        self.commit('123+example' + '@users.noreply.github.com')
        (self.root / 'README.md').write_text('Clean current file')
        self.run_git('add', 'README.md')
        self.commit('123+example' + '@users.noreply.github.com')
        self.assertTrue(any('historical file' in error for error in check(self.root, history=True)))

    def test_image_metadata_in_history(self):
        self.run_git('init', '-b', 'main')
        (self.root / IMAGE).write_bytes(webp((b'XMP ', b'<x:xmpmeta/>')))
        self.run_git('add', IMAGE)
        self.commit('123+example' + '@users.noreply.github.com')
        (self.root / IMAGE).write_bytes(webp((b'VP8 ', bytes(9))))
        self.run_git('add', IMAGE)
        self.commit('123+example' + '@users.noreply.github.com')
        self.assertEqual(check(self.root), [])
        self.assertTrue(any('metadata' in error for error in check(self.root, history=True)))


if __name__ == '__main__':
    unittest.main()
