"""Test submodule “rename.py”."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from mscxyz import Score, rename
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
    @staticmethod
    def _target_path_cwd(filename: str) -> str:
        return os.path.join(os.getcwd(), filename)

    @staticmethod
    def _exists_in_cwd(filename: str) -> bool:
        return os.path.exists(os.path.join(os.getcwd(), filename))

    @staticmethod
    def _rm_in_cwd(filename: str) -> None:
        return os.remove(os.path.join(os.getcwd(), filename))

    def _test_simple(self, version: int) -> None:
        stdout: str = Cli(
            "--config-file",
            ini_file,
            "rename",
            get_file("simple.mscx", version),
            legacy=True,
        ).stdout()
        target: str = self._target_path_cwd("Title (Composer).mscx")
        assert os.path.exists(target)
        assert "simple.mscx -> " in stdout
        assert "Title (Composer).mscx" in stdout
        os.remove(target)

    def test_simple(self) -> None:
        self._test_simple(version=2)
        self._test_simple(version=3)

    def _test_without_arguments(self, version: int) -> None:
        stdout: str = Cli(
            "rename", get_file("meta-all-values.mscx", version), legacy=True
        ).stdout()
        target: str = self._target_path_cwd("vbox_title (vbox_composer).mscx")
        assert os.path.exists(target)
        assert "vbox_title (vbox_composer).mscx" in stdout
        os.remove(target)

    def test_without_arguments(self) -> None:
        self._test_without_arguments(version=2)
        self._test_without_arguments(version=3)

    def test_format(self, cwd_tmpdir: Path) -> None:
        stdout: str = Cli(
            "rename",
            "--format",
            "${vbox_composer}_${vbox_title}",
            get_file("score.mscz", 4),
            append_score=False,
            legacy=True,
        ).stdout()
        target = cwd_tmpdir / "Composer_Title.mscz"
        assert os.path.exists(target)
        assert "Composer_Title.mscz" in stdout

    def test_no_whitespace(self) -> None:
        stdout: str = Cli(
            "rename", "--no-whitespace", get_file("meta-real-world.mscx"), legacy=True
        ).stdout()
        new_name = "Wir-sind-des-Geyers-schwarze-Haufen (Florian-Geyer).mscx"
        target: str = self._target_path_cwd(new_name)
        assert os.path.exists(target)
        assert new_name in stdout
        os.remove(target)

    def test_alphanum(self) -> None:
        stdout: str = Cli(
            "rename", "--alphanum", get_file("meta-all-values.mscx"), legacy=True
        ).stdout()
        target: str = self._target_path_cwd("vbox title (vbox composer).mscx")
        assert os.path.exists(target)
        assert "vbox title (vbox composer).mscx" in stdout
        os.remove(target)

    def test_ascii(self) -> None:
        stdout: str = Cli(
            "rename", "--ascii", get_file("unicode.mscx"), legacy=True
        ).stdout()
        target: str = self._target_path_cwd("Tuetlae (Coempoesser).mscx")
        assert os.path.exists(target)
        assert "Tuetlae (Coempoesser).mscx" in stdout
        os.remove(target)

    def test_rename_file_twice(self) -> None:
        Cli("rename", get_file("simple.mscx"), legacy=True).execute()
        stdout = Cli("rename", get_file("simple.mscx"), legacy=True).stdout()
        target = self._target_path_cwd("Title (Composer).mscx")
        assert "with the same checksum (sha1) already" in stdout
        os.remove(target)

    def test_rename_same_filename(self) -> None:
        Cli("rename", "-f", "same", get_file("simple.mscx"), legacy=True).execute()
        Cli("rename", "-f", "same", get_file("lyrics.mscx"), legacy=True).execute()
        Cli("rename", "-f", "same", get_file("no-vbox.mscx"), legacy=True).execute()
        assert self._exists_in_cwd("same.mscx")
        assert not self._exists_in_cwd("same1.mscx")
        assert self._exists_in_cwd("same2.mscx")
        assert self._exists_in_cwd("same3.mscx")
        self._rm_in_cwd("same.mscx")
        self._rm_in_cwd("same2.mscx")
        self._rm_in_cwd("same3.mscx")

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

    def test_rename_skip_pass(self) -> None:
        stdout: str = Cli(
            "--config-file",
            ini_file,
            "rename",
            "--skip-if-empty",
            "metatag_composer,metatag_work_title",
            get_file("simple.mscx"),
            legacy=True,
        ).stdout()
        target: str = self._target_path_cwd("Title (Composer).mscx")
        assert os.path.exists(target)
        assert "simple.mscx -> " in stdout
        assert "Title (Composer).mscx" in stdout
        os.remove(target)

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
