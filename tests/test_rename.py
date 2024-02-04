"""Test submodule “rename.py”."""

from __future__ import annotations

from pathlib import Path

import pytest

from mscxyz import Score, rename, supported_versions
from mscxyz.settings import reset_args
from tests.helper import Cli, get_dir, get_file


class TestFunctions:
    def test_function_prepare_fields(self) -> None:
        reset_args()
        fields = {
            "field1": " Subtitle ",
            "field2": "Title / Composer",
        }
        result: dict[str, str] = rename._prepare_fields(fields)
        assert result == {
            "field1": "Subtitle",
            "field2": "Title - Composer",
        }

    def test_function_get_checksum(self) -> None:
        tmp: str = get_file("simple.mscx")
        assert rename._get_checksum(tmp) == "dacd912aa0f6a1a67c3b13bb947395509e19dce2"


class TestCli:
    @pytest.mark.parametrize("version", supported_versions)
    def test_simple(self, version: int, cwd_tmpdir: Path) -> None:
        stdout: str = Cli(
            "--rename",
            "$title ($composer)",
            get_file("simple.mscx", version),
        ).stdout()
        filename = "Title (Composer).mscx"
        target = Path(cwd_tmpdir / filename)
        assert target.exists()
        assert "simple.mscx -> " in stdout
        assert filename in stdout
        target.unlink()

    @pytest.mark.parametrize("version", supported_versions)
    def test_without_arguments(self, version: int, cwd_tmpdir: Path) -> None:
        stdout: str = Cli(
            "--rename", "$title ($composer)", get_file("meta-all-values.mscx", version)
        ).stdout()
        filename = "vbox_title (vbox_composer).mscx"
        dest = Path(cwd_tmpdir / filename)
        assert dest.exists()
        assert filename in stdout
        dest.unlink()

    def test_format(self, cwd_tmpdir: Path) -> None:
        stdout: str = Cli("--rename", "${vbox_composer}_${vbox_title}").stdout()
        filename = "Composer_Title.mscz"
        assert Path(cwd_tmpdir / filename).exists()
        assert filename in stdout

    def test_no_whitespace(self, cwd_tmpdir: Path) -> None:
        stdout: str = (
            Cli("--rename", "$title ($composer)", "--no-whitespace")
            .append_score("meta-real-world.mscz")
            .stdout()
        )
        filename = "Wir-sind-des-Geyers-schwarze-Haufen (Florian-Geyer).mscz"
        assert Path(cwd_tmpdir / filename).exists()
        assert filename in stdout

    def test_alphanum(self, cwd_tmpdir: Path) -> None:
        stdout: str = (
            Cli(
                "--rename",
                "$title ($composer)",
                "--alphanum",
            )
            .append_score("meta-all-values.mscz")
            .stdout()
        )
        filename = "vbox title (vbox composer).mscz"
        assert Path(cwd_tmpdir / filename).exists()
        assert filename in stdout

    def test_ascii(self, cwd_tmpdir: Path) -> None:
        stdout: str = (
            Cli("--rename", "$title ($composer)", "--ascii")
            .append_score("unicode.mscz")
            .stdout()
        )
        filename = "Tuetlae (Coempoesser).mscz"
        assert Path(cwd_tmpdir / filename).exists()
        assert filename in stdout

    def test_rename_file_twice(self, cwd_tmpdir: Path) -> None:
        Cli("--rename", "$title ($composer)").execute()
        assert Path(cwd_tmpdir / "Title (Composer).mscz").exists()
        assert (
            "with the same checksum (sha1) already"
            in Cli("--rename", "$title ($composer)").stdout()
        )

    def test_rename_same_filename(self, cwd_tmpdir: Path) -> None:
        for filename in ("simple.mscx", "lyrics.mscx", "no-vbox.mscx"):
            Cli("--rename", "same", get_file(filename)).execute()
        assert Path(cwd_tmpdir / "same.mscx").exists()
        assert not Path(cwd_tmpdir / "same1.mscx").exists()
        assert Path(cwd_tmpdir / "same2.mscx").exists()
        assert Path(cwd_tmpdir / "same3.mscx").exists()

    def test_rename_skips(self) -> None:
        assert (
            "Field “metatag_source” is empty! Skipping"
            in Cli(
                "--rename",
                "$title ($composer)",
                "--skip-if-empty",
                "metatag_composer,metatag_source",
            ).stdout()
        )

    def test_rename_skip_pass(self, cwd_tmpdir: Path) -> None:
        stdout: str = Cli(
            "--bail",
            "--rename",
            "$title ($composer)",
            "--skip-if-empty",
            "metatag_composer,metatag_work_title",
        ).stdout()
        filename = "Title (Composer).mscz"
        target: Path = cwd_tmpdir / filename
        assert target.exists()
        assert "score.mscz -> " in stdout
        assert filename in stdout

    def test_rename_target(self, score: Score, cwd_tmpdir: Path) -> None:
        Cli(
            "--rename",
            "$title ($composer)",
            "--target",
            cwd_tmpdir,
            score,
            append_score=False,
        ).execute()
        target: Path = cwd_tmpdir / "Title (Composer).mscz"
        assert target.exists()


def test_option_only_filename() -> None:
    src = Path(get_dir("leadsheets", 4))
    Cli(
        "--rename",
        "filename",
        "--only-filename",
        src / "Jackson.mscz",
    ).execute()

    assert (src / "filename.mscz").exists()
