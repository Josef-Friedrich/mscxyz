"""Wrapper for the command line interface."""

from __future__ import annotations

import argparse
import importlib
import textwrap
import typing
from typing import Sequence

import shtab
import tmep

import mscxyz.export
from mscxyz import utils
from mscxyz.meta import Metatag, Vbox
from mscxyz.rename import rename
from mscxyz.score import Score
from mscxyz.settings import parse_args
from mscxyz.style import inch, mm


def _embed_fields(
    fields: Sequence[str], prefix: str = " Available fields: ", suffix: str = "."
) -> str:
    joined_fields: str = ", ".join(fields)
    return f"{prefix}{joined_fields}{suffix}"


class LineWrapRawTextHelpFormatter(argparse.RawDescriptionHelpFormatter):
    """https://stackoverflow.com/a/35925919"""

    def __init__(self, prog: typing.Text) -> None:
        super().__init__(prog, width=80)

    def _split_lines(self, text: typing.Text, width: int) -> typing.List[str]:
        text = self._whitespace_matcher.sub(" ", text).strip()
        return textwrap.wrap(text, 60)


file_completers: list[argparse.Action] = []


parser = argparse.ArgumentParser(
    description="The next generation command "
    'line tool to manipulate the XML based "*.mscX" and "*.mscZ" '
    "files of the notation software MuseScore.",
    formatter_class=LineWrapRawTextHelpFormatter,
)

shtab.add_argument_to(parser, ["--print-completion"])

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
    "--bail",
    dest="general_bail",
    action="store_true",
    help="Stop execution when an exception occurs.",
)

parser.add_argument(
    "-k",
    "--colorize",
    action="store_true",
    dest="general_colorize",
    help="Colorize the command line print statements.",
)

file_completers.append(
    parser.add_argument(
        "-C",
        "--config-file",
        dest="general_config_file",
        help="Specify a configuration file in the INI format.",
    )
)

parser.add_argument(
    "-d",
    "--dry-run",
    action="store_true",
    dest="general_dry_run",
    help="Simulate the actions.",
)

parser.add_argument(
    "-m",
    "--mscore",
    action="store_true",
    dest="general_mscore",
    help="Open and save the XML file in MuseScore after manipulating the XML "
    "with lxml to avoid differences in the XML structure.",
)

parser.add_argument(
    "--diff",
    action="store_true",
    dest="general_diff",
    help="Show a diff of the XML file before and after the manipulation.",
)

file_completers.append(
    parser.add_argument(
        "-e",
        "--executable",
        dest="general_executable",
        help="Path of the musescore executable.",
        metavar="FILE_PATH",
    )
)

parser.add_argument(
    "-v",
    "--verbose",
    action="count",
    dest="general_verbose",
    default=0,
    help="Make commands more verbose. You can specifiy "
    "multiple arguments (. g.: -vvv) to make the command more "
    "verbose.",
)


###############################################################################
# groups in alphabetical order
###############################################################################

###############################################################################
# export
###############################################################################

parser.add_argument(
    "-E",
    "--export",
    dest="export_extension",
    choices=mscxyz.export.extensions,
    metavar="<extension>",
    help="Export the scores in a format defined by the extension. The exported file "
    "has the same path, only the file extension is different. Further information "
    "can be found at the MuseScore website: "
    "https://musescore.org/en/handbook/2/file-formats, "
    "https://musescore.org/en/handbook/3/file-export, "
    "https://musescore.org/en/handbook/4/file-export. "
    "MuseScore must be installed and the script must know the location of the "
    "binary file.",
)

###############################################################################
# meta
###############################################################################

