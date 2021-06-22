"""A collection of classes intended to represent one MuseScore file.

The classes build on each other hierarchically. The class hierarchy:

.. code ::

    MscoreFile
        MscoreXmlTree
            MscoreStyleInterface
            MscoreLyricsInterface
"""


from mscxyz.utils import mscore, re_open
import lxml.etree  # Needed for type hints
import fnmatch
import lxml
import os
import shutil
import string
import zipfile
import tempfile


def list_scores(path: str, extension: str = 'both', glob: str = None) -> list:
    """List all scores in path.

    :param path: The path so search for score files.
    :param extension: Possible values: “both”, “mscz” or “mscx”.
    :param glob: A glob string, see fnmatch
    """
    if not glob:
        if extension == 'both':
            glob = '*.msc[xz]'
        elif extension in ('mscx', 'mscz'):
            glob = '*.{}'.format(extension)
        else:
            raise ValueError('Possible values for the argument “extension” '
                             'are: “both”, “mscx”, “mscz”')
    if os.path.isfile(path):
        if fnmatch.fnmatch(path, glob):
            return [path]
        else:
            return []
    out = []
    for root, _, scores in os.walk(path):
        for score in scores:
            if fnmatch.fnmatch(score, glob):
                scores_path = os.path.join(root, score)
                out.append(scores_path)
    out.sort()
    return out


def list_zero_alphabet() -> list:
    """Build a list: 0, a, b, c etc."""
    score_dirs = ['0']
    for char in string.ascii_lowercase:
        score_dirs.append(char)
    return score_dirs


###############################################################################
# Class hierarchy level 1
###############################################################################


class MscoreFile(object):
    """This class holds basic file properties of the MuseScore score file.

    :param relpath: The relative (or absolute) path of a MuseScore
        file.
    """

    def __init__(self, relpath: str):
        self.errors = []
        """A list to store errors."""

        self.relpath = relpath
        """The relative path of the score file, for example:
        ``files_mscore2/simple.mscx``.
        """

        self.abspath = os.path.abspath(relpath)
        """The absolute path of the score file, for example:
        ``/home/jf/test/files_mscore2/simple.mscx``."""

        self.extension = relpath.split('.')[-1].lower()
        """The extension (``mscx`` or ``mscz``) of the score file, for
        example: ``mscx``."""

        self.relpath_backup = relpath.replace(
            '.' + self.extension, '_bak.' + self.extension)
        """The backup path of the score file, for example:
        ``files_mscore2/simple_bak.mscx``."""

        self.dirname = os.path.dirname(relpath)
        """The name of the containing directory of the MuseScore file, for
        example: ``files_mscore2``."""

        self.filename = os.path.basename(relpath)
        """The filename of the MuseScore file, for example:
        ``simple.mscx``."""

        self.basename = self.filename.replace('.mscx', '')
        """The basename of the score file, for example: ``simple``."""

        if self.extension == 'mscz':
            self.loadpath = self._unzip(self.abspath)
            """The load path of the score file"""

        else:
            self.loadpath = self.abspath

    @staticmethod
    def _unzip(abspath: str):
        tmp_zipdir = tempfile.mkdtemp()
        zip_ref = zipfile.ZipFile(abspath, 'r')
        zip_ref.extractall(tmp_zipdir)
        zip_ref.close()
        con = os.path.join(tmp_zipdir, 'META-INF', 'container.xml')
        container_info = lxml.etree.parse(con)
        mscx = container_info \
            .xpath('string(/container/rootfiles/rootfile/@full-path)')
        return os.path.join(tmp_zipdir, mscx)

    def backup(self):
        """Make a copy of the MuseScore file."""
        shutil.copy2(self.relpath, self.relpath_backup)

    def export(self, extension: str = 'pdf'):
        """Export the score to the specifed file type.

        :param extension: The extension (default: pdf)
        """
        score = self.relpath
        mscore(['--export-to',
                score.replace('.' + self.extension, '.' + extension), score])


###############################################################################
# Class hierarchy level 2
###############################################################################


