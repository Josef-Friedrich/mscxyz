"""Manipulate the lyrics"""

from __future__ import annotations

import typing

from lxml.etree import _Element

if typing.TYPE_CHECKING:
    from mscxyz.score import Score


class NumberedLyricsElement:
    no: int
    element: _Element


class Lyrics:
    score: "Score"

    elements: list[NumberedLyricsElement]

    def __init__(self, score: "Score") -> None:
        self.score = score
        self.elements = self.__renumber()

    def __renumber(self) -> list[NumberedLyricsElement]:
        """Normalize numbering of verses to natural numbering (1,2,3).

        From

        .. code-block:: xml

                <Lyrics>
                        <text>1. la</text>
                </Lyrics>
                <Lyrics>
                        <no>1</no>
                        <style>Lyrics Even Lines</style>
                        <text>2. li</text>
                </Lyrics>
                <Lyrics>
                        <no>2</no>
                        <text>3. lo</text>
                </Lyrics>

        To

        .. code-block:: python

                [
                        {'number': 1, 'element': lyrics_tag},
                        {'number': 2, 'element': lyrics_tag},
                        {'number': 3, 'element': lyrics_tag},
                ]
        """
        lyrics: list[NumberedLyricsElement] = []
        for lyric in self.score.xml_root.findall(".//Lyrics"):
            numbered = NumberedLyricsElement()
            numbered.element = lyric
            number: _Element | None = lyric.find("no")

            if number is not None and number.text is not None:
                no = int(number.text) + 1
            else:
                no = 1
            numbered.no = no

            lyrics.append(numbered)

        return lyrics

    @property
    def number_of_verses(self) -> int:
        """Retrieve the number of verses.

        From:

                1. La
                2. La
                3. La

        To:

                3

        """
        max_lyric = 0
        for element in self.elements:
            if element.no > max_lyric:
                max_lyric = element.no

        return max_lyric

    def remap(self, remap_string: str) -> None:
        for pair in remap_string.split(","):
            old = pair.split(":")[0]
            new = pair.split(":")[1]
            for element in self.elements:
                if element.no == int(old):
                    self.score.xml.find_safe("no", element.element).text = str(
                        int(new) - 1
                    )

    def __extract_one_lyrics_verse(self, number: int, mscore: bool = False) -> None:
        """Extract a lyric verse by verse number.

        :param number: The number of the lyrics verse starting by 1
        """

        score = self.score.new()

        for element in score.lyrics.elements:
            tag = element.element

            if element.no != number:
                self.score.xml.remove(tag)
            elif number != 1:
                self.score.xml.set_text("no", 0, tag)

        ext: str = "." + score.extension
        new_name: str = str(score.path).replace(ext, "_" + str(number) + ext)
        score.save(new_name, mscore)

    def extract_lyrics(self, number: int | None = None) -> None:
        """Extract one lyric verse or all lyric verses.

        :param number: The lyric verse number. 1 is the first verse.
        """
        if number is None or number == 0:
            for n in range(1, self.number_of_verses + 1):
                self.__extract_one_lyrics_verse(n)
        else:
            self.__extract_one_lyrics_verse(number)

    def fix_lyrics_verse(self, verse_number: int) -> None:
        """
        from:

        .. code-block:: xml

                <Lyrics>
                        <text>la-</text>
                </Lyrics>
                <Lyrics>
                        <syllabic>end</syllabic>
                        <text>la-</text>
                </Lyrics>
                <Lyrics>
                        <text>la.</text>
                </Lyrics>

        to:

        .. code-block:: xml

                <Lyrics>
                        <syllabic>begin</syllabic>
                        <text>la</text>
                </Lyrics>
                <Lyrics>
                        <syllabic>middle</syllabic>
                        <text>la</text>
                </Lyrics>
                <Lyrics>
                        <syllabic>end</syllabic>
                        <text>la.</text>
                </Lyrics>
        """

        syllabic = False
        for element in self.elements:
            if element.no == verse_number:
                tag: _Element = element.element
                element_text: _Element = self.score.xml.find_safe(
                    "text",
                    tag,
                )
                text = self.score.xml.get_text_safe(element_text)
                element_syllabic: _Element = self.score.xml.create_element("syllabic")
                append_syllabic: bool = True
                if text.endswith("-"):
                    element_text.text = text[:-1]
                    if not syllabic:
                        element_syllabic.text = "begin"
                        syllabic = True
                    else:
                        element_syllabic.text = "middle"
                else:
                    if syllabic:
                        element_syllabic.text = "end"
                        syllabic = False
                    else:
                        append_syllabic = False

                if append_syllabic:
                    tag.append(element_syllabic)

    def fix_lyrics(self, mscore: bool = False) -> None:
        for verse_number in range(1, self.number_of_verses + 1):
            self.fix_lyrics_verse(verse_number)

        self.score.save(mscore=mscore)

    def reload(self, save: bool = False) -> Lyrics:
        """
        Reload the MuseScore file.

        :param save: Whether to save the changes before reloading. Default is False.

        :return: The reloaded Lyrics object.

        :see: :meth:`mscxyz.score.Score.reload`
        """
        return self.score.reload(save).lyrics
