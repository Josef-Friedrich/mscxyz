"""A collection of useful utility functions"""

from __future__ import annotations  # For subprocess.Popen[Any]

import fnmatch
import os
import platform
import string
import subprocess
import typing
from pathlib import Path
from typing import Any, List, Literal, Optional

import lxml
import lxml.etree
import termcolor
from lxml.etree import _Element, _ElementTree

from mscxyz.settings import DefaultArguments

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


def get_args() -> DefaultArguments:
    """Get the ``args`` object (the ``argparse`` object) which is stored in
    the .settings.py submodule for all other submodules.

    :return: the ``argparse`` object
    """
    from mscxyz import settings

    return getattr(settings, "args")


def set_args(args: DefaultArguments) -> DefaultArguments:
    """Set the ``args`` object (the ``argparse`` object) which is stored in
    the .settings.py submodule for all other submodules to import.
    """
    from mscxyz import settings

    setattr(settings, "args", args)
    return args


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
        binary = subprocess.check_output([cmd, "mscore"])
        binary = binary.decode("utf-8")
        binary = binary.replace("\n", "")

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
        return lxml.etree.parse(path).getroot()

    @staticmethod
    def write(path: str | Path, element: _Element | _ElementTree) -> None:
        with open(path, "w") as document:
            # maybe use: xml_declaration=True, pretty_print=True
            # TestFileCompare not passing ...
            document.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            document.write(
                lxml.etree.tostring(element, encoding="UTF-8").decode("utf-8")
            )
            document.write("\n")

    @staticmethod
    def find_safe(element: _Element, path: str) -> _Element:
        result: _Element | None = element.find(path)
        if result is None:
            raise ValueError(f"Path {path} not found in element {element}!")
        return result

    @staticmethod
    def xpath(element: _Element, path: str) -> _Element | None:
        output: list[_Element] | None = xml.xpathall(element, path)
        if output and len(output) > 0:
            return output[0]

        return None

    @staticmethod
    def xpath_safe(element: _Element, path: str) -> _Element:
        output: list[_Element] = xml.xpathall_safe(element, path)
        if len(output) > 1:
            raise ValueError(
                f"XPath “{path}” found more than one element in {element}!"
            )
        return output[0]

    @staticmethod
    def xpathall(element: _Element, path: str) -> list[_Element] | None:
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
        output: list[_Element] | None = xml.xpathall(element, path)
        if output is None:
            raise ValueError(f"XPath “{path}” not found in element {element}!")
        return output

    @staticmethod
    def text(element: _Element | None) -> str | None:
        if element is None:
            return None
        if element.text is None:
            return None
        return element.text
