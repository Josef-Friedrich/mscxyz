# -*- coding: utf-8 -*-

"""Rename MuseScore files"""

from mscxyz.fileloader import File
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


def asciify(name):
    umlaute = {'ae': u'ä', 'oe': u'ö', 'ue': u'ü',
               'Ae': u'Ä', 'Oe': u'Ö', 'Ue': u'Ü'}
    for replace, search in umlaute.items():
        name = name.replace(search, replace)
    return unidecode.unidecode(name)


def replace_to_dash(name, *characters):
    for character in characters:
        name = name.replace(character, '-')
    return name


def delete_characters(name, *characters):
    for character in characters:
        name = name.replace(character, '')
    return name


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
        name = asciify(name)
    if args.rename_no_whitespace:
        name = replace_to_dash(name, ' ', ';', '?', '!', '_', '#', '&', '+',
                               ':')
        name = delete_characters(name, ',', '.', '\'', '`', ')')
        name = clean_up(name)
    return name


def show(old, new):
    args = get_settings('args')
    print('{} -> {}'.format(color(old, 'red'), color(new, 'yellow')))


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
    target_filename = apply_format_string(meta.interface.export_to_dict())

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
