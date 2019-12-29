"""A collection of useful utility functions"""

import os
import platform
import subprocess
import termcolor


def get_args():
    """Get the ``args`` object (the ``argparse`` object) which is stored in
    the .settings.py submodule for all other submodules.

    :return: the ``argparse`` object
    """
    from mscxyz import settings
    return getattr(settings, 'args')


def set_args(args):
    """Set the ``args`` object (the ``argparse`` object) which is stored in
    the .settings.py submodule for all other submodules to import.
    """
    from mscxyz import settings
    return setattr(settings, 'args', args)


def get_mscore_bin():
    """Check the existance of the executable mscore

    :return: Path of the executable if true, else false.
    """
    args = get_args()
    system = platform.system()
    if args and args.general_executable:
        binary = args.general_executable
    elif system == 'Darwin':
        binary = '/Applications/MuseScore 2.app/Contents/MacOS/mscore'
    else:
        cmd = 'where' if system == 'Windows' else 'which'
        binary = subprocess.check_output([cmd, 'mscore'])
        binary = binary.decode('utf-8')
        binary = binary.replace('\n', '')

    if os.path.exists(binary):
        return binary
    else:
        raise ValueError('mscore binary could not be found.')


def mscore(commands):
    executable = get_mscore_bin()
    commands.insert(0, executable)
    p = subprocess.Popen(commands, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    p.wait()
    if p.returncode != 0:
        for line in p.stderr:
            print(line.decode('utf-8'))
        raise ValueError('mscore exit with returncode != 0')
    return p


def re_open(input_file):
    mscore(['-o', input_file, input_file])


def convert_mxl(input_file):
    output_file = input_file.replace('.mxl', '.mscx')
    mscore(['-o', output_file, input_file])
    os.remove(input_file)


def color(*args):
    settings = get_args()
    if settings.general_colorize:
        return termcolor.colored(*args)
    else:
        return args[0]
