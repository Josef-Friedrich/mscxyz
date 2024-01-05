"""Test the examples from the README.rst file."""

from __future__ import annotations

from mscxyz import Score


def test_instantiate_a_score_object(score_file: str) -> None:
    score = Score(score_file)
    assert score.path.exists()
    assert score.filename == "score.mscz"
    assert score.basename == "score"
    assert score.extension == "mscz"
    assert score.version == 4.20
    assert score.version_major == 4


def test_set_meta_tag_composer(score: Score) -> None:
    assert score.meta.interface.metatag_composer == "Composer"

    score.meta.interface.metatag_composer = "Mozart"
    score.save()

    new_score: Score = score.reload()
    assert new_score.meta.interface.metatag_composer == "Mozart"


def test_set_all_font_faces_using_for_loop(score: Score) -> None:
    assert score.style.get_value("defaultFontFace") == "FreeSerif"

    for element in score.style.styles:
        if "FontFace" in element.tag:
            element.text = "Alegreya"
    score.save()

    new_score: Score = score.reload()
    assert new_score.style.get_value("defaultFontFace") == "Alegreya"


def test_set_all_font_faces_using_method(score: Score) -> None:
    assert score.style.get_value("defaultFontFace") == "FreeSerif"

    response = score.style.set_all_font_faces("Alegreya")

    assert response == [
        ("lyricsOddFontFace", "FreeSerif", "Alegreya"),
        ("lyricsEvenFontFace", "FreeSerif", "Alegreya"),
        ("hairpinFontFace", "FreeSerif", "Alegreya"),
        ("pedalFontFace", "FreeSerif", "Alegreya"),
        ("chordSymbolAFontFace", "FreeSerif", "Alegreya"),
        ("chordSymbolBFontFace", "FreeSerif", "Alegreya"),
        ("romanNumeralFontFace", "Campania", "Alegreya"),
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
        ("dynamicsFontFace", "FreeSerif", "Alegreya"),
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
        ("figuredBassFontFace", "MScoreBC", "Alegreya"),
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
    assert new_score.style.get_value("defaultFontFace") == "Alegreya"