class MscoreXmlTree(MscoreFile):
    """XML tree manipulation

    :param relpath: The relative (or absolute) path of a MuseScore file.
    """

    def __init__(self, relpath: str):
        super(MscoreXmlTree, self).__init__(relpath)
        try:
            self.xml_tree = lxml.etree.parse(self.loadpath)
        except lxml.etree.XMLSyntaxError as e:
            self.errors.append(e)
        else:
            self.xml_root = self.xml_tree.getroot()
            musescore = self.xml_tree.xpath('/museScore')
            version = musescore[0].get('version')
            self.version_major = int(version.split('.')[0])
            """The major MuseScore version, for example 2 or 3"""
            self.version = float(version)
            """The MuseScore version, for example 2.03 or 3.01"""

    def add_sub_element(self, root_tag, tag, text: str):
        tag = lxml.etree.SubElement(root_tag, tag)
        tag.text = text

    def strip_tags(self, *tag_names: str):
        """Delete / strip some tag names."""
        lxml.etree.strip_tags(self.xml_tree, tag_names)

    def remove_tags_by_xpath(self, *xpath_strings: str):
        """Remove tags by xpath strings.

        :param xpath_strings: A xpath string.

        .. code:: Python

            tree.remove_tags_by_xpath(
                '/museScore/Score/Style', '//LayoutBreak', '//StemDirection'
            )

        """
        for xpath_string in xpath_strings:
            for rm in self.xml_tree.xpath(xpath_string):
                rm.getparent().remove(rm)

    def merge_style(self, styles: str):
        """Merge styles into the XML tree.

        :param styles: The path of the style file or a string containing
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
        """Remove the style, the layout breaks, the stem directions and the
        ``font``, ``b``, ``i``, ``pos``, ``offset`` tags"""
        self.remove_tags_by_xpath(
            '/museScore/Score/Style', '//LayoutBreak', '//StemDirection')
        self.strip_tags('font', 'b', 'i', 'pos', 'offset')

    def save(self, new_name: str = '', mscore: bool = False):
        """Save the MuseScore file.

        :param new_name: Save the MuseScore file under a new name.
        :param mscore: Save the MuseScore file by opening it with the
          MuseScore executable and save it there.
        """
        if new_name:
            filename = new_name
        else:
            filename = self.relpath
        if not self.errors:
            # To get the same xml tag structure as the original score file
            # has.
            for xpath in ('//LayerTag',
                          '//metaTag',
                          '//font',
                          '//i',
                          '//evenFooterL',
                          '//evenFooterC',
                          '//evenFooterR',
                          '//oddFooterL',
                          '//oddFooterC',
                          '//oddFooterR',
                          '//chord/name',
                          '//chord/render',
                          '//StaffText/text',
                          '//Jump/continueAt',
                          ):

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

class MscoreStyleInterface(MscoreXmlTree):
    """
    Interface specialized for the style manipulation.

    :param relpath: The relative (or absolute) path of a MuseScore file.
    """
    def __init__(self, relpath: str):
        super(MscoreStyleInterface, self).__init__(relpath)
        styles = self.xml_tree.xpath('/museScore/Score/Style')
        if styles:
            self.style = styles[0]
            """The ``/museScore/Score/Style`` element object, see
            https://lxml.de/tutorial.html#the-element-class
            """
        else:
            self.style = self._create_parent_style()

    def _create_parent_style(self):
        score = self.xml_tree.xpath('/museScore/Score')
        return lxml.etree.SubElement(score[0], 'Style')

    def _create(self, tag: str) -> lxml.etree.Element:
        """
        :param tag: Nested tags are supported, for example ``TextStyle/halign``
        """
        tags = tag.split('/')
        parent = self.style
        for tag in tags:
            element = parent.find(tag)
            if element is None:
                parent = lxml.etree.SubElement(parent, tag)
            else:
                parent = element
        return parent

    def get_element(self, element_path: str,
                    create: bool = False) -> lxml.etree.Element:
        """
        Get a lxml element which is parent to the ``Style`` tag.

        :param element_path: see
          http://lxml.de/tutorial.html#elementpath
        :param create: Create the element if not present in the parent
          ``Style`` tag.

        Example code:

        .. code:: Python

            # Set attributes on a maybe non-existent style tag.
            # <measureNumberOffset x="0.5" y="-2"/>
            test = MscoreStyleInterface('text.mscx')
            element = test.get_element('measureNumberOffset', create=True)
            element.attrib['x'] = '0.5'
            element.attrib['y'] = '-2'
            test.save()
        """
        element = self.style.find(element_path)
        if element is None and create:
            element = self._create(element_path)
        return element

    def get_value(self, element_path: str) -> str:
        """
        Get the value (text) of a style tag.

        :param element_path: see
          http://lxml.de/tutorial.html#elementpath
        """
        element = self.get_element(element_path)
        return element.text

    def set_attributes(self, element_path: str,
                       attributes: dict) -> lxml.etree.Element:
        """Set attributes on a style child tag.

        :param element_path: see
          http://lxml.de/tutorial.html#elementpath
        """
        element = self.get_element(element_path, create=True)
        for name, value in attributes.items():
            element.attrib[name] = str(value)
        return element

    def set_value(self, element_path: str, value: str):
        """
        :param element_path: see
          http://lxml.de/tutorial.html#elementpath
        """
        element = self.style.find(element_path)
        if element is None:
            element = self._create(element_path)
        element.text = str(value)

    def _get_text_style_element(self, name: str) -> lxml.etree.Element:
        if self.version_major != 2:
            raise ValueError(
                'This operation is only allowed for MuseScore 2 score files'
            )
        xpath = '//TextStyle/name[contains(., "{}")]'.format(name)
        child = self.xml_tree.xpath(xpath)
        if child:
            return child[0].getparent()
        else:
            el_text_style = lxml.etree.SubElement(self.style, 'TextStyle')
            el_name = lxml.etree.SubElement(el_text_style, 'name')
            el_name.text = name
            return el_text_style

    def get_text_style(self, name: str) -> dict:
        """Get text styles. Only MuseScore2!

        :param name: The name of the text style.
        """
        text_style = self._get_text_style_element(name)
        out = {}
        for child in text_style.iterchildren():
            out[child.tag] = child.text
        return out

    def set_text_style(self, name: str, values: dict):
        """Set text styles. Only MuseScore2!

        :param name: The name of the text style.
        :param values: A dictionary. The keys are the tag names, values are
          the text values of the child tags, for example
          ``{size: 14, bold: 1}``.
        """
        text_style = self._get_text_style_element(name)
        for element_name, value in values.items():
            el = text_style.find(element_name)
            if el is None:
                el = lxml.etree.SubElement(text_style, element_name)
            el.text = str(value)
