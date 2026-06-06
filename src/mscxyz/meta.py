"""Class for metadata maniplation"""

from __future__ import annotations

import typing
from typing import Optional

import tmep
from lxml.etree import Element, _Element

if typing.TYPE_CHECKING:
    from mscxyz.score import Score


class UnmatchedFormatStringError(Exception):
    def __init__(self, format_string: str, input_string: str) -> None:
        self.msg = f"Your format string “{format_string}” doesn’t match on this input string: “{input_string}”"
        Exception.__init__(self, self.msg)


class FormatStringNoFieldError(Exception):
    def __init__(self, format_string: str) -> None:
        self.msg = f"No fields found in your format string “{format_string}”!"
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

    def __get_text(self, field: str) -> Optional[str]:
        element: _Element | None = self.__get_element(field)
        return self.score.xml.get_text(element)

    def __set_text(self, field: str, value: Optional[str]) -> None:
        element: _Element = self.__get_element(field)
        element.text = value

    @property
    def arranger(self) -> Optional[str]:
        """
        .. code-block:: xml

            <metaTag name="arranger">...</metaTag>
        """
        return self.__get_text("arranger")

    @arranger.setter
    def arranger(self, value: Optional[str]) -> None:
        self.__set_text("arranger", value)

    @property
    def audio_com_url(self) -> Optional[str]:
        """
        .. code-block:: xml

            <metaTag name="audioComUrl">...</metaTag>
        """
        return self.__get_text("audioComUrl")

    @audio_com_url.setter
    def audio_com_url(self, value: Optional[str]) -> None:
        self.__set_text("audioComUrl", value)

    @property
    def composer(self) -> Optional[str]:
        """Same text as "Composer" on the first page of the score

        .. code-block:: xml

            <metaTag name="composer">...</metaTag>
        """
        return self.__get_text("composer")

    @composer.setter
    def composer(self, value: Optional[str]) -> None:
        self.__set_text("composer", value)

    @property
    def copyright(self) -> Optional[str]:
        """Same text as "Copyright" on the first page of the score.

        .. code-block:: xml

            <metaTag name="copyright">...</metaTag>
        """
        return self.__get_text("copyright")

    @copyright.setter
    def copyright(self, value: Optional[str]) -> None:
        self.__set_text("copyright", value)

    @property
    def creation_date(self) -> Optional[str]:
        """
        https://github.com/musescore/MuseScore/blob/06793ff5ff3065fe87fe9a8a651a6d20f49fd28c/src/engraving/dom/masterscore.cpp#L93

        .. code-block:: xml

            <metaTag name="creationDate">2024-01-05</metaTag>
        """
        return self.__get_text("creationDate")

    @creation_date.setter
    def creation_date(self, value: Optional[str]) -> None:
        self.__set_text("creationDate", value)

    @property
    def lyricist(self) -> Optional[str]:
        """Same text as “Lyricist” on the first page of the score.

        .. code-block:: xml

            <metaTag name="lyricist">...</metaTag>
        """
        return self.__get_text("lyricist")

    @lyricist.setter
    def lyricist(self, value: Optional[str]) -> None:
        self.__set_text("lyricist", value)

    @property
    def movement_number(self) -> Optional[str]:
        """
        .. code-block:: xml

            <metaTag name="movementNumber">...</metaTag>
        """
        return self.__get_text("movementNumber")

    @movement_number.setter
    def movement_number(self, value: Optional[str]) -> None:
        self.__set_text("movementNumber", value)

    @property
    def movement_title(self) -> Optional[str]:
        """
        .. code-block:: xml

            <metaTag name="movementTitle">...</metaTag>
        """
        return self.__get_text("movementTitle")

    @movement_title.setter
    def movement_title(self, value: Optional[str]) -> None:
        self.__set_text("movementTitle", value)

    @property
    def msc_version(self) -> Optional[str]:
        """
        .. code-block:: xml

            <metaTag name="mscVersion">4.20</metaTag>
        """
        return self.__get_text("mscVersion")

    @msc_version.setter
    def msc_version(self, value: Optional[str]) -> None:
        self.__set_text("mscVersion", value)

    @property
    def platform(self) -> Optional[str]:
        """The computing platform the score was created on. This might be empty if the score was saved in test mode.

        https://github.com/musescore/MuseScore/blob/06793ff5ff3065fe87fe9a8a651a6d20f49fd28c/src/engraving/dom/masterscore.cpp#L74-L81

        .. code-block:: xml

            <metaTag name="platform">Linux</metaTag>
            <metaTag name="platform">Apple Macintosh</metaTag>
        """
        return self.__get_text("platform")

    @platform.setter
    def platform(self, value: Optional[str]) -> None:
        self.__set_text("platform", value)

    @property
    def poet(self) -> Optional[str]:
        """
        .. code-block:: xml

            <metaTag name="poet">...</metaTag>
        """
        return self.__get_text("poet")

    @poet.setter
    def poet(self, value: Optional[str]) -> None:
        self.__set_text("poet", value)

    @property
    def source(self) -> Optional[str]:
        """May contain a URL if the score was downloaded from or Publish to MuseScore.com.

        .. code-block:: xml

            <metaTag name="source">http://musescore.com/isaacweiss/getting-started</metaTag>
            <metaTag name="source">http://musescore.com/score/111410</metaTag>
        """

        return self.__get_text("source")

    @source.setter
    def source(self, value: Optional[str]) -> None:
        self.__set_text("source", value)

    @property
    def source_revision_id(self) -> Optional[str]:
        """
        .. code-block:: xml

            <metaTag name="sourceRevisionId">...</metaTag>
        """
        return self.__get_text("sourceRevisionId")

    @source_revision_id.setter
    def source_revision_id(self, value: Optional[str]) -> None:
        self.__set_text("sourceRevisionId", value)

    @property
    def subtitle(self) -> Optional[str]:
        """
        The subtitle. It has the same text as “Subtitle” on the first page of the score.

        .. code-block:: xml

            <metaTag name="subtitle">Subtitle</metaTag>
        """
        return self.__get_text("subtitle")

    @subtitle.setter
    def subtitle(self, value: Optional[str]) -> None:
        self.__set_text("subtitle", value)

    @property
    def translator(self) -> Optional[str]:
        """
        .. code-block:: xml

            <metaTag name="translator">...</metaTag>
        """
        return self.__get_text("translator")

    @translator.setter
    def translator(self, value: Optional[str]) -> None:
        self.__set_text("translator", value)

    @property
    def work_number(self) -> Optional[str]:
        """
        .. code-block:: xml

            <metaTag name="workNumber">...</metaTag>
        """
        return self.__get_text("workNumber")

    @work_number.setter
    def work_number(self, value: Optional[str]) -> None:
        self.__set_text("workNumber", value)

    @property
    def work_title(self) -> Optional[str]:
        """
        The Work Title. It has the same text as “Title” on the first page of the score.

        .. code-block:: xml

            <metaTag name="workTitle">Untitled score</metaTag>
        """
        return self.__get_text("workTitle")

    @work_title.setter
    def work_title(self, value: Optional[str]) -> None:
        self.__set_text("workTitle", value)

    def clean(self) -> None:
        for field in self.fields:
            setattr(self, field, None)


