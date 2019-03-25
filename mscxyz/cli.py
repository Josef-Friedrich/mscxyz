"""Wrapper for the command line interface"""

from mscxyz._version import get_versions
from mscxyz.meta import InterfaceReadWrite, Interface
import argparse
import textwrap
import tmep


def list_fields(fields, prefix='', suffix=''):
    out = []
    for field in fields:
        out.append(prefix + '- ' + field + suffix)
    return '\n'.join(out)


parser = argparse.ArgumentParser(description='A command \
    line tool to manipulate the XML based "*.mscX" and "*.mscZ" \
    files of the notation software MuseScore.')

###############################################################################
# Global options
###############################################################################

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
    dest='general_backup',
    action='store_true',
    help='Create a backup file.')


parser.add_argument(
    '-c',
    '--colorize',
    action='store_true',
    dest='general_colorize',
    help='Colorize the command line print statements.')


parser.add_argument(
    '-d',
    '--dry-run',
    action='store_true',
    dest='general_dry_run',
    help='Simulate the actions.')

parser.add_argument(
    '-g',
    '--glob',
    dest='general_glob',
    default='*.mscx',
    help='Handle only files which matches against Unix style \
    glob patterns (e. g. "*.mscx", "* - *"). If you omit this \
    option, the standard glob pattern "*.mscx" is used.')

parser.add_argument(
    '-m',
    '--mscore',
    action='store_true',
    dest='general_mscore',
    help='Open and save the XML file in MuseScore after manipulating the XML \
    with lxml to avoid differences in the XML structure.')

parser.add_argument(
    '-v',
    '--verbose',
    action='count',
    dest='general_verbose',
    default=0,
    help='Make commands more verbose. You can specifiy \
    multiple arguments (. g.: -vvv) to make the command more \
    verbose.')

###############################################################################
# subparser
###############################################################################

subparser = parser.add_subparsers(
    title='Subcommands',
    dest='subcommand',
    help='Run "subcommand --help" for more \
    informations.')

###############################################################################
# clean
###############################################################################

sub_clean = subparser.add_parser(
    'clean', help='Clean and reset the formating of the "*.mscx" file')

sub_clean.add_argument(
    '-s',
    '--style',
    dest='clean_style',
    type=open,
    help='Load a "*.mss" style file and include the contents of \
    this file.')

###############################################################################
# meta
###############################################################################

sub_meta = subparser.add_parser(
    'meta',
    help='Deal with meta data informations stored in the MuseScore file.',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent('''\
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

    You have access to all this metadata fields through following fields:''')
    + '\n\n' + list_fields(InterfaceReadWrite.get_all_fields(), prefix='    '))

sub_meta.add_argument(
    '-c',
    '--clean',
    nargs=1,
    dest='meta_clean',
    help='Clean the meta data fields. Possible values: „all“ or \
    „field_one,field_two“.')

sub_meta.add_argument(
    '-D',
    '--delete-duplicates',
    dest='meta_delete',
    action='store_true',
    help='Deletes combined_lyricist if this field is equal to '
    'combined_composer. Deletes combined_subtitle if this field is equal to'
    'combined_title. Move combined_subtitle to combimed_title if '
    'combined_title is empty.')

sub_meta.add_argument(
    '-d',
    '--distribute-fields',
    dest='meta_dist',
    action='append',
    nargs=2,
    metavar=('SOURCE_FIELDS', 'FORMAT_STRING'),
    help='Distribute source fields to target fields applying a format string \
    on the source fields. It is possible to apply multiple \
    --distribute-fields options. SOURCE_FIELDS can be a single field or a \
    comma separated list of fields: field_one,field_two. The program \
    tries first to match the FORMAT_STRING on the first source field. If this\
    fails, it tries the second source field ... an so on.')

sub_meta.add_argument(
    '-j',
    '--json',
    action='store_true',
    dest='meta_json',
    help='Additionally write the meta data to a json file.')

sub_meta.add_argument(
    '-l',
    '--log',
    nargs=2,
    metavar=('DESTINATION', 'FORMAT_STRING'),
    dest='meta_log',
    help='Write one line per file to a text file. e. g. --log '
    '/tmp/mscx-manager.log \'$title $composer\'')

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
    '--set-field',
    nargs=2,
    action='append',
    metavar=('DESTINATION_FIELD', 'FORMAT_STRING'),
    dest='meta_set',
    help='Set value to meta data fields.')

###############################################################################
# lyrics
###############################################################################

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
    dest='lyrics_extract',
    default='all',
    help='The lyric verse number to extract or "all".'
)

sub_lyrics.add_argument(
    '-r',
    '--remap',
    dest='lyrics_remap',
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
    dest='lyrics_fix',
    help='Fix lyrics: Convert trailing hyphens ("la- la- la") \
    to a correct hyphenation ("la - la - la")')

###############################################################################
# rename
###############################################################################

sub_rename = subparser.add_parser(
    'rename',
    help='Rename the "*.mscx" files.',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description='Fields and functions you can use in the format '
    'string (-f, --format):\n\n'
    'Fields\n======\n\n{}\n\n'
    'Functions\n=========\n\n{}'
    .format(list_fields(Interface.get_all_fields(), prefix='    '),
            tmep.doc.Doc().get()))

sub_rename.add_argument(
    '-f',
    '--format',
    dest='rename_format',
    default='$combined_title ($combined_composer)',
    help='Format string.')

sub_rename.add_argument(
    '-A',
    '--alphanum',
    dest='rename_alphanum',
    action='store_true',
    help='Use only alphanumeric characters.')

sub_rename.add_argument(
    '-a',
    '--ascii',
    dest='rename_ascii',
    action='store_true',
    help='Use only ASCII characters.')

sub_rename.add_argument(
    '-n',
    '--no-whitespace',
    dest='rename_no_whitespace',
    action='store_true',
    help='Replace all whitespaces with dashes or \
    sometimes underlines.')

sub_rename.add_argument(
    '-s',
    '--skip-if-empty',
    dest='rename_skip',
    metavar='FIELDS',
    help='Skip rename action if FIELDS are empty. Separate FIELDS using \
    commas: combined_composer,combined_title',
)

sub_rename.add_argument(
    '-t',
    '--target',
    dest='rename_target',
    help='Target directory',
)

###############################################################################
# export
###############################################################################

sub_export = subparser.add_parser(
    'export',
    help='Export the scores to PDFs or to the specified \
    extension.')

sub_export.add_argument(
    '-e',
    '--extension',
    dest='export_extension',
    default='pdf',
    help='Extension to export. If this option \
    is omitted, then the default extension is "pdf".')

###############################################################################
# help
###############################################################################

sub_help = subparser.add_parser(
    'help',
    help='Show help. Use “{} help all” to show help \
    messages of all subcommands. Use \
    “{} help <subcommand>” to show only help messages \
    for the given subcommand.'.format(parser.prog, parser.prog))

sub_help.add_argument(
    '-m',
    '--markdown',
    dest='help_markdown',
    action='store_true',
    help='Show help in markdown format. \
    This option enables to generate the README file directly \
    form the command line output.')

sub_help.add_argument(
    '-r',
    '--rst',
    dest='help_rst',
    action='store_true',
    help='Show help in reStructuresText \
    format. This option enables to generate the README file \
    directly form the command line output.')

###############################################################################
# help
###############################################################################

parser.add_argument(
    'path',
    help='Path to a "*.mscx" file \
    or a folder which contains "*.mscx" files. In conjunction \
    with the subcommand "help" this positional parameter \
    accepts the names of all other subcommands or the word \
    "all".')
