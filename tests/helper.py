"""Score for various tests"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from typing import Optional, Sequence, Union

from lxml.etree import _Element

from mscxyz import Score
from mscxyz.cli import execute
from mscxyz.cli_legacy import execute as execute_legacy
from mscxyz.lyrics import Lyrics
from mscxyz.meta import Meta
from mscxyz.style import Style

test_dir = os.path.dirname(os.path.abspath(__file__))
ini_file = os.path.join(test_dir, "mscxyz.ini")

mscore_executable: str | None = shutil.which("mscore")
# mscore_executable: str | None = None


def get_path(filename: str, version: int = 2) -> Path:
    """
    Returns the path of a file based on the given filename and version.

    :param filename: The name of the file.
    :param version: The version of the file (default is 2).
    :return: The path of the file.
    """

    if version > 3 and filename.endswith(".mscx"):
        base = filename[:-5]
        filename = str(Path(base) / filename)
    return Path(test_dir) / "files" / "by_version" / str(version) / filename


def get_dir(dirname: str, version: int = 2) -> str:
    """
    Get a temporary directory containing a copy of the specified directory.

    :param dirname: The name of the directory to copy.
    :param version: The version of the directory to copy (default is 2).
    :return: The path of the temporary directory.
    """
    orig: Path = get_path(dirname, version)
    tmp: str = tempfile.mkdtemp()
    shutil.copytree(orig, tmp, dirs_exist_ok=True)
    return tmp


def get_file(filename: str, version: int = 2) -> str:
    """
    Returns the path of a temporary file created by copying the original file.

    :param filename: The name of the file relative to ``tests/files/by_version/X`` to be copied.
    :param version: The version of the file, defaults to 2.
    :return: The path of the temporary file.
    """
    orig: Path = get_path(filename, version)
    tmp_dir: str = tempfile.mkdtemp()
    tmp: str = os.path.join(tmp_dir, filename)
    shutil.copyfile(orig, tmp)
    return tmp


def get_score(filename: str, version: int = 2) -> Score:
    return Score(get_file(filename, version))


def get_meta(filename: str, version: int = 2) -> Meta:
    return get_score(filename, version).meta


def get_lyrics(filename: str, version: int = 2) -> Lyrics:
    return get_score(filename, version).lyrics


def get_style(filename: str, version: int = 2) -> Style:
    return get_score(filename, version).style


def get_xml_root(filename: str, version: int = 2) -> _Element:
    """
    Get the XML tree from the specified file.

    :param filename: The name of the file relative to ``tests/files/by_version/X`` to be copied.
    :param version: The version of the file (default is 2).
    :return: The XML tree.
    """
    return get_score(filename, version).xml_root


def reload(src: Score | str | Path) -> Score:
    if isinstance(src, str) or isinstance(src, Path):
        return Score(src)
    return Score(src.path)


def read_file(filename: str | Path) -> str:
    tmp = open(filename)
    output = tmp.read()
    tmp.close()
    return output


def get_file_type(file: str | Path) -> str:
    """Get the type of a file using the `file` command."""
    output: str = subprocess.check_output(
        ("file", "--brief", "--mime", file), encoding="utf-8"
    )
    return output.split(";")[0]


def assert_file_type(file: str | Path, expected: str) -> None:
    """Assert that the type of a file is equal to the expected type."""
    assert get_file_type(file) == expected


CliArg = Union[str, Path, Score]


def __stringify_args(args: Sequence[CliArg]) -> list[str]:
    result: list[str] = []
    for arg in args:
        if isinstance(arg, Path):
            result.append(str(arg))
        elif isinstance(arg, Score):
            result.append(str(arg.path))
        else:
            result.append(arg)
    return result


def __simluate_cli(*args: CliArg) -> None:
    execute(__stringify_args(args))


def cli_legacy(*args: CliArg) -> None:
    execute_legacy(__stringify_args(args))


def stderr(*cli_args: CliArg) -> str:
    f = StringIO()
    with redirect_stderr(f):
        __simluate_cli(*cli_args)
    return f.getvalue()


def stdout(*cli_args: CliArg) -> str:
    f = StringIO()
    with redirect_stdout(f):
        __simluate_cli(*cli_args)
    return f.getvalue()


def cli(*cli_args: CliArg) -> None:
    """
    TODO replacie with cli_on_score
    """
    __simluate_cli(*cli_args)


def cli_on_score(*cli_args: CliArg) -> Score:
    """
    TODO rename to cli?

    By default a version 4 score object (score.mscz) is appened to the args list.

    :returns: A reloaded score object.
    """
    args = list(cli_args)
    if not isinstance(args[-1], Score):
        score: Score = get_score("score.mscz", version=4)
        args.append(score)
    else:
        score = args[-1]
    __simluate_cli(*args)
    return score.reload()


class Cli:
    __args: list[CliArg]
    __score_old: Optional[Score] = None
    __score: Optional[Score] = None
    __executed: bool = False
    __stdout: Optional[str] = None
    __stderr: Optional[str] = None
    __returncode: int

    def __init__(self, *args: CliArg, append_score: bool = True) -> None:
        self.__args = list(args)
        last = self.__args[-1]

        if not append_score:
            return

        if isinstance(last, Score):
            self.__score_old = last
            self.__score = last
            return

        if not (isinstance(last, str) and Path(last).exists()) and not isinstance(
            last, Score
        ):
            self.__score_old = get_score("score.mscz", version=4)
            self.__score = self.__score_old
            self.__args.append(self.__score)

    @property
    def __stringified_args(self) -> list[str]:
        result: list[str] = []
        for arg in self.__args:
            if isinstance(arg, Path):
                result.append(str(arg))
            elif isinstance(arg, Score):
                result.append(str(arg.path))
            else:
                result.append(arg)
        return result

    @property
    def score_old(self) -> Score:
        if self.__score_old is None:
            raise Exception("No score object")
        return self.__score_old

    def __execute(self) -> None:
        if not self.__executed:
            stdout = StringIO()
            stderr = StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                execute(self.__stringified_args)
            if self.__score is not None:
                self.__score = self.__score.reload()
            self.__stdout = stdout.getvalue()
            self.__stderr = stderr.getvalue()
            self.__executed = True

    def score(self) -> Score:
        self.__execute()
        if self.__score is None:
            raise Exception("No score object")
        return self.__score

    def stdout(self) -> str:
        self.__execute()
        if self.__stdout is None:
            raise Exception("No stdout")
        return self.__stdout

    def stderr(self) -> str:
        self.__execute()
        if self.__stderr is None:
            raise Exception("No stderr")
        return self.__stderr

    def sysexit(self) -> str:
        if not self.__executed:
            result = subprocess.run(
                ["musescore-manager"] + self.__stringified_args,
                capture_output=True,
                encoding="utf-8",
            )
            self.__returncode = result.returncode
            self.__stderr = result.stderr
            self.__stdout = result.stdout
            self.__executed = True
        if self.__stdout is None or self.__stderr is None:
            raise Exception("No stdout or stderr")
        return self.__stderr + self.__stdout


def sysexit(*cli_args: CliArg) -> str:
    result = subprocess.run(
        ["musescore-manager"] + __stringify_args(cli_args),
        capture_output=True,
        encoding="utf-8",
    )
    return result.stderr + result.stdout


def run(*args: str) -> str:
    """
    Run the mscx-manager command on the command line with the given arguments
    and return the output as a string.

    :param args: The arguments to pass to the mscx-manager command.
    :return: The output of the mscx-manager command as a string.
    """
    return subprocess.check_output(["mscx-manager"] + list(args)).decode("utf-8")


def open_in_gui(file: str | Path) -> None:
    """Open a file wiht xdg-open in the background"""
    subprocess.Popen(("/usr/local/bin/mscore", str(file)))
