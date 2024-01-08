"""Wrapper for the command line interface."""

from __future__ import annotations

import argparse
import importlib
import sys
import textwrap
import typing
from typing import Type

import lxml
import lxml.etree
import tmep
from lxml.etree import LxmlError

import mscxyz.settings as settings
from mscxyz import Score, cli_legacy, utils
from mscxyz.meta import Interface, InterfaceReadWrite
from mscxyz.rename import rename_filename


def list_fields(
    fields: typing.Sequence[str], prefix: str = "", suffix: str = ""
) -> str:
    out: list[str] = []
    for field in fields:
        out.append(prefix + "- " + field + suffix)
    return "\n".join(out)


class LineWrapRawTextHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """https://stackoverflow.com/a/35925919"""

    def __init__(self, prog: typing.Text) -> None:
        super().__init__(prog, width=80)

    def _split_lines(self, text: typing.Text, width: int) -> typing.List[str]:
        text = self._whitespace_matcher.sub(" ", text).strip()
        return textwrap.wrap(text, 60)


parser = argparse.ArgumentParser(
    description="aaaaaaA command "
    'line tool to manipulate the XML based "*.mscX" and "*.mscZ" '
    "files of the notation software MuseScore.",
    formatter_class=LineWrapRawTextHelpFormatter,
)

###############################################################################
# Global options
###############################################################################

parser.add_argument(
    "-V",
    "--version",
    action="version",
    version="%(prog)s {version}".format(version="0.0.0"),
)

parser.add_argument(
    "-b",
    "--backup",
    dest="general_backup",
    action="store_true",
    help="Create a backup file.",
)


parser.add_argument(
    "-c",
    "--colorize",
    action="store_true",
    dest="general_colorize",
    help="Colorize the command line print statements.",
)

parser.add_argument(
    "-C",
    "--config-file",
    dest="general_config_file",
    help="Specify a configuration file in the INI format.",
)

parser.add_argument(
    "-d",
    "--dry-run",
    action="store_true",
    dest="general_dry_run",
    help="Simulate the actions.",
)

parser.add_argument(
    "-g",
    "--glob",
    dest="general_glob",
    default="*.msc[xz]",
    help='Handle only files which matches against Unix style \
    glob patterns (e. g. "*.mscx", "* - *"). If you omit this \
    option, the standard glob pattern "*.msc[xz]" is used.',
)

parser.add_argument(
    "-m",
    "--mscore",
    action="store_true",
    dest="general_mscore",
    help="Open and save the XML file in MuseScore after manipulating the XML \
    with lxml to avoid differences in the XML structure.",
)

parser.add_argument(
    "--diff",
    action="store_true",
    dest="general_diff",
    help="Show a diff of the XML file before and after the manipulation.",
)

parser.add_argument(
    "-e",
    "--executable",
    dest="general_executable",
    help="Path of the musescore executable.",
    metavar="FILE_PATH",
)

parser.add_argument(
    "-v",
    "--verbose",
    action="count",
    dest="general_verbose",
    default=0,
    help="Make commands more verbose. You can specifiy \
    multiple arguments (. g.: -vvv) to make the command more \
    verbose.",
)

###############################################################################
# subparser in alphabetical order
###############################################################################

subparser = parser.add_subparsers(
    title="Subcommands",
    dest="subcommand",
    help='Run "subcommand --help" for more \
    informations.',
)

###############################################################################
# clean
###############################################################################

sub_clean = subparser.add_parser(
    "clean",
    help='Clean and reset the formating of the "*.mscx" file',
    formatter_class=LineWrapRawTextHelpFormatter,
)

sub_clean.add_argument(
    "-s",
    "--style",
    dest="clean_style",
    type=open,
    help='Load a "*.mss" style file and include the contents of \
    this file.',
)

###############################################################################
# export
###############################################################################

sub_export = subparser.add_parser(
    "export",
    help="Export the scores to PDFs or to a format specified by the \
    extension. The exported file has the same path, only the file extension is \
    different. See \
    https://musescore.org/en/handbook/2/file-formats \
    https://musescore.org/en/handbook/3/file-export \
    https://musescore.org/en/handbook/4/file-export",
    formatter_class=LineWrapRawTextHelpFormatter,
)

sub_export.add_argument(
    "-e",
    "--extension",
    dest="export_extension",
    default="pdf",
    help='Extension to export. If this option \
    is omitted, then the default extension is "pdf".',
)

###############################################################################
# help
###############################################################################

sub_help = subparser.add_parser(
    "help",
    help="Show help. Use “{} help all” to show help \
    messages of all subcommands. Use \
    “{} help <subcommand>” to show only help messages \
    for the given subcommand.".format(parser.prog, parser.prog),
    formatter_class=LineWrapRawTextHelpFormatter,
)

