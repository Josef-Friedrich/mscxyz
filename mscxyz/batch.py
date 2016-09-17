# -*- coding: utf-8 -*-

"""Load multiple MuseScore files"""

import os
import fnmatch


class Batch(object):

    def __init__(self, path, glob='*.mscx'):
        self.path = path
        self.files = []

        for root, dirs, files in os.walk(path):
            for file in files:
                if fnmatch.fnmatch(file, glob):
                    file_path = os.path.join(root, file)
                    self.files.append(file_path)

        self.files.sort()

    def pick(self, pick=1, cycle_length=4):
        hit = int(pick)
        counter = 0

        output = []
        for score in self.files:

            counter += 1
            if hit == counter:
                output.append(score)
                hit = hit + pick

        self.files = output

    def getFiles(self):
        if os.path.isdir(self.path):
            return self.files
        else:
            return [self.path]
