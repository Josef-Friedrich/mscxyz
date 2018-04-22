# -*- coding: utf-8 -*-

"""A collection of classes intended to represent one MuseScore file.

The classes build on each other hierarchically. The class hierarchy:

.. code ::

    ScoreScoreFile
        XMLXMLTree
            Meta
            Lyrics
            Rename

Depending on the subcommand


"""


from mscxyz.utils import mscore, re_open
import fnmatch
import lxml
import os
import shutil
import six
import string


def list_scores(path, extension='both', glob=None):
    if not glob:
        if extension == 'both':
            glob='*.msc[xz]'
        elif extension in ('mscx', 'mscz'):
            glob='*.{}'.format(extension)
        else:
            raise ValueError('Possible values for the argument “extension” '
                             'are: “both”, “mscx”, “mscz”')
    if os.path.isfile(path):
        if fnmatch.fnmatch(path, glob):
            return [path]
        else:
            return []
    out = []
    for root, dirs, scores in os.walk(path):
        for score in scores:
            if fnmatch.fnmatch(score, glob):
                scores_path = os.path.join(root, score)
                out.append(scores_path)
    out.sort()
    return out


def list_zero_alphabet():
    score_dirs = ['0']
    for char in string.ascii_lowercase:
        score_dirs.append(char)
    return score_dirs


###############################################################################
# Class hierarchy level 1
###############################################################################


class ScoreFile(object):
    """Basic file loading"""

    def __init__(self, relpath):
        self.errors = []
        self.relpath = relpath
        self.abspath = os.path.abspath(relpath)
        self.extension = relpath.split('.')[-1]
        self.relpath_backup = relpath.replace(
            '.' + self.extension, '_bak.' + self.extension)
        self.dirname = os.path.dirname(relpath)
        self.filename = os.path.basename(relpath)
        if six.PY2:
            self.basename = self.filename.replace('.mscx', '').decode('utf-8')
        else:
            self.basename = self.filename.replace('.mscx', '')

    def backup(self):
        """Make a copy of the MuseScore"""
        shutil.copy2(self.relpath, self.relpath_backup)

    def export(self, extension='pdf'):
        """Export the score to the specifed file type

        :param str extension: The extension (default: pdf)
        """
        score = self.relpath
        mscore(['--export-to', score.replace('.mscx', '.' + extension), score])


###############################################################################
# Class hierarchy level 2
###############################################################################


class XMLTree(ScoreFile):
    """XML tree manipulation"""

    def __init__(self, relpath):
        super(XMLTree, self).__init__(relpath)
        try:
            self.xml_tree = lxml.etree.parse(self.relpath)
        except lxml.etree.XMLSyntaxError as e:
            self.errors.append(e)
        else:
            self.xml_root = self.xml_tree.getroot()

    def add_sub_element(self, root_tag, tag, text):
        tag = lxml.etree.SubElement(root_tag, tag)
        tag.text = text

    def strip_tags(self, *tags):
        lxml.etree.strip_tags(self.xml_tree, tags)

    def remove_tags_by_xpath(self, *xpath_strings):
        for xpath_string in xpath_strings:
            for rm in self.xml_tree.xpath(xpath_string):
                rm.getparent().remove(rm)

    def merge_style(self, styles):
        """Merge styles into the XML tree.

        :param str styles: The path of the style file or a string containing
          the XML style markup.

        ``styles`` may not contain surrounding ``<Style>`` tags. This input is
        valid:

        .. code :: XML

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

        This input is invalid:

        .. code :: XML

            <?xml version="1.0"?>
            <museScore version="2.06">
              <Style>
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
                </Style>
              </museScore>




        """
        if os.path.exists(styles):
            style = lxml.etree.parse(styles).getroot()
        else:
            # <?xml ... tag without encoding to avoid this error:
            # ValueError: Unicode strings with encoding declaration are
            # not supported. Please use bytes input or XML fragments without
            # declaration.
            pre = '<?xml version="1.0"?><museScore version="2.06"><Style>'
            post = '</Style></museScore>'
            style = lxml.etree.XML(pre + styles + post)

        for score in self.xml_tree.xpath('/museScore/Score'):
            score.insert(0, style[0])

    def clean(self):
        self.remove_tags_by_xpath(
            '/museScore/Score/Style', '//LayoutBreak', '//StemDirection')
        self.strip_tags('font', 'b', 'i', 'pos')

    def save(self, new_name='', mscore=False):
        if new_name:
            filename = new_name
        else:
            filename = self.relpath
        if not self.errors:
            # To get the same xml tag structure as the original score file
            # has.
            for xpath in ('//LayerTag', '//metaTag', '//font', '//i'):
                for tag in self.xml_tree.xpath(xpath):
                    if not tag.text:
                        tag.text = ''

            score = open(filename, 'w')
            score.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            score.write(lxml.etree.tostring(self.xml_root, encoding='UTF-8')
                        .decode('utf-8'))
            score.write('\n')
            score.close()
            if mscore:
                re_open(filename)


###############################################################################
# Class hierarchy level 3
###############################################################################
