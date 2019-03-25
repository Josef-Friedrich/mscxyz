"""Manipulate the lyrics"""

from mscxyz.score_file_classes import XMLTree
import lxml.etree as etree


class Lyrics(XMLTree):

    def __init__(self, relpath):
        super(Lyrics, self).__init__(relpath)
        self.lyrics = self.normalize_lyrics()
        self.max = self.get_max()

    def normalize_lyrics(self):
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
        lyrics = []
        for lyric in self.xml_tree.findall('.//Lyrics'):
            safe = {}
            safe['element'] = lyric
            number = lyric.find('no')

            if hasattr(number, 'text'):
                no = int(number.text) + 1
            else:
                no = 1
            safe['number'] = no

            lyrics.append(safe)

        return lyrics

    def get_max(self):
        """Retrieve the number of verses.

        From:

                1. La
                2. La
                3. La

        To:

                3

        """
        max_lyric = 0
        for element in self.lyrics:
            if element['number'] > max_lyric:
                max_lyric = element['number']

        return max_lyric

    def remap(self, remap_string, mscore=False):
        for pair in remap_string.split(','):
            old = pair.split(':')[0]
            new = pair.split(':')[1]
            for element in self.lyrics:
                if element['number'] == int(old):
                    element['element'].find('no').text = str(int(new) - 1)

        self.save(mscore)

    def extract_one_lyrics_verse(self, number, mscore=False):
        """Extract a lyric verse by verse number.

        :param int number: The number of the lyrics verse starting by 1
        """
        score = Lyrics(self.relpath)

        for element in score.lyrics:
            tag = element['element']

            if element['number'] != number:
                tag.getparent().remove(tag)
            elif number != 1:
                tag.find('no').text = '0'

        ext = '.' + self.extension
        new_name = score.relpath.replace(ext, '_' + str(number) + ext)
        score.save(new_name, mscore)

    def extract_lyrics(self, number=None, mscore=False):
        """Extract one lyric verse or all lyric verses.

        :param mixed number: The lyric verse number or 'all'
        """

        if number == 'all':
            for n in range(1, self.max + 1):
                self.extract_one_lyrics_verse(n)
        else:
            self.extract_one_lyrics_verse(int(number))

    def fix_lyrics_verse(self, verse_number):
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
        for element in self.lyrics:
            if element['number'] == verse_number:
                tag = element['element']
                tag_text = tag.find('text')
                text = tag_text.text
                tag_syl = etree.Element('syllabic')
                if text.endswith('-'):
                    tag_text.text = text[:-1]
                    if not syllabic:
                        tag_syl.text = 'begin'
                        syllabic = True
                    else:
                        tag_syl.text = 'middle'
                else:
                    if syllabic:
                        tag_syl.text = 'end'
                        syllabic = False
                    else:
                        tag_syl = False

                if not isinstance(tag_syl, bool):
                    tag.append(tag_syl)

    def fix_lyrics(self, mscore=False):
        for verse_number in range(1, self.max + 1):
            self.fix_lyrics_verse(verse_number)

        self.save(mscore=False)
