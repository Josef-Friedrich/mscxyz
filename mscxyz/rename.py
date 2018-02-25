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


def create_dir(path):
    try:
        os.makedirs(path)
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


def generate_filename(name):
    name = replace_to_dash(name, ' ', ';', '?', '!', '_', '#', '&', '+', ':')
    name = delete_characters(name, ',', '.', '\'', '`', ')')
    name = clean_up(name)
    return name


class Rename(File):

    def __init__(self, relpath):
        super(Rename, self).__init__(relpath)
        self.score = Meta(self.relpath)
        self.workname = self.basename

    def asciify(self):
        umlaute = {'ae': u'ä', 'oe': u'ö', 'ue': u'ü',
                   'Ae': u'Ä', 'Oe': u'Ö', 'Ue': u'Ü'}
        for replace, search in umlaute.items():
            self.workname = self.workname.replace(search, replace)

        self.workname = unidecode.unidecode(self.workname)

    def replace_to_dash(self, *characters):
        for character in characters:
            self.workname = self.workname.replace(character, '-')

    def delete_characters(self, *characters):
        for character in characters:
            self.workname = self.workname.replace(character, '')

    def clean_up(self):
        string = self.workname
        string = string.replace('(', '_')
        string = string.replace('-_', '_')

        # Replace two or more dashes with one.
        string = re.sub('-{2,}', '_', string)
        string = re.sub('_{2,}', '_', string)
        # Remove dash at the begining
        string = re.sub('^-', '', string)
        # Remove the dash from the end
        string = re.sub('-$', '', string)

        self.workname = string

    def no_whitespace(self):
        self.replace_to_dash(' ', ';', '?', '!', '_', '#', '&', '+', ':')
        self.delete_characters(',', '.', '\'', '`', ')')
        self.clean_up()

    def debug(self):
        print(self.workname)

    def get_field(self, field):
        return getattr(self.score.interface, 'combined_' + field)

    def apply_format_string(self,
                            format_string='$vbox_title ($vbox_composer)'):
        self.workname = tmep.parse(format_string,
                                   self.score.interface.export_to_dict())

    def execute(self):
        args = get_settings('args')
        if args.general_dry_run or args.general_verbose > 0:
            print('{} -> {}'.format(color(self.basename, 'red'),
                                    color(self.workname, 'yellow')))

        if not args.general_dry_run:
            newpath = self.workname + '.' + self.extension
            newdir = os.path.dirname(newpath)
            if newdir:
                create_dir(os.path.dirname(newpath))
            os.rename(self.relpath, newpath)
