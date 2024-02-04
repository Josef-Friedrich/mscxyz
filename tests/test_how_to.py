"""Test the examples from the README.rst file."""

from __future__ import annotations

from pathlib import Path

import pytest
from lxml.etree import _Element

from mscxyz import Score, list_path
from tests import helper
from tests.helper import Cli, assert_file_type


class TestSpecifyMusescoreFiles:
    def test_without_an_argument(self, cwd_test_path: Path) -> None:
        assert (
            "files/by_version/4/score.mscz"
            in Cli("--list-files", append_score=False).stdout()
        )

    def test_dot_to_specify_pwd(self, cwd_test_path: Path) -> None:
        assert (
            "files/by_version/4/nested-folders/level1/level2/level3/score3.mscz"
            in Cli("-L", ".").stdout()
        )

    def test_pass_multiple_files(self, cwd_test_path: Path) -> None:
        file2 = "files/by_version/2/score.mscz"
        file3 = "files/by_version/3/score.mscz"
        file4 = "files/by_version/4/score.mscz"

        stdout = Cli(
            "-L",
            file2,
            file3,
            file4,
        ).stdout()

        assert file2 in stdout
        assert file3 in stdout
        assert file4 in stdout

    def test_pass_multiple_directories(self, cwd_test_path: Path) -> None:
        dir2 = "files/by_version/2"
        dir3 = "files/by_version/3"
        dir4 = "files/by_version/4"

        stdout = Cli(
            "-L",
            dir2,
            dir3,
            dir4,
        ).stdout()

        assert dir2 in stdout
        assert dir3 in stdout
        assert dir4 in stdout

    def test_glob(self, cwd_test_path: Path) -> None:
        stdout = Cli(
            "-L", "--glob", "*/by_version/4/*.mscz", append_score=False
        ).stdout()
        assert "/by_version/4/" in stdout
        assert ".mscz" in stdout
        assert "/by_version/3/" not in stdout
        assert ".mscx" not in stdout

    def test_mscz_only(self, cwd_test_path: Path) -> None:
        stdout = Cli("-L", "--mscz", append_score=False).stdout()
        assert "score.mscz" in stdout
        assert "score.mscx" not in stdout

    def test_mscx_only(self, cwd_test_path: Path) -> None:
        stdout = Cli("-L", "--mscx", append_score=False).stdout()
        assert "score.mscz" not in stdout
        assert "simple.mscx" in stdout

    def test_dont_mix_mscz_and_mscx(self) -> None:
        assert (
            "--mscx: not allowed with argument --mscz"
            in Cli("-L", "--mscz", "--mscx").sysexit()
        )

    def test_dont_mix_mscz_and_glob(self) -> None:
        assert (
            "--glob: not allowed with argument --mscz"
            in Cli("-L", "--mscz", "--glob", "*").sysexit()
        )

    def test_dont_mix_mscx_and_glob(self) -> None:
        assert (
            "--glob: not allowed with argument --mscx"
            in Cli("-L", "--mscx", "-glob", "*").sysexit()
        )


def test_list_path(nested_dir: Path) -> None:
    score_paths: list[str] = []
    for score_path in list_path(src=str(nested_dir), extension="mscz"):
        score = Score(score_path)
        assert score.path.exists()
        assert score.extension == "mscz"
        score_paths.append(str(score_path))

    assert len(score_paths) == 4

    assert "level1/level2/level3/score3.mscz" in score_paths[3]
    assert "level1/level2/score2.mscz" in score_paths[2]
    assert "level1/score1.mscz" in score_paths[1]
    assert "score0.mscz" in score_paths[0]