class VboxText:
    """
    Manage one ``<Text>`` entry inside a ``<VBox>`` element.

    .. code-block:: xml

        <Text>
            <eid>hibWj5obkBO_6AUar0D+y6K</eid>
            <style>title</style>
            <text>Untitled score</text>
        </Text>

    Text style overrides:
    =====================

    Global overrides:
    -----------------

    .. code-block:: xml

        <Text>
            <eid>MX+29xsCL0G_gQ+qjPGU4EO</eid>
            <style>title</style>
            <family>FreeSans</family>
            <bold>1</bold>
            <italic>1</italic>
            <text><b><i><font face="FreeSans"/>Untitled score</i></b></text>
        </Text>

    Inline overrides:
    -----------------

    .. code-block:: xml

        <Text>
            <eid>0iZtR+qEd6C_jIRPV50caLG</eid>
            <style>composer</style>
            <text><i>Composer</i> / <b>arranger</b></text>
        </Text>

    :param style: The style name used in ``<style>...</style>``.
    :param parent_vbox: The parent ``<VBox>`` element where ``<Text>`` lives.
    :param container: The existing ``<Text>`` element or ``None``.
    """

    __parent_vbox: _Element
    """The parent vbox element."""

    def __init__(
        self,
        style: str,
        parent_vbox: _Element,
        container: Optional[_Element],
    ) -> None:
        self.__style = style
        self.__parent_vbox = parent_vbox
        self.__container = container
        self.__style_element = None
        self.__text_element = None

        if self.__container is not None:
            self.__style_element = self.__container.find("style")
            self.__text_element = self.__container.find("text")

    def exists(self) -> bool:
        """Checks whether the ``<Text>...</Text>`` element with the given style name
        exists.

        :return: ``True`` if the ``</Text>`` element with the given style name,
           otherwise ``False``.
        """
        return self.__container is not None

    def reset_text_style_overrides(self) -> None:
        """Reset the text style override

        This method removes style override tags from the ``<Text>`` container and
        keeps only ``<eid>``, ``<style>``, and ``<text>`` tags.

        Before:

        .. code-block:: xml

            <Text>
                <eid>MX+29xsCL0G_gQ+qjPGU4EO</eid>
                <style>title</style>
                <family>FreeSans</family>
                <bold>1</bold>
                <italic>1</italic>
                <text><b><i><font face="FreeSans"/>Untitled score</i></b></text>
            </Text>

        After:

        .. code-block:: xml

            <Text>
                <eid>MX+29xsCL0G_gQ+qjPGU4EO</eid>
                <style>title</style>
                <text>Untitled score</text>
            </Text>

        """
        if self.__container is None:
            return
        for element in list(self.__container):
            if element.tag not in ("eid", "style", "text"):
                self.__container.remove(element)
        # The get the plain text and remove the HMTL style tags.
        self.text = self.text

    def remove(self) -> None:
        """Remove the container element ``<Text>...</Text>`` from the
        parent ``<Vbox>...</Vbox>`` element."""
        if self.__container is not None:
            self.__parent_vbox.remove(self.__container)

            self.__container = None
            self.__style_element = None
            self.__text_element = None

        return None

    __container: Optional[_Element]
    """The surrounding text element in uppercase letters
    (``<Text>...</Text>``)."""

    @property
    def _container(self) -> _Element:
        """The surrounding text element in uppercase letters
        (``<Text>...</Text>``)."""
        if self.__container is None:
            self.__container = Element("Text")
            self.__parent_vbox.append(self.__container)
        return self.__container

    __style_element: Optional[_Element]
    """The style element, for example ``<style>title</style>``."""

    @property
    def _style_element(self) -> _Element:
        if self.__style_element is None:
            self.__style_element = Element("style")
            self.__style_element.text = self.__style
            self._container.append(self.__style_element)
        return self.__style_element

    __text_element: Optional[_Element]
    """The text element in lowercase letters inside the container
    (``<text>...</text>``)."""

    __style: str
    """The name of the style."""

    @property
    def style(self) -> str:
        """The name of the style.

        For example, in the XML markup
        ``<style>title</style>`` the style name is ``title``."""
        return self.__style

    @style.setter
    def style(self, style: str) -> None:
        self.__style = style
        self._style_element.text = style

    @property
    def _text_element(self) -> _Element:
        if self.__text_element is None:
            self.__text_element = Element("text")
            self._container.append(self.__text_element)
        return self.__text_element

    @property
    def text(self) -> Optional[str]:
        """
        The plain text content.

        Setting ``text`` to ``None`` removes the entire ``<Text>`` container."""
        if self.__container is None:
            return None
        # To get the content of all child elements,
        # for example: ``<text><b><i><font face="FreeSans"/>Untitled score</i></b></text>``
        content = self._text_element.xpath(".//text()")
        if (
            isinstance(content, bool)
            or isinstance(content, float)
            or isinstance(content, int)
        ):
            return str(content)
        elements: list[str] = []
        for i in content:
            elements.append(str(i))

        if len(elements) == 0:
            return None
        return "".join(elements)

    @text.setter
    def text(self, content: Optional[str]) -> None:
        if content is None:
            self.remove()
            return None
        # To create the style-tag
        self.style = self.__style
        self._text_element.clear()
        self._text_element.text = content


