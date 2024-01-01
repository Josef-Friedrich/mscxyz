"""A collection of classes intended to represent one MuseScore file.

The classes build on each other hierarchically. The class hierarchy:

.. code ::

    MscoreFile
        MscoreXmlTree
            MscoreStyleInterface
            MscoreLyricsInterface
"""

from __future__ import annotations

import fnmatch
import os
import shutil
import string
import tempfile
import typing
import zipfile
from pathlib import Path
from typing import List, Optional

import lxml
import lxml.etree  # Required for the type hints
from lxml.etree import _Element, _ElementTree, strip_tags

from mscxyz.utils import mscore, re_open

if typing.TYPE_CHECKING:
    from lxml.etree import _XPathObject


def list_scores(
    path: str, extension: str = "both", glob: Optional[str] = None
) -> list[str]:
    """List all scores in path.

    :param path: The path so search for score files.
    :param extension: Possible values: “both”, “mscz” or “mscx”.
    :param glob: A glob string, see fnmatch
    """
    if not glob:
        if extension == "both":
            glob = "*.msc[xz]"
        elif extension in ("mscx", "mscz"):
            glob = "*.{}".format(extension)
        else:
            raise ValueError(
                "Possible values for the argument “extension” "
                "are: “both”, “mscx”, “mscz”"
            )
    if os.path.isfile(path):
        if fnmatch.fnmatch(path, glob):
            return [path]
        else:
            return []
    out: List[str] = []
    for root, _, scores in os.walk(path):
        for score in scores:
            if fnmatch.fnmatch(score, glob):
                scores_path = os.path.join(root, score)
                out.append(scores_path)
    out.sort()
    return out


def list_zero_alphabet() -> List[str]:
    """Build a list: 0, a, b, c etc."""
    score_dirs = ["0"]
    for char in string.ascii_lowercase:
        score_dirs.append(char)
    return score_dirs


###############################################################################
# Class hierarchy level 1
###############################################################################


class MscoreFile:
    """This class holds basic file properties of the MuseScore score file.

    :param relpath: The relative (or absolute) path of a MuseScore
        file.
    """

    errors: List[Exception]
    """A list to store errors."""

    path: Path
    """The absolute path of the input file."""

    loadpath: str
    """The path of the uncompressed MuseScore file in XML format file. 
    This path may be located in the temporary directory."""

    relpath: str
    """The relative path of the score file, for example:
    ``files_mscore2/simple.mscx``.
    """

    abspath: str
    """The absolute path of the score file, for example:
    ``/home/jf/test/files_mscore2/simple.mscx``."""

    relpath_backup: str

    dirname: str
    """The name of the containing directory of the MuseScore file, for
    example: ``files_mscore2``."""

    basename: str
    """The basename of the score file, for example: ``simple``."""

    zip_container: Optional[ZipContainer]

    def __init__(self, relpath: str) -> None:
        self.errors = []
        self.relpath = relpath
        self.path = Path(relpath).resolve()
        self.abspath = os.path.abspath(relpath)
        self.relpath_backup = relpath.replace(
            "." + self.extension, "_bak." + self.extension
        )
        self.dirname = os.path.dirname(relpath)
        self.basename = self.filename.replace(".mscx", "")

        if self.extension == "mscz":
            self.zip_container = ZipContainer(self.path)
            self.loadpath = str(self.zip_container.mscx_file)
        else:
            self.loadpath = self.abspath

    @property
    def filename(self) -> str:
        """The filename of the MuseScore file, for example:
        ``simple.mscx``."""
        return self.path.name

    @property
    def extension(self) -> str:
        """The extension (``mscx`` or ``mscz``) of the score file, for
        example: ``mscx``."""
        return self.filename.split(".")[-1].lower()

    def backup(self) -> None:
        """Make a copy of the MuseScore file."""
        shutil.copy2(self.relpath, self.relpath_backup)

    def export(self, extension: str = "pdf") -> None:
        """Export the score to the specifed file type.

        :param extension: The extension (default: pdf)
        """
        score: str = self.relpath
        mscore(
            ["--export-to", score.replace("." + self.extension, "." + extension), score]
        )


