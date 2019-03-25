"""Rename MuseScore files"""

from mscxyz.meta import Meta
from mscxyz.utils import color, get_settings
from tmep.format import alphanum, asciify, nowhitespace
import errno
import hashlib
import os
import tmep


def create_dir(path):
    try:
        os.makedirs(os.path.dirname(path))
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def prepare_fields(fields):
    args = get_settings('args')
    out = {}
    for field, value in fields.items():
        if value:
            if args.rename_alphanum:
                value = alphanum(value)
                value = value.strip()
            if args.rename_ascii:
                value = asciify(value)
            if args.rename_no_whitespace:
                value = nowhitespace(value)
            value = value.strip()
            value = value.replace('/', '-')
        out[field] = value
    return out


def apply_format_string(fields):
    args = get_settings('args')
    fields = prepare_fields(fields)
    name = tmep.parse(args.rename_format, fields)
    return name


def show(old, new):
    print('{} -> {}'.format(color(old, 'yellow'), color(new, 'green')))


def get_checksum(filename):
    BLOCKSIZE = 65536
    hasher = hashlib.sha1()
    with open(filename, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()


def rename_filename(source):
    args = get_settings('args')

    meta = Meta(source)
    meta_values = meta.interface.export_to_dict()
    target_filename = apply_format_string(meta_values)

    if args.rename_skip:
        skips = args.rename_skip.split(',')
        for skip in skips:
            if not meta_values[skip]:
                print(color('Field “{}” is empty! Skipping'.format(skip),
                            'red'))
                return meta

    if args.rename_target:
        target_base = os.path.abspath(args.rename_target)
    else:
        target_base = os.getcwd()

    target = os.path.join(target_base,
                          target_filename + '.' + meta.extension)

    if os.path.exists(target):
        target_format = target.replace('.mscx', '{}.mscx')
        i = ''
        while os.path.exists(target_format.format(i)):
            target = target_format.format(i)
            if get_checksum(source) == get_checksum(target):
                print(color('The file “{}” with the same checksum (sha1) '
                            'already exists in the target path “{}”!'
                            .format(source, target), 'red'))
                return meta
            if i == '':
                i = 1
            i += 1

        target = target_format.format(i)

    show(source, target)

    if not args.general_dry_run:

        create_dir(target)
        os.rename(source, target)

    return meta
