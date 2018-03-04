# -*- coding: utf-8 -*-

"""Test module “lyrics.py”."""


import helper
import unittest
from mscxyz import rename
import mscxyz
import os
import tempfile


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

    def test_function_clean_up(self):
        clean = rename.clean_up
        self.assertEqual(clean('-abc-'), 'abc')
        self.assertEqual(clean('a-b-c'), 'a-b-c')
        self.assertEqual(clean('a--b'), 'a_b')
        self.assertEqual(clean('a---b'), 'a_b')
        self.assertEqual(clean('a__b'), 'a_b')
        self.assertEqual(clean('a___b'), 'a_b')

    def test_function_apply_format_string(self):
        from mscxyz import settings
        settings.args = settings.DefaultArguments()
        meta = mscxyz.meta.Meta(
            helper.get_tmpfile_path('meta-all-values.mscx'))
        fields = meta.interface.export_to_dict()
        name = rename.apply_format_string(fields)
        self.assertEqual(name, 'vbox_title (vbox_composer)')

    def test_function_format_filename(self):
        from mscxyz import settings
        settings.args = settings.DefaultArguments()
        settings.args.rename_ascii = True
        settings.args.rename_no_whitespace = True

        f = rename.format_filename
        self.assertEqual(f('  Löl   '), 'Loel')
        self.assertEqual(f('folder/file'), 'folder/file')

    def test_function_get_checksum(self):
        tmp = helper.get_tmpfile_path('simple.mscx')
        self.assertEqual(rename.get_checksum(tmp),
                         'dacd912aa0f6a1a67c3b13bb947395509e19dce2')


class TestIntegration(unittest.TestCase):

    @staticmethod
    def _get(filename):
        return helper.get_tmpfile_path(filename)

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

    def test_simple(self):
        output = self._execute(['rename', self._get('simple.mscx')])
        target = self._target_path_cwd('Title (Composer).mscx')
        self.assertTrue(os.path.exists(target))
        self.assertTrue('simple.mscx -> ' in ' '.join(output))
        self.assertTrue('Title (Composer).mscx' in ' '.join(output))
        os.remove(target)

    def test_without_arguments(self):
        output = self._execute(['rename', self._get('meta-all-values.mscx')])
        target = self._target_path_cwd('vbox_title (vbox_composer).mscx')
        self.assertTrue(os.path.exists(target))
        self.assertTrue('vbox_title (vbox_composer).mscx' in ' '.join(output))
        os.remove(target)

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
                                self._get('simple.mscx')])
        target = self._target_path_cwd('Title_Composer.mscx')
        self.assertTrue(os.path.exists(target))
        self.assertTrue('Title_Composer.mscx' in ' '.join(output))
        os.remove(target)

    def test_unicode(self):
        output = self._execute(['rename', '--ascii',
                                self._get('unicode.mscx')])
        target = self._target_path_cwd('Tuetlae (Coempoesser).mscx')
        self.assertTrue(os.path.exists(target))
        self.assertTrue('Tuetlae (Coempoesser).mscx' in ' '.join(output))
        os.remove(target)

    def test_rename_file_twice(self):
        self._execute(['rename', self._get('simple.mscx')])
        output = self._execute(['rename', self._get('simple.mscx')])
        target = self._target_path_cwd('Title (Composer).mscx')
        self.assertTrue('with the same checksum (sha1) already' in
                        ' '.join(output))
        os.remove(target)

    def test_rename_same_filename(self):
        self._execute(['rename', '-f', 'same', self._get('simple.mscx')])
        self._execute(['rename', '-f', 'same', self._get('lyrics.mscx')])
        self._execute(['rename', '-f', 'same', self._get('no-vbox.mscx')])

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
        output = helper.run('rename', '--skip-if-empty',
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
