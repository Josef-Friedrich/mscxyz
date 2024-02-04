"""Class for metadata maniplation"""

from __future__ import annotations

import typing

import tmep
from lxml.etree import _Element

if typing.TYPE_CHECKING:
    from mscxyz.score import Score


class UnmatchedFormatStringError(Exception):
    def __init__(self, format_string: str, input_string: str) -> None:
        self.msg = (
            "Your format string “{}” doesn’t match on this "
            "input string: “{}”".format(format_string, input_string)
        )
        Exception.__init__(self, self.msg)


class FormatStringNoFieldError(Exception):
    def __init__(self, format_string: str) -> None:
        self.msg = "No fields found in your format string “{}”!".format(format_string)
        Exception.__init__(self, self.msg)


class Metatag:
    """
    The class provides access to the MuseScore metadata fields.

    The class should not be renamed to ``MetaTag`` because it would conflict with the
    naming scheme of the fields ``metatag_title`` etc.

    :see: `MuseScore Handbook <https://musescore.org/en/handbook/4/project-properties>`_

    The available ``metaTag`` fields are:

    * `arranger`
    * `audioComUrl` (new in v4)
    * `composer`
    * `copyright`
    * `creationDate`
    * `lyricist`
    * `movementNumber`
    * `movementTitle`
    * `mscVersion`
    * `platform`
    * `poet` (not in v4)
    * `source`
    * `sourceRevisionId`
    * `subtitle`
    * `translator`
    * `workNumber`
    * `workTitle`

    version 4

    .. code-block:: xml

            <museScore version="4.20">
                <Score>
                    <metaTag name="arranger"></metaTag>
                    <metaTag name="audioComUrl"></metaTag>
                    <metaTag name="composer">Composer / arranger</metaTag>
                    <metaTag name="copyright"></metaTag>
                    <metaTag name="creationDate">2024-01-05</metaTag>
                    <metaTag name="lyricist"></metaTag>
                    <metaTag name="movementNumber"></metaTag>
                    <metaTag name="movementTitle"></metaTag>
                    <metaTag name="platform">Linux</metaTag>
                    <metaTag name="source"></metaTag>
                    <metaTag name="sourceRevisionId"></metaTag>
                    <metaTag name="subtitle">Subtitle</metaTag>
                    <metaTag name="translator"></metaTag>
                    <metaTag name="workNumber"></metaTag>
                    <metaTag name="workTitle">Untitled score</metaTag>
    """

    fields = (
        "arranger",
        "audio_com_url",
        "composer",
        "copyright",
        "creation_date",
        "lyricist",
        "movement_number",
        "movement_title",
        "msc_version",
        "platform",
        "poet",
        "source",
        "source_revision_id",
        "subtitle",
        "translator",
        "work_number",
        "work_title",
    )

    score: "Score"

    xml_root: _Element

    def __init__(self, score: "Score") -> None:
        self.score = score
        self.xml_root = score.xml_root

    def __get_element(self, field: str) -> _Element:
        score_element: _Element = self.score.xml.find_safe("Score")
        element: _Element | None = self.score.xml.xpath(
            '//metaTag[@name="' + field + '"]'
        )
        if element is None:
            _, element = self.score.xml.create_sub_element(
                score_element, "metaTag", "", attrib={"name": field}
            )
        return element

    def __get_text(self, field: str) -> str | None:
        element: _Element | None = self.__get_element(field)
        return self.score.xml.get_text(element)

    def __set_text(self, field: str, value: str | None) -> None:
        element: _Element = self.__get_element(field)
        element.text = value

    @property
    def arranger(self) -> str | None:
        """
        .. code-block:: xml

            <metaTag name="arranger">...</metaTag>
        """
        return self.__get_text("arranger")

    @arranger.setter
    def arranger(self, value: str | None) -> None:
        self.__set_text("arranger", value)

    @property
    def audio_com_url(self) -> str | None:
        """
        .. code-block:: xml

            <metaTag name="audioComUrl">...</metaTag>
        """
        return self.__get_text("audioComUrl")

    @audio_com_url.setter
    def audio_com_url(self, value: str | None) -> None:
        self.__set_text("audioComUrl", value)

    @property
    def composer(self) -> str | None:
        """Same text as "Composer" on the first page of the score

        .. code-block:: xml

            <metaTag name="composer">...</metaTag>
        """
        return self.__get_text("composer")

    @composer.setter
    def composer(self, value: str | None) -> None:
        self.__set_text("composer", value)

    @property
    def copyright(self) -> str | None:
        """Same text as "Copyright" on the first page of the score.

        .. code-block:: xml

            <metaTag name="copyright">...</metaTag>
        """
        return self.__get_text("copyright")

    @copyright.setter
    def copyright(self, value: str | None) -> None:
        self.__set_text("copyright", value)

    @property
    def creation_date(self) -> str | None:
        """
        https://github.com/musescore/MuseScore/blob/06793ff5ff3065fe87fe9a8a651a6d20f49fd28c/src/engraving/dom/masterscore.cpp#L93

        .. code-block:: xml

            <metaTag name="creationDate">2024-01-05</metaTag>
        """
        return self.__get_text("creationDate")

    @creation_date.setter
    def creation_date(self, value: str | None) -> None:
        self.__set_text("creationDate", value)

    @property
    def lyricist(self) -> str | None:
        """Same text as “Lyricist” on the first page of the score.

        .. code-block:: xml

            <metaTag name="lyricist">...</metaTag>
        """
        return self.__get_text("lyricist")

    @lyricist.setter
    def lyricist(self, value: str | None) -> None:
        self.__set_text("lyricist", value)

    @property
    def movement_number(self) -> str | None:
        """
        .. code-block:: xml

            <metaTag name="movementNumber">...</metaTag>
        """
        return self.__get_text("movementNumber")

    @movement_number.setter
    def movement_number(self, value: str | None) -> None:
        self.__set_text("movementNumber", value)

    @property
    def movement_title(self) -> str | None:
        """
        .. code-block:: xml

            <metaTag name="movementTitle">...</metaTag>
        """
        return self.__get_text("movementTitle")

    @movement_title.setter
    def movement_title(self, value: str | None) -> None:
        self.__set_text("movementTitle", value)

    @property
    def msc_version(self) -> str | None:
        """
        .. code-block:: xml

            <metaTag name="mscVersion">4.20</metaTag>
        """
        return self.__get_text("mscVersion")

    @msc_version.setter
    def msc_version(self, value: str | None) -> None:
        self.__set_text("mscVersion", value)

    @property
    def platform(self) -> str | None:
        """The computing platform the score was created on. This might be empty if the score was saved in test mode.

        https://github.com/musescore/MuseScore/blob/06793ff5ff3065fe87fe9a8a651a6d20f49fd28c/src/engraving/dom/masterscore.cpp#L74-L81

        .. code-block:: xml

            <metaTag name="platform">Linux</metaTag>
            <metaTag name="platform">Apple Macintosh</metaTag>
        """
        return self.__get_text("platform")

    @platform.setter
    def platform(self, value: str | None) -> None:
        self.__set_text("platform", value)

    @property
    def poet(self) -> str | None:
        """
        .. code-block:: xml

            <metaTag name="poet">...</metaTag>
        """
        return self.__get_text("poet")

    @poet.setter
    def poet(self, value: str | None) -> None:
        self.__set_text("poet", value)

    @property
    def source(self) -> str | None:
        """May contain a URL if the score was downloaded from or Publish to MuseScore.com.

        .. code-block:: xml

            <metaTag name="source">http://musescore.com/isaacweiss/getting-started</metaTag>
            <metaTag name="source">http://musescore.com/score/111410</metaTag>
        """

        return self.__get_text("source")

    @source.setter
    def source(self, value: str | None) -> None:
        self.__set_text("source", value)

    @property
    def source_revision_id(self) -> str | None:
        """
        .. code-block:: xml

            <metaTag name="sourceRevisionId">...</metaTag>
        """
        return self.__get_text("sourceRevisionId")

    @source_revision_id.setter
    def source_revision_id(self, value: str | None) -> None:
        self.__set_text("sourceRevisionId", value)

    @property
    def subtitle(self) -> str | None:
        """
        The subtitle. It has the same text as “Subtitle” on the first page of the score.

        .. code-block:: xml

            <metaTag name="subtitle">Subtitle</metaTag>
        """
        return self.__get_text("subtitle")

    @subtitle.setter
    def subtitle(self, value: str | None) -> None:
        self.__set_text("subtitle", value)

    @property
    def translator(self) -> str | None:
        """
        .. code-block:: xml

            <metaTag name="translator">...</metaTag>
        """
        return self.__get_text("translator")

    @translator.setter
    def translator(self, value: str | None) -> None:
        self.__set_text("translator", value)

    @property
    def work_number(self) -> str | None:
        """
        .. code-block:: xml

            <metaTag name="workNumber">...</metaTag>
        """
        return self.__get_text("workNumber")

    @work_number.setter
    def work_number(self, value: str | None) -> None:
        self.__set_text("workNumber", value)

    @property
    def work_title(self) -> str | None:
        """
        The Work Title. It has the same text as “Title” on the first page of the score.

        .. code-block:: xml

            <metaTag name="workTitle">Untitled score</metaTag>
        """
        return self.__get_text("workTitle")

    @work_title.setter
    def work_title(self, value: str | None) -> None:
        self.__set_text("workTitle", value)

    def clean(self) -> None:
        for field in self.fields:
            setattr(self, field, None)


