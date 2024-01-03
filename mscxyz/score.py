"""A class that represents one MuseScore file.
"""

from __future__ import annotations

import os
import shutil
import tempfile
import typing
import zipfile
from pathlib import Path
from typing import List, Optional

import lxml
import lxml.etree  # Required for the type hints
from lxml.etree import _Element, _ElementTree, strip_tags

from mscxyz.style import MscoreStyleInterface
from mscxyz.utils import mscore, re_open, xpathall

if typing.TYPE_CHECKING:
    from lxml.etree import _XPathObject


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


class Score:
    """This class holds basic file properties of the MuseScore score file.

    :param relpath: The relative (or absolute) path of a MuseScore
        file.
    """

    path: Path
    """The absolute path of the input file."""

    loadpath: str
    """The path of the uncompressed MuseScore file in XML format file. 
    This path may be located in the temporary directory."""

    relpath: str
    """The relative path of the score file, for example:
    ``files/by_version/2/simple.mscx``.
    """

    xml_tree: _ElementTree

    xml_root: _Element

    version_major: int
    """The major MuseScore version, for example 2 or 3"""

    version: float
    """The MuseScore version, for example 2.03 or 3.01"""

    zip_container: Optional[ZipContainer]

    errors: List[Exception]
    """A list to store errors."""

    __style: Optional[MscoreStyleInterface]

    def __init__(self, relpath: str) -> None:
        self.__style = None
        self.errors = []
        self.relpath = relpath
        self.path = Path(relpath).resolve()

        if self.extension == "mscz":
            self.zip_container = ZipContainer(self.path)
            self.loadpath = str(self.zip_container.mscx_file)
        else:
            self.loadpath = str(self.path)

        try:
            self.xml_tree = lxml.etree.parse(self.loadpath)
        except lxml.etree.XMLSyntaxError as e:
            self.errors.append(e)
        else:
            self.xml_root: _Element = self.xml_tree.getroot()
            self.version = self.get_version()
            self.version_major = int(self.version)

    @property
    def relpath_backup(self) -> str:
        return self.relpath.replace("." + self.extension, "_bak." + self.extension)

    @property
    def dirname(self) -> str:
        """The name of the containing directory of the MuseScore file, for
        example: ``/home/xyz/score_files``."""
        return os.path.dirname(self.path)

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

    @property
    def basename(self) -> str:
        """The basename of the score file, for example: ``simple``."""
        return self.filename.replace("." + self.extension, "")

    def make_path(
        self, suffix: Optional[str] = None, extension: Optional[str] = None
    ) -> Path:
        path = str(self.path)
        if suffix:
            path = path.replace(f".{self.extension}", f"_{suffix}.{self.extension}")
        if extension:
            path = path.replace(f".{self.extension}", f".{extension}")
        return Path(path)

    @property
    def style(self) -> MscoreStyleInterface:
        if self.__style is None:
            self.__style = MscoreStyleInterface(self)
        return self.__style

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
                x: list[_Element] | None = xpathall(self.xml_root, xpath)
                if x:
                    for tag in x:
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
