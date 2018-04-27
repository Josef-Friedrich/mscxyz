# -*- coding: utf-8 -*-

"""A collection of useful utility functions"""

import os
import platform
import subprocess
import termcolor


def get_mscore_bin():
    """Check the existance of the executable mscore

    :return: Path of the executable if true, else false.
    """
    system = platform.system()
    if system == 'Darwin':
        bin = '/Applications/MuseScore 2.app/Contents/MacOS/mscore'
    else:
        cmd = 'where' if system == 'Windows' else 'which'
        bin = subprocess.check_output([cmd, 'mscore'])
        bin = bin.replace(b'\n', b'')

    if os.path.exists(bin):
        return bin
    else:
        raise FileNotFoundError('mscore binary could not be found.') # noqa F821


def mscore(commands):
    executable = get_mscore_bin()
    if executable:
        commands.insert(0, executable)

        # OUT=None
        OUT = open(os.devnull, 'wb')
        subprocess.call(commands, stdout=OUT, stderr=OUT)
        OUT.close()


def re_open(input_file):
    mscore(['-o', input_file, input_file])


def convert_mxl(input_file):
    output_file = input_file.replace('.mxl', '.mscx')
    mscore(['-o', output_file, input_file])
    os.remove(input_file)


def get_settings(key):
    from mscxyz import settings
    return getattr(settings, key)


def set_settings(key, value):
    from mscxyz import settings
    return setattr(settings, key, value)


def color(*args):
    settings = get_settings('args')
    if settings.general_colorize:
        return termcolor.colored(*args)
    else:
        return args[0]