group_meta = parser.add_argument_group(
    "meta",
    "Deal with meta data informations stored in the MuseScore file. "
    + textwrap.dedent(
        """\
    MuseScore can store meta data informations in different places:

    # metatag

    ## XML structure of a meta tag:

        <metaTag name="tag"></metaTag>

    ## All meta tags:

    - arranger
    - audioComUrl (new in v4
    - composer
    - copyright
    - creationDate
    - lyricist
    - movementNumber
    - movementTitle
    - mscVersion
    - platform
    - poet (not in v4)
    - source
    - sourceRevisionId
    - subtitle
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

        - title (v2,3: Title)
        - subtitle (v2,3: Subtitle)
        - composer (v2,3: Composer)
        - lyricist (v2,3: Lyricist)

    This command line tool bundles some meta data informations:

    # Combined meta data fields:

        - title (1. vbox_title 2. metatag_work_title)
        - subtitle (1. vbox_subtitle 2. metatag_movement_title)
        - composer (1. vbox_composer 2. metatag_composer)
        - lyricist (1. vbox_lyricist 2. metatag_lyricist)
    """
    ),
)

group_meta.add_argument(
    "-c",
    "--clean-meta",
    dest="meta_clean",
    help="Clean the meta data fields. Possible values: „all“ or a comma separated "
    "list of fields, for example: "
    "„field_one,field_two“.",
)

group_meta.add_argument(
    "-D",
    "--delete-duplicates",
    dest="meta_delete",
    action="store_true",
    help="Deletes combined_lyricist if this field is equal to "
    "combined_composer. Deletes combined_subtitle if this field is equal to"
    "combined_title. Move combined_subtitle to combimed_title if "
    "combined_title is empty.",
)

group_meta.add_argument(
    "-i",
    "--distribute-fields",
    dest="meta_dist",
    action="append",
    nargs=2,
    metavar=("<source-fields>", "<format-string>"),
    help="Distribute source fields to target fields by applying a format string "
    "on the source fields. It is possible to apply multiple "
    "--distribute-fields options. <source-fields> can be a single field or a "
    "comma separated list of fields: field_one,field_two. The program "
    "tries first to match the <format-string> on the first source field. If this"
    "fails, it tries the second source field ... and so on.",
)

group_meta.add_argument(
    "-j",
    "--json",
    action="store_true",
    dest="meta_json",
    help="Write the meta data to a json file. The resulting file has the same "
    "path as the input file, only the extension is changed to “json”.",
)

group_meta.add_argument(
    "-l",
    "--log",
    nargs=2,
    metavar=("<log-file>", "<format-string>"),
    dest="meta_log",
    help="Write one line per file to a text file. e. g. --log "
    "/tmp/musescore-manager.log '$title $composer'",
)

group_meta.add_argument(
    "-y",
    "--synchronize",
    action="store_true",
    dest="meta_sync",
    help="Synchronize the values of the first vertical frame (vbox) "
    "(title, subtitle, composer, lyricist) with the corresponding "
    "metadata fields",
)

group_meta.add_argument(
    "-S",
    "--set-field",
    nargs=2,
    action="append",
    metavar=("DESTINATION_FIELD", "FORMAT_STRING"),
    dest="meta_set",
    help="Set value to meta data fields.",
)

group_meta.add_argument(
    "--metatag",
    "--metatag-meta",
    nargs=2,
    action="append",
    metavar=("<field>", "<value>"),
    dest="meta_metatag",
    help="Define the metadata in MetaTag elements." + _embed_fields(Metatag.fields),
)

group_meta.add_argument(
    "--vbox",
    "--vbox-meta",
    nargs=2,
    action="append",
    metavar=("<field>", "<value>"),
    dest="meta_vbox",
    help="Define the metadata in VBox elements." + _embed_fields(Vbox.fields),
)

###############################################################################
# lyrics
###############################################################################

group_lyrics = parser.add_argument_group("lyrics")

group_lyrics.add_argument(
    "-x",
    "--extract",
    "--extract-lyrics",
    dest="lyrics_extract",
    help="Extract each lyrics verse into a separate MuseScore file. "
    "Specify ”all” to extract all lyrics "
    "verses. The old verse number is appended to the file name, e. g.: "
    "score_1.mscx.",
)