sub_help.add_argument(
    "-m",
    "--markdown",
    dest="help_markdown",
    action="store_true",
    help="Show help in markdown format. \
    This option enables to generate the README file directly \
    form the command line output.",
)

sub_help.add_argument(
    "-r",
    "--rst",
    dest="help_rst",
    action="store_true",
    help="Show help in reStructuresText \
    format. This option enables to generate the README file \
    directly form the command line output.",
)

###############################################################################
# meta
###############################################################################

sub_meta = subparser.add_parser(
    "meta",
    help="Deal with meta data informations stored in the MuseScore file.",
    formatter_class=LineWrapRawTextHelpFormatter,
    description=textwrap.dedent(
        """\
    MuseScore can store meta data informations in different places:

    # metatag

    ## XML structure of a meta tag:

        <metaTag name="tag"></metaTag>

    ## All meta tags:

        - arranger
        - composer
        - copyright
        - creationDate
        - lyricist
        - movementNumber
        - movementTitle
        - platform
        - poet
        - source
        - translator
        - workNumber
        - workTitle

    # vbox

    ## XML structure of a vbox tag:

        <VBox>
          <Text>
            <style>Title</style>
            <text>Some title text</text>
            </Text>

    ## All vbox tags:

        - Title
        - Subtitle
        - Composer
        - Lyricist

    This command line tool bundles some meta data informations:

    # Combined meta data fields:

        - title (1. vbox_title 2. metatag_work_title)
        - subtitle (1. vbox_subtitle 2. metatag_movement_title)
        - composer (1. vbox_composer 2. metatag_composer)
        - lyricist (1. vbox_lyricist 2. metatag_lyricist)

    You have access to all this metadata fields through following fields:"""
    )
    + "\n\n"
    + list_fields(InterfaceReadWrite.get_all_fields(), prefix="    "),
)

sub_meta.add_argument(
    "-c",
    "--clean",
    dest="meta_clean",
    help="Clean the meta data fields. Possible values: „all“ or \
    „field_one,field_two“.",
)

sub_meta.add_argument(
    "-D",
    "--delete-duplicates",
    dest="meta_delete",
    action="store_true",
    help="Deletes combined_lyricist if this field is equal to "
    "combined_composer. Deletes combined_subtitle if this field is equal to"
    "combined_title. Move combined_subtitle to combimed_title if "
    "combined_title is empty.",
)

sub_meta.add_argument(
    "-d",
    "--distribute-fields",
    dest="meta_dist",
    action="append",
    nargs=2,
    metavar=("SOURCE_FIELDS", "FORMAT_STRING"),
    help="Distribute source fields to target fields applying a format string \
    on the source fields. It is possible to apply multiple \
    --distribute-fields options. SOURCE_FIELDS can be a single field or a \
    comma separated list of fields: field_one,field_two. The program \
    tries first to match the FORMAT_STRING on the first source field. If this\
    fails, it tries the second source field ... an so on.",
)

sub_meta.add_argument(
    "-j",
    "--json",
    action="store_true",
    dest="meta_json",
    help="Additionally write the meta data to a json file.",
)

sub_meta.add_argument(
    "-l",
    "--log",
    nargs=2,
    metavar=("DESTINATION", "FORMAT_STRING"),
    dest="meta_log",
    help="Write one line per file to a text file. e. g. --log "
    "/tmp/musescore-manager.log '$title $composer'",
)

sub_meta.add_argument(
    "-s",
    "--synchronize",
    action="store_true",
    dest="meta_sync",
    help="Synchronize the values of the first vertical frame (vbox) \
    (title, subtitle, composer, lyricist) with the corresponding \
    metadata fields",
)

sub_meta.add_argument(
    "-S",
    "--set-field",
    nargs=2,
    action="append",
    metavar=("DESTINATION_FIELD", "FORMAT_STRING"),
    dest="meta_set",
    help="Set value to meta data fields.",
)

###############################################################################
# lyrics
###############################################################################

sub_lyrics = subparser.add_parser(
    "lyrics",
    help="Extract lyrics. Without any option this subcommand \
    extracts all lyrics verses into separate mscx files. \
    This generated mscx files contain only one verse. The old \
    verse number is appended to the file name, e. g.: \
    score_1.mscx.",
    formatter_class=LineWrapRawTextHelpFormatter,
)

sub_lyrics.add_argument(
    "-e",
    "--extract",
    dest="lyrics_extract_legacy",
    default="all",
    help='The lyric verse number to extract or "all".',
)

sub_lyrics.add_argument(
    "-r",
    "--remap",
    dest="lyrics_remap",
    help='Remap lyrics. Example: "--remap 3:2,5:3". This \
    example remaps lyrics verse 3 to verse 2 and verse 5 to 3. \
    Use commas to specify multiple remap pairs. One remap pair \
    is separated by a colon in this form: "old:new": "old" \
    stands for the old verse number. "new" stands for the new \
    verse number.',
)

