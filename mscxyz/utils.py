"""A collection of useful utility functions"""

from __future__ import annotations  # For subprocess.Popen[Any]

import fnmatch
import os
import platform
import string
import subprocess
import tempfile
import zipfile
from os import PathLike
from pathlib import Path
from typing import Any, Generator, List, Literal, Optional, Union

import termcolor

from mscxyz.settings import get_args
from mscxyz.xml import XmlManipulator

ListExtension = Literal["mscz", "mscx", "both"]
PathOrStr = Union[PathLike[str], str, Path]


INCH = 25.4


def list_path(
    src: PathOrStr | list[PathOrStr],
    extension: ListExtension = "both",
    glob: Optional[str] = None,
) -> Generator[Path, None, None]:
    """List all scores in path.

    :param src: A directory to search for files or a file path or multiple directories or paths.
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

    if not isinstance(src, list):
        src = [src]

    for s in src:
        path = Path(s)
        if path.is_file() and fnmatch.fnmatch(str(s), glob):
            yield path
        elif path.is_dir():
            for root, _, files in os.walk(path):
                for file in files:
                    relpath = Path(root) / file
                    if fnmatch.fnmatch(str(relpath), glob):
                        yield relpath


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
    # https://doc.qt.io/qt-5/qguiapplication.html#supported-command-line-options
    # https://doc.qt.io/qt-5/qguiapplication.html#platformName-prop
    # cli_args = [executable, "-platform", "offscreen"] + cli_args
    cli_args = [executable] + cli_args

    p = subprocess.Popen(
        cli_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
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


def round_float(value: str | int | float) -> float:
    return float(round(float(value), 4))


Unit = Literal["mm", "in"]


class Dimension:
    value: float

    unit: Unit

    def __init__(self, value: str) -> None:
        self.value, self.unit = Dimension.parse(value)

    @staticmethod
    def parse(dimension: str) -> tuple[float, Unit]:
        unit: str = dimension[-2:]
        unit = unit.lower()
        if unit not in ("mm", "in"):
            raise ValueError(f"Unknown unit: {unit}. Allowed are mm and in.")
        value = float(dimension[:-2])
        return (value, unit)  # type: ignore

    @staticmethod
    def convert(value: float, from_unit: Unit, to_unit: Unit) -> float:
        if from_unit == "in" and to_unit == "mm":
            value = value * INCH
        elif from_unit == "mm" and to_unit == "in":
            value = value / INCH
        return value

    def to(self, unit: Unit) -> float:
        return Dimension.convert(self.value, self.unit, unit)


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


def colorize(
    text: str, color: Optional[Color] = None, on_color: Optional[Highlight] = None
) -> str:
    """Wrapper function around ``termcolor.colored()`` to easily turn off and
    on colorized terminal output on the command line.

    Example usage:

    .. code:: Python

        color('“{}”'.format(post[field]), 'yellow')
    """
    settings = get_args()
    if settings.info_color:
        return termcolor.colored(text, color, on_color)
    else:
        return text


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

    def add_suffix(self, suffix: Any) -> Path:
        return Path(
            str(self.path)[0 : -len(self.extension) - 1] + f"_{suffix}.{self.extension}"
        )

    def change(
        self,
        suffix: Optional[Any] = None,
        extension: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> Path:
        if filename is not None:
            return self.path.parent / filename
        path_changer: PathChanger = self.new()
        if suffix:
            path_changer = PathChanger(path_changer.add_suffix(suffix))
        if extension:
            path_changer = PathChanger(path_changer.change_extension(extension))
        return Path(path_changer.path)


def change_path(
    path: str | Path, suffix: Optional[Any] = None, extension: Optional[str] = None
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

        xml = XmlManipulator(file_path=self.tmp_dir / "META-INF" / "container.xml")

        for root_file in xml.findall(".//rootfiles/rootfile"):
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


def read_file(filename: str | Path) -> str:
    """Read the file as text.

    :return: The content of file as text.
    """
    with open(filename, "r") as f:
        return f.read()
