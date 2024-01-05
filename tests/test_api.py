"""Test API interface. The mscxyz module is used in Python code not on the
command line."""


from mscxyz import (
    Lyrics,
    Meta,
    Score,
    Style,
    list_score_paths,
)


def test_class_score() -> None:
    assert Score.__name__ == "Score"


def test_class_lyrics() -> None:
    assert Lyrics.__name__ == "Lyrics"


def test_class_meta() -> None:
    assert Meta.__name__ == "Meta"


def test_class_style() -> None:
    assert Style.__name__ == "Style"


def test_function_list_scores() -> None:
    assert list_score_paths.__name__ == "list_score_paths"
