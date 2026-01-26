from __future__ import annotations

import typing
from pathlib import Path

from mscxyz import utils

if typing.TYPE_CHECKING:
    from mscxyz.score import Score


extensions = (
    # Vendor specific formats
    "mscz",  # https://github.com/musescore/MuseScore/blob/75fe9addbfd1b2588f4b817668e396a317131f8b/src/notation/notationmodule.cpp#L128
    "mscx",  # https://github.com/musescore/MuseScore/blob/75fe9addbfd1b2588f4b817668e396a317131f8b/src/notation/notationmodule.cpp#L129
    "spos",  # https://github.com/musescore/MuseScore/blob/75fe9addbfd1b2588f4b817668e396a317131f8b/src/notation/notationmodule.cpp#L126
    "mpos",  # https://github.com/musescore/MuseScore/blob/75fe9addbfd1b2588f4b817668e396a317131f8b/src/notation/notationmodule.cpp#L127
    # Graphical formats
    "pdf",  # https://github.com/musescore/MuseScore/blob/75fe9addbfd1b2588f4b817668e396a317131f8b/src/importexport/imagesexport/imagesexportmodule.cpp#L54
    "svg",  # https://github.com/musescore/MuseScore/blob/75fe9addbfd1b2588f4b817668e396a317131f8b/src/importexport/imagesexport/imagesexportmodule.cpp#L55
    "png",  # https://github.com/musescore/MuseScore/blob/75fe9addbfd1b2588f4b817668e396a317131f8b/src/importexport/imagesexport/imagesexportmodule.cpp#L56
    # Audio formats
    "wav",  # https://github.com/musescore/MuseScore/blob/75fe9addbfd1b2588f4b817668e396a317131f8b/src/importexport/audioexport/audioexportmodule.cpp#L56
    "mp3",  # https://github.com/musescore/MuseScore/blob/75fe9addbfd1b2588f4b817668e396a317131f8b/src/importexport/audioexport/audioexportmodule.cpp#L57
    "ogg",  # https://github.com/musescore/MuseScore/blob/75fe9addbfd1b2588f4b817668e396a317131f8b/src/importexport/audioexport/audioexportmodule.cpp#L58
    "flac",  # https://github.com/musescore/MuseScore/blob/75fe9addbfd1b2588f4b817668e396a317131f8b/src/importexport/audioexport/audioexportmodule.cpp#L59
    # Hybrid formats
    "mid",  # https://github.com/musescore/MuseScore/blob/75fe9addbfd1b2588f4b817668e396a317131f8b/src/importexport/midi/midimodule.cpp#L59
    "midi",  # https://github.com/musescore/MuseScore/blob/75fe9addbfd1b2588f4b817668e396a317131f8b/src/importexport/midi/midimodule.cpp#L59
    "kar",  # https://github.com/musescore/MuseScore/blob/75fe9addbfd1b2588f4b817668e396a317131f8b/src/importexport/midi/midimodule.cpp#L59
    # Score formats
    "musicxml",  # https://github.com/musescore/MuseScore/blob/75fe9addbfd1b2588f4b817668e396a317131f8b/src/importexport/musicxml/musicxmlmodule.cpp#L71
    "xml",  # https://github.com/musescore/MuseScore/blob/75fe9addbfd1b2588f4b817668e396a317131f8b/src/importexport/musicxml/musicxmlmodule.cpp#L71
    "mxl",  # https://github.com/musescore/MuseScore/blob/75fe9addbfd1b2588f4b817668e396a317131f8b/src/importexport/musicxml/musicxmlmodule.cpp#L71
    "brf",  # https://github.com/musescore/MuseScore/blob/75fe9addbfd1b2588f4b817668e396a317131f8b/src/braille/braillemodule.cpp#L53
    "mei",  # https://github.com/musescore/MuseScore/blob/75fe9addbfd1b2588f4b817668e396a317131f8b/src/importexport/mei/meimodule.cpp#L58
)
"""Supported file extensions for export in MuseScore version 4."""


class Export:
    score: "Score"

    def __init__(self, score: "Score") -> None:
        self.score = score

    def to_extension(self, extension: str = "pdf") -> Path:
        """Export the score to the specifed file type.

        :param extension: The extension (default: pdf)

        :return: The path of the exported file.
        """

        extension = extension.lower()

        if extension not in extensions:
            raise ValueError(
                f"Unsupported extension: {extension}! Supported extensions: {extensions}"
            )

        dest: Path = self.score.change_path(extension=extension)
        utils.execute_musescore(
            [
                "--export-to",
                str(dest),
                str(self.score.path),
            ]
        )
        return dest

    def compress(self, remove_origin: bool = False) -> Path:
        """Compress the score.

        :return: The path of the new compressed score or the path of the score itself
          if it is already compressed.
        """
        if not self.score.is_uncompressed:
            return self.score.path
        new_path = self.to_extension("mscz")
        if remove_origin:
            self.score.path.unlink()
        return new_path

    def reload(self, save: bool = False) -> Export:
        """
        Reload the MuseScore file.

        :param save: Whether to save the changes before reloading. Default is False.

        :return: The reloaded Export object.

        :see: :meth:`mscxyz.score.Score.reload`
        """
        return self.score.reload(save).export
