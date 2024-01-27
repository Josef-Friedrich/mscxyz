"""Test API interface. The mscxyz module is used in Python code not on the
command line."""


from mscxyz import (
    Score,
    list_path,
)


def test_class_score() -> None:
    assert Score.__name__ == "Score"


def test_function_list_scores() -> None:
    assert list_path.__name__ == "list_path"
