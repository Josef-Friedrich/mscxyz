"""Test module “lyrics.py”."""


from mscxyz import rename
import helper
from helper import ini_file
import mscxyz
import os
import tempfile
import unittest


class TestFunctions(unittest.TestCase):

    def test_function_prepare_fields(self):
        fields = {
            'field1': ' Subtitle ',
            'field2': 'Title / Composer',
        }
        result = rename.prepare_fields(fields)
        self.assertEqual(result, {
            'field1': 'Subtitle',
            'field2': 'Title - Composer',
        })

    def test_function_apply_format_string(self):
        from mscxyz import settings
        settings.args = settings.DefaultArguments()
        meta = mscxyz.meta.Meta(
            helper.get_tmpfile_path('meta-all-values.mscx'))
        fields = meta.interface.export_to_dict()
        name = rename.apply_format_string(fields)
        self.assertEqual(name, 'vbox_title (vbox_composer)')

    def test_function_get_checksum(self):
        tmp = helper.get_tmpfile_path('simple.mscx')
        self.assertEqual(rename.get_checksum(tmp),
                         'dacd912aa0f6a1a67c3b13bb947395509e19dce2')


class TestIntegration(unittest.TestCase):

    @staticmethod
    def _get(filename, version=2):
        return helper.get_tmpfile_path(filename, version)

    @staticmethod
    def _target_path_cwd(filename):
        return os.path.join(os.getcwd(), filename)

    @staticmethod
    def _execute(args):
        with helper.Capturing() as output:
            mscxyz.execute(args)
        return output

    @staticmethod
    def _exists_in_cwd(filename):
        return os.path.exists(os.path.join(os.getcwd(), filename))

    @staticmethod
    def _rm_in_cwd(filename):
        return os.remove(os.path.join(os.getcwd(), filename))

    def _test_simple(self, version):
        output = self._execute(['--config-file', ini_file, 'rename',
                                self._get('simple.mscx', version)])
        target = self._target_path_cwd('Title (Composer).mscx')
        self.assertTrue(os.path.exists(target))
        self.assertTrue('simple.mscx -> ' in ' '.join(output))
        self.assertTrue('Title (Composer).mscx' in ' '.join(output))
        os.remove(target)

    def test_simple(self):
        self._test_simple(version=2)
        self._test_simple(version=3)

    def _test_without_arguments(self, version):
        output = self._execute(['rename', self._get('meta-all-values.mscx',
                               version)])
        target = self._target_path_cwd('vbox_title (vbox_composer).mscx')
        self.assertTrue(os.path.exists(target))
        self.assertTrue('vbox_title (vbox_composer).mscx' in ' '.join(output))
        os.remove(target)

    def test_without_arguments(self):
        self._test_without_arguments(version=2)
        self._test_without_arguments(version=3)

    def test_format(self):
        output = self._execute(['rename', '--format',
                                '${vbox_composer}_${vbox_title}',
                                self._get('simple.mscx')])
        target = self._target_path_cwd('Composer_Title.mscx')
        self.assertTrue(os.path.exists(target))
        self.assertTrue('Composer_Title.mscx' in ' '.join(output))
        os.remove(target)

    def test_no_whitespace(self):
        output = self._execute(['rename', '--no-whitespace',
                                self._get('meta-real-world.mscx')])
        n = 'Wir-sind-des-Geyers-schwarze-Haufen (Florian-Geyer).mscx'
        target = self._target_path_cwd(n)
        self.assertTrue(os.path.exists(target))
        self.assertTrue(n in ' '.join(output))
        os.remove(target)

    def test_alphanum(self):
        output = helper.run('rename', '--alphanum',
                            self._get('meta-all-values.mscx'))
        target = self._target_path_cwd('vbox title (vbox composer).mscx')
        self.assertTrue(os.path.exists(target))
        self.assertTrue('vbox title (vbox composer).mscx' in output)
        os.remove(target)

    def test_ascii(self):
        output = helper.run('rename', '--ascii', self._get('unicode.mscx'))
        target = self._target_path_cwd('Tuetlae (Coempoesser).mscx')
        self.assertTrue(os.path.exists(target))
        self.assertTrue('Tuetlae (Coempoesser).mscx' in output)
        os.remove(target)

    def test_rename_file_twice(self):
        helper.run('rename', self._get('simple.mscx'))
        output = helper.run('rename', self._get('simple.mscx'))
        target = self._target_path_cwd('Title (Composer).mscx')
        self.assertTrue('with the same checksum (sha1) already' in output)
        os.remove(target)

    def test_rename_same_filename(self):
        helper.run('rename', '-f', 'same', self._get('simple.mscx'))
        helper.run('rename', '-f', 'same', self._get('lyrics.mscx'))
        helper.run('rename', '-f', 'same', self._get('no-vbox.mscx'))
        self.assertTrue(self._exists_in_cwd('same.mscx'))
        self.assertFalse(self._exists_in_cwd('same1.mscx'))
        self.assertTrue(self._exists_in_cwd('same2.mscx'))
        self.assertTrue(self._exists_in_cwd('same3.mscx'))
        self._rm_in_cwd('same.mscx')
        self._rm_in_cwd('same2.mscx')
        self._rm_in_cwd('same3.mscx')

    def test_rename_skips(self):
        output = helper.run('rename', '--skip-if-empty',
                            'metatag_composer,metatag_source',
                            self._get('simple.mscx'))
        self.assertTrue('Field “metatag_source” is empty! Skipping' in output)

    def test_rename_skip_pass(self):
        output = helper.run('--config-file', ini_file, 'rename',
                            '--skip-if-empty',
                            'metatag_composer,metatag_work_title',
                            self._get('simple.mscx'))
        target = self._target_path_cwd('Title (Composer).mscx')
        self.assertTrue(os.path.exists(target))
        self.assertTrue('simple.mscx -> ' in output)
        self.assertTrue('Title (Composer).mscx' in output)
        os.remove(target)

    def test_rename_target(self):
        tmp_dir = tempfile.mkdtemp()
        helper.run('rename', '--target', tmp_dir, self._get('simple.mscx'))
        target = os.path.join(tmp_dir, 'Title (Composer).mscx')
        self.assertTrue(os.path.exists(target))
        os.remove(target)


if __name__ == '__main__':
    unittest.main()
