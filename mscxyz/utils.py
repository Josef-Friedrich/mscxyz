"""A collection of useful utility functions"""

import os
import platform
import subprocess
import termcolor
from typing import Sequence
from mscxyz.settings import DefaultArguments


def get_args() -> DefaultArguments:
    """Get the ``args`` object (the ``argparse`` object) which is stored in
    the .settings.py submodule for all other submodules.

    :return: the ``argparse`` object
    """
    from mscxyz import settings
    return getattr(settings, 'args')


def set_args(args) -> DefaultArguments:
    """Set the ``args`` object (the ``argparse`` object) which is stored in
    the .settings.py submodule for all other submodules to import.
    """
    from mscxyz import settings
    setattr(settings, 'args', args)
    return args


def get_mscore_bin() -> str:
    """Check the existance of the executable mscore

    :return: Path of the executable.
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


def mscore(cli_args: Sequence[str]) -> subprocess.Popen:
    """
    :param cli_args: Command line arguments to call the mscore binary with.
    """
    executable = get_mscore_bin()
    cli_args.insert(0, executable)
    p = subprocess.Popen(cli_args, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    p.wait()
    if p.returncode != 0:
        for line in p.stderr:
            print(line.decode('utf-8'))
        raise ValueError('mscore exits with returncode != 0')
    return p


def re_open(input_file: str):
    """Open and save a MuseScore file with the ``mscore`` binary under the same
    file path.

    :param input_file: The path (relative or absolute) of a MuseScore file.
    """
    mscore(['-o', input_file, input_file])


def convert_mxl(input_file: str):
    """
    Convert a MusicXML file into a MuseScore file.

    :param input_file: The path (relative or absolute) of a MusicXML file.
    """
    output_file = input_file.replace('.mxl', '.mscx')
    mscore(['-o', output_file, input_file])
    os.remove(input_file)


def color(*args) -> str:
    """Wrapper function around ``termcolor.colored()`` to easily turn off and
    on colorized terminal output on the command line.

    :param args: First arg must be an string to print out, second arg a color
      name.

    Example usage:

    .. code:: Python

        color('“{}”'.format(post[field]), 'yellow')
    """
    settings = get_args()
    if settings.general_colorize:
        return termcolor.colored(*args)
    else:
        return args[0]
