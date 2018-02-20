# -*- coding: utf-8 -*-

"""A command line tool to manipulate the XML based mscX and mscZ
files of the notation software MuseScore
"""

from mscxyz.batch import Batch
from mscxyz.lyrics import Lyrics
from mscxyz.meta import Meta
from mscxyz import cli
from mscxyz.rename import Rename
from mscxyz.tree import Tree
import six
import sys

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

if six.PY2:
    reload(sys)
    sys.setdefaultencoding('utf8')


def heading(args, text, level=1):
    length = len(text)
    if args.markdown:
        print('\n' + ('#' * level) + ' ' + text + '\n')
    elif args.rst:
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


def code_block(args, text):
    if args.markdown:
        print('```\n' + text + '\n```')
    elif args.rst:
        print('.. code-block:: text\n\n  ' + text.replace('\n', '\n  '))
    else:
        print(text)


def show_all_help(args):
    subcommands = ('clean', 'meta', 'lyrics', 'rename', 'export', 'help')

    if args.path == 'all':
        heading(args, 'mscxyz', 1)
        code_block(args, cli.parser.format_help())

        heading(args, 'Subcommands', 1)

        for subcommand in subcommands:
            command = getattr(cli, subcommand)
            heading(args, command.prog, 2)
            code_block(args, command.format_help())

    else:
        code_block(args, getattr(cli, args.path).format_help())


def execute(args=None):
    args = cli.parser.parse_args(args)

    if args.subcommand == 'help':
        show_all_help(args)
        sys.exit()

    batch = Batch(args.path, args.glob)

    if args.pick:
        batch.pick(args.pick, args.cycle_length)

    files = batch.get_files()

    output = []
    for file in files:

        if args.backup:
            from mscxyz.fileloader import File
            score = File(file)
            score.backup()

        if args.subcommand == 'clean':
            score = Tree(file)
            score.clean()
            if args.style:
                score.merge_style(args.style.name)
            score.write()

        elif args.subcommand == 'lyrics':
            score = Lyrics(file)
            if args.remap:
                score.remap(args.remap)
            elif args.fix:
                score.fix_lyrics()
            else:
                score.extract_lyrics(args.extract)

        elif args.subcommand == 'meta':
            score = Meta(file)
            if args.show:
                score.show()
            else:
                if args.json:
                    score.export_json()
                score.sync_meta_tags()
                score.write()

        elif args.subcommand == 'rename':
            score = Rename(file)
            if args.format:
                score.apply_format_string(args.format)

            if args.ascii:
                score.asciify()

            if args.no_whitespace:
                score.no_whitespace()
            score.execute(args.dry_run, args.verbose)

        elif args.subcommand == 'export':
            from mscxyz.fileloader import File
            score = File(file)
            score.export(args.extension)

        output.append(score)

    return output


if __name__ == '__main__':
    execute()
