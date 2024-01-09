"""Test the examples from the README.rst file."""

from __future__ import annotations

from tests.helper import stdout, sysexit


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

    def test_glob(self) -> None:
        output = stdout("-L", "--glob", "*/by_version/4/*.mscz")
        assert "/by_version/4/" in output
        assert ".mscz" in output
        assert "/by_version/3/" not in output
        assert ".mscx" not in output

    def test_mscz_only(self) -> None:
        output = stdout("-L", "--mscz")
        assert "score.mscz" in output
        assert "score.mscx" not in output

    def test_mscx_only(self) -> None:
        output = stdout("-L", "--mscx")
        assert "score.mscz" not in output
        assert "simple.mscx" in output

    def test_dont_mix_mscz_and_mscx(self) -> None:
        assert "--mscx: not allowed with argument --mscz" in sysexit(
            "-L", "--mscz", "--mscx"
        )

    def test_dont_mix_mscz_and_glob(self) -> None:
        assert "--glob: not allowed with argument --mscz" in sysexit(
            "-L", "--mscz", "--glob", "*"
        )

    def test_dont_mix_mscx_and_glob(self) -> None:
        assert "--glob: not allowed with argument --mscx" in sysexit(
            "-L", "--mscx", "-glob", "*"
        )