class Vbox:
    """The first `vertical` box or frame of a score.

    Available fields:

    * `title`: Title
    * `subtitle`: Subtitle
    * `composer`: Composer
    * `lyricist` (poet): Lyricist
    * `instrument_excerpt`: Part name

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

    Version 4.6.5 (lyricist is now poet)

    .. code-block:: xml

        <Staff id="1">
            <VBox>
                <height>10</height>
                <eid>3yH8HKTgwb_p8uM4j9efcE</eid>
                <Text>
                    <eid>hibWj5obkBO_6AUar0D+y6K</eid>
                    <style>title</style>
                    <text>Untitled score</text>
                </Text>
                <Text>
                    <eid>mDB0b0Sa0SM_73LrivvAWEC</eid>
                    <style>subtitle</style>
                    <text>Subtitle</text>
                </Text>
                <Text>
                    <eid>13Y3EfRgceC_QRif2MiL9ZM</eid>
                    <style>composer</style>
                    <text>Composer / arranger</text>
                </Text>
                <Text>
                    <eid>5bIbUnhSBCP_qqv84cvOnMO</eid>
                    <style>poet</style>
                    <text>Lyricist</text>
                </Text>
            </VBox>
        </Staff>

    """

    # eid
    # eid Refactor EID into a pseudo-UUID https://github.com/musescore/MuseScore/commit/a6784896ae10a08559ac48ca4fba9ba63d2b471d

    # https://github.com/musescore/MuseScore/blob/master/src/engraving/infrastructure/eid.cpp
    # https://github.com/musescore/MuseScore/blob/master/src/engraving/infrastructure/eidregister.cpp

    # https://musescore.org/en/node/379559
    # However, in 4.4.4 it is of the 'numeric' type, while in 4.5.2 it is of the 'alphanumeric' type.
    # I believe their main purpose is to link elements between main score and parts.

    # EID: same examples
    # TVJRSgwuZD_EwSwNORnKz
    # pYMYtt7e63I_bcIcXkGdYWH
    # /da47B/ELqH_MFU63hCcg7F
    # OTzv11PTP6E_aqOziUGyuBF
    # UUID: 907a3f91-5c2a-441e-98c2-7c65d4b4b0b5

    # as base64: b8tRS7h4TJ2Vt43Dp85v2A
    # as uuid  : 6fcb514b-b878-4c9d-95b7-8dc3a7ce6fd8

    fields = (
        "composer",
        "instrument_excerpt",
        "lyricist",
        "subtitle",
        "title",
    )

    _score: "Score"

    _vbox: _Element

    def __init__(self, score: "Score") -> None:
        self._score = score
        xpath = '/museScore/Score/Staff[@id="1"]'

        vbox = self._score.xml.xpath(xpath + "/VBox")
        if vbox is None:
            vbox, _ = self._score.xml.create_sub_element("VBox", "height", "10")
            self._score.xml.xpath_safe(xpath).insert(0, vbox)
        self._vbox = vbox
        self.migrate_lyricist()

    def __normalize_style_name(self, style: str) -> str:
        """
        :param style: The string inside the ``<style>`` tags, for example
          ``Title`` or ``Composer`` or for v4 ``title`` or ``composer``.
        """
        if self._score.version_major in (2, 3):
            style = style.title()
        elif self._score.version_major == 4:
            style = style.lower()
        return style

    def __get_container(self, style: str) -> Optional[_Element]:
        """
        :param style: The string inside the ``<style>`` tags, for example
        ``Title`` or ``Composer`` or for v4 ``title`` or ``composer``.
        """
        for element in self._vbox:
            s = element.find("style")
            if s is not None and s.text == self.__normalize_style_name(style):
                return element
        return None

    def __create_vbox_text(self, style_name: str) -> VboxText:
        return VboxText(
            self.__normalize_style_name(style_name),
            self._vbox,
            self.__get_container(style_name),
        )

    __title: Optional[VboxText] = None

    @property
    def title_element(self) -> VboxText:
        """
        The title element of the first `vertical` box or frame of a score.

        .. code-block:: xml

            <Staff id="1">
                <VBox>
                    <height>10</height>
                    <boxAutoSize>0</boxAutoSize>
                    <eid>3yH8HKTgwb_p8uM4j9efcE</eid>
                    <Text>
                        <eid>9EZXpseYfo_z5oSRZ7xoaL</eid>
                        <style>title</style>
                        <text>Mondscheinsonate</text>
                    </Text>
                </VBox>
            </Staff>
        """
        if self.__title is None:
            self.__title = self.__create_vbox_text("title")
        return self.__title

    @property
    def title(self) -> Optional[str]:
        """
        The title text field of the first `vertical` box or frame of a score.

        .. code-block:: xml

            <Staff id="1">
                <VBox>
                    <height>10</height>
                    <boxAutoSize>0</boxAutoSize>
                    <eid>3yH8HKTgwb_p8uM4j9efcE</eid>
                    <Text>
                        <eid>9EZXpseYfo_z5oSRZ7xoaL</eid>
                        <style>title</style>
                        <text>Mondscheinsonate</text>
                    </Text>
                </VBox>
            </Staff>
        """
        return self.title_element.text

    @title.setter
    def title(self, value: Optional[str]) -> None:
        """
        The title plain text content of the first `vertical` box or frame of
        a score.

        Setting this field to ``None`` will delete the corresponding XML element
        from the score.

        If this field is ``None``, the corresponding XML element does not exist.
        """
        self.title_element.text = value

    __subtitle: Optional[VboxText] = None

    @property
    def subtitle_element(self) -> VboxText:
        """
        The subtitle element of the first `vertical` box or frame of a score.

        .. code-block:: xml

            <Staff id="1">
                <VBox>
                    <height>10</height>
                    <boxAutoSize>0</boxAutoSize>
                    <eid>3yH8HKTgwb_p8uM4j9efcE</eid>
                    <Text>
                        <eid>W2TmIWNulw_3xwF7Hs22D</eid>
                        <style>subtitle</style>
                        <text>1. Satz</text>
                    </Text>
                </VBox>
            </Staff>
        """
        if self.__subtitle is None:
            self.__subtitle = self.__create_vbox_text("subtitle")
        return self.__subtitle

    @property
    def subtitle(self) -> Optional[str]:
        """
        The subtitle plain text content of the first `vertical` box or frame of
        a score.

        Setting this field to ``None`` will delete the corresponding XML element
        from the score.

        If this field is ``None``, the corresponding XML element does not exist.
        """
        return self.subtitle_element.text

    @subtitle.setter
    def subtitle(self, value: Optional[str]) -> None:
        self.subtitle_element.text = value

    __composer: Optional[VboxText] = None

    @property
    def composer_element(self) -> VboxText:
        """
        The composer element of the first `vertical` box or frame of a score.

        .. code-block:: xml

            <Staff id="1">
                <VBox>
                    <height>10</height>
                    <boxAutoSize>0</boxAutoSize>
                    <eid>3yH8HKTgwb_p8uM4j9efcE</eid>
                    <Text>
                        <eid>TzY/P+VBDFG_lyazF6x468M</eid>
                        <style>composer</style>
                        <text>Ludwig van Beethoven</text>
                    </Text>
                </VBox>
            </Staff>
        """
        if self.__composer is None:
            self.__composer = self.__create_vbox_text("composer")
        return self.__composer

    @property
    def composer(self) -> Optional[str]:
        """
        The composer plain text content of the first `vertical` box or frame of
        a score.

        Setting this field to ``None`` will delete the corresponding XML element
        from the score.

        If this field is ``None``, the corresponding XML element does not exist.
        """
        return self.composer_element.text

    @composer.setter
    def composer(self, value: Optional[str]) -> None:
        self.composer_element.text = value

    __lyricist: Optional[VboxText] = None

    @property
    def _legacy_lyricist_element(self) -> VboxText:
        if self.__lyricist is None:
            self.__lyricist = self.__create_vbox_text("lyricist")
        return self.__lyricist

    __poet: Optional[VboxText] = None

    @property
    def lyricist_element(self) -> VboxText:
        """
        The lyricist element of the first `vertical` box or frame of a score.

        .. code-block:: xml

            <Staff id="1">
                <VBox>
                    <height>10</height>
                    <boxAutoSize>0</boxAutoSize>
                    <eid>3yH8HKTgwb_p8uM4j9efcE</eid>
                    <Text>
                        <eid>iklYO/iK0CE_kALp5O5iuVN</eid>
                        <style>poet</style>
                        <text>Johann Wolfgang von Goethe</text>
                    </Text>
                </VBox>
            </Staff>
        """
        if self.__poet is None:
            self.__poet = self.__create_vbox_text("poet")
        return self.__poet

    def migrate_lyricist(self) -> None:
        """Migrate the lyricist text element by renaming the style from
        ``lyricist`` to ``poet``."""
        if (
            self._legacy_lyricist_element.exists()
            and not self.lyricist_element.exists()
        ):
            self._legacy_lyricist_element.style = "poet"
            self.__poet = self.__lyricist
            self.__lyricist = None
        elif self._legacy_lyricist_element.exists() and self.lyricist_element.exists():
            self._legacy_lyricist_element.remove()

    @property
    def lyricist(self) -> Optional[str]:
        """
        The lyricist plain text content of the first `vertical` box or frame of
        a score.

        Setting this field to ``None`` will delete the corresponding XML element
        from the score.

        If this field is ``None``, the corresponding XML element does not exist.
        """
        return self.lyricist_element.text

    @lyricist.setter
    def lyricist(self, value: Optional[str]) -> None:
        self.lyricist_element.text = value

    __instrument_excerpt: Optional[VboxText] = None

    @property
    def _instrument_excerpt(self) -> VboxText:
        if self.__instrument_excerpt is None:
            self.__instrument_excerpt = self.__create_vbox_text("instrument_excerpt")
        return self.__instrument_excerpt

    @property
    def instrument_excerpt(self) -> Optional[str]:
        """
        The instrument excerpt text field of the first `vertical` box or frame of a score.

        .. code-block:: xml

            <Staff id="1">
                <VBox>
                    <height>10</height>
                    <boxAutoSize>0</boxAutoSize>
                    <eid>4294967418</eid>
                    <Text>
                        <eid>fx/RTjxo4CE_M0P0jIU0j3L</eid>
                        <style>instrument_excerpt</style>
                        <text>Instrument Name</text>
                    </Text>
                </VBox>
            </Staff>
        """
        return self._instrument_excerpt.text

    @instrument_excerpt.setter
    def instrument_excerpt(self, value: Optional[str]) -> None:
        self._instrument_excerpt.text = value

    def clean(self) -> None:
        for field in self.fields:
            setattr(self, field, None)


