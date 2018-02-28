# -*- coding: utf-8 -*-

"""Rename MuseScore files"""

from mscxyz.score_file_classes import ScoreFile
from mscxyz.meta import Meta
from mscxyz.utils import color, get_settings
import errno
import os
import re
import tmep
import unidecode
import hashlib


def create_dir(path):
    try:
        os.makedirs(os.path.dirname(path))
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def prepare_fields(fields):
    def prepare(value):
        value = value.strip()
        return value.replace('/', '-')
    out = {}
    for field, value in fields.items():
        out[field] = prepare(value)
    return out


def clean_up(name):
    name = name.replace('(', '_')
    name = name.replace('-_', '_')
    # Replace two or more dashes with one.
    name = re.sub('-{2,}', '_', name)
    name = re.sub('_{2,}', '_', name)
    # Remove dash at the begining
    name = re.sub('^-', '', name)
    # Remove the dash from the end
    name = re.sub('-$', '', name)
    return name


def apply_format_string(fields):
    args = get_settings('args')
    fields = prepare_fields(fields)
    name = tmep.parse(args.rename_format, fields)
    return name


def format_filename(name):
    args = get_settings('args')
    name = name.strip()
    if args.rename_ascii:
        name = tmep.Functions.tmpl_asciify(name)
    if args.rename_no_whitespace:
        name = tmep.Functions.tmpl_replchars(name, '-', (' ', ';', '?', '!',
                                             '_', '#', '&', '+', ':'))
        name = tmep.Functions.tmpl_delchars(name, (',', '.', '\'', '`', ')'))
        name = clean_up(name)
    return name


def show(old, new):
    args = get_settings('args')
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

    target_filename = format_filename(target_filename)

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