@pytest.mark.slow
@pytest.mark.skipif(
    helper.mscore_executable is None, reason="mscore executable not found"
)
class TestExport:
    def get_export_path(self, score: Score, extension: str) -> Path:
        numbering = ""
        if extension in ("svg", "png"):
            numbering = "-1"
        return Path(str(score.path).replace(".mscz", f"{numbering}.{extension}"))

    @pytest.mark.parametrize(
        "extension, expected",
        [
            ("mscz", "application/zip"),
            ("mscx", "text/xml"),
            ("spos", "text/xml"),
            ("mpos", "text/xml"),
            ("pdf", "application/pdf"),
            ("svg", "image/svg+xml"),
            ("png", "image/png"),
            ("wav", "audio/x-wav"),
            ("mp3", "audio/mpeg"),
            ("ogg", "audio/ogg"),
            ("flac", "audio/flac"),
            ("mid", "audio/midi"),
            ("midi", "audio/midi"),
            ("kar", "audio/midi"),
            ("musicxml", "text/xml"),
            ("xml", "text/xml"),
            ("mxl", "application/zip"),
            ("brf", "text/plain"),
            ("mei", "text/xml"),
        ],
    )
    def test_cli(self, extension: str, expected: str) -> None:
        score = Cli("--export", extension).score()
        dest = self.get_export_path(score, extension)
        assert dest.exists()
        assert_file_type(dest, expected)

    def test_python_api(self) -> None:
        score = helper.get_score("simple.mscz", version=4)
        score.export.to_extension("musicxml")
        dest = self.get_export_path(score, "musicxml")
        assert dest.exists()
        assert_file_type(dest, "text/xml")


class TestStyle:
    def test_set_style_single(self) -> None:
        c = Cli("--style", "staffDistance", "7.5").execute()
        assert c.pre.style.get("staffDistance") == "6.5"
        assert c.post.style.get("staffDistance") == "7.5"

    def test_set_style_multiple(self) -> None:
        c = Cli(
            "-s",
            "staffUpperBorder",
            "5.5",
            "--style",
            "staffLowerBorder",
            "5.5",
        ).execute()

        assert c.pre.style.get("staffUpperBorder") == "7"
        assert c.pre.style.get("staffLowerBorder") == "7"

        assert c.post.style.get("staffUpperBorder") == "5.5"
        assert c.post.style.get("staffLowerBorder") == "5.5"

    def test_set_text_fonts(self) -> None:
        c = Cli("--text-font", "Alegreya").execute()

        assert c.pre.style.get("defaultFontFace") == "FreeSerif"
        assert c.pre.style.get("titleFontFace") == "FreeSerif"
        assert c.pre.style.get("romanNumeralFontFace") == "Campania"

        assert c.post.style.get("defaultFontFace") == "Alegreya"
        assert c.post.style.get("titleFontFace") == "Alegreya"
        assert c.post.style.get("romanNumeralFontFace") == "Campania"

    def test_set_title_fonts(self) -> None:
        c = Cli("--title-font", "Alegreya Sans").execute()

        assert c.pre.style.get("titleFontFace") == "FreeSerif"
        assert c.pre.style.get("subTitleFontFace") == "FreeSerif"

        assert c.post.style.get("defaultFontFace") == "FreeSerif"
        assert c.post.style.get("titleFontFace") == "Alegreya Sans"
        assert c.post.style.get("subTitleFontFace") == "Alegreya Sans"

    def test_set_musical_symbols_font(self) -> None:
        c = Cli("--musical-symbol-font", "Emmentaler").execute()

        assert c.pre.style.get("musicalSymbolFont") == "Leland"
        assert c.pre.style.get("dynamicsFont") == "Leland"
        assert c.pre.style.get("dynamicsFontFace") == "FreeSerif"

        assert c.post.style.get("musicalSymbolFont") == "Emmentaler"
        assert c.post.style.get("dynamicsFont") == "Emmentaler"
        assert c.post.style.get("dynamicsFontFace") == "Emmentaler"

    def test_set_musical_symbol_font(self) -> None:
        Cli("--musical-symbol-font", "XXX").sysexit(assert_none_zero=True)
        c = Cli("--musical-symbol-font", "Emmentaler").execute()

        assert c.pre.style.get("musicalSymbolFont") == "Leland"
        assert c.pre.style.get("dynamicsFont") == "Leland"
        assert c.pre.style.get("dynamicsFontFace") == "FreeSerif"

        assert c.post.style.get("musicalSymbolFont") == "Emmentaler"
        assert c.post.style.get("dynamicsFont") == "Emmentaler"
        assert c.post.style.get("dynamicsFontFace") == "Emmentaler"

    def test_set_musical_text_font(self) -> None:
        Cli("--musical-text-font", "XXX Text").sysexit(assert_none_zero=True)
        c = Cli("--musical-text-font", "Emmentaler Text").execute()
        assert c.pre.style.get("musicalTextFont") == "Leland Text"
        assert c.post.style.get("musicalTextFont") == "MScore Text"


