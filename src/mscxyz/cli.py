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
from mscxyz.fields import FieldsManager
from mscxyz.meta import Metatag, Vbox
from mscxyz.rename import rename
from mscxyz.score import Score
from mscxyz.settings import DefaultArguments, parse_args
from mscxyz.style import inch, mm, musical_symbol_font_faces, musical_text_font_faces


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


def setup_parser() -> argparse.ArgumentParser:
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

    file_completers.append(
        parser.add_argument(
            "-C",
            "--config-file",
            metavar="<file-path>",
            dest="general_config_file",
            help="Specify a configuration file in the INI format.",
        )
    )

    # backup and dry run

    parser.add_argument(
        "-b",
        "--backup",
        dest="general_backup",
        action="store_true",
        help="Create a backup file.",
    )

    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        dest="general_dry_run",
        help="Simulate the actions.",
    )

    parser.add_argument(
        "--catch-errors",
        dest="general_catch_errors",
        action="store_true",
        help="Print error messages instead stop execution in a batch run.",
    )

    # musescore executable

    parser.add_argument(
        "-m",
        "--mscore",
        "--save-in-mscore",
        action="store_true",
        dest="general_mscore",
        help="Open and save the XML file in MuseScore after manipulating the XML "
        "with lxml to avoid differences in the XML structure.",
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

    ###############################################################################
    # groups in alphabetical order
    ###############################################################################

    ###############################################################################
    # export
    ###############################################################################

    export = parser.add_argument_group(
        "export", "Export the scores in different formats."
    )

    export.add_argument(
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

    export.add_argument(
        "--compress",
        dest="export_compress",
        action="store_true",
        help="Save an uncompressed MuseScore file (*.mscx) as a compressed file (*.mscz).",
    )

    export.add_argument(
        "--remove-origin",
        dest="export_remove_origin",
        action="store_true",
        help="Delete the uncompressed original MuseScore file (*.mscx) if it has been "
        "successfully converted to a compressed file (*.mscz).",
    )

    ###############################################################################
    # info
    ###############################################################################

    info = parser.add_argument_group(
        "info", "Print informations about the score and the CLI interface itself."
    )

    info.add_argument(
        "-V",
        "--version",
        action="version",
        version="%(prog)s {version}".format(version="0.0.0"),
    )

    info.add_argument(
        "-v",
        "--verbose",
        action="count",
        dest="info_verbose",
        default=0,
        help="Make commands more verbose. You can specifiy "
        "multiple arguments (. g.: -vvv) to make the command more "
        "verbose.",
    )

    info.add_argument(
        "-k",
        "--color",
        action=argparse.BooleanOptionalAction,
        dest="info_color",
        default=True,
        help="Colorize the command line print statements.",
    )

    info.add_argument(
        "--diff",
        action="store_true",
        dest="info_diff",
        help="Show a diff of the XML file before and after the manipulation.",
    )

    info.add_argument(
        "--print-xml",
        action="store_true",
        dest="info_print_xml",
        help="Print the XML markup of the score.",
    )

    ###############################################################################
    # meta
    ###############################################################################

    meta = parser.add_argument_group(
        "meta", "Deal with meta data informations stored in the MuseScore file."
    )

    meta.add_argument(
        "-c",
        "--clean-meta",
        metavar="<fields>",
        dest="meta_clean",
        help="Clean the meta data fields. Possible values: „all“ or a comma separated "
        "list of fields, for example: "
        "„field_one,field_two“.",
    )

    meta.add_argument(
        "-D",
        "--delete-duplicates",
        dest="meta_delete",
        action="store_true",
        help="Deletes lyricist if this field is equal to "
        "composer. Deletes subtitle if this field is equal to"
        "title. Move subtitle to combimed_title if "
        "title is empty.",
    )

    meta.add_argument(
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

    meta.add_argument(
        "-j",
        "--json",
        action="store_true",
        dest="meta_json",
        help="Write the meta data to a json file. The resulting file has the same "
        "path as the input file, only the extension is changed to “json”.",
    )

    meta.add_argument(
        "-l",
        "--log",
        nargs=2,
        metavar=("<log-file>", "<format-string>"),
        dest="meta_log",
        help="Write one line per file to a text file. e. g. --log "
        "/tmp/musescore-manager.log '$title $composer'",
    )

    meta.add_argument(
        "-y",
        "--synchronize",
        action="store_true",
        dest="meta_sync",
        help="Synchronize the values of the first vertical frame (vbox) "
        "(title, subtitle, composer, lyricist) with the corresponding "
        "metadata fields",
    )

    meta.add_argument(
        "-S",
        "--set-field",
        nargs=2,
        action="append",
        metavar=("<field>", "<format-string>"),
        dest="meta_set",
        help="Set value to meta data fields.",
    )

    meta.add_argument(
        "--metatag",
        "--metatag-meta",
        nargs=2,
        action="append",
        metavar=("<field>", "<value>"),
        dest="meta_metatag",
        help="Define the metadata in MetaTag elements." + _embed_fields(Metatag.fields),
    )

    meta.add_argument(
        "--vbox",
        "--vbox-meta",
        nargs=2,
        action="append",
        metavar=("<field>", "<value>"),
        dest="meta_vbox",
        help="Define the metadata in VBox elements." + _embed_fields(Vbox.fields),
    )

    meta.add_argument(
        "--title",
        metavar=("<string>"),
        dest="meta_title",
        help="Create a vertical frame (vbox) containing a title text field and "
        "set the corresponding document properties work title field (metatag).",
    )

    meta.add_argument(
        "--subtitle",
        metavar=("<string>"),
        dest="meta_subtitle",
        help="Create a vertical frame (vbox) containing a subtitle text field and "
        "set the corresponding document properties subtitle and movement title filed (metatag).",
    )

    meta.add_argument(
        "--composer",
        metavar=("<string>"),
        dest="meta_composer",
        help="Create a vertical frame (vbox) containing a composer text field and "
        "set the corresponding document properties composer field (metatag).",
    )

    meta.add_argument(
        "--lyricist",
        metavar=("<string>"),
        dest="meta_lyricist",
        help="Create a vertical frame (vbox) containing a lyricist text field and "
        "set the corresponding document properties lyricist field (metatag).",
    )

    ###############################################################################
    # lyrics
    ###############################################################################

    lyrics = parser.add_argument_group("lyrics")

    lyrics.add_argument(
        "-x",
        "--extract",
        "--extract-lyrics",
        dest="lyrics_extract",
        metavar="<number-or-all>",
        help="Extract each lyrics verse into a separate MuseScore file. "
        "Specify ”all” to extract all lyrics "
        "verses. The old verse number is appended to the file name, e. g.: "
        "score_1.mscx.",
    )

    lyrics.add_argument(
        "-r",
        "--remap",
        "--remap-lyrics",
        dest="lyrics_remap",
        metavar="<remap-pairs>",
        help='Remap lyrics. Example: "--remap 3:2,5:3". This '
        "example remaps lyrics verse 3 to verse 2 and verse 5 to 3. "
        "Use commas to specify multiple remap pairs. One remap pair "
        'is separated by a colon in this form: "old:new": "old" '
        'stands for the old verse number. "new" stands for the new '
        "verse number.",
    )

    lyrics.add_argument(
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

    rename = parser.add_argument_group("rename", "Rename the “*.msc[zx]” files. ")

    rename.add_argument(
        "--rename",
        dest="rename_rename",
        metavar="<path-template>",
        help="A path template string to set the destination location.",
    )

    rename_target = rename.add_mutually_exclusive_group()

    rename_target.add_argument(
        "-t",
        "--target",
        dest="rename_target",
        metavar="<directory>",
        help="Target directory",
    )

    rename_target.add_argument(
        "--only-filename",
        action="store_true",
        dest="rename_only_filename",
        help="Rename only the filename and don’t move the score to a different directory.",
    )

    rename.add_argument(
        "-A",
        "--alphanum",
        dest="rename_alphanum",
        action="store_true",
        help="Use only alphanumeric characters.",
    )

    rename.add_argument(
        "-a",
        "--ascii",
        dest="rename_ascii",
        action="store_true",
        help="Use only ASCII characters.",
    )

    rename.add_argument(
        "-n",
        "--no-whitespace",
        dest="rename_no_whitespace",
        action="store_true",
        help="Replace all whitespaces with dashes or sometimes underlines.",
    )

    rename.add_argument(
        "-K",
        "--skip-if-empty",
        dest="rename_skip",
        metavar="<fields>",
        help="Skip the rename action if the fields specified in <fields> are empty. "
        "Multiple fields can be separated by commas, e. g.: composer,title",
    )

    rename.add_argument(
        "--list-fields",
        dest="rename_list_fields",
        action="store_true",
        help="List all available fields that can be used in the path templates.",
    )

    rename.add_argument(
        "--list-functions",
        dest="rename_list_functions",
        action="store_true",
        help="List all available functions that can be used in the path templates.",
    )

    ###############################################################################
    # selection
    ###############################################################################

    selection = parser.add_argument_group(
        "selection",
        "The following options affect how the manager selects the MuseScore files.",
    )

    selection.add_argument(
        "-L",
        "--list-files",
        action="store_true",
        dest="selection_list",
        help="Only list files and do nothing else.",
    )

    exclusive_selection = selection.add_mutually_exclusive_group()

    exclusive_selection.add_argument(
        "-g",
        "--glob",
        dest="selection_glob",
        metavar="<glob-pattern>",
        default="*.msc[xz]",
        help="Handle only files which matches against Unix style "
        'glob patterns (e. g. "*.mscx", "* - *"). If you omit this '
        'option, the standard glob pattern "*.msc[xz]" is used.',
    )

    exclusive_selection.add_argument(
        "--mscz",
        dest="selection_mscz",
        action="store_true",
        help='Take only "*.mscz" files into account.',
    )

    exclusive_selection.add_argument(
        "--mscx",
        dest="selection_mscx",
        action="store_true",
        help='Take only "*.mscx" files into account.',
    )

    ###############################################################################
    # style
    ###############################################################################

    style = parser.add_argument_group("style", "Change the styles.")

    style.add_argument(
        "-s",
        "--style",
        nargs=2,
        action="append",
        metavar=("<style-name>", "<value>"),
        default=[],
        dest="style_value",
        help="Set a single style value. For example: --style pageWidth 8.5",
    )

    style.add_argument(
        "--clean",
        dest="style_clean",
        action="store_true",
        help='Clean and reset the formating of the "*.mscx" file',
    )

    file_completers.append(
        style.add_argument(
            "-Y",
            "--style-file",
            dest="style_file",
            metavar="<file>",
            type=open,
            help='Load a "*.mss" style file and include the contents of this file.',
        )
    )

    style.add_argument(
        "--s3",
        "--styles-v3",
        dest="style_styles_v3",
        action="store_true",
        help="List all possible version 3 styles.",
    )

    style.add_argument(
        "--s4",
        "--styles-v4",
        dest="style_styles_v4",
        action="store_true",
        help="List all possible version 4 styles.",
    )

    style.add_argument(
        "--reset-small-staffs",
        dest="style_reset_small_staffs",
        action="store_true",
        help="Reset all small staffs to normal size.",
    )

    # font (style)

    font = parser.add_argument_group(
        "font (style)", "Change the font faces of a score."
    )

    font.add_argument(
        "--list-fonts",
        dest="style_list_fonts",
        action="store_true",
        help="List all font related styles.",
    )

    font.add_argument(
        "--text-font",
        dest="style_text_font",
        metavar="<font-face>",
        help="Set nearly all fonts except “romanNumeralFontFace”, “figuredBassFontFace”, "
        "“dynamicsFontFace“, “musicalSymbolFont” and “musicalTextFont”.",
    )

    font.add_argument(
        "--title-font",
        dest="style_title_font",
        metavar="<font-face>",
        help="Set “titleFontFace” and “subTitleFontFace”.",
    )

    font.add_argument(
        "--musical-symbol-font",
        dest="style_musical_symbol_font",
        choices=musical_symbol_font_faces,
        help="Set “musicalSymbolFont”, “dynamicsFont” and  “dynamicsFontFace”.",
    )

    font.add_argument(
        "--musical-text-font",
        dest="style_musical_text_font",
        choices=musical_text_font_faces,
        help="Set “musicalTextFont”.",
    )

    # page (style)

    page = parser.add_argument_group("page (style)", "Page settings.")

    page.add_argument(
        "--staff-space",
        dest="style_staff_space",
        type=mm,
        metavar="<dimension>",
        help="Set the staff space or spatium. This is the vertical distance between "
        "two lines of a music staff.",
    )

    page.add_argument(
        "--page-size",
        dest="style_page_size",
        nargs=2,
        metavar=("<width>", "<height>"),
        help="Set the page size.",
    )

    page.add_argument(
        "--a4",
        "--din-a4",
        dest="style_page_size_a4",
        action="store_true",
        help="Set the paper size to DIN A4 (210 by 297 mm).",
    )

    page.add_argument(
        "--letter",
        dest="style_page_size_letter",
        action="store_true",
        help="Set the paper size to Letter (8.5 by 11 in).",
    )

    page.add_argument(
        "--margin",
        dest="style_margin",
        metavar="<dimension>",
        help="Set the top, right, bottom and left margins to the same value.",
    )

    # header (style)

    header = parser.add_argument_group("header (style)", "Change the header.")

    header.add_argument(
        "--show-header",
        dest="style_show_header",
        action=argparse.BooleanOptionalAction,
        help="Show or hide the header.",
    )

    header.add_argument(
        "--header-first-page",
        dest="style_header_first_page",
        action=argparse.BooleanOptionalAction,
        help="Show the header on the first page.",
    )

    header.add_argument(
        "--different-odd-even-header",
        dest="style_different_odd_even_header",
        action=argparse.BooleanOptionalAction,
        help="Use different header for odd and even pages.",
    )

    header.add_argument(
        "--header",
        nargs=3,
        dest="style_header_all",
        metavar=("<left>", "<center>", "<right>"),
        help="Set the header for all pages.",
    )

    header.add_argument(
        "--header-odd-even",
        nargs=6,
        dest="style_header_odd_even",
        metavar=(
            "<odd-left>",
            "<even-left>",
            "<odd-center>",
            "<even-center>",
            "<odd-right>",
            "<even-right>",
        ),
        help="Set different headers for odd and even pages.",
    )

    header.add_argument(
        "--clear-header",
        dest="style_clear_header",
        action="store_true",
        help="Clear all header fields by setting all fields to empty strings. The header is hidden.",
    )

    # footer (style)

    footer = parser.add_argument_group("footer (style)", "Change the footer.")

    footer.add_argument(
        "--show-footer",
        dest="style_show_footer",
        action=argparse.BooleanOptionalAction,
        help="Show or hide the footer.",
    )

    footer.add_argument(
        "--footer-first-page",
        dest="style_footer_first_page",
        action=argparse.BooleanOptionalAction,
        help="Show the footer on the first page.",
    )

    footer.add_argument(
        "--different-odd-even-footer",
        dest="style_different_odd_even_footer",
        action=argparse.BooleanOptionalAction,
        help="Use different footers for odd and even pages.",
    )

    footer.add_argument(
        "--footer",
        nargs=3,
        dest="style_footer_all",
        metavar=("<left>", "<center>", "<right>"),
        help="Set the footer for all pages.",
    )

    footer.add_argument(
        "--footer-odd-even",
        nargs=6,
        dest="style_footer_odd_even",
        metavar=(
            "<odd-left>",
            "<even-left>",
            "<odd-center>",
            "<even-center>",
            "<odd-right>",
            "<even-right>",
        ),
        help="Set different footers for odd and even pages.",
    )

    footer.add_argument(
        "--clear-footer",
        action="store_true",
        dest="style_clear_footer",
        help="Clear all footer fields by setting all fields to empty strings. The footer is hidden.",
    )

    # lyrics (style)

    lyrics_style = parser.add_argument_group(
        "lyrics (style)", "Change the lyrics styles."
    )

    lyrics_style.add_argument(
        "--lyrics-font-size",
        type=float,
        dest="style_lyrics_font_size",
        help="Set the font size of both even and odd lyrics.",
    )

    lyrics_style.add_argument(
        "--lyrics-min-distance",
        type=float,
        dest="style_lyrics_min_distance",
        help="Set the minimum gap or minimum distance between syllables or words.",
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

    return parser


def _print_error(error: Exception) -> None:
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


def get_args(cli_args: Sequence[str] | None = None) -> DefaultArguments:
    return parse_args(setup_parser(), cli_args)


def execute(cli_args: Sequence[str] | None = None) -> None:
    args = get_args(cli_args)

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

    if args.rename_list_fields:
        FieldsManager.print()
        return

    if args.rename_list_functions:
        print(tmep.get_doc())
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

            score.make_snapshot()

            if args.export_compress:
                score = Score(score.export.compress(args.export_remove_origin))

            # style

            if args.style_clean:
                score.style.clean()

            for style_name, value in args.style_value:
                score.style.set(style_name, value)

            if args.style_file:
                score.style.load_style_file(args.style_file.name)

            # font (style)

            if args.style_text_font is not None:
                score.style.set_text_fonts(args.style_text_font)

            if args.style_title_font is not None:
                score.style.set_title_fonts(args.style_title_font)

            if args.style_musical_symbol_font is not None:
                score.style.musical_symbol_font = args.style_musical_symbol_font

            if args.style_musical_text_font is not None:
                score.style.musical_text_font = args.style_musical_text_font

            # page (style)

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

            # header (style)

            if args.style_show_header is not None:
                score.style.show_header = args.style_show_header

            if args.style_header_first_page is not None:
                score.style.header_first_page = args.style_header_first_page

            if args.style_different_odd_even_header is not None:
                score.style.header_odd_even = args.style_different_odd_even_header

            if args.style_header_all:
                score.style.set_header_all(*args.style_header_all)

            if args.style_header_odd_even:
                score.style.set_header_odd_even(*args.style_header_odd_even)

            if args.style_clear_header:
                score.style.clear_header()

            # footer (style)

            if args.style_show_footer is not None:
                score.style.show_footer = args.style_show_footer

            if args.style_footer_first_page is not None:
                score.style.footer_first_page = args.style_footer_first_page

            if args.style_different_odd_even_footer is not None:
                score.style.footer_odd_even = args.style_different_odd_even_footer

            if args.style_footer_all:
                score.style.set_footer_all(*args.style_footer_all)

            if args.style_footer_odd_even:
                score.style.set_footer_odd_even(*args.style_footer_odd_even)

            if args.style_clear_footer:
                score.style.clear_footer()

            # lyrics (style)

            if args.style_lyrics_font_size is not None:
                score.style.lyrics_font_size = args.style_lyrics_font_size

            if args.style_lyrics_min_distance is not None:
                score.style.lyrics_min_distance = args.style_lyrics_min_distance

            # small staffs

            if args.style_reset_small_staffs:
                score.style.reset_small_staffs()

            # lyrics

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
                or args.meta_title
                or args.meta_subtitle
                or args.meta_composer
                or args.meta_lyricist
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

            if args.meta_title:
                score.meta.title = args.meta_title

            if args.meta_subtitle:
                score.meta.subtitle = args.meta_subtitle

            if args.meta_composer:
                score.meta.composer = args.meta_composer

            if args.meta_lyricist:
                score.meta.lyricist = args.meta_lyricist

            if manipulate_meta:
                score.fields.diff(args)

            # info

            if args.info_diff:
                score.print_diff()

            if args.info_print_xml:
                print(score.xml_string)

            # save

            if not args.general_dry_run:
                score.save()

            # export

            if args.export_extension:
                score.export.to_extension(args.export_extension)

            # rename

            if args.rename_rename:
                rename(score, args.rename_rename)

        except Exception as e:
            if not args.general_catch_errors:
                raise e
            else:
                _print_error(e)
