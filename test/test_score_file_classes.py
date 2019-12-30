"""ScoreFile for various tests"""

from mscxyz.score_file_classes import ScoreFile, list_scores, \
                                      list_zero_alphabet, XMLTree, Style
import helper
from unittest import mock
import mscxyz
import os
import shutil
import unittest
import filecmp


class TestFunctions(unittest.TestCase):

    @staticmethod
    def _list_scores(path, extension='both', glob=None):
        with mock.patch('os.walk') as mockwalk:
            mockwalk.return_value = [
                ('/a', ('bar',), ('lorem.mscx',)),
                ('/a/b', (), ('impsum.mscz', 'dolor.mscx', 'sit.txt')),
            ]
            return list_scores(path, extension, glob)

    @mock.patch('mscxyz.Meta')
    def test_batch(self, Meta):
        with helper.Capturing():
            mscxyz.execute(['meta', helper.get_tmpdir_path('batch')])
        self.assertEqual(Meta.call_count, 3)

    def test_without_extension(self):
        result = self._list_scores('/test')
        self.assertEqual(result, ['/a/b/dolor.mscx', '/a/b/impsum.mscz',
                                  '/a/lorem.mscx'])

    def test_extension_both(self):
        result = self._list_scores('/test', extension='both')
        self.assertEqual(result, ['/a/b/dolor.mscx', '/a/b/impsum.mscz',
                                  '/a/lorem.mscx'])

    def test_extension_mscx(self):
        result = self._list_scores('/test', extension='mscx')
        self.assertEqual(result, ['/a/b/dolor.mscx', '/a/lorem.mscx'])

    def test_extension_mscz(self):
        result = self._list_scores('/test', extension='mscz')
        self.assertEqual(result, ['/a/b/impsum.mscz'])

    def test_raises_exception(self):
        with self.assertRaises(ValueError):
            self._list_scores('/test', extension='lol')

    def test_isfile(self):
        with mock.patch('os.path.isfile') as mock_isfile:
            mock_isfile.return_value = True
            result = list_scores('/a/b/lorem.mscx')
            self.assertEqual(result, ['/a/b/lorem.mscx'])

    def test_isfile_no_match(self):
        with mock.patch('os.path.isfile') as mock_isfile:
            mock_isfile.return_value = True
            result = list_scores('/a/b/lorem.lol')
            self.assertEqual(result, [])

    def test_arg_glob_txt(self):
        result = self._list_scores('/test', glob='*.txt')
        self.assertEqual(result, ['/a/b/sit.txt'])

    def test_arg_glob_lol(self):
        result = self._list_scores('/test', glob='*.lol')
        self.assertEqual(result, [])

    def test_function_list_zero_alphabet(self):
        result = list_zero_alphabet()
        self.assertEqual(result[0], '0')
        self.assertEqual(result[26], 'z')


class TestScoreFile(unittest.TestCase):

    def setUp(self):
        self.file = ScoreFile(helper.get_tmpfile_path('simple.mscx'))

    def test_attribute_relpath(self):
        self.assertTrue(self.file.relpath)

    def test_attribute_dirname(self):
        self.assertTrue(self.file.dirname)

    def test_attribute_filename(self):
        self.assertEqual(self.file.filename, 'simple.mscx')

    def test_attribute_basename(self):
        self.assertEqual(self.file.basename, 'simple')

    def test_attribute_extension(self):
        self.assertEqual(self.file.extension, 'mscx')

    def test_attribute_abspath(self):
        self.assertEqual(self.file.abspath, self.file.loadpath)


class TestScoreFileMscz(unittest.TestCase):

    def setUp(self):
        self.file = ScoreFile(helper.get_tmpfile_path('simple.mscz'))

    def test_attribute_extension(self):
        self.assertEqual(self.file.extension, 'mscz')

    def test_attribute_loadpath(self):
        self.assertIn('simple.mscx', self.file.loadpath)


