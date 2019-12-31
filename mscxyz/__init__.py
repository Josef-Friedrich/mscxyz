"""A command line tool to manipulate the XML based mscX and mscZ
files of the notation software MuseScore.

API Interface:

Classes:

.. code ::

    MscoreFile
        MscoreXmlTree
            MscoreLyricsInterface
            MscoreMetaInterface
            MscoreStyleInterface


Functions:

.. code ::

    exec_mscore_binary
    list_scores
"""

from mscxyz import cli
from mscxyz.lyrics import MscoreLyricsInterface
from mscxyz.meta import Meta
from mscxyz.rename import rename_filename
from mscxyz.score_file_classes import MscoreFile, \
                                      MscoreXmlTree, \
                                      MscoreStyleInterface, \
                                      list_scores
from mscxyz.utils import set_args, color, mscore
from mscxyz.settings import DefaultArguments
import lxml
import sys
import os
import configparser
import typing

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

###############################################################################
# API INTERFACE BEGIN
###############################################################################

# Classes

# Level 1

MscoreFile
"""see submodule ``score_file_classes.py``"""

# Level 2

MscoreXmlTree
"""see submodule ``score_file_classes.py``"""

# Level 3

MscoreLyricsInterface
"""see submodule ``lyrics.py``"""

MscoreMetaInterface = Meta
"""see submodule ``meta.py``"""

MscoreStyleInterface
"""see submodule ``score_file_classes.py``"""

# Functions

exec_mscore_binary = mscore
"""see submodule ``utils.py``"""

list_scores
"""see submodule ``score_file_classes.py``"""

###############################################################################
# API INTERFACE END
###############################################################################


def parse_config_ini(relpath: str = None) -> configparser.ConfigParser:
    """Parse the configuration file. The file format is INI. The default
    location is ``/etc/mscxyz.ini``."""
    if not relpath:
        ini_file = os.path.abspath(os.path.join(os.sep, 'etc', 'mscxyz.ini'))
    else:
        ini_file = relpath
    config = configparser.ConfigParser()
    if os.path.exists(ini_file):
        config.read(ini_file)
        return config


def merge_config_into_args(config: configparser.ConfigParser,
                           args: DefaultArguments) -> DefaultArguments:
    for section in config.sections():
        for key, value in config[section].items():
            arg = '{}_{}'.format(section, key)
            if not hasattr(args, arg) or not getattr(args, arg):
                setattr(args, arg, value)

    for arg in ['general_backup', 'general_colorize', 'general_dry_run',
                'general_mscore', 'help_markdown', 'help_rst',
                'lyrics_fix', 'meta_json', 'meta_sync',
                'rename_alphanum', 'rename_ascii',
                'rename_no_whitespace']:
        if hasattr(args, arg):
            value = getattr(args, arg)
            if value == 1 or value == 'true' or value == 'True':
                setattr(args, arg, True)
            else:
                setattr(args, arg, False)

    return args


def heading(args: DefaultArguments, text: str, level: int = 1):
    length = len(text)
    if args.help_markdown:
        print('\n' + ('#' * level) + ' ' + text + '\n')
    elif args.help_rst:
        if level == 1:
            underline = '='
        elif level == 2:
            underline = '-'
        elif level == 3:
            underline = '^'
        elif level == 4:
            underline = '"'
        else:
            underline = '-'
        print('\n' + text + '\n' + (underline * length) + '\n')
    else:
        print(text)


def code_block(args: DefaultArguments, text: str):
    if args.help_markdown:
        print('```\n' + text + '\n```')
    elif args.help_rst:
        print('.. code-block:: text\n\n  ' + text.replace('\n', '\n  '))
    else:
        print(text)


def show_all_help(args: DefaultArguments):
    subcommands = ('clean', 'meta', 'lyrics', 'rename', 'export', 'help')

    if args.path == 'all':
        heading(args, 'mscxyz', 1)
        code_block(args, cli.parser.format_help())

        heading(args, 'Subcommands', 1)

        for subcommand in subcommands:
            command = getattr(cli, 'sub_' + subcommand)
            heading(args, command.prog, 2)
            code_block(args, command.format_help())

    else:
        code_block(args, getattr(cli, args.path).format_help())


def report_errors(errors: typing.Sequence):
    for error in errors:
        print('{}: {}; message: {}'.format(
            color('Error', 'white', 'on_red'),
            color(error.__class__.__name__, 'red'),
            error.msg
        ))


def no_error(error, errors):
    for e in errors:
        if isinstance(e, error):
            return False
    return True


def execute(args: typing.Sequence = None):
    args = cli.parser.parse_args(args)
    config = parse_config_ini(args.general_config_file)
    if config:
        args = merge_config_into_args(config, args)
    set_args(args)

    if args.subcommand == 'help':
        show_all_help(args)
        sys.exit()

    files = list_scores(path=args.path, glob=args.general_glob)

    for file in files:

        print('\n' + color(file, 'red'))

        if args.general_backup:
            from mscxyz.score_file_classes import MscoreFile
            score = MscoreFile(file)
            score.backup()

        if args.subcommand == 'clean':
            score = MscoreXmlTree(file)
            print(score.filename)
            score.clean()
            if args.clean_style:
                score.merge_style(styles=args.clean_style.name)
            score.save(mscore=args.general_mscore)

        elif args.subcommand == 'lyrics':
            score = MscoreLyricsInterface(file)
            if args.lyrics_remap:
                score.remap(remap_string=args.lyrics_remap,
                            mscore=args.general_mscore)
            elif args.lyrics_fix:
                score.fix_lyrics(mscore=args.general_mscore)
            else:
                score.extract_lyrics(number=args.lyrics_extract,
                                     mscore=args.general_mscore)

        elif args.subcommand == 'meta':
            score = Meta(file)
            if no_error(lxml.etree.XMLSyntaxError, score.errors):
                pre = score.interface.export_to_dict()
                if args.meta_clean:
                    score.clean(fields=args.meta_clean)
                if args.meta_json:
                    score.export_json()
                if args.meta_dist:
                    for a in args.meta_dist:
                        score.distribute_field(source_fields=a[0],
                                               format_string=a[1])
                if args.meta_set:
                    for a in args.meta_set:
                        score.set_field(destination_field=a[0],
                                        format_string=a[1])
                if args.meta_delete:
                    score.delete_duplicates()
                if args.meta_sync:
                    score.sync_fields()
                if args.meta_log:
                    score.write_to_log_file(args.meta_log[0], args.meta_log[1])
                post = score.interface.export_to_dict()
                score.show(pre, post)
            if not args.general_dry_run and not score.errors and pre != post:
                score.save(mscore=args.general_mscore)

        elif args.subcommand == 'rename':
            score = rename_filename(file)

        elif args.subcommand == 'export':
            from mscxyz.score_file_classes import MscoreFile
            score = MscoreFile(file)
            score.export(extension=args.export_extension)

        report_errors(score.errors)


if __name__ == '__main__':
    execute()