class ZipContainer:
    """Container for the file paths of the different files in an unzipped MuseScore file

    .. code :: XML

        <?xml version="1.0" encoding="UTF-8"?>
        <container>
            <rootfiles>
                <rootfile full-path="score_style.mss"/>
                <rootfile full-path="test.mscx"/>
                <rootfile full-path="Thumbnails/thumbnail.png"/>
                <rootfile full-path="audiosettings.json"/>
                <rootfile full-path="viewsettings.json"/>
                </rootfiles>
            </container>
    """

    tmp_dir: Path
    """Absolute path of the temporary directory where the unzipped files are stored"""

    mscx_file: Path
    """Absolute path of the uncompressed XML score file"""

    score_style_file: Optional[Path]
    """Absolute path of the score style file"""

    thumbnail_file: Optional[Path]
    """Absolute path of the thumbnail file"""

    audiosettings_file: Optional[Path]
    """Absolute path of the audio settings file"""

    viewsettings_file: Optional[Path]
    """Absolute path of the view settings file"""

    def __init__(self, abspath: str | Path) -> None:
        self.tmp_dir = ZipContainer._extract_zip(abspath)
        container_info: _ElementTree = lxml.etree.parse(
            self.tmp_dir / "META-INF" / "container.xml"
        )
        root_files: _XPathObject = container_info.xpath("/container/rootfiles")
        if isinstance(root_files, list):
            for root_file in root_files[0]:
                if isinstance(root_file, _Element):
                    relpath = root_file.get("full-path")
                    if isinstance(relpath, str):
                        abs_path: Path = self.tmp_dir / relpath
                        if relpath.endswith(".mscx"):
                            self.mscx_file = abs_path
                        elif relpath.endswith(".mss"):
                            self.score_style_file = abs_path
                        elif relpath.endswith(".png"):
                            self.thumbnail_file = abs_path
                        elif relpath.endswith("audiosettings.json"):
                            self.audiosettings_file = abs_path
                        elif relpath.endswith("viewsettings.json"):
                            self.viewsettings_file = abs_path

    @staticmethod
    def _extract_zip(abspath: str | Path) -> Path:
        tmp_zipdir = Path(tempfile.mkdtemp())
        zip = zipfile.ZipFile(abspath, "r")
        zip.extractall(tmp_zipdir)
        zip.close()
        return tmp_zipdir

    def save(self, dest: str | Path) -> None:
        zip = zipfile.ZipFile(dest, "w")
        for r, _, files in os.walk(self.tmp_dir):
            root = Path(r)
            relpath: Path = root.relative_to(self.tmp_dir)
            for file_name in files:
                zip.write(root / file_name, relpath / file_name)
        zip.close()


###############################################################################
# Class hierarchy level 2
###############################################################################


