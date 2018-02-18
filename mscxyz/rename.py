# -*- coding: utf-8 -*-

"""Rename MuseScore files"""

import os
from termcolor import colored
import tmep
import unidecode
import re
import errno

from mscxyz.fileloader import File
from mscxyz.meta import Meta


TOKEN = (
    'composer',
    'lyricist',
    'subtitle',
    'title',
)


def create_dir(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


class Rename(File):

    def __init__(self, fullpath):
        super(Rename, self).__init__(fullpath)
        self.score = Meta(self.fullpath)
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
        self.replace_to_dash(' ', ';', '?', '!', '_', '#', '&', '+', '/', ':')
        self.delete_characters(',', '.', '\'', '`', ')')
        self.clean_up()

    def debug(self):
        print(self.workname)

    def get_token(self, token):
        return self.score.get(token)

    def apply_format_string(self, format='$title ($composer)'):
        values = {}
        for key in TOKEN:
            values[key] = self.get_token(key)

        self.workname = tmep.parse(format, values)

    def execute(self, dry_run=False, verbose=0):
        if dry_run or verbose > 0:
            print(colored(self.basename, 'red') + ' -> ' +
                  colored(self.workname, 'yellow'))

        if not dry_run:
            newpath = self.workname + '.' + self.extension
            newdir = os.path.dirname(newpath)
            if newdir:
                create_dir(os.path.dirname(newpath))
            os.rename(self.fullpath, newpath)
