import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'versionamiento.py'
spec = importlib.util.spec_from_file_location('versionamiento', SCRIPT)
versionamiento = importlib.util.module_from_spec(spec)
spec.loader.exec_module(versionamiento)


class FormatTests(unittest.TestCase):
    def test_valid_keywords_and_alias(self):
        for subject, kind in [('feat(auth): high [1.0.0] romper contrato', 'high'),
                              ('feat: LOW [0.1.0] funcionalidad', 'low'),
                              ('fix: parch [0.0.1] reparar', 'parch'),
                              ('fix(ui): patch [0.0.1] reparar', 'patch')]:
            self.assertEqual(versionamiento.keyword(subject), kind)

    def test_unversioned_and_bot_subjects_ignored(self):
        self.assertIsNone(versionamiento.keyword('docs: actualizar guía'))
        self.assertIsNone(versionamiento.keyword('feat: highlight catálogo'))
        self.assertIsNone(versionamiento.keyword('chore(version-bump): 5.1.0 (origen: feat: low [0.1.0] ejemplo)'))

    def test_malformed_or_incoherent_declarations_fail(self):
        for subject in ['feat: low [5.1.0] feature', 'fix: parch [1.0.0] bug',
                        'feat: high [1.0] cambio', 'feat: low falta etiqueta',
                        'low [0.1.0] sin tipo', 'feat: patch [0.0.1]']:
            with self.subTest(subject=subject), self.assertRaises(ValueError):
                versionamiento.keyword(subject)

    def test_increment_resets_correct_segments(self):
        self.assertEqual(versionamiento.increment('3.12.4', 'high'), '4.0.0')
        self.assertEqual(versionamiento.increment('3.12.4', 'low'), '3.13.0')
        self.assertEqual(versionamiento.increment('3.12.4', 'patch'), '3.12.5')


class GitIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='amazon-version-test-')
        self.root = Path(self.temp.name)
        self.env = dict(os.environ, GIT_AUTHOR_NAME='Test', GIT_AUTHOR_EMAIL='test@example.test',
                        GIT_COMMITTER_NAME='Test', GIT_COMMITTER_EMAIL='test@example.test')
        self.env.pop('GITHUB_OUTPUT', None)
        self.git('init', '-b', 'main')
        (self.root / 'VERSION').write_text('5.0.0\n')
        (self.root / 'README.md').write_text('# Proyecto\n\nVersión: **5.0.0**\n')
        (self.root / 'CHANGELOG.md').write_text('# Changelog\n\n### 5.0.0 — Histórico\n\nHistorial preservado.\n')
        frontend = self.root / 'frontend_project'
        frontend.mkdir()
        (frontend / 'package.json').write_text(json.dumps({'name': 'fixture', 'version': '5.0.0'}))
        (frontend / 'package-lock.json').write_text(json.dumps({'version': '5.0.0', 'packages': {'': {'version': '5.0.0'}}}))
        self.git('add', '.')
        self.git('commit', '-m', 'chore: base existente')
        self.base = self.git('rev-parse', 'HEAD')

    def tearDown(self):
        self.temp.cleanup()

    def git(self, *args):
        return subprocess.check_output(['git', *args], cwd=self.root, env=self.env, text=True, stderr=subprocess.DEVNULL).strip()

    def commit(self, subject):
        self.git('commit', '--allow-empty', '-m', subject)
        return self.git('rev-parse', 'HEAD')

    def run_script(self, mode, before=None, after=None, *extra):
        command = ['python3', str(SCRIPT), mode]
        if mode != 'check':
            command += ['--before', before or self.base, '--after', after or self.git('rev-parse', 'HEAD')]
        result = subprocess.run(command + list(extra), cwd=self.root, env=self.env, text=True, capture_output=True)
        return result

    def test_batch_order_tags_sync_and_rerun(self):
        origins = [self.commit('feat(api): low [0.1.0] una función'),
                   self.commit('docs: aclarar instrucciones'),
                   self.commit('fix(auth): parch [0.0.1] reparar acceso'),
                   self.commit('feat: high [1.0.0] nueva arquitectura')]
        after = origins[-1]
        result = self.run_script('bump', after=after)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git('tag').splitlines(), ['v5.1.0', 'v5.1.1', 'v6.0.0'])
        for tag, original in zip(['v5.1.0', 'v5.1.1', 'v6.0.0'], [origins[0], origins[2], origins[3]]):
            self.assertEqual(self.git('cat-file', '-t', tag), 'tag')
            self.assertIn(original, self.git('show', '-s', '--format=%B', tag + '^{}'))
        self.assertEqual(self.run_script('check').returncode, 0)
        self.assertIn('Versión: **6.0.0**', (self.root / 'README.md').read_text())
        self.assertIn('Historial preservado.', (self.root / 'CHANGELOG.md').read_text())
        head = self.git('rev-parse', 'HEAD')
        self.assertEqual(self.run_script('bump', after=after).returncode, 0)
        self.assertEqual(self.git('rev-parse', 'HEAD'), head)

    def test_initial_release_starts_at_five_and_patch_is_idempotent(self):
        after = self.commit('chore(versioning): parch [0.0.1] probar automatización')
        result = self.run_script('bump', None, after, '--initial-version', '5.0.0')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.git('tag').splitlines(), ['v5.0.0', 'v5.0.1'])
        self.assertEqual(self.git('cat-file', '-t', 'v5.0.0'), 'tag')
        self.assertEqual(self.git('rev-parse', 'v5.0.0^{}'), after)
        self.assertEqual(self.git('show', 'v5.0.0:VERSION'), '5.0.0')
        self.assertEqual(self.git('show', 'v5.0.1:VERSION'), '5.0.1')
        head = self.git('rev-parse', 'HEAD')
        self.assertEqual(self.run_script('bump', None, after, '--initial-version', '5.0.0').returncode, 0)
        self.assertEqual(self.git('rev-parse', 'HEAD'), head)

    def test_initial_tag_is_not_created_for_invalid_batch(self):
        after = self.commit('fix: patch [1.0.0] incoherente')
        self.assertNotEqual(self.run_script('bump', None, after, '--initial-version', '5.0.0').returncode, 0)
        self.assertEqual(self.git('tag'), '')

    def test_initial_push_and_missing_version(self):
        (self.root / 'VERSION').unlink()
        self.git('add', 'VERSION')
        self.git('commit', '-m', 'chore: retirar versión de fixture')
        after = self.commit('feat: high [1.0.0] comienzo')
        result = self.run_script('bump', '0' * 40, after)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.root / 'VERSION').read_text(), '1.0.0\n')

    def test_standard_batch_makes_no_commits(self):
        after = self.commit('docs: actualizar documentación')
        self.assertEqual(self.run_script('bump', after=after).returncode, 0)
        self.assertEqual(self.git('rev-parse', 'HEAD'), after)
        self.assertEqual(self.git('tag'), '')

    def test_invalid_batch_does_not_partially_version(self):
        self.commit('feat: low [0.1.0] válido')
        after = self.commit('fix: patch [1.0.0] incoherente')
        result = self.run_script('bump', after=after)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.git('rev-parse', 'HEAD'), after)
        self.assertEqual(self.git('tag'), '')
        self.assertNotEqual(self.run_script('lint', after=after).returncode, 0)

    def test_corrupt_version_fails_before_mutation(self):
        for value in ['5. 0.0', '05.0.0', 'texto']:
            (self.root / 'VERSION').write_text(value)
            self.git('add', 'VERSION')
            self.git('commit', '-m', 'chore: alterar fixture')
            after = self.commit('fix: patch [0.0.1] prueba')
            self.assertNotEqual(self.run_script('bump', after=after).returncode, 0)
            self.assertEqual(self.git('rev-parse', 'HEAD'), after)
            self.assertEqual(self.git('tag'), '')

    def test_existing_tag_never_overwritten(self):
        self.git('tag', '-a', 'v5.1.0', '-m', 'tag ya publicado')
        tag_sha = self.git('rev-parse', 'v5.1.0')
        after = self.commit('feat: low [0.1.0] feature')
        self.assertNotEqual(self.run_script('bump', after=after).returncode, 0)
        self.assertEqual(self.git('rev-parse', 'HEAD'), after)
        self.assertEqual(self.git('rev-parse', 'v5.1.0'), tag_sha)

    def test_dirty_checkout_and_feature_branch_rejected(self):
        after = self.commit('feat: low [0.1.0] feature')
        (self.root / 'untracked').write_text('cambio')
        self.assertNotEqual(self.run_script('bump', after=after).returncode, 0)
        (self.root / 'untracked').unlink()
        self.assertNotEqual(self.run_script('bump', None, after, '--branch', 'feature/test').returncode, 0)

    def test_non_fast_forward_range_fails(self):
        self.git('checkout', '-b', 'side')
        before = self.commit('docs: rama paralela')
        self.git('checkout', 'main')
        after = self.commit('feat: low [0.1.0] función')
        self.assertNotEqual(self.run_script('bump', before, after).returncode, 0)
        self.assertEqual(self.git('tag'), '')

    def test_merge_commit_preserves_individual_versions(self):
        self.git('checkout', '-b', 'feature')
        first = self.commit('feat: low [0.1.0] módulo')
        second = self.commit('fix: parch [0.0.1] ajuste')
        self.git('checkout', 'main')
        self.git('merge', '--no-ff', 'feature', '-m', 'Merge feature')
        after = self.git('rev-parse', 'HEAD')
        self.assertEqual(self.run_script('lint', after=after).returncode, 0)
        self.assertEqual(self.run_script('bump', after=after).returncode, 0)
        self.assertEqual(self.git('tag').splitlines(), ['v5.1.0', 'v5.1.1'])
        self.assertIn(first, self.git('show', '-s', '--format=%B', 'v5.1.0^{}'))
        self.assertIn(second, self.git('show', '-s', '--format=%B', 'v5.1.1^{}'))

    def test_subject_is_data_not_shell_code(self):
        after = self.commit('feat: low [0.1.0] $(touch EXPUESTO) `touch EXPUESTO2`')
        self.assertEqual(self.run_script('bump', after=after).returncode, 0)
        self.assertFalse((self.root / 'EXPUESTO').exists())
        self.assertFalse((self.root / 'EXPUESTO2').exists())

    def test_atomic_push_only_publishes_generated_tags(self):
        with tempfile.TemporaryDirectory(prefix='amazon-version-remote-') as destination:
            subprocess.run(['git', 'init', '--bare', destination], capture_output=True, check=True)
            self.git('remote', 'add', 'origin', destination)
            self.git('push', 'origin', 'main')
            self.git('tag', '-a', 'private-fixture', '-m', 'no publicar')
            after = self.commit('feat: low [0.1.0] feature')
            result = self.run_script('bump', None, after, '--initial-version', '5.0.0', '--push')
            self.assertEqual(result.returncode, 0, result.stderr)
            refs = self.git('ls-remote', 'origin', 'refs/tags/*')
            self.assertIn('refs/tags/v5.0.0', refs)
            self.assertIn('refs/tags/v5.1.0', refs)
            self.assertNotIn('private-fixture', refs)
            self.assertIn(self.git('rev-parse', 'HEAD'), self.git('ls-remote', 'origin', 'refs/heads/main'))


if __name__ == '__main__':
    unittest.main()
