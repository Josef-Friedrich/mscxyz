"""A class that represents one MuseScore file.
"""

from __future__ import annotations

import difflib
import os
import shutil
import typing
from pathlib import Path
from typing import Optional

import lxml
import lxml.etree
from lxml.etree import _Element, strip_tags

from mscxyz import utils
from mscxyz.export import Export
from mscxyz.lyrics import Lyrics
from mscxyz.meta import Meta
from mscxyz.settings_legacy import get_args
from mscxyz.style import Style

if typing.TYPE_CHECKING:
    from lxml.etree import _XPathObject


class Score:
    """This class holds basic file properties of the MuseScore score file.

    :param src: The relative (or absolute) path of a MuseScore
        file.
    """

    path: Path
    """The absolute path of the input file.
    """

    xml_file: str
    """The path of the uncompressed MuseScore file in XML format file.
    This path may be located in the temporary directory."""

    style_file: Optional[Path] = None
    """Score files created with MuseScore 4 have a separate style file."""

    xml_root: _Element
    """The root element of the XML tree. See the `lxml API <https://lxml.de/api.html>`_."""

    version: float
    """The MuseScore version, for example 2.03 or 3.01"""

    zip_container: Optional[utils.ZipContainer] = None

    errors: list[Exception]
    """A list to store errors."""

    __xml_string_initial: Optional[str] = None

    __export: Optional[Export] = None

    __lyrics: Optional[Lyrics] = None

    __meta: Optional[Meta] = None

    __style: Optional[Style] = None

    def __init__(self, src: str | Path) -> None:
        self.path = Path(src).resolve()

        if self.extension == "mscz":
            self.zip_container = utils.ZipContainer(self.path)
            self.xml_file = str(self.zip_container.xml_file)
        else:
            self.xml_file = str(self.path)

        self.errors = []
        try:
            self.xml_root = lxml.etree.parse(self.xml_file).getroot()
        except lxml.etree.XMLSyntaxError as e:
            self.errors.append(e)
        else:
            self.version = self.get_version()

        if self.extension == "mscz" and self.version_major == 4 and self.zip_container:
            self.style_file = self.zip_container.score_style_file

    @property
    def xml_string(self) -> str:
        return utils.xml.tostring(self.xml_root)

    @property
    def version_major(self) -> int:
        """The major MuseScore version, for example 2 or 3"""
        return int(self.version)

    @property
    def relpath_backup(self) -> str:
        return str(self.path).replace("." + self.extension, "_bak." + self.extension)

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

    def change_path(
        self, suffix: Optional[str] = None, extension: Optional[str] = None
    ) -> Path:
        return utils.PathChanger(self.path).change(suffix=suffix, extension=extension)

    @property
    def export(self) -> Export:
        if self.__export is None:
            self.__export = Export(self)
        return self.__export

    @property
    def lyrics(self) -> Lyrics:
        if self.__lyrics is None:
            self.__lyrics = Lyrics(self)
        return self.__lyrics

    @property
    def meta(self) -> Meta:
        if self.__meta is None:
            self.__meta = Meta(self)
        return self.__meta

    @property
    def style(self) -> Style:
        if self.__style is None:
            self.__style = Style(self)
        return self.__style

    def make_snapshot(self) -> None:
        self.__xml_string_initial = self.xml_string

    def new(self) -> Score:
        return Score(self.path)

    def backup(self) -> None:
        """Make a copy of the MuseScore file."""
        shutil.copy2(self.path, self.relpath_backup)

    def get_version(self) -> float:
        """
        Get the version number of the MuseScore file.

        :return: The version number as a float.
        :raises ValueError: If the version number cannot be retrieved.
        """
        version: _XPathObject = self.xml_root.xpath("number(/museScore[1]/@version)")
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
            x: _XPathObject = self.xml_root.xpath(xpath_string)
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
        strip_tags(self.xml_root, "font", "b", "i", "pos", "offset")

    def print_diff(self) -> None:
        if self.__xml_string_initial is None:
            return
        green = "\x1b[32m"
        red = "\x1b[31m"
        reset = "\x1b[0m"

        diff = difflib.unified_diff(
            self.__xml_string_initial.splitlines(),
            self.xml_string.splitlines(),
            lineterm="",
        )

        for line in diff:
            if line.startswith("-"):
                print(red + line + reset)
            elif line.startswith("+"):
                print(green + line + reset)
            else:
                print(line)

    def save(self, new_dest: str = "", mscore: bool = False) -> None:
        """Save the MuseScore file.

        :param new_dest: Save the MuseScore file under a new name.
        :param mscore: Save the MuseScore file by opening it with the
          MuseScore executable and save it there.
        """
        args = get_args()
        if args.general_dry_run:
            return
        if new_dest:
            dest: str = new_dest
        else:
            dest = str(self.path)
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
                x: list[_Element] | None = utils.xml.xpathall(self.xml_root, xpath)
                if x:
                    for tag in x:
                        if not tag.text:
                            tag.text = ""

            xml_dest = dest

            if self.extension == "mscz":
                xml_dest = self.xml_file
            utils.xml.write(xml_dest, self.xml_root)

            # Since MuseScore 4 the style is stored in a separate file.
            if self.style_file:
                element: _Element = lxml.etree.Element(
                    "museScore", {"version": str(self.version)}
                )
                element.append(self.style.parent_element)
                utils.xml.write(self.style_file, element)

            if self.extension == "mscz" and self.zip_container:
                self.zip_container.save(dest)

            if mscore:
                utils.re_open(dest)

    def read_as_text(self) -> str:
        """Read the MuseScore XML file as text.

        :return: The content of the MuseScore XML file as text.
        """
        with open(self.xml_file, "r") as f:
            return f.read()

    def reload(self, save: bool = False) -> Score:
        """
        Reload the MuseScore file.

        :param save: Whether to save the changes before reloading. Default is False.

        :return: The reloaded Score object.
        """
        if save:
            self.save()
        return Score(self.path)