class Vbox:
    """The first `vertical` box or frame of a score.

    Available fields:

    * `Composer`
    * `Lyricist`
    * `Subtitle`
    * `Title`

    Version 2, 3

    .. code-block:: xml

        <Staff id="1">
            <VBox>
                <height>10</height>
                <Text>
                    <style>Title</style>
                    <text>Title</text>
                </Text>
                <Text>
                    <style>Composer</style>
                    <text>Composer</text>
                </Text>
            </VBox>
        </Staff>


    Version 4

    .. code-block:: xml

        <Staff id="1">
            <VBox>
                <height>10</height>
                <boxAutoSize>0</boxAutoSize>
                <eid>4294967418</eid>
                <Text>
                    <eid>8589934598</eid>
                    <style>title</style>
                    <text>Title</text>
                </Text>
                <Text>
                    <eid>12884901894</eid>
                    <style>composer</style>
                    <text>Composer</text>
                </Text>
            </VBox>
        </Staff>
    """

    fields = (
        "composer",
        "lyricist",
        "subtitle",
        "title",
    )

    score: "Score"

    xml_root: _Element

    vbox: _Element

    def __init__(self, score: "Score") -> None:
        self.score = score
        self.xml_root = score.xml_root
        xpath = '/museScore/Score/Staff[@id="1"]'

        vbox = self.score.xml.xpath(xpath + "/VBox")
        if vbox is None:
            vbox, _ = self.score.xml.create_sub_element("VBox", "height", "10")

            self.score.xml.xpath_safe(xpath).insert(0, vbox)
        self.vbox = vbox

    def __normalize_style_name(self, style: str) -> str:
        """
        :param style: The string inside the ``<style>`` tags, for example
          ``Title`` or ``Composer`` or for v4 ``title`` or ``composer``.
        """
        if self.score.version_major in (2, 3):
            style = style.title()
        elif self.score.version_major == 4:
            style = style.lower()
        return style

    def __get_element(self, style: str) -> _Element | None:
        """
        :param style: The string inside the ``<style>`` tags, for example
          ``Title`` or ``Composer`` or for v4 ``title`` or ``composer``.
        """
        for element in self.vbox:
            s: _Element | None = element.find("style")
            if s is not None and s.text == self.__normalize_style_name(style):
                return element.find("text")
        return None

    def __get_text(self, style: str) -> str | None:
        """
        :param style: The string inside the ``<style>`` tags, for example
          ``Title`` or ``Composer``.
        """
        element: _Element | None = self.__get_element(style)
        if element is not None and hasattr(element, "text"):
            return element.text
        return None

    def __create_text_element(self, style: str, text: str) -> None:
        """
        Version 2, 3

        .. code-block:: xml

            <Text>
                <style>Title</style>
                <text>Title</text>
            </Text>

        Version 4

        .. code-block:: xml

            <Text>
                <eid>8589934598</eid>
                <style>title</style>
                <text>Title</text>
            </Text>


        :param style: The string inside the ``<style>`` tags, for example
          ``Title`` or ``Composer`` or for v4 ``title`` or ``composer``.
        :param text: The string inside the ``<text>`` tags.
        """
        text_element: _Element = self.score.xml.create_element("Text")

        if self.score.version_major in (2, 3):
            style = style.title()
        else:
            style = style.lower()

        self.score.xml.create_sub_element(
            text_element, "style", self.__normalize_style_name(style)
        )
        self.score.xml.create_sub_element(text_element, "text", text)
        self.vbox.append(text_element)

    def __set_text(self, style: str, text: str | None) -> None:
        """
        :param style: The string inside the ``<style>`` tags, for example
          ``Title`` or ``Composer`` or for v4 ``title`` or ``composer``.
        """

        if text is None:
            self.__remove_text_element(style)
            return None

        element: _Element | None = self.__get_element(style)
        if hasattr(element, "text"):
            if element is not None:
                element.text = text
        else:
            self.__create_text_element(style, text)

    def __remove_text_element(self, style: str) -> None:
        """
        :param style: The string inside the ``<style>`` tags, for example
          ``Title`` or ``Composer`` or for v4 ``title`` or ``composer``.
        """
        self.score.xml.remove(self.__get_element(style))
        return None

    @property
    def title(self) -> str | None:
        """
        The title text field of the first `vertical` box or frame of a score.

        .. code-block:: xml

            <Staff id="1">
                <VBox>
                    <height>10</height>
                    <boxAutoSize>0</boxAutoSize>
                    <eid>4294967418</eid>
                    <Text>
                        <eid>8589934598</eid>
                        <style>title</style>
                        <text>Mondscheinsonate</text>
                    </Text>
                </VBox>
            </Staff>
        """
        return self.__get_text("title")

    @title.setter
    def title(self, value: str | None) -> None:
        self.__set_text("title", value)

    @property
    def subtitle(self) -> str | None:
        """
        The subtitle text field of the first `vertical` box or frame of a score.

        .. code-block:: xml

            <Staff id="1">
                <VBox>
                    <height>10</height>
                    <boxAutoSize>0</boxAutoSize>
                    <eid>4294967418</eid>
                    <Text>
                        <eid>8589934598</eid>
                        <style>subtitle</style>
                        <text>1. Satz</text>
                    </Text>
                </VBox>
            </Staff>
        """
        return self.__get_text("subtitle")

    @subtitle.setter
    def subtitle(self, value: str | None) -> None:
        self.__set_text("subtitle", value)

    @property
    def composer(self) -> str | None:
        """
        The composer text field of the first `vertical` box or frame of a score.

        .. code-block:: xml

            <Staff id="1">
                <VBox>
                    <height>10</height>
                    <boxAutoSize>0</boxAutoSize>
                    <eid>4294967418</eid>
                    <Text>
                        <eid>8589934598</eid>
                        <style>composer</style>
                        <text>Ludwig van Beethoven</text>
                    </Text>
                </VBox>
            </Staff>
        """
        return self.__get_text("composer")

    @composer.setter
    def composer(self, value: str | None) -> None:
        self.__set_text("composer", value)

    @property
    def lyricist(self) -> str | None:
        """
        The composer text field of the first `vertical` box or frame of a score.

        .. code-block:: xml

            <Staff id="1">
                <VBox>
                    <height>10</height>
                    <boxAutoSize>0</boxAutoSize>
                    <eid>4294967418</eid>
                    <Text>
                        <eid>8589934598</eid>
                        <style>lyricist</style>
                        <text>Johann Wolfgang von Goethe</text>
                    </Text>
                </VBox>
            </Staff>
        """
        return self.__get_text("lyricist")

    @lyricist.setter
    def lyricist(self, value: str | None) -> None:
        self.__set_text("lyricist", value)

    def clean(self) -> None:
        for field in self.fields:
            setattr(self, field, None)


