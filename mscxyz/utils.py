"""A collection of useful utility functions"""

from __future__ import annotations  # For subprocess.Popen[Any]

import fnmatch
import os
import platform
import string
import subprocess
import tempfile
import typing
import zipfile
from pathlib import Path
from typing import Any, List, Literal, Optional

import lxml
import lxml.etree
import termcolor
from lxml.etree import _Element, _ElementTree

from mscxyz.settings import get_args

if typing.TYPE_CHECKING:
    from lxml.etree import _XPathObject


ListExtension = Literal["mscz", "mscx", "both"]


def list_score_paths(
    path: str, extension: ListExtension = "both", glob: Optional[str] = None
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
            glob = f"*.{extension}"
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


def get_musescore_bin() -> str:
    """Check the existance of the executable mscore

    :return: Path of the executable.
    """
    args = get_args()
    system = platform.system()
    if args and args.general_executable:
        binary = args.general_executable
    elif system == "Darwin":
        binary = "/Applications/MuseScore 2.app/Contents/MacOS/mscore"
    else:
        cmd = "where" if system == "Windows" else "which"
        binary = (
            subprocess.check_output([cmd, "mscore"]).decode("utf-8").replace("\n", "")
        )

    if os.path.exists(binary):
        return binary
    else:
        raise ValueError("mscore binary could not be found.")


def execute_musescore(cli_args: list[str]) -> subprocess.Popen[Any]:
    """
    :param cli_args: Command line arguments to call the mscore binary with.
    """
    executable = get_musescore_bin()
    cli_args.insert(0, executable)
    p = subprocess.Popen(cli_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    if p.returncode != 0:
        if p.stderr is not None:
            for line in p.stderr:
                print(line.decode("utf-8"))
            raise ValueError("mscore exits with returncode != 0")
    return p


def re_open(input_file: str) -> None:
    """Open and save a MuseScore file with the ``mscore`` binary under the same
    file path.

    :param input_file: The path (relative or absolute) of a MuseScore file.
    """
    execute_musescore(["-o", input_file, input_file])


def convert_mxl(input_file: str) -> None:
    """
    Convert a MusicXML file into a MuseScore file.

    :param input_file: The path (relative or absolute) of a MusicXML file.
    """
    output_file = input_file.replace(".mxl", ".mscx")
    execute_musescore(["-o", output_file, input_file])
    os.remove(input_file)


# https://github.com/termcolor/termcolor/issues/62
Color = Literal[
    "black",
    "grey",
    "red",
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "light_grey",
    "dark_grey",
    "light_red",
    "light_green",
    "light_yellow",
    "light_blue",
    "light_magenta",
    "light_cyan",
    "white",
]

Highlight = Literal[
    "on_black",
    "on_grey",
    "on_red",
    "on_green",
    "on_yellow",
    "on_blue",
    "on_magenta",
    "on_cyan",
    "on_light_grey",
    "on_dark_grey",
    "on_light_red",
    "on_light_green",
    "on_light_yellow",
    "on_light_blue",
    "on_light_magenta",
    "on_light_cyan",
    "on_white",
]


def color(
    text: str, color: Optional[Color] = None, on_color: Optional[Highlight] = None
) -> str:
    """Wrapper function around ``termcolor.colored()`` to easily turn off and
    on colorized terminal output on the command line.

    Example usage:

    .. code:: Python

        color('“{}”'.format(post[field]), 'yellow')
    """
    settings = get_args()
    if settings.general_colorize:
        return termcolor.colored(text, color, on_color)
    else:
        return text


class xml:
    @staticmethod
    def read(path: str | Path) -> _Element:
        """
        Read an XML file and return the root element.

        :param path: The path to the XML file.
        :return: The root element of the XML file.
        """
        return lxml.etree.parse(path).getroot()

    @staticmethod
    def tostring(element: _Element | _ElementTree) -> str:
        """
        Convert the XML element or tree to a string.

        :param element: The XML element or tree to write.
        :return: None
        """
        # maybe use: xml_declaration=True, pretty_print=True
        # TestFileCompare not passing ...
        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            + lxml.etree.tostring(element, encoding="UTF-8").decode("utf-8")
            + "\n"
        )

    @staticmethod
    def write(path: str | Path, element: _Element | _ElementTree) -> None:
        """
        Write the XML element or tree to the specified file.

        :param path: The path to the file.
        :param element: The XML element or tree to write.
        :return: None
        """
        with open(path, "w") as document:
            document.write(xml.tostring(element))

    @staticmethod
    def find_safe(element: _Element, path: str) -> _Element:
        """
        Find an element in the given XML element using the specified element path.

        :param element: The XML element to search within.
        :param path: The path to the desired element.
        :return: The found element.
        :raises ValueError: If the element is not found.
        """
        result: _Element | None = element.find(path)
        if result is None:
            raise ValueError(f"Path {path} not found in element {element}!")
        return result

    @staticmethod
    def xpath(element: _Element, path: str) -> _Element | None:
        """
        Find the first matching element in the XML tree using XPath.

        :param element: The root element of the XML tree.
        :param path: The XPath expression to search for.
        :return: The first matching element or None if no match is found.
        """
        output: list[_Element] | None = xml.xpathall(element, path)
        if output and len(output) > 0:
            return output[0]

        return None

    @staticmethod
    def xpath_safe(element: _Element, path: str) -> _Element:
        """
        Safely retrieves the first matching XML element using the given XPath expression.

        :param element: The XML element to search within.
        :param path: The XPath expression to match elements.
        :return: The first matching XML element.XPath
        :raises ValueError: If more than one element is found matching the XPath expression.
        """
        output: list[_Element] = xml.xpathall_safe(element, path)
        if len(output) > 1:
            raise ValueError(
                f"XPath “{path}” found more than one element in {element}!"
            )
        return output[0]

    @staticmethod
    def xpathall(element: _Element, path: str) -> list[_Element] | None:
        """
        Returns a list of elements matching the given XPath expression.

        :param element: The XML element to search within.
        :param path: The XPath expression to match elements.
        :return: A list of elements matching the XPath expression, or None if no
          elements are found.
        """
        result: _XPathObject = element.xpath(path)
        output: list[_Element] = []

        if isinstance(result, list):
            for item in result:
                if isinstance(item, _Element):
                    output.append(item)

        if len(output) > 0:
            return output

        return None

    @staticmethod
    def xpathall_safe(element: _Element, path: str) -> list[_Element]:
        """
        Safely retrieves a list of elements matching the given XPath expression within
        the specified element.

        :param element: The XML element to search within.
        :param path: The XPath expression to match elements.
        :return: A list of elements matching the XPath expression.
        :raises ValueError: If the XPath expression is not found in the element.
        """
        output: list[_Element] | None = xml.xpathall(element, path)
        if output is None:
            raise ValueError(f"XPath “{path}” not found in element {element}!")
        return output

    @staticmethod
    def get_text(element: _Element | None) -> str | None:
        """
        Get the text content of an XML element.

        :param element: The XML element.
        :return: The text content of the XML element, or None if the element is None.
        """
        if element is None:
            return None
        if element.text is None:
            return None
        return element.text

    @staticmethod
    def get_text_safe(element: _Element | None) -> str:
        """
        Safely retrieves the text content from an XML element.

        :param element: The XML element to retrieve the text from.
        :return: The text content of the element.
        :raises ValueError: If the element is None or has no text content.
        """
        if element is None or element.text is None:
            raise ValueError(f"Element {element} has no text!")
        return element.text

    @staticmethod
    def set_text(element: _Element, path: str, value: str | int | float) -> None:
        """
        Set the text value of an XML element at the specified element path.

        :param element: The XML element to modify.
        :param path: The element path expression to locate the target element.
        :param value: The new value to set for the element's text.
        :return: None
        """
        xml.find_safe(element, path).text = str(value)

    @staticmethod
    def remove(element: _Element | None) -> None:
        """
        Remove the given element from its parent.

        :param element: The element to be removed.
        """
        if element is None:
            return None

        parent: _Element | None = element.getparent()
        if parent is None:
            return None

        parent.remove(element)

    @staticmethod
    def create_element(tag_name: str) -> _Element:
        return lxml.etree.Element(tag_name)

    @staticmethod
    def create_sub_element(
        parrent: _Element, tag_name: str, text: Optional[str] = None
    ) -> _Element:
        element: _Element = lxml.etree.SubElement(parrent, tag_name)
        if text:
            element.text = text
        return element


class PathChanger:
    path: Path

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    @property
    def extension(self) -> str:
        return str(self.path).split(".")[-1].lower()

    @property
    def base(self) -> str:
        return str(self.path)[0 : -len(self.extension) - 1]

    def new(self) -> PathChanger:
        return PathChanger(self.path)

    def change_extension(self, new_extension: str) -> Path:
        return Path(str(self.path)[0 : -len(self.extension) - 1] + "." + new_extension)

    def add_suffix(self, suffix: str) -> Path:
        return Path(
            str(self.path)[0 : -len(self.extension) - 1]
            + "_"
            + suffix
            + "."
            + self.extension
        )

    def change(
        self, suffix: Optional[str] = None, extension: Optional[str] = None
    ) -> Path:
        path_changer: PathChanger = self.new()
        if suffix:
            path_changer = PathChanger(path_changer.add_suffix(suffix))
        if extension:
            path_changer = PathChanger(path_changer.change_extension(extension))
        return Path(path_changer.path)


def change_path(
    path: str | Path, suffix: Optional[str] = None, extension: Optional[str] = None
) -> Path:
    return PathChanger(path).change(suffix=suffix, extension=extension)


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

    xml_file: Path
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
                            self.xml_file = abs_path
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