group_lyrics.add_argument(
    "-r",
    "--remap",
    "--remap-lyrics",
    dest="lyrics_remap",
    help='Remap lyrics. Example: "--remap 3:2,5:3". This '
    "example remaps lyrics verse 3 to verse 2 and verse 5 to 3. "
    "Use commas to specify multiple remap pairs. One remap pair "
    'is separated by a colon in this form: "old:new": "old" '
    'stands for the old verse number. "new" stands for the new '
    "verse number.",
)

group_lyrics.add_argument(
    "-F",
    "--fix",
    "--fix-lyrics",
    action="store_true",
    dest="lyrics_fix",
    help='Fix lyrics: Convert trailing hyphens ("la- la- la") '
    'to a correct hyphenation ("la - la - la")',
)

###############################################################################
# rename
###############################################################################

group_rename = parser.add_argument_group(
    "rename",
    "Rename the “*.msc[zx]” files."
    "Fields and functions you can use in the format "
    "string (-f, --format):\n\n"
    "Functions\n=========\n\n{}".format(tmep.get_doc()),
)

group_rename.add_argument(
    "--rename",
    dest="rename_rename",
    action="store_true",
    help="Format string.",
)

group_rename.add_argument(
    "-f",
    "--format",
    dest="rename_format",
    default="$title ($composer)",
    help="Format string.",
)

group_rename.add_argument(
    "-A",
    "--alphanum",
    dest="rename_alphanum",
    action="store_true",
    help="Use only alphanumeric characters.",
)

group_rename.add_argument(
    "-a",
    "--ascii",
    dest="rename_ascii",
    action="store_true",
    help="Use only ASCII characters.",
)

group_rename.add_argument(
    "-n",
    "--no-whitespace",
    dest="rename_no_whitespace",
    action="store_true",
    help="Replace all whitespaces with dashes or sometimes underlines.",
)

group_rename.add_argument(
    "-K",
    "--skip-if-empty",
    dest="rename_skip",
    metavar="FIELDS",
    help="Skip rename action if FIELDS are empty. Separate FIELDS using "
    "commas: composer,title",
)

group_rename.add_argument(
    "-t",
    "--target",
    dest="rename_target",
    help="Target directory",
)

###############################################################################
# selection
###############################################################################

group_selection = parser.add_argument_group(
    "selection",
    "The following options affect how the manager selects the MuseScore files.",
)

group_selection.add_argument(
    "-L",
    "--list-files",
    action="store_true",
    dest="selection_list",
    help="Only list files and do nothing else.",
)

group_selection_exclusive = group_selection.add_mutually_exclusive_group()

group_selection_exclusive.add_argument(
    "-g",
    "--glob",
    dest="selection_glob",
    metavar="<glob-pattern>",
    default="*.msc[xz]",
    help="Handle only files which matches against Unix style "
    'glob patterns (e. g. "*.mscx", "* - *"). If you omit this '
    'option, the standard glob pattern "*.msc[xz]" is used.',
)

group_selection_exclusive.add_argument(
    "--mscz",
    dest="selection_mscz",
    action="store_true",
    help='Take only "*.mscz" files into account.',
)

group_selection_exclusive.add_argument(
    "--mscx",
    dest="selection_mscx",
    action="store_true",
    help='Take only "*.mscx" files into account.',
)


###############################################################################
# style
###############################################################################

group_style = parser.add_argument_group("style", "Change the styles.")

group_style.add_argument(
    "-s",
    "--style",
    nargs=2,
    action="append",
    metavar=("<style-name>", "<value>"),
    default=[],
    dest="style_value",
    help="Set a single style value. For example: --style pageWidth 8.5",
)

group_style.add_argument(
    "--clean",
    dest="style_clean",
    action="store_true",
    help='Clean and reset the formating of the "*.mscx" file',
)

file_completers.append(
    group_style.add_argument(
        "-Y",
        "--style-file",
        dest="style_file",
        metavar="<file>",
        type=open,
        help='Load a "*.mss" style file and include the contents of this file.',
    )
)