class TestClassXMLTree(unittest.TestCase):

    def test_property_version(self):
        tree = XMLTree(helper.get_tmpfile_path('simple.mscx', version=2))
        self.assertEqual(tree.version, 2.06)
        self.assertEqual(tree.version_major, 2)

        tree = XMLTree(helper.get_tmpfile_path('simple.mscx', version=3))
        self.assertEqual(tree.version, 3.01)
        self.assertEqual(tree.version_major, 3)

    def test_method_merge_style(self):
        tree = XMLTree(helper.get_tmpfile_path('simple.mscx'))
        styles = """
            <TextStyle>
              <halign>center</halign>
              <valign>bottom</valign>
              <xoffset>0</xoffset>
              <yoffset>-1</yoffset>
              <offsetType>spatium</offsetType>
              <name>Form Section</name>
              <family>Alegreya Sans</family>
              <size>12</size>
              <bold>1</bold>
              <italic>1</italic>
              <sizeIsSpatiumDependent>1</sizeIsSpatiumDependent>
              <frameWidthS>0.1</frameWidthS>
              <paddingWidthS>0.2</paddingWidthS>
              <frameRound>0</frameRound>
              <frameColor r="0" g="0" b="0" a="255"/>
              </TextStyle>
        """
        tree.clean()
        tree.merge_style(styles)

        xml_tree = tree.xml_tree
        result = xml_tree.xpath('/museScore/Score/Style')
        self.assertEqual(result[0][0][0].tag, 'halign')
        self.assertEqual(result[0][0][0].text, 'center')

    def test_method_clean(self):
        tmp = helper.get_tmpfile_path('clean.mscx', version=3)
        tree = XMLTree(tmp)
        tree.clean()
        tree.save()
        tree = XMLTree(tmp)
        xml_tree = tree.xml_tree
        self.assertEqual(xml_tree.xpath('/museScore/Score/Style'), [])
        self.assertEqual(xml_tree.xpath('//LayoutBreak'), [])
        self.assertEqual(xml_tree.xpath('//StemDirection'), [])
        self.assertEqual(xml_tree.xpath('//font'), [])
        self.assertEqual(xml_tree.xpath('//b'), [])
        self.assertEqual(xml_tree.xpath('//i'), [])
        self.assertEqual(xml_tree.xpath('//pos'), [])
        self.assertEqual(xml_tree.xpath('//offset'), [])

    def test_method_save(self):
        tmp = helper.get_tmpfile_path('simple.mscx')
        tree = XMLTree(tmp)
        tree.save()
        result = helper.read_file(tmp)
        self.assertTrue('<metaTag name="arranger"></metaTag>' in result)

    def test_method_save_new_name(self):
        tmp = helper.get_tmpfile_path('simple.mscx')
        tree = XMLTree(tmp)
        tree.save(new_name=tmp)
        result = helper.read_file(tmp)
        self.assertTrue('<metaTag name="arranger"></metaTag>' in result)

    def test_mscz(self):
        tmp = helper.get_tmpfile_path('simple.mscz')
        tree = XMLTree(tmp)
        result = tree.xml_tree.xpath('/museScore/Score/Style')
        self.assertEqual(result[0].tag, 'Style')


class TestClassStyle(unittest.TestCase):

    def setUp(self):
        self.style = Style(helper.get_tmpfile_path('All_Dudes.mscx',
                           version=2))

    def test_attributes_style(self):
        self.assertEqual(self.style.style.tag, 'Style')

    def test_method_get(self):
        self.assertEqual(self.style.get('staffUpperBorder'), '6.5')

    def test_method_get_muliple_element_path(self):
        self.assertEqual(self.style.get('page-layout/page-height'), '1584')

    def test_method_set(self):
        self.style.set('staffUpperBorder', 99)
        self.style.save()
        style2 = Style(self.style.abspath)
        self.assertEqual(style2.get('staffUpperBorder'), '99')

    def test_method_set_create(self):
        self.style.set('lol', 'lol')
        self.style.save()
        style2 = Style(self.style.abspath)
        self.assertEqual(style2.get('lol'), 'lol')

    def test_method_set_muliple_element_path(self):
        self.style.set('page-layout/page-height', 99)
        self.style.save()
        style2 = Style(self.style.abspath)
        self.assertEqual(style2.get('page-layout/page-height'), '99')

    def test_method_set_muliple_element_path_multiple_times(self):
        self.style.set('page-layout/page-height', 99)
        self.style.set('page-layout/page-width', 100)
        self.style.set('page-layout/page-depth', 101)
        self.style.save()
        style2 = Style(self.style.abspath)
        self.assertEqual(style2.get('page-layout/page-depth'), '101')
        self.assertEqual(style2.get('page-layout/page-height'), '99')
        self.assertEqual(style2.get('page-layout/page-width'), '100')

    def test_method_get_text_style(self):
        title = self.style.get_text_style('Title')
        self.assertEqual(title, {'halign': 'center',
                                 'size': '28',
                                 'family': 'MuseJazz',
                                 'bold': '1',
                                 'valign': 'top',
                                 'name': 'Title',
                                 'offsetType': 'absolute'})

    def test_method_set_text_style(self):
        self.style.set_text_style('Title', {'size': 99})
        self.style.save()
        style2 = Style(self.style.abspath)
        title = style2.get_text_style('Title')
        self.assertEqual(title['size'], '99')


