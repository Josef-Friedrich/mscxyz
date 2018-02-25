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
from mscxyz.utils import set_settings, color

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

if six.PY2:
    reload(sys)
    sys.setdefaultencoding('utf8')


def heading(args, text, level=1):
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


def code_block(args, text):
    if args.help_markdown:
        print('```\n' + text + '\n```')
    elif args.help_rst:
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


def execute(args=None):
    args = cli.parser.parse_args(args)
    set_settings('args', args)

    if args.subcommand == 'help':
        show_all_help(args)
        sys.exit()

    batch = Batch(path=args.path, glob=args.general_glob)
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
                score.merge_style(style_file=args.clean_style.name)
            score.save(mscore=args.general_mscore)

        elif args.subcommand == 'lyrics':
            score = Lyrics(file)
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
                        score.distribute_field(source_field=a[0],
                                               format_string=a[1])
                if args.meta_set:
                    for a in args.meta_set:
                        score.set_field(destination_field=a[0],
                                        format_string=a[1])
                if args.meta_sync:
                    score.sync_fields()
                post = score.interface.export_to_dict()
                score.show(pre, post, colorize= args.general_colorize)
            if not args.general_dry_run and not score.errors and pre != post:
                score.save(mscore=args.general_mscore)

        elif args.subcommand == 'rename':
            score = Rename(file)
            if args.rename_format:
                score.apply_format_string(format_string=args.rename_format)
            if args.rename_ascii:
                score.asciify()
            if args.rename_no_whitespace:
                score.no_whitespace()
            score.execute(dry_run=args.general_dry_run,
                          verbose=args.general_verbose)

        elif args.subcommand == 'export':
            from mscxyz.fileloader import File
            score = File(file)
            score.export(extension=args.export_extension)

        report_errors(score.errors)


if __name__ == '__main__':
    execute()