group_style.add_argument(
    "--s3",
    "--styles-v3",
    dest="style_styles_v3",
    action="store_true",
    help="List all possible version 3 styles.",
)

group_style.add_argument(
    "--s4",
    "--styles-v4",
    dest="style_styles_v4",
    action="store_true",
    help="List all possible version 4 styles.",
)

group_style.add_argument(
    "--list-fonts",
    dest="style_list_fonts",
    action="store_true",
    help="List all font related styles.",
)

group_style.add_argument(
    "--text-font",
    dest="style_text_font",
    metavar="<font-face>",
    help="Set nearly all fonts except “romanNumeralFontFace”, “figuredBassFontFace”, "
    "“dynamicsFontFace“, “musicalSymbolFont” and “musicalTextFont”.",
)

group_style.add_argument(
    "--title-font",
    dest="style_title_font",
    metavar="<font-face>",
    help="Set “titleFontFace” and “subTitleFontFace”.",
)

group_style.add_argument(
    "--musical-symbol-font",
    dest="style_musical_symbol_font",
    metavar="<font-face>",
    help="Set “musicalSymbolFont”, “dynamicsFont” and  “dynamicsFontFace”.",
)

group_style.add_argument(
    "--musical-text-font",
    dest="style_musical_text_font",
    metavar="<font-face>",
    help="Set “musicalTextFont”.",
)

group_style.add_argument(
    "--staff-space",
    dest="style_staff_space",
    type=mm,
    metavar="<dimension>",
    help="Set the staff space or spatium. This is the vertical distance between "
    "two lines of a music staff.",
)

group_style.add_argument(
    "--page-size",
    dest="style_page_size",
    nargs=2,
    metavar=("<width>", "<height>"),
    help="Set the page size.",
)

group_style.add_argument(
    "--a4",
    "--din-a4",
    dest="style_page_size_a4",
    action="store_true",
    help="Set the paper size to DIN A4 (210 by 297 mm).",
)

group_style.add_argument(
    "--letter",
    dest="style_page_size_letter",
    action="store_true",
    help="Set the paper size to Letter (8.5 by 11 in).",
)

group_style.add_argument(
    "--margin",
    dest="style_margin",
    metavar="<dimension>",
    help="Set the top, right, bottom and left margins to the same value.",
)

group_style.add_argument(
    "--header",
    dest="style_show_header",
    action=argparse.BooleanOptionalAction,
    help="Show or hide the header",
)

group_style.add_argument(
    "--footer",
    dest="style_show_footer",
    action=argparse.BooleanOptionalAction,
    help="Show or hide the footer.",
)

###############################################################################
# last positional parameter
###############################################################################

file_completers.append(
    parser.add_argument(
        "path",
        nargs="*",
        default=["."],
        metavar="<path>",
        help='Path to a "*.msc[zx]" file or a folder containing "*.msc[zx]" files. '
        "can be specified several times.",
    )
)

for action in file_completers:
    action.complete = shtab.FILE  # type: ignore


def __print_error(error: Exception) -> None:
    msg = ""

    if isinstance(error, SyntaxError):
        msg = error.msg

    print(
        "{}: {}; message: {}".format(
            utils.colorize("Error", "white", "on_red"),
            utils.colorize(error.__class__.__name__, "red"),
            msg,
        )
    )