class TestClassStyle3(unittest.TestCase):

    def setUp(self):
        self.style = Style(helper.get_tmpfile_path('All_Dudes.mscx',
                           version=3))

    def test_attributes_style(self):
        self.assertEqual(self.style.style.tag, 'Style')

    def test_method_get(self):
        self.assertEqual(self.style.get('staffUpperBorder'), '6.5')

    def test_method_set(self):
        self.style.set('staffUpperBorder', 99)
        self.style.save()
        style2 = Style(self.style.abspath)
        self.assertEqual(style2.get('staffUpperBorder'), '99')

    def test_method_set_create(self):
        self.style.set('lol', 'lol')
        self.style.save()
        style2 = Style(self.style.abspath)
        self.assertEqual(style2.get('lol'), 'lol')


class TestClassStyleWithoutTags(unittest.TestCase):

    def setUp(self):
        self.style = Style(helper.get_tmpfile_path('without-style.mscx'))

    def test_load(self):
        self.assertEqual(self.style.style.tag, 'Style')

    def test_method_set(self):
        self.style.set('staffUpperBorder', 99)
        self.style.save()
        style2 = Style(self.style.abspath)
        self.assertEqual(style2.get('staffUpperBorder'), '99')

    def test_method_set_element_path_multiple(self):
        self.style.set('lol/troll', 99)
        self.style.save()
        style2 = Style(self.style.abspath)
        self.assertEqual(style2.get('lol/troll'), '99')

    def test_method_get_text_style_unkown(self):
        unkown = self.style.get_text_style('Unkown')
        self.assertEqual(unkown, {'name': 'Unkown'})

    def test_method_set_text_style_unkown(self):
        self.style.set_text_style('Unkown', {'size': 99})
        self.style.save()
        style2 = Style(self.style.abspath)
        unkown = style2.get_text_style('Unkown')
        self.assertEqual(unkown['size'], '99')


class TestFileCompare(unittest.TestCase):

    def assertDiff(self, filename, version=2):
        orig = os.path.join(os.path.expanduser('~'), filename)
        saved = orig.replace('.mscx', '_saved.mscx')
        tmp = helper.get_tmpfile_path(filename, version=version)
        shutil.copy2(tmp, orig)
        tree = XMLTree(tmp)
        tree.save(new_name=saved)
        self.assertTrue(filecmp.cmp(orig, saved))
        os.remove(orig)
        os.remove(saved)

    def test_getting_started(self):
        self.assertDiff('Getting_Started_English.mscx', version=2)
        self.assertDiff('Getting_Started_English.mscx', version=3)

    def test_lyrics(self):
        self.assertDiff('lyrics.mscx', version=2)
        self.assertDiff('lyrics.mscx', version=3)

    def test_chords(self):
        self.assertDiff('chords.mscx', version=2)
        self.assertDiff('chords.mscx', version=3)

    def test_unicode(self):
        self.assertDiff('unicode.mscx', version=2)
        self.assertDiff('unicode.mscx', version=3)

    def test_real_world_ragtime_3(self):
        self.assertDiff('Ragtime_3.mscx', version=2)
        # self.assertDiff('Ragtime_3.mscx', version=3)

    def test_real_world_zum_tanze(self):
        self.assertDiff('Zum-Tanze-da-geht-ein-Maedel.mscx', version=2)
        self.assertDiff('Zum-Tanze-da-geht-ein-Maedel.mscx', version=3)

    def test_real_world_all_dudes(self):
        self.assertDiff('All_Dudes.mscx', version=2)
        self.assertDiff('All_Dudes.mscx', version=3)

    def test_real_world_reunion(self):
        self.assertDiff('Reunion.mscx', version=2)
        self.assertDiff('Reunion.mscx', version=3)

    def test_real_world_triumph(self):
        self.assertDiff('Triumph.mscx', version=2)
        self.assertDiff('Triumph.mscx', version=3)


if __name__ == '__main__':
    unittest.main()
