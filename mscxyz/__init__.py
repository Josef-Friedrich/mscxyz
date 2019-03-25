"""A command line tool to manipulate the XML based mscX and mscZ
files of the notation software MuseScore
"""

from mscxyz import cli
from mscxyz.lyrics import Lyrics
from mscxyz.meta import Meta
from mscxyz.rename import rename_filename
from mscxyz.score_file_classes import XMLTree, list_scores
from mscxyz.utils import set_settings, color
import lxml
import sys

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions


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

    files = list_scores(path=args.path, glob=args.general_glob)

    for file in files:

        print('\n' + color(file, 'red'))

        if args.general_backup:
            from mscxyz.score_file_classes import ScoreFile
            score = ScoreFile(file)
            score.backup()

        if args.subcommand == 'clean':
            score = XMLTree(file)
            print(score.filename)
            score.clean()
            if args.clean_style:
                score.merge_style(styles=args.clean_style.name)
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
            from mscxyz.score_file_classes import ScoreFile
            score = ScoreFile(file)
            score.export(extension=args.export_extension)

        report_errors(score.errors)


if __name__ == '__main__':
    execute()