def execute(cli_args: Sequence[str] | None = None) -> None:
    args = parse_args(parser, cli_args)

    if args.style_styles_v3 or args.style_styles_v4:

        def list_styles(version: int) -> None:
            """There are many styles in MuseScore. We dynamically
            import the module to avoid long load time"""
            style_names = importlib.import_module("mscxyz.style_names", package=None)
            style_names.list_styles(version)

        if args.style_styles_v3:
            list_styles(3)
            return
        if args.style_styles_v4:
            list_styles(4)
            return

    selection_glob: str = args.selection_glob
    if args.selection_mscz:
        selection_glob = "*.mscz"
    elif args.selection_mscx:
        selection_glob = "*.mscx"

    for file in utils.list_path(src=args.path, glob=selection_glob):
        try:
            if args.selection_list:
                print(file)
                continue

            score = Score(file)

            if args.style_list_fonts:
                score.style.print_all_font_faces()
                continue

            if args.general_backup:
                score.backup()

            if args.general_diff:
                score.make_snapshot()

            # style

            if args.style_clean:
                score.style.clean()

            for style_name, value in args.style_value:
                score.style.set(style_name, value)

            if args.style_file:
                score.style.load_style_file(args.style_file.name)

            if args.style_text_font is not None:
                score.style.set_text_fonts(args.style_text_font)

            if args.style_title_font is not None:
                score.style.set_title_fonts(args.style_title_font)

            if args.style_musical_symbol_font is not None:
                score.style.set_musical_symbol_fonts(args.style_musical_symbol_font)

            if args.style_musical_text_font is not None:
                score.style.set_musical_text_font(args.style_musical_text_font)

            if args.style_staff_space is not None:
                score.style.staff_space = args.style_staff_space

            if args.style_page_size is not None:
                score.style.set_page_size(*args.style_page_size)

            if args.style_page_size_a4:
                score.style.set_page_size_a4()

            if args.style_page_size_letter:
                score.style.set_page_size_letter()

            if args.style_margin is not None:
                score.style.margin = inch(args.style_margin)

            if args.style_show_header is not None:
                score.style.show_header = args.style_show_header

            if args.style_show_footer is not None:
                score.style.show_footer = args.style_show_footer

            if args.lyrics_remap:
                score.lyrics.remap(args.lyrics_remap)

            if args.lyrics_fix:
                score.lyrics.fix_lyrics(mscore=args.general_mscore)

            if args.lyrics_extract:
                no = 0
                if args.lyrics_extract != "all":
                    no = int(args.lyrics_extract)
                score.lyrics.extract_lyrics(no)

            # meta

            manipulate_meta: bool = False

            if (
                args.meta_metatag
                or args.meta_vbox
                or args.meta_set
                or args.meta_clean
                or args.meta_dist
                or args.meta_dist
                or args.meta_delete
                or args.meta_sync
            ):
                manipulate_meta = True
                # to get score.fields.pre
                score.fields

            if args.meta_metatag:
                for a in args.meta_metatag:
                    field = a[0]
                    value = a[1]
                    if field not in Metatag.fields:
                        raise ValueError(
                            f"Unknown field {field}. "
                            f"Possible fields: {', '.join(Metatag.fields)}"
                        )
                    setattr(score.meta.metatag, field, value)

            if args.meta_vbox:
                for a in args.meta_vbox:
                    field = a[0]
                    value = a[1]
                    if field not in Vbox.fields:
                        raise ValueError(
                            f"Unknown field {field}. "
                            f"Possible fields: {', '.join(Vbox.fields)}"
                        )
                    setattr(score.meta.vbox, field, value)

            if args.meta_set:
                for a in args.meta_set:
                    score.fields.set(a[0], a[1])

            if args.meta_clean:
                score.fields.clean(args.meta_clean)

            if args.meta_json:
                score.fields.export_json()

            if args.meta_dist:
                for a in args.meta_dist:
                    score.fields.distribute(source_fields=a[0], format_string=a[1])

            if args.meta_delete:
                score.meta.delete_duplicates()

            if args.meta_sync:
                score.meta.sync_fields()

            if args.meta_log:
                score.meta.write_to_log_file(args.meta_log[0], args.meta_log[1])

            if manipulate_meta:
                score.fields.diff(args)

            # rename

            if args.rename_rename:
                rename(score)

            if args.export_extension:
                score.export.to_extension(args.export_extension)

            if args.general_diff:
                score.print_diff()

            if not args.general_dry_run:
                score.save()

        except Exception as e:
            if args.general_bail:
                raise e
            else:
                __print_error(e)
