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
"""Score""" ""

Lyrics = mscxyz.lyrics.Lyrics
"""Lyrics"""

Meta = mscxyz.meta.Meta
"""Meta"""

Style = mscxyz.style.Style
"""Style"""

list_score_paths = utils.list_score_paths
"""list_score_paths"""