sub_lyrics.add_argument(
    "-f",
    "--fix",
    action="store_true",
    dest="lyrics_fix",
    help='Fix lyrics: Convert trailing hyphens ("la- la- la") \
    to a correct hyphenation ("la - la - la")',
)

###############################################################################
# rename
###############################################################################

sub_rename = subparser.add_parser(
    "rename",
    help='Rename the "*.mscx" files.',
    formatter_class=LineWrapRawTextHelpFormatter,
    description="Fields and functions you can use in the format "
    "string (-f, --format):\n\n"
    "Fields\n======\n\n{}\n\n"
    "Functions\n=========\n\n{}".format(
        list_fields(Interface.get_all_fields(), prefix="    "), tmep.get_doc()
    ),
)

sub_rename.add_argument(
    "-f",
    "--format",
    dest="rename_format",
    default="$combined_title ($combined_composer)",
    help="Format string.",
)

sub_rename.add_argument(
    "-A",
    "--alphanum",
    dest="rename_alphanum",
    action="store_true",
    help="Use only alphanumeric characters.",
)

sub_rename.add_argument(
    "-a",
    "--ascii",
    dest="rename_ascii",
    action="store_true",
    help="Use only ASCII characters.",
)

sub_rename.add_argument(
    "-n",
    "--no-whitespace",
    dest="rename_no_whitespace",
    action="store_true",
    help="Replace all whitespaces with dashes or \
    sometimes underlines.",
)

sub_rename.add_argument(
    "-s",
    "--skip-if-empty",
    dest="rename_skip",
    metavar="FIELDS",
    help="Skip rename action if FIELDS are empty. Separate FIELDS using \
    commas: combined_composer,combined_title",
)

sub_rename.add_argument(
    "-t",
    "--target",
    dest="rename_target",
    help="Target directory",
)

###############################################################################
# style
###############################################################################

sub_style = subparser.add_parser(
    "style", help="Change the styles.", formatter_class=LineWrapRawTextHelpFormatter
)

sub_style.add_argument(
    "--list-3",
    dest="style_list_3",
    action="store_true",
    help="List all possible version 3 styles.",
)

sub_style.add_argument(
    "--list-4",
    dest="style_list_4",
    action="store_true",
    help="List all possible version 4 styles.",
)

sub_style.add_argument(
    "-y",
    "--set-style",
    nargs=2,
    action="append",
    metavar=("STYLE", "VALUE"),
    dest="style_set",
    help="Set a single style. For example: --set-style pageWidth 8.5",
)


###############################################################################
# last positional parameter
###############################################################################

parser.add_argument(
    "path",
    help='Path to a *.msc[zx]" file \
    or a folder which contains "*.msc[zx]" files. In conjunction \
    with the subcommand "help" this positional parameter \
    accepts the names of all other subcommands or the word \
    "all".',
)


def heading(args: settings.DefaultArguments, text: str, level: int = 1) -> None:
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


def code_block(args: settings.DefaultArguments, text: str) -> None:
    if args.help_markdown:
        print("```\n" + text + "\n```")
    elif args.help_rst:
        print(".. code-block:: text\n\n  " + text.replace("\n", "\n  "))
    else:
        print(text)


def show_all_help(args: settings.DefaultArguments) -> None:
    subcommands = ("clean", "meta", "lyrics", "rename", "export", "help")

    if args.path == "all":
        heading(args, "mscxyz", 1)
        code_block(args, cli_legacy.parser.format_help())

        heading(args, "Subcommands", 1)

        for subcommand in subcommands:
            command = getattr(cli_legacy, "sub_" + subcommand)
            heading(args, command.prog, 2)
            code_block(args, command.format_help())

    else:
        code_block(args, getattr(cli_legacy, args.path).format_help())


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
    args: settings.DefaultArguments = typing.cast(
        settings.DefaultArguments, cli_legacy.parser.parse_args(cli_args)
    )
    if args.general_config_file:
        config = settings.parse_config_ini(args.general_config_file)
        if config:
            args = settings.merge_config_into_args(config, args)
    settings.set_args(args)

    if args.subcommand == "help":
        show_all_help(args)
        sys.exit()

    files = utils.list_score_paths(path=args.path, glob=args.general_glob)

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
                score.style.load_style_file(args.clean_style.name)
            score.save(mscore=args.general_mscore)

        elif args.subcommand == "lyrics":
            score = Score(file)
            if args.lyrics_remap:
                score.lyrics.remap(remap_string=args.lyrics_remap)
                score.save(mscore=args.general_mscore)
            elif args.lyrics_fix:
                score.lyrics.fix_lyrics(mscore=args.general_mscore)
            else:
                no: int | None = None
                if args.lyrics_extract_legacy != "all":
                    no = int(args.lyrics_extract_legacy)
                score.lyrics.extract_lyrics(no)

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

                if args.general_diff:
                    score.print_diff()

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
