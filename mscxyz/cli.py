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

clean = subparser.add_parser(
    'clean', help='Clean and reset the formating of the "*.mscx" file')

clean.add_argument(
    '-s',
    '--style',
    type=open,
    help='Load a "*.mss" style file and include the contents of \
    this file.')

# meta

meta = subparser.add_parser(
    'meta',
    help='Synchronize the values of the first vertical frame \
    (title, composer, lyricist) with the corresponding \
    metadata fields.',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent('''\
    # XML structure of a meta tag:

        <metaTag name="tag"></metaTag>

    # All meta tags:

        - arranger
        - composer
        - copyright
        - creationDate
        - lyricist
        - movementNumber
        - movementTitle
        - originalFormat
        - platform
        - poet
        - source
        - translator
        - workNumber
        - workTitle

    # XML structure of a vbox tag:

        <VBox>
          <Text>
            <style>Title</style>
            <text>Some title text</text>
            </Text>

    # All vbox tags:

        - Title
        - Subtitle
        - Composer
        - Lyricis
    '''))

meta.add_argument(
    '-c',
    '--clean',
    action='store_true',
    dest='meta_clean',
    help='Clean the meta data.')

meta.add_argument(
    '-j',
    '--json',
    action='store_true',
    dest='meta_json',
    help='Additionally write the meta data to a json file.')

meta.add_argument(
    '-s',
    '--show',
    action='store_true',
    dest='meta_show',
    help='Show all metadata.')

# lyrics

lyrics = subparser.add_parser(
    'lyrics',
    help='Extract lyrics. Without any option this subcommand \
    extracts all lyrics verses into separate mscx files. \
    This generated mscx files contain only one verse. The old \
    verse number is appended to the file name, e. g.: \
    score_1.mscx.')

lyrics.add_argument(
    '-e',
    '--extract',
    default='all',
    help='The lyric verse number to extract or "all".'
)

lyrics.add_argument(
    '-r',
    '--remap',
    help='Remap lyrics. Example: "--remap 3:2,5:3". This \
    example remaps lyrics verse 3 to verse 2 and verse 5 to 3. \
    Use commas to specify multiple remap pairs. One remap pair \
    is separated by a colon in this form: "old:new": "old" \
    stands for the old verse number. "new" stands for the new \
    verse number.')

lyrics.add_argument(
    '-f',
    '--fix',
    action='store_true',
    help='Fix lyrics: Convert trailing hyphens ("la- la- la") \
    to a correct hyphenation ("la - la - la")')

# rename

rename = subparser.add_parser(
    'rename',
    help='Rename the "*.mscx" files.',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='Tokens and functions you can use in the format '
    'string (-f, --format):\n\n'
    'Tokens\n======\n\n' + format_field() + '\n\n'
    'Functions\n=========\n' + tmep.doc.Doc().get())

rename.add_argument(
    '-d',
    '--dry-run',
    action='store_true',
    help='Do not rename the scores')

rename.add_argument(
    '-f',
    '--format',
    default='$title ($composer)',
    help='Format string.')

rename.add_argument(
    '-a',
    '--ascii',
    action='store_true',
    help='Use only ASCII characters.')

rename.add_argument(
    '-n',
    '--no-whitespace',
    action='store_true',
    help='Replace all whitespaces with dashes or \
    sometimes underlines.')

# export

export = subparser.add_parser(
    'export',
    help='Export the scores to PDFs or to the specified \
    extension.')

export.add_argument(
    '-e',
    '--extension',
    default='pdf',
    help='Extension to export. If this option \
    is omitted, then the default extension is "pdf".')

# help

help = subparser.add_parser(
    'help',
    help='Show help. Use "mscxyz.py help all" to show help \
    messages of all subcommands. Use \
    "mscxyz.py help <subcommand>" to show only help messages \
    for the given subcommand.')

help.add_argument(
    '-m',
    '--markdown',
    action='store_true',
    help='Show help in markdown format. \
    This option enables to generate the README file directly \
    form the command line output.')

help.add_argument(
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
