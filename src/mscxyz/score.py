"""A class that represents one MuseScore file."""

from __future__ import annotations

import difflib
import os
import shutil
from pathlib import Path
from typing import Any, Optional

from lxml.etree import _Element

from mscxyz import utils
from mscxyz.export import Export
from mscxyz.fields import FieldsManager
from mscxyz.lyrics import Lyrics
from mscxyz.meta import Meta
from mscxyz.settings import get_args
from mscxyz.style import Style
from mscxyz.xml import XmlManipulator


class Score:
    """This class holds basic file properties of the MuseScore score file.

    :param src: The relative (or absolute) path of a MuseScore
        file.
    """

    path: Path
    """The absolute path of the MuseScore file, for example ``/home/xyz/score.mscz``.
    """

    xml_file: str
    """The path of the uncompressed MuseScore file in XML format file.
    This path may be located in the temporary directory."""

    style_file: Optional[Path] = None
    """Score files created with MuseScore 4 have a separate style file."""

    xml_root: _Element
    """The root element of the XML tree. It is the ``<museScore version="X.X">`` Tag.
      See the `lxml API <https://lxml.de/api.html>`_."""

    xml: XmlManipulator

    version: float
    """The MuseScore version as a floating point number, for example ``2.03``, ``3.01`` or ``4.20``."""

    zip_container: Optional[utils.ZipContainer] = None

    __xml_string_initial: Optional[str] = None

    __fields: Optional[FieldsManager] = None

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

        self.xml = XmlManipulator(file_path=self.xml_file)
        self.xml_root = self.xml.root
        self.version = self.get_version()

        if self.extension == "mscz" and self.version_major == 4 and self.zip_container:
            self.style_file = self.zip_container.score_style_file

        # Initialize the Style class to embed the style file into the score file.
        self.style

    @property
    def xml_string(self) -> str:
        return self.xml.tostring(self.xml_root)

    @property
    def version_major(self) -> int:
        """The major MuseScore version, for example ``2``, ``3`` or ``4``"""
        return int(self.version)

    @property
    def program_version(self) -> str:
        """
        The semantic version number of the MuseScore program, for example: ``4.2.0``.

        .. code-block:: xml

            <programVersion>4.2.0</programVersion>

        :see: `MuseScore C++ source code: writer.cpp line 56 <https://github.com/musescore/MuseScore/blob/ed678925efbbdbb9bd14ea3f6f7c9b5ab42491e7/src/engraving/rw/write/writer.cpp#L56>`_

        """
        return self.xml.get_text_safe(element_path="programVersion")

    @property
    def program_revision(self) -> str:
        """
        The revision number of the MuseScore program, for example: ``eb8d33c``.

        .. code-block:: xml

            <programRevision>eb8d33c</programRevision>

        :see: `MuseScore C++ source code: writer.cpp line 57 <https://github.com/musescore/MuseScore/blob/ed678925efbbdbb9bd14ea3f6f7c9b5ab42491e7/src/engraving/rw/write/writer.cpp#L57>`_

        """
        return self.xml.get_text_safe(element_path="programRevision")

    @property
    def backup_file(self) -> Path:
        """The absolute path of the backup file.
        The string ``_bak`` is appended to the file name before the extension."""
        return self.change_path(suffix="bak")

    @property
    def json_file(self) -> Path:
        """The absolute path of the JSON file in which the metadata can be exported."""
        return self.change_path(extension="json")

    @property
    def dirname(self) -> str:
        """The name of the containing directory of the MuseScore file, for
        example: ``/home/xyz/score_files``."""
        return os.path.dirname(self.path)

    @property
    def filename(self) -> str:
        """The filename of the MuseScore file, for example:
        ``score.mscz``."""
        return self.path.name

    @property
    def basename(self) -> str:
        """The basename of the score file, for example: ``score``."""
        return self.filename.replace("." + self.extension, "")

    @property
    def extension(self) -> str:
        """The extension (``mscx`` or ``mscz``) of the score file."""
        return self.filename.split(".")[-1].lower()

    @property
    def is_uncompressed(self) -> bool:
        """Whether the MuseScore file is uncompressed , i.e. it is a ``*.mscx`` file"""
        return self.extension != "mscz"

    def change_path(
        self,
        suffix: Optional[Any] = None,
        extension: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> Path:
        return utils.PathChanger(self.path).change(
            suffix=suffix, extension=extension, filename=filename
        )

    @property
    def export(self) -> Export:
        if self.__export is None:
            self.__export = Export(self)
        return self.__export

    @property
    def fields(self) -> FieldsManager:
        if self.__fields is None:
            self.__fields = FieldsManager(self)
        return self.__fields

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
        if self.__xml_string_initial is not None:
            raise ValueError("Snapshot already exists")
        self.__xml_string_initial = self.xml_string

    def new(
        self,
        suffix: Optional[Any] = None,
        extension: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> Score:
        return Score(
            self.change_path(suffix=suffix, extension=extension, filename=filename)
        )

    def __str__(self) -> str:
        return str(self.path)

    def exists(self) -> bool:
        return self.path.exists()

    def backup(self) -> None:
        """Make a copy of the MuseScore file."""
        shutil.copy2(self.path, self.backup_file)

    def get_version(self) -> float:
        """
        Get the version number of the MuseScore file.

        :return: The version number as a float.
        :raises ValueError: If the version number cannot be retrieved.
        """
        version = self.xml_root.xpath("number(/museScore[1]/@version)")
        if isinstance(version, float):
            return version
        raise ValueError("Could not get version number")

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

        if (
            self.__xml_string_initial is not None
            and self.__xml_string_initial == self.xml_string
        ):
            return

        if new_dest:
            dest: str = new_dest
        else:
            dest = str(self.path)

        xml_dest = dest

        if self.extension == "mscz":
            xml_dest = self.xml_file

        # Since MuseScore 4 the style is stored in a separate file.
        if self.style_file:
            element = self.xml.create_element(
                "museScore", {"version": str(self.version)}
            )
            element.append(self.style.parent_element)
            self.xml.write(self.style_file, element)
            self.xml.remove_tags("./Score/Style")

        self.xml.write(xml_dest)

        if self.extension == "mscz" and self.zip_container:
            self.zip_container.save(dest)

        if mscore:
            utils.re_open(dest)

    def read_as_text(self) -> str:
        """Read the MuseScore XML file as text.

        :return: The content of the MuseScore XML file as text.
        """
        return utils.read_file(self.xml_file)

    def reload(self, save: bool = False) -> Score:
        """
        Reload the MuseScore file.

        :param save: Whether to save the changes before reloading. Default is False.

        :return: The reloaded Score object.
        """
        if save:
            self.save()
        return self.new()
