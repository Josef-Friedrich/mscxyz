"""Test the examples from the README.rst file."""

from __future__ import annotations

from tests.helper import stdout


class TestSpecifyMusescoreFiles:
    def test_without_an_argument(self) -> None:
        assert "tests/files/by_version/4/score.mscz" in stdout("--list-files")

    def test_dot_to_specify_pwd(self) -> None:
        assert (
            "tests/files/by_version/4/nested-folders/level1/level2/level3/score3.mscz"
            in stdout("-L", ".")
        )

    def test_pass_multiple_files(self) -> None:
        file2 = "tests/files/by_version/2/score.mscz"
        file3 = "tests/files/by_version/3/score.mscz"
        file4 = "tests/files/by_version/4/score.mscz"

        output = stdout(
            "-L",
            file2,
            file3,
            file4,
        )

        assert file2 in output
        assert file3 in output
        assert file4 in output

    def test_pass_multiple_directories(self) -> None:
        dir2 = "tests/files/by_version/2"
        dir3 = "tests/files/by_version/3"
        dir4 = "tests/files/by_version/4"

        output = stdout(
            "-L",
            dir2,
            dir3,
            dir4,
        )

        assert dir2 in output
        assert dir3 in output
        assert dir4 in output

    def test_mscz_only(self) -> None:
        assert "score.mscz" in stdout("--mscz")
