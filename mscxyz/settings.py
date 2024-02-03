"""This submodule provides default parameters for args. Here is the
``args`` object stored from ``argparse``. It can be accessed by the other
submodules using the function `get_args()`."""

from __future__ import annotations

import argparse
import configparser
import os
from io import TextIOWrapper
from typing import Optional, Sequence, cast


class DefaultArguments:
    general_backup: bool = False
    general_bail: bool = False
    general_colorize: bool = False
    general_config_file: Optional[str] = None
    general_diff: bool = False
    general_dry_run: bool = False
    general_executable: Optional[str] = None
    general_mscore: bool = False

    general_verbose: int = 0

    # Groups alphabetically
    # in groups related not alphabetically
    # keep Order in sync with cli.py

    # export
    export_extension: Optional[str] = None
    export_compress: bool = False

    # help
    help_markdown: bool = False
    help_rst: bool = False

    # lyrics
    lyrics_extract: Optional[str] = None
    lyrics_fix: bool = False
    lyrics_remap: Optional[str] = None

    # meta
    meta_clean: Optional[str] = None
    meta_delete: bool = False
    meta_dist: Optional[list[tuple[str, str]]] = None
    meta_log: Optional[list[str]] = None
    meta_json: bool = False
    meta_sync: bool = False
    meta_set: Optional[list[tuple[str, str]]] = None
    meta_metatag: Optional[list[tuple[str, str]]] = None
    meta_vbox: Optional[list[tuple[str, str]]] = None
    meta_combined: Optional[list[tuple[str, str]]] = None
    meta_title: Optional[str] = None
    meta_subtitle: Optional[str] = None
    meta_composer: Optional[str] = None
    meta_lyricist: Optional[str] = None

    # rename
    rename_rename: Optional[str] = None
    rename_target: Optional[str] = None
    rename_only_filename: bool = False
    rename_alphanum: bool = False
    rename_ascii: bool = False
    rename_no_whitespace = False
    rename_skip: Optional[str] = None

    # selection
    selection_list: bool = False
    selection_glob: str = "*.mscx"
    selection_mscz: bool = False
    selection_mscx: bool = False

    # style
    style_value: list[tuple[str, str]] = []
    style_clean: bool = False
    style_file: Optional[TextIOWrapper] = None
    style_styles_v3: bool = False
    style_styles_v4: bool = False
    style_list_fonts: bool = False
    style_text_font: Optional[str] = None
    style_title_font: Optional[str] = None
    style_musical_symbol_font: Optional[str] = None
    style_musical_text_font: Optional[str] = None
    style_staff_space: Optional[float] = None
    style_page_size: Optional[tuple[str, str]] = None
    style_page_size_a4: bool = False
    style_page_size_letter: bool = False
    style_margin: Optional[str] = None
    style_show_header: Optional[bool] = None
    style_show_footer: Optional[bool] = None
    style_reset_small_staffs: bool = False

    # positional argument
    path: str = "."


args = DefaultArguments()


def get_args() -> DefaultArguments:
    """Get the ``args`` object (the ``argparse`` object) which is stored in
    the .settings.py submodule for all other submodules.

    :return: the ``argparse`` object
    """
    return args


def set_args(new_args: DefaultArguments) -> DefaultArguments:
    """Set the ``args`` object (the ``argparse`` object) which is stored in
    the .settings.py submodule for all other submodules to import.
    """
    global args
    args = new_args
    return args


def reset_args() -> DefaultArguments:
    """Reset the ``args`` object (the ``argparse`` object) which is stored in
    the .settings.py submodule for all other submodules to import.
    """
    global args
    args = DefaultArguments()
    return args


def parse_config_ini(
    relpath: Optional[str] = None,
) -> Optional[configparser.ConfigParser]:
    """Parse the configuration file. The file format is INI. The default
    location is ``/etc/mscxyz.ini``."""
    if not relpath:
        ini_file = os.path.abspath(os.path.join(os.sep, "etc", "mscxyz.ini"))
    else:
        ini_file = relpath
    config = configparser.ConfigParser()
    if os.path.exists(ini_file):
        config.read(ini_file)
        return config
    return None


def merge_config_into_args(
    config: configparser.ConfigParser, args: DefaultArguments
) -> DefaultArguments:
    for section in config.sections():
        for key, value in config[section].items():
            arg = "{}_{}".format(section, key)
            if not hasattr(args, arg) or not getattr(args, arg):
                setattr(args, arg, value)

    for arg in [
        "general_backup",
        "general_colorize",
        "general_dry_run",
        "general_mscore",
        "help_markdown",
        "help_rst",
        "lyrics_fix",
        "meta_json",
        "meta_sync",
        "rename_alphanum",
        "rename_ascii",
        "rename_no_whitespace",
    ]:
        if hasattr(args, arg):
            value2 = getattr(args, arg)
            if value2 == 1 or value2 == "true" or value2 == "True":
                setattr(args, arg, True)
            else:
                setattr(args, arg, False)

    return args


def parse_args(
    parser: argparse.ArgumentParser, cli_args: Sequence[str] | None = None
) -> DefaultArguments:
    args: DefaultArguments = cast(DefaultArguments, parser.parse_args(cli_args))
    if args.general_config_file:
        config = parse_config_ini(args.general_config_file)
        if config:
            args = merge_config_into_args(config, args)
    set_args(args)

    return args