def test_set_all_font_faces_using_for_loop(score: Score) -> None:
    assert score.style.get("defaultFontFace") == "FreeSerif"

    for element in score.style.styles:
        if "FontFace" in element.tag:
            element.text = "Alegreya"
    score.save()

    new_score: Score = score.reload()
    assert new_score.style.get("defaultFontFace") == "Alegreya"


def test_set_all_font_faces_using_method(score: Score) -> None:
    assert score.style.get("defaultFontFace") == "FreeSerif"

    response = score.style.set_text_fonts("Alegreya")

    assert response == [
        ("lyricsOddFontFace", "FreeSerif", "Alegreya"),
        ("lyricsEvenFontFace", "FreeSerif", "Alegreya"),
        ("hairpinFontFace", "FreeSerif", "Alegreya"),
        ("pedalFontFace", "FreeSerif", "Alegreya"),
        ("chordSymbolAFontFace", "FreeSerif", "Alegreya"),
        ("chordSymbolBFontFace", "FreeSerif", "Alegreya"),
        ("nashvilleNumberFontFace", "FreeSerif", "Alegreya"),
        ("voltaFontFace", "FreeSerif", "Alegreya"),
        ("ottavaFontFace", "FreeSerif", "Alegreya"),
        ("tupletFontFace", "FreeSerif", "Alegreya"),
        ("defaultFontFace", "FreeSerif", "Alegreya"),
        ("titleFontFace", "FreeSerif", "Alegreya"),
        ("subTitleFontFace", "FreeSerif", "Alegreya"),
        ("composerFontFace", "FreeSerif", "Alegreya"),
        ("lyricistFontFace", "FreeSerif", "Alegreya"),
        ("fingeringFontFace", "FreeSerif", "Alegreya"),
        ("lhGuitarFingeringFontFace", "FreeSerif", "Alegreya"),
        ("rhGuitarFingeringFontFace", "FreeSerif", "Alegreya"),
        ("stringNumberFontFace", "FreeSerif", "Alegreya"),
        ("harpPedalDiagramFontFace", "Edwin", "Alegreya"),
        ("harpPedalTextDiagramFontFace", "Edwin", "Alegreya"),
        ("longInstrumentFontFace", "FreeSerif", "Alegreya"),
        ("shortInstrumentFontFace", "FreeSerif", "Alegreya"),
        ("partInstrumentFontFace", "FreeSerif", "Alegreya"),
        ("expressionFontFace", "FreeSerif", "Alegreya"),
        ("tempoFontFace", "FreeSerif", "Alegreya"),
        ("tempoChangeFontFace", "Edwin", "Alegreya"),
        ("metronomeFontFace", "FreeSerif", "Alegreya"),
        ("measureNumberFontFace", "FreeSerif", "Alegreya"),
        ("mmRestRangeFontFace", "Edwin", "Alegreya"),
        ("translatorFontFace", "FreeSerif", "Alegreya"),
        ("systemFontFace", "FreeSerif", "Alegreya"),
        ("staffFontFace", "FreeSerif", "Alegreya"),
        ("rehearsalMarkFontFace", "FreeSerif", "Alegreya"),
        ("repeatLeftFontFace", "FreeSerif", "Alegreya"),
        ("repeatRightFontFace", "FreeSerif", "Alegreya"),
        ("frameFontFace", "FreeSerif", "Alegreya"),
        ("textLineFontFace", "FreeSerif", "Alegreya"),
        ("systemTextLineFontFace", "Edwin", "Alegreya"),
        ("glissandoFontFace", "FreeSerif", "Alegreya"),
        ("bendFontFace", "FreeSerif", "Alegreya"),
        ("headerFontFace", "FreeSerif", "Alegreya"),
        ("footerFontFace", "FreeSerif", "Alegreya"),
        ("instrumentChangeFontFace", "FreeSerif", "Alegreya"),
        ("stickingFontFace", "FreeSerif", "Alegreya"),
        ("user1FontFace", "FreeSerif", "Alegreya"),
        ("user2FontFace", "FreeSerif", "Alegreya"),
        ("user3FontFace", "FreeSerif", "Alegreya"),
        ("user4FontFace", "FreeSerif", "Alegreya"),
        ("user5FontFace", "FreeSerif", "Alegreya"),
        ("user6FontFace", "FreeSerif", "Alegreya"),
        ("user7FontFace", "FreeSerif", "Alegreya"),
        ("user8FontFace", "FreeSerif", "Alegreya"),
        ("user9FontFace", "FreeSerif", "Alegreya"),
        ("user10FontFace", "FreeSerif", "Alegreya"),
        ("user11FontFace", "FreeSerif", "Alegreya"),
        ("user12FontFace", "FreeSerif", "Alegreya"),
        ("letRingFontFace", "FreeSerif", "Alegreya"),
        ("palmMuteFontFace", "FreeSerif", "Alegreya"),
    ]
    score.save()

    new_score: Score = score.reload()
    assert new_score.style.get("defaultFontFace") == "Alegreya"