class Meta:
    score: "Score"

    metatag: Metatag

    vbox: Vbox

    def __init__(self, score: "Score") -> None:
        self.score = score

        self.metatag = Metatag(self.score)
        self.vbox = Vbox(self.score)

    def sync_fields(self) -> None:
        self.title = self.title
        self.subtitle = self.subtitle
        self.composer = self.composer
        self.lyricist = self.lyricist

    def write_to_log_file(self, log_file: str, format_string: str) -> None:
        log = open(log_file, "w")
        log.write(tmep.parse(format_string, self.score.fields.export_to_dict()) + "\n")
        log.close()

    def clean(self) -> None:
        """
        Clean all metadata fields of the object.
        """
        self.metatag.clean()
        self.vbox.clean()

    def delete_duplicates(self) -> None:
        """
        Delete duplicates in the metadata.

        This method checks if the :attr:`lyricist` and :attr:`composer` are the same,
        and if so, it sets :attr:`lyricist` to an empty string.

        It also checks if :attr:`title` is empty but :attr:`subtitle` is not,
        and if so, it sets :attr:`title` to :attr:`subtitle`.

        Finally, it checks if :attr:`subtitle` is the same as :attr:`title`,
        and if so, it sets :attr:`subtitle` to an empty string.
        """
        if self.lyricist == self.composer:
            self.lyricist = None

        if not self.title and self.subtitle:
            self.title = self.subtitle

        if self.subtitle == self.title:
            self.subtitle = None

    def reload(self, save: bool = False) -> Meta:
        """
        Reload the MuseScore file.

        :param save: Whether to save the changes before reloading. Default is False.

        :return: The reloaded Meta object.

        :see: :meth:`mscxyz.Score.reload`
        """
        return self.score.reload(save).meta

    def __pick_value(self, *values: str | None) -> str | None:
        for value in values:
            if value:
                return value
        return None

    @property
    def title(self) -> str | None:
        """
        Get and set the value of :attr:`Vbox.title` and :attr:`Metatag.work_title` all at once.

        If the attributes have different values, then the attribute :attr:`Vbox.title` is preferred.
        """
        return self.__pick_value(self.vbox.title, self.metatag.work_title)

    @title.setter
    def title(self, value: str | None) -> None:
        self.vbox.title = self.metatag.work_title = value

    @property
    def subtitle(self) -> str | None:
        """
        Get and set the value of :attr:`Vbox.subtitle`, :attr:`Metatag.subtitle` and :attr:`Metatag.movement_title` all at once.

        If the attributes have different values, then the attribute :attr:`Vbox.subtitle` is preferred.
        """
        return self.__pick_value(
            self.vbox.subtitle, self.metatag.subtitle, self.metatag.movement_title
        )

    @subtitle.setter
    def subtitle(self, value: str | None) -> None:
        self.vbox.subtitle = self.metatag.subtitle = self.metatag.movement_title = value

    @property
    def composer(self) -> str | None:
        """
        Get and set the value of :attr:`Vbox.composer` and :attr:`Metatag.composer` all at once.

        If the attributes have different values, then the attribute :attr:`Vbox.composer` is preferred.
        """
        return self.__pick_value(self.vbox.composer, self.metatag.composer)

    @composer.setter
    def composer(self, value: str | None) -> None:
        self.vbox.composer = self.metatag.composer = value

    @property
    def lyricist(self) -> str | None:
        """
        Get and set the value of :attr:`Vbox.lyricist` and :attr:`Metatag.lyricist` all at once.

        If the attributes have different values, then the attribute :attr:`Vbox.lyricist` is preferred.
        """
        return self.__pick_value(self.vbox.lyricist, self.metatag.lyricist)

    @lyricist.setter
    def lyricist(self, value: str | None) -> None:
        self.vbox.lyricist = self.metatag.lyricist = value
