"""A command line tool to manipulate the XML based mscX and mscZ
files of the notation software MuseScore.
"""

from __future__ import annotations

import configparser
import importlib
import os
import sys
import typing
from importlib import metadata
from typing import Optional, Type

import lxml
import lxml.etree
from lxml.etree import LxmlError

import mscxyz
import mscxyz.lyrics
import mscxyz.meta
import mscxyz.score
import mscxyz.style
from mscxyz import cli, utils
from mscxyz.rename import rename_filename
from mscxyz.settings import DefaultArguments

__version__: str = metadata.version("mscxyz")

Score = mscxyz.score.Score

Lyrics = mscxyz.lyrics.Lyrics

Meta = mscxyz.meta.Meta

Style = mscxyz.style.Style

list_scores = utils.list_scores


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


def heading(args: DefaultArguments, text: str, level: int = 1) -> None:
    length = len(text)
    if args.help_markdown:
        print("\n" + ("#" * level) + " " + text + "\n")
    elif args.help_rst:
        if level == 1:
            underline = "="
        elif level == 2:
            underline = "-"
        elif level == 3:
            underline = "^"
        elif level == 4:
            underline = '"'
        else:
            underline = "-"
        print("\n" + text + "\n" + (underline * length) + "\n")
    else:
        print(text)


def code_block(args: DefaultArguments, text: str) -> None:
    if args.help_markdown:
        print("```\n" + text + "\n```")
    elif args.help_rst:
        print(".. code-block:: text\n\n  " + text.replace("\n", "\n  "))
    else:
        print(text)


def show_all_help(args: DefaultArguments) -> None:
    subcommands = ("clean", "meta", "lyrics", "rename", "export", "help")

    if args.path == "all":
        heading(args, "mscxyz", 1)
        code_block(args, cli.parser.format_help())

        heading(args, "Subcommands", 1)

        for subcommand in subcommands:
            command = getattr(cli, "sub_" + subcommand)
            heading(args, command.prog, 2)
            code_block(args, command.format_help())

    else:
        code_block(args, getattr(cli, args.path).format_help())


def report_errors(errors: list[Exception]) -> None:
    for error in errors:
        msg = ""

        if isinstance(error, SyntaxError):
            msg = error.msg

        print(
            "{}: {}; message: {}".format(
                utils.color("Error", "white", "on_red"),
                utils.color(error.__class__.__name__, "red"),
                msg,
            )
        )


def no_error(error: Type[LxmlError], errors: list[Exception]) -> bool:
    for e in errors:
        if isinstance(e, error):
            return False
    return True


def execute(cli_args: typing.Sequence[str] | None = None) -> None:
    args: DefaultArguments = typing.cast(
        DefaultArguments, cli.parser.parse_args(cli_args)
    )
    if args.general_config_file:
        config = parse_config_ini(args.general_config_file)
        if config:
            args = merge_config_into_args(config, args)
    utils.set_args(args)

    if args.subcommand == "help":
        show_all_help(args)
        sys.exit()

    files = utils.list_scores(path=args.path, glob=args.general_glob)

    for file in files:
        print("\n" + utils.color(file, "red"))

        if args.general_backup:
            score = Score(file)
            score.backup()

        if args.subcommand == "clean":
            score = Score(file)
            print(score.filename)
            score.clean()
            if args.clean_style:
                score.style.merge(styles=args.clean_style.name)
            score.save(mscore=args.general_mscore)

        elif args.subcommand == "lyrics":
            score = Score(file)
            if args.lyrics_remap:
                score.lyrics.remap(
                    remap_string=args.lyrics_remap, mscore=args.general_mscore
                )
            elif args.lyrics_fix:
                score.lyrics.fix_lyrics(mscore=args.general_mscore)
            else:
                score.lyrics.extract_lyrics(
                    number=args.lyrics_extract, mscore=args.general_mscore
                )

        elif args.subcommand == "meta":
            score = Score(file)
            if no_error(lxml.etree.XMLSyntaxError, score.errors):
                pre: dict[str, str] = score.meta.interface.export_to_dict()
                if args.meta_clean:
                    score.meta.clean_metadata(fields_spec=args.meta_clean)
                if args.meta_json:
                    score.meta.export_json()
                if args.meta_dist:
                    for a in args.meta_dist:
                        score.meta.distribute_field(
                            source_fields=a[0], format_string=a[1]
                        )
                if args.meta_set:
                    for a in args.meta_set:
                        score.meta.set_field(destination_field=a[0], format_string=a[1])
                if args.meta_delete:
                    score.meta.delete_duplicates()
                if args.meta_sync:
                    score.meta.sync_fields()
                if args.meta_log:
                    score.meta.write_to_log_file(args.meta_log[0], args.meta_log[1])
                post: dict[str, str] = score.meta.interface.export_to_dict()
                score.meta.show(pre, post)
                if not args.general_dry_run and not score.errors and pre != post:
                    score.save(mscore=args.general_mscore)

        elif args.subcommand == "rename":
            score = rename_filename(file)

        elif args.subcommand == "export":
            score = Score(file)
            if args.export_extension:
                score.export.to_extension(extension=args.export_extension)
            else:
                score.export.to_extension()
        elif args.subcommand == "style":
            score = Score(file)

            if args.style_list_3 or args.style_list_4:

                def list_styles(version: int) -> None:
                    """There are many styles in MuseScore. We dynamically
                    import the module to avoid long load time"""
                    style_names = importlib.import_module(
                        "mscxyz.style_names", package=None
                    )
                    style_names.list_styles(version)
                    sys.exit()

                if args.style_list_3:
                    list_styles(3)
                if args.style_list_4:
                    list_styles(3)

            if args.style_set:
                for a in args.style_set:
                    score.style.set_value(a[0], a[1])
            score.save()
        else:
            raise ValueError("Unknown subcommand")

        report_errors(score.errors)


if __name__ == "__main__":
    execute()
