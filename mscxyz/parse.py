# -*- coding: utf-8 -*-
"""Wrapper for the command line interface"""

import argparse
import textwrap
from ._version import get_versions


class Parse(object):
    """Expose the command line interface."""

    def __init__(self):
        self.sub = {}
        self.initParser()
        self.addArguments()
        self.addSubParser()
        self.addPositional()

    def initParser(self):
        self.parser = argparse.ArgumentParser(description='A command \
            line tool to manipulate the XML based *.mscX and *.mscZ \
            files of the notation software MuseScore.')

    def addArguments(self):
        parser = self.parser

        parser.add_argument(
            '-V',
            '--version',
            action='version',
            version='%(prog)s {version}'.format(version=get_versions()['version'])
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
            '-p',
            '--pick',
            type=int,
            default=0,
            help='The --pick option can be used to run multiple \
            mscxyz.py commands in parallel on multiple consoles. If \
            you like so, using this option a "poor man\'s \
            multithreading" can be accomplished. Multicore CPUs can be \
            used to full capacity. \
            By default every fourth file gets picked up. The option \
            "-p N" begins the picking on the Nth file of a cycle. The \
            corresponding option is named "-c" or "--cycle-length".')

        parser.add_argument(
            '-c',
            '--cycle-length',
            type=int,
            default=4,
            help='This option specifies the distance between the \
            picked files. The option "-c N" picks every Nth file. The \
            corresponding options is named "-p" or "--pick".')

        parser.add_argument(
            '-v',
            '--verbose',
            action='count',
            default=0,
            help='Make commands more verbose. You can specifiy \
            multiple arguments (. g.: -vvv) to make the command more \
            verbose.')

    def addSubParser(self):

        self.sparser = self.parser.add_subparsers(
            title='Subcommands',
            dest='subcommand',
            help='Run "subcommand --help" for more \
            informations.')

        # clean

        self.sub['clean'] = self.sparser.add_parser(
            'clean', help='Clean and reset the formating of the *.mscx file')

        self.sub['clean'].add_argument(
            '-s',
            '--style',
            type=open,
            help='Load a *.mss style file and include the contents of \
            this file.')

        # meta

        self.sub['meta'] = self.sparser.add_parser(
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

        self.sub['meta'].add_argument(
            '-j',
            '--json',
            action='store_true',
            help='Additionally write the metadata to a json file.')

        self.sub['meta'].add_argument(
            '-s', '--show', action='store_true', help='Show all metadata.')

        # lyrics

        self.sub['lyrics'] = self.sparser.add_parser(
            'lyrics',
            help='Extract lyrics. Without any option this subcommand \
            extracts all lyrics verses into separate mscx files. \
            This generated mscx files contain only one verse. The old \
            verse number is appended to the file name, e. g.: \
            score_1.mscx.')

        self.sub['lyrics'].add_argument(
            '-e',
            '--extract',
            default='all',
            help='The lyric verse number to extract or "all".'
        )

        self.sub['lyrics'].add_argument(
            '-r',
            '--remap',
            help='Remap lyrics. Example: "--remap 3:2,5:3". This \
            example remaps lyrics verse 3 to verse 2 and verse 5 to 3. \
            Use commas to specify multiple remap pairs. One remap pair \
            is separated by a colon in this form: "old:new": "old" \
            stands for the old verse number. "new" stands for the new \
            verse number.')

        self.sub['lyrics'].add_argument(
            '-f',
            '--fix',
            action='store_true',
            help='Fix lyrics: Convert trailing hyphens ("la- la- la") \
            to a correct hyphenation ("la - la - la")')

        # rename

        self.sub['rename'] = self.sparser.add_parser(
            'rename',
            help='Rename the *.mscx files.',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=textwrap.dedent('''\
            Tokens you can use in the format string (-f, --format):
            '''))

        self.sub['rename'].add_argument(
            '-d',
            '--dry-run',
            action='store_true',
            help='Do not rename the scores')

        self.sub['rename'].add_argument(
            '-f',
            '--format',
            default='$title ($composer)',
            help='Format string.')

        self.sub['rename'].add_argument(
            '-a',
            '--ascii',
            action='store_true',
            help='Use only ASCII characters.')

        self.sub['rename'].add_argument(
            '-n',
            '--no-whitespace',
            action='store_true',
            help='Replace all whitespaces with dashes or \
            sometimes underlines.')

        # export

        self.sub['export'] = self.sparser.add_parser(
            'export',
            help='Export the scores to PDFs or to the specified \
            extension.')

        self.sub['export'].add_argument(
            '-e',
            '--extension',
            default='pdf',
            help='Extension to export. If this option \
            is omitted, then the default extension is "pdf".')

        # help

        self.sub['help'] = self.sparser.add_parser(
            'help',
            help='Show help. Use "mscxyz.py help all" to show help \
            messages of all subcommands. Use \
            "mscxyz.py help <subcommand>" to show only help messages \
            for the given subcommand.')

        self.sub['help'].add_argument(
            '-m',
            '--markdown',
            action='store_true',
            help='Show help in markdown format. \
            This option enables to generate the README file directly \
            form the command line output.')

        self.sub['help'].add_argument(
            '-r',
            '--rst',
            action='store_true',
            help='Show help in reStructuresText \
            format. This option enables to generate the README file \
            directly form the command line output.')

    def addPositional(self):
        self.parser.add_argument(
            'path',
            help='Path to a *.mscx file \
            or a folder which contains *.mscx files. In conjunction \
            with the subcommand "help" this positional parameter \
            accepts the names of all other subcommands or the word \
            "all".')

    def parse(self, args=None):
        self.args = self.parser.parse_args(args)
        return self.args

    def heading(self, text, level=1):
        length = len(text)
        if self.args.markdown:
            print('\n' + ('#' * level) + ' ' + text + '\n')
        elif self.args.rst:
            if level == 1:
                underline = '='
            elif level == 2:
                underline = '-'
            elif level == 2:
                underline = '^'
            elif level == 2:
                underline = '"'
            else:
                underline = '-'
            print('\n' + text + '\n' + (underline * length) + '\n')
        else:
            print(text)

    def codeBlock(self, text):
        if self.args.markdown:
            print('```\n' + text + '\n```')
        elif self.args.rst:
            print('.. code-block:: text\n\n  ' + text.replace('\n', '\n  '))
        else:
            print(text)

    def showAllHelp(self):
        if self.args.path == 'all':
            self.heading('mscxyz', 1)
            self.codeBlock(self.parser.format_help())

            self.heading('Subcommands', 1)

            for sub, command in self.sub.items():
                self.heading(command.prog, 2)
                self.codeBlock(command.format_help())

        else:
            self.codeBlock(self.sub[self.args.path].format_help())
