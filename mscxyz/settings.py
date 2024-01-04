"""This submodule provides default parameters for args. Here is the
``args`` object stored from ``argparse``. It can be accessed by the other
submodules using the function `get_args()`."""

from __future__ import annotations

from io import TextIOWrapper
from typing import Literal, Optional


class DefaultArguments:
    general_backup: bool = False
    general_colorize: bool = False
    general_config_file: Optional[str] = None
    general_dry_run: bool = False
    general_executable: Optional[str] = None
    general_glob: str = "*.mscx"
    general_mscore: bool = False
    general_verbose: int = 0

    subcommand: Optional[
        Literal["clean", "export", "help", "lyrics", "meta", "rename", "style"]
    ] = None

    # clean
    clean_style: Optional[TextIOWrapper] = None

    # export
    export_extension: Optional[str] = None

    # help
    help_markdown: bool = False
    help_rst: bool = False

    # lyrics
    lyrics_extract: str = "all"
    lyrics_fix: bool = False
    lyrics_remap: Optional[str] = None

    # meta
    meta_clean: Optional[str] = None
    meta_delete: bool = False
    meta_dist: Optional[list[list[str]]] = None
    meta_log: Optional[list[str]] = None
    meta_json: bool = False
    meta_sync: bool = False
    meta_set: Optional[list[list[str]]] = None

    # rename
    rename_alphanum = False
    rename_ascii = False
    rename_format: str = "$combined_title ($combined_composer)"
    rename_no_whitespace = False
    rename_skip: Optional[str] = None
    rename_target: Optional[str] = None

    # style
    style_list_3: bool = False
    style_list_4: bool = False
    style_set: Optional[list[list[str]]] = None

    path: str = "."


args = DefaultArguments()


def reset_args() -> DefaultArguments:
    """Reset the ``args`` object (the ``argparse`` object) which is stored in
    the .settings.py submodule for all other submodules to import.
    """
    global args
    args = DefaultArguments()
    return args
