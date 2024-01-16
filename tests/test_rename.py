"""Test submodule “rename.py”."""

from __future__ import annotations

from pathlib import Path

import pytest

from mscxyz import Score, rename, supported_versions
from mscxyz.settings import reset_args
from tests.helper import Cli, get_file, get_score, ini_file


class TestFunctions:
    def test_function_prepare_fields(self) -> None:
        reset_args()
        fields: dict[str, str] = {
            "field1": " Subtitle ",
            "field2": "Title / Composer",
        }
        result: dict[str, str] = rename.prepare_fields(fields)
        assert result == {
            "field1": "Subtitle",
            "field2": "Title - Composer",
        }

    def test_function_apply_format_string(self) -> None:
        reset_args()
        score = get_score("meta-all-values.mscx")
        fields: dict[str, str] = score.meta.interface.export_to_dict()
        name: str = rename.apply_format_string(fields)
        assert name == "vbox_title (vbox_composer)"

    def test_function_get_checksum(self) -> None:
        tmp: str = get_file("simple.mscx")
        assert rename.get_checksum(tmp) == "dacd912aa0f6a1a67c3b13bb947395509e19dce2"


class TestIntegration:
    @pytest.mark.legacy
    @pytest.mark.parametrize("version", supported_versions)
    def test_simple(self, version: int, cwd_tmpdir: Path) -> None:
        stdout: str = Cli(
            "--config-file",
            ini_file,
            "rename",
            get_file("simple.mscx", version),
            legacy=True,
        ).stdout()
        filename = "Title (Composer).mscx"
        target = Path(cwd_tmpdir / filename)
        assert target.exists()
        assert "simple.mscx -> " in stdout
        assert filename in stdout
        target.unlink()

    @pytest.mark.legacy
    @pytest.mark.parametrize("version", supported_versions)
    def test_without_arguments(self, version: int, cwd_tmpdir: Path) -> None:
        stdout: str = Cli(
            "rename", get_file("meta-all-values.mscx", version), legacy=True
        ).stdout()
        filename = "vbox_title (vbox_composer).mscx"
        dest = Path(cwd_tmpdir / filename)
        assert dest.exists()
        assert filename in stdout
        dest.unlink()

    @pytest.mark.legacy
    def test_format(self, cwd_tmpdir: Path) -> None:
        stdout: str = Cli(
            "rename",
            "--format",
            "${vbox_composer}_${vbox_title}",
            get_file("score.mscz", 4),
            append_score=False,
            legacy=True,
        ).stdout()
        filename = "Composer_Title.mscz"
        assert Path(cwd_tmpdir / filename).exists()
        assert filename in stdout

    @pytest.mark.legacy
    def test_no_whitespace(self, cwd_tmpdir: Path) -> None:
        stdout: str = Cli(
            "rename", "--no-whitespace", get_file("meta-real-world.mscx"), legacy=True
        ).stdout()
        filename = "Wir-sind-des-Geyers-schwarze-Haufen (Florian-Geyer).mscx"
        assert Path(cwd_tmpdir / filename).exists()
        assert filename in stdout

    @pytest.mark.legacy
    def test_alphanum(self, cwd_tmpdir: Path) -> None:
        stdout: str = Cli(
            "rename", "--alphanum", get_file("meta-all-values.mscx"), legacy=True
        ).stdout()
        filename = "vbox title (vbox composer).mscx"
        assert Path(cwd_tmpdir / filename).exists()
        assert filename in stdout

    @pytest.mark.legacy
    def test_ascii(self, cwd_tmpdir: Path) -> None:
        stdout: str = Cli(
            "rename", "--ascii", get_file("unicode.mscx"), legacy=True
        ).stdout()
        filename = "Tuetlae (Coempoesser).mscx"
        assert Path(cwd_tmpdir / filename).exists()
        assert filename in stdout

    @pytest.mark.legacy
    def test_rename_file_twice(self, cwd_tmpdir: Path) -> None:
        Cli("rename", get_file("simple.mscx"), legacy=True).execute()
        assert Path(cwd_tmpdir / "Title (Composer).mscx").exists()
        assert (
            "with the same checksum (sha1) already"
            in Cli("rename", get_file("simple.mscx"), legacy=True).stdout()
        )

    @pytest.mark.legacy
    def test_rename_same_filename(self, cwd_tmpdir: Path) -> None:
        for filename in ("simple.mscx", "lyrics.mscx", "no-vbox.mscx"):
            Cli("rename", "-f", "same", get_file(filename), legacy=True).execute()
        assert Path(cwd_tmpdir / "same.mscx").exists()
        assert not Path(cwd_tmpdir / "same1.mscx").exists()
        assert Path(cwd_tmpdir / "same2.mscx").exists()
        assert Path(cwd_tmpdir / "same3.mscx").exists()

    @pytest.mark.legacy
    def test_rename_skips(self) -> None:
        assert (
            "Field “metatag_source” is empty! Skipping"
            in Cli(
                "rename",
                "--skip-if-empty",
                "metatag_composer,metatag_source",
                get_file("simple.mscx"),
                legacy=True,
            ).stdout()
        )

    @pytest.mark.legacy
    def test_rename_skip_pass(self, cwd_tmpdir: Path) -> None:
        stdout: str = Cli(
            "--config-file",
            ini_file,
            "rename",
            "--skip-if-empty",
            "metatag_composer,metatag_work_title",
            get_file("simple.mscx"),
            legacy=True,
        ).stdout()
        target: Path = cwd_tmpdir / "Title (Composer).mscx"
        assert target.exists()
        assert "simple.mscx -> " in stdout
        assert "Title (Composer).mscx" in stdout

    @pytest.mark.legacy
    def test_rename_target_legacy(self, score: Score, cwd_tmpdir: Path) -> None:
        Cli(
            "rename",
            "--target",
            cwd_tmpdir,
            score,
            append_score=False,
            legacy=True,
        ).execute()
        target: Path = cwd_tmpdir / "Title (Composer).mscz"
        assert target.exists()

    def test_rename_target(self, score: Score, cwd_tmpdir: Path) -> None:
        Cli("--rename", "--target", cwd_tmpdir, score, append_score=False).execute()
        target: Path = cwd_tmpdir / "Title (Composer).mscz"
        assert target.exists()