class Meta:
    """
    High-level interface for score metadata.

    This class combines metadata stored in MuseScore ``metaTag`` elements
    (:class:`Metatag`) and text objects in the first vertical frame
    (:class:`Vbox`) and exposes them through a unified API.

    MuseScore version 4.7.2 metatag_lyricist == vbox_poet
    """

    score: "Score"

    metatag: Metatag

    vbox: Vbox

    def __init__(self, score: "Score") -> None:
        """Initialize metadata helpers for a score."""
        self.score = score
        self.metatag = Metatag(self.score)
        self.vbox = Vbox(self.score)

    def sync_fields(self) -> None:
        """
        Re-assign key fields to trigger internal synchronization.

        This forces current values to be written back through property setters,
        ensuring ``metaTag`` and ``VBox`` representations are aligned.
        """
        self.title = self.title
        self.subtitle = self.subtitle
        self.composer = self.composer
        self.lyricist = self.lyricist

    def write_to_log_file(self, log_file: str, format_string: str) -> None:
        """
        Write formatted exported score fields to a log file.

        :param log_file: Path of the output log file.
        :param format_string: Template string parsed with exported fields.
        """
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

    def __pick_value(self, *values: Optional[str]) -> Optional[str]:
        for value in values:
            if value:
                return value
        return None

    @property
    def title(self) -> Optional[str]:
        """
        Get and set the value of :attr:`Vbox.title` and :attr:`Metatag.work_title` all at once.

        If the attributes have different values, then the attribute :attr:`Vbox.title` is preferred.
        """
        return self.__pick_value(self.vbox.title, self.metatag.work_title)

    @title.setter
    def title(self, value: Optional[str]) -> None:
        self.vbox.title = self.metatag.work_title = value

    @property
    def subtitle(self) -> Optional[str]:
        """
        Get and set the value of :attr:`Vbox.subtitle`, :attr:`Metatag.subtitle` and :attr:`Metatag.movement_title` all at once.

        If the attributes have different values, then the attribute :attr:`Vbox.subtitle` is preferred.
        """
        return self.__pick_value(
            self.vbox.subtitle, self.metatag.subtitle, self.metatag.movement_title
        )

    @subtitle.setter
    def subtitle(self, value: Optional[str]) -> None:
        self.vbox.subtitle = self.metatag.subtitle = self.metatag.movement_title = value

    @property
    def composer(self) -> Optional[str]:
        """
        Get and set the value of :attr:`Vbox.composer` and :attr:`Metatag.composer` all at once.

        If the attributes have different values, then the attribute :attr:`Vbox.composer` is preferred.
        """
        return self.__pick_value(self.vbox.composer, self.metatag.composer)

    @composer.setter
    def composer(self, value: Optional[str]) -> None:
        self.vbox.composer = self.metatag.composer = value

    @property
    def lyricist(self) -> Optional[str]:
        """
        Get and set the value of :attr:`Vbox.lyricist` and :attr:`Metatag.lyricist` all at once.

        If the attributes have different values, then the attribute :attr:`Vbox.lyricist` is preferred.
        """
        return self.__pick_value(self.vbox.lyricist, self.metatag.lyricist)

    @lyricist.setter
    def lyricist(self, value: Optional[str]) -> None:
        self.vbox.lyricist = self.metatag.lyricist = value
