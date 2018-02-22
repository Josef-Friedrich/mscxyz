# -*- coding: utf-8 -*-
"""Wrapper for the command line interface"""

from mscxyz._version import get_versions
from mscxyz.rename import FIELDS
import argparse
import textwrap
import tmep


def format_field():
    out = []
    for field in FIELDS:
        out.append('- ' + field)

    return '\n'.join(out)


parser = argparse.ArgumentParser(description='A command \
    line tool to manipulate the XML based "*.mscX" and "*.mscZ" \
    files of the notation software MuseScore.')


parser.add_argument(
    '-V',
    '--version',
    action='version',
    version='%(prog)s {version}'.format(
        version=get_versions()['version']
    )
)

parser.add_argument(
    '-b',
    '--backup',
    action='store_true',
    help='Create a backup file.')

parser.add_argument(
    '-g',
    '--glob',
    default='*.mscx',
    help='Handle only files which matches against Unix style \
    glob patterns (e. g. "*.mscx", "* - *"). If you omit this \
    option, the standard glob pattern "*.mscx" is used.')

parser.add_argument(
    '-v',
    '--verbose',
    action='count',
    default=0,
    help='Make commands more verbose. You can specifiy \
    multiple arguments (. g.: -vvv) to make the command more \
    verbose.')


subparser = parser.add_subparsers(
    title='Subcommands',
    dest='subcommand',
    help='Run "subcommand --help" for more \
    informations.')

# clean

sub_clean = subparser.add_parser(
    'clean', help='Clean and reset the formating of the "*.mscx" file')

sub_clean.add_argument(
    '-s',
    '--style',
    type=open,
    help='Load a "*.mss" style file and include the contents of \
    this file.')

# meta

sub_meta = subparser.add_parser(
    'meta',
    help='Deal with meta data informations stored in the MuseScore file.',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent('''\
    # XML structure of a meta tag:

        <metaTag name="tag"></metaTag>

    # All meta tags:

        - meta_arranger
        - meta_composer
        - meta_copyright
        - meta_creationDate
        - meta_lyricist
        - meta_movementNumber
        - meta_movementTitle
        - meta_platform
        - meta_poet
        - meta_source
        - meta_translator
        - meta_workNumber
        - meta_workTitle

    # XML structure of a vbox tag:

        <VBox>
          <Text>
            <style>Title</style>
            <text>Some title text</text>
            </Text>

    # All vbox tags:

        - vbox_Title
        - vbox_Subtitle
        - vbox_Composer
        - vbox_Lyricist

    # Combined meta data fields:

        - combined_title
        - combined_subtitle
        - combined_composer
        - combined_lyricist
    '''))

sub_meta.add_argument(
    '-c',
    '--clean',
    action='store_true',
    dest='meta_clean',
    help='Clean the meta data.')

sub_meta.add_argument(
    '-d',
    '--distribute-fields',
    dest='meta_dist',
    nargs=2,
    metavar=('SOURCE_FIELD', 'FORMAT_STRING'),
    help='Distribute a source field to target fields applying a format string \
    on the source field.')

sub_meta.add_argument(
    '-j',
    '--json',
    action='store_true',
    dest='meta_json',
    help='Additionally write the meta data to a json file.')

sub_meta.add_argument(
    '-s',
    '--synchronize',
    action='store_true',
    dest='meta_sync',
    help='Synchronize the values of the first vertical frame (vbox) \
    (title, subtitle, composer, lyricist) with the corresponding \
    metadata fields')

sub_meta.add_argument(
    '-S',
    '--set',
    action='store_true',
    dest='meta_set',
    help='Set value to meta data fields.')

# lyrics

sub_lyrics = subparser.add_parser(
    'lyrics',
    help='Extract lyrics. Without any option this subcommand \
    extracts all lyrics verses into separate mscx files. \
    This generated mscx files contain only one verse. The old \
    verse number is appended to the file name, e. g.: \
    score_1.mscx.')

sub_lyrics.add_argument(
    '-e',
    '--extract',
    default='all',
    help='The lyric verse number to extract or "all".'
)

sub_lyrics.add_argument(
    '-r',
    '--remap',
    help='Remap lyrics. Example: "--remap 3:2,5:3". This \
    example remaps lyrics verse 3 to verse 2 and verse 5 to 3. \
    Use commas to specify multiple remap pairs. One remap pair \
    is separated by a colon in this form: "old:new": "old" \
    stands for the old verse number. "new" stands for the new \
    verse number.')

sub_lyrics.add_argument(
    '-f',
    '--fix',
    action='store_true',
    help='Fix lyrics: Convert trailing hyphens ("la- la- la") \
    to a correct hyphenation ("la - la - la")')

# rename

sub_rename = subparser.add_parser(
    'rename',
    help='Rename the "*.mscx" files.',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='Tokens and functions you can use in the format '
    'string (-f, --format):\n\n'
    'Tokens\n======\n\n' + format_field() + '\n\n'
    'Functions\n=========\n' + tmep.doc.Doc().get())

sub_rename.add_argument(
    '-d',
    '--dry-run',
    action='store_true',
    help='Do not rename the scores')

sub_rename.add_argument(
    '-f',
    '--format',
    default='$title ($composer)',
    help='Format string.')

sub_rename.add_argument(
    '-a',
    '--ascii',
    action='store_true',
    help='Use only ASCII characters.')

sub_rename.add_argument(
    '-n',
    '--no-whitespace',
    action='store_true',
    help='Replace all whitespaces with dashes or \
    sometimes underlines.')

# export

sub_export = subparser.add_parser(
    'export',
    help='Export the scores to PDFs or to the specified \
    extension.')

sub_export.add_argument(
    '-e',
    '--extension',
    default='pdf',
    help='Extension to export. If this option \
    is omitted, then the default extension is "pdf".')

# help

sub_help = subparser.add_parser(
    'help',
    help='Show help. Use “' + parser.prog + ' help all” to show help \
    messages of all subcommands. Use \
    “' + parser.prog + ' help <subcommand>” to show only help messages \
    for the given subcommand.')

sub_help.add_argument(
    '-m',
    '--markdown',
    action='store_true',
    help='Show help in markdown format. \
    This option enables to generate the README file directly \
    form the command line output.')

sub_help.add_argument(
    '-r',
    '--rst',
    action='store_true',
    help='Show help in reStructuresText \
    format. This option enables to generate the README file \
    directly form the command line output.')

parser.add_argument(
    'path',
    help='Path to a "*.mscx" file \
    or a folder which contains "*.mscx" files. In conjunction \
    with the subcommand "help" this positional parameter \
    accepts the names of all other subcommands or the word \
    "all".')