class MscoreXmlTree(MscoreFile):
    """XML tree manipulation

    :param relpath: The relative (or absolute) path of a MuseScore file.
    """

    xml_tree: _ElementTree

    version_major: int
    """The major MuseScore version, for example 2 or 3"""

    version: float
    """The MuseScore version, for example 2.03 or 3.01"""

    def __init__(self, relpath: str) -> None:
        super(MscoreXmlTree, self).__init__(relpath)
        try:
            self.xml_tree = lxml.etree.parse(self.loadpath)
        except lxml.etree.XMLSyntaxError as e:
            self.errors.append(e)
        else:
            self.xml_root: _Element = self.xml_tree.getroot()
            self.version = self.get_version()
            self.version_major = int(self.version)

    def get_version(self) -> float:
        """
        Get the version number of the MuseScore file.

        :return: The version number as a float.
        :raises ValueError: If the version number cannot be retrieved.
        """
        version: _XPathObject = self.xml_tree.xpath("number(/museScore[1]/@version)")
        if isinstance(version, float):
            return version
        raise ValueError("Could not get version number")

    def remove_tags_by_xpath(self, *xpath_strings: str) -> None:
        """Remove tags by xpath strings.

        :param xpath_strings: A xpath string.

        .. code:: Python

            tree.remove_tags_by_xpath(
                '/museScore/Score/Style', '//LayoutBreak', '//StemDirection'
            )

        """
        for xpath_string in xpath_strings:
            x: _XPathObject = self.xml_tree.xpath(xpath_string)
            if isinstance(x, list):
                for rm in x:
                    if isinstance(rm, _Element):
                        p: _Element | None = rm.getparent()
                        if isinstance(p, _Element):
                            p.remove(rm)

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
            style: _Element = lxml.etree.parse(styles).getroot()
        else:
            # <?xml ... tag without encoding to avoid this error:
            # ValueError: Unicode strings with encoding declaration are
            # not supported. Please use bytes input or XML fragments without
            # declaration.
            pre = '<?xml version="1.0"?><museScore version="2.06"><Style>'
            post = "</Style></museScore>"
            style = lxml.etree.XML(pre + styles + post)

        for score in self.xml_tree.xpath("/museScore/Score"):
            score.insert(0, style[0])

    def clean(self) -> None:
        """Remove the style, the layout breaks, the stem directions and the
        ``font``, ``b``, ``i``, ``pos``, ``offset`` tags"""
        self.remove_tags_by_xpath(
            "/museScore/Score/Style", "//LayoutBreak", "//StemDirection"
        )
        strip_tags(self.xml_tree, "font", "b", "i", "pos", "offset")

    def save(self, new_name: str = "", mscore: bool = False):
        """Save the MuseScore file.

        :param new_name: Save the MuseScore file under a new name.
        :param mscore: Save the MuseScore file by opening it with the
          MuseScore executable and save it there.
        """
        if new_name:
            filename: str = new_name
        elif self.extension == "mscz":
            filename = self.loadpath
        else:
            filename = self.relpath
        if not self.errors:
            # To get the same xml tag structure as the original score file
            # has.
            for xpath in (
                "//LayerTag",
                "//metaTag",
                "//font",
                "//i",
                "//evenFooterL",
                "//evenFooterC",
                "//evenFooterR",
                "//oddFooterL",
                "//oddFooterC",
                "//oddFooterR",
                "//chord/name",
                "//chord/render",
                "//StaffText/text",
                "//Jump/continueAt",
            ):
                for tag in self.xml_tree.xpath(xpath):
                    if not tag.text:
                        tag.text = ""

            score = open(filename, "w")
            score.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            score.write(
                lxml.etree.tostring(self.xml_root, encoding="UTF-8").decode("utf-8")
            )
            score.write("\n")
            score.close()

            if self.extension == "mscz" and self.zip_container:
                self.zip_container.save(filename)

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

    style: _Element

    def __init__(self, relpath: str):
        super(MscoreStyleInterface, self).__init__(relpath)
        styles: _XPathObject = self.xml_tree.xpath("/museScore/Score/Style")
        if styles:
            self.style = styles[0]
            """The ``/museScore/Score/Style`` element object, see
            https://lxml.de/tutorial.html#the-element-class
            """
        else:
            self.style: _Element = self._create_parent_style()

    def _create_parent_style(self):
        score: _XPathObject = self.xml_tree.xpath("/museScore/Score")
        return lxml.etree.SubElement(score[0], "Style")

    def _create(self, tag: str) -> _Element:
        """
        :param tag: Nested tags are supported, for example ``TextStyle/halign``
        """
        tags = tag.split("/")
        parent = self.style
        for tag in tags:
            element = parent.find(tag)
            if element is None:
                parent = lxml.etree.SubElement(parent, tag)
            else:
                parent = element
        return parent

    def get_element(self, element_path: str, create: bool = False) -> _Element:
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

    def set_attributes(self, element_path: str, attributes: dict) -> _Element:
        """Set attributes on a style child tag.

        :param element_path: see
          http://lxml.de/tutorial.html#elementpath
        """
        element: _Element = self.get_element(element_path, create=True)
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
            element: _Element = self._create(element_path)
        element.text = str(value)

    def _get_text_style_element(self, name: str) -> _Element:
        if self.version_major != 2:
            raise ValueError(
                "This operation is only allowed for MuseScore 2 score files"
            )
        xpath = '//TextStyle/name[contains(., "{}")]'.format(name)
        child = self.xml_tree.xpath(xpath)
        if child:
            return child[0].getparent()
        else:
            el_text_style: _Element = lxml.etree.SubElement(self.style, "TextStyle")
            el_name: _Element = lxml.etree.SubElement(el_text_style, "name")
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
