"""A command line tool to manipulate the XML based mscX and mscZ
files of the notation software MuseScore.
"""

from __future__ import annotations

from importlib import metadata

import mscxyz
import mscxyz.lyrics
import mscxyz.meta
import mscxyz.score
import mscxyz.style
from mscxyz import utils

__version__: str = metadata.version("mscxyz")

supported_versions = (2, 3, 4)

Score = mscxyz.score.Score

list_path = utils.list_path
