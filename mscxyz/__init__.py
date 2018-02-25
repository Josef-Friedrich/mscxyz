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
import lxml

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
        elif level == 3:
            underline = '^'
        elif level == 4:
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
            command = getattr(cli, 'sub_' + subcommand)
            heading(args, command.prog, 2)
            code_block(args, command.format_help())

    else:
        code_block(args, getattr(cli, args.path).format_help())


def report_errors(errors):
    for error in errors:
        print('Error: {}; message: {}'.format(
            error.__class__.__name__,
            error.msg
        ))

def no_error(error, errors):
    for e in errors:
        if isinstance(e, error):
            return False
    return True


def execute(args=None):
    args = cli.parser.parse_args(args)

    if args.subcommand == 'help':
        show_all_help(args)
        sys.exit()

    batch = Batch(args.path, glob=args.general_glob)
    files = batch.get_files()

    for file in files:

        if args.general_backup:
            from mscxyz.fileloader import File
            score = File(file)
            score.backup()

        if args.subcommand == 'clean':
            score = Tree(file)
            score.clean()
            if args.clean_style:
                score.merge_style(args.clean_style.name)
            score.save(mscore=args.general_mscore)

        elif args.subcommand == 'lyrics':
            score = Lyrics(file)
            if args.remap:
                score.remap(args.remap, mscore=args.general_mscore)
            elif args.fix:
                score.fix_lyrics(mscore=args.general_mscore)
            else:
                score.extract_lyrics(args.extract, mscore=args.general_mscore)

        elif args.subcommand == 'meta':
            score = Meta(file)
            if no_error(lxml.etree.XMLSyntaxError, score.errors):
                pre = score.interface.export_to_dict()
                if args.meta_clean:
                    score.clean(args.meta_clean)
                if args.meta_json:
                    score.export_json()
                if args.meta_dist:
                    for a in args.meta_dist:
                        score.distribute_field(a[0], a[1])
                if args.meta_set:
                    for a in args.meta_set:
                        score.set_field(a[0], a[1])
                if args.meta_sync:
                    score.sync_fields()
                post = score.interface.export_to_dict()
                score.show(pre, post)
            if not args.general_dry_run and not score.errors and pre != post:
                score.save(mscore=args.general_mscore)

        elif args.subcommand == 'rename':
            score = Rename(file)
            if args.format:
                score.apply_format_string(args.format)

            if args.ascii:
                score.asciify()

            if args.no_whitespace:
                score.no_whitespace()
            score.execute(dry_run=args.general_dry_run,
                          verbose=args.general_verbose)

        elif args.subcommand == 'export':
            from mscxyz.fileloader import File
            score = File(file)
            score.export(args.extension)

        report_errors(score.errors)


if __name__ == '__main__':
    execute()