class TestAutocomplete:
    def test_bash(self) -> None:
        assert (
            "# AUTOMATICALLY GENERATED by `shtab`"
            in Cli("--print-completion", "bash").sysexit()
        )

    def test_zsh(self) -> None:
        assert (
            "# AUTOMATICALLY GENERATED by `shtab`"
            in Cli("--print-completion", "zsh").sysexit()
        )

    def test_tcsh(self) -> None:
        assert (
            "# AUTOMATICALLY GENERATED by `shtab`"
            in Cli("--print-completion", "tcsh").sysexit()
        )


def test_rename(tmp_path: Path) -> None:
    src = helper.get_dir("leadsheets", 4)
    dest = tmp_path
    Cli(
        "--rename",
        "%lower{%shorten{$title,1}}/$title",
        "--target",
        dest,
        "--no-whitespace",
        src,
    ).execute()

    assert (dest / "i" / "I-Walk-the-Line.mscz").exists()
    assert (dest / "j" / "Jackson.mscz").exists()
    assert (dest / "f" / "Folsom-Prison-Blues.mscz").exists()


def test_instantiate_a_score_object(score_file: str) -> None:
    score = Score(score_file)
    assert score.path.exists()
    assert score.filename == "score.mscz"
    assert score.basename == "score"
    assert score.extension == "mscz"
    assert score.version == 4.20
    assert score.version_major == 4


def test_investigate_xml_root(score_file: str) -> None:
    score = Score(score_file)

    def print_elements(element: _Element, level: int) -> None:
        for sub_element in element:
            print(f"{'    ' * level}<{sub_element.tag}>")
            print_elements(sub_element, level + 1)

    print_elements(score.xml_root, 0)


def test_set_meta_tag_composer(score: Score) -> None:
    assert score.meta.metatag.composer == "Composer"

    score.meta.metatag.composer = "Mozart"
    score.save()

    new_score: Score = score.reload()
    assert new_score.meta.metatag.composer == "Mozart"
