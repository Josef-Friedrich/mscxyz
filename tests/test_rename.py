"""Test submodule “rename.py”."""

from __future__ import annotations

import os
import tempfile

from mscxyz import rename
from mscxyz.settings import reset_args
from tests import helper
from tests.helper import ini_file


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
        score = helper.get_score("meta-all-values.mscx")
        fields: dict[str, str] = score.meta.interface.export_to_dict()
        name: str = rename.apply_format_string(fields)
        assert name == "vbox_title (vbox_composer)"

    def test_function_get_checksum(self) -> None:
        tmp: str = helper.get_file("simple.mscx")
        assert rename.get_checksum(tmp) == "dacd912aa0f6a1a67c3b13bb947395509e19dce2"


class TestIntegration:
    @staticmethod
    def _get(filename: str, version: int = 2) -> str:
        return helper.get_file(filename, version)

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
        output: str = helper.run(
            "--config-file", ini_file, "rename", self._get("simple.mscx", version)
        )
        target: str = self._target_path_cwd("Title (Composer).mscx")
        assert os.path.exists(target)
        assert "simple.mscx -> " in output
        assert "Title (Composer).mscx" in output
        os.remove(target)

    def test_simple(self) -> None:
        self._test_simple(version=2)
        self._test_simple(version=3)

    def _test_without_arguments(self, version: int) -> None:
        output: str = helper.run("rename", self._get("meta-all-values.mscx", version))
        target: str = self._target_path_cwd("vbox_title (vbox_composer).mscx")
        assert os.path.exists(target)
        assert "vbox_title (vbox_composer).mscx" in output
        os.remove(target)

    def test_without_arguments(self) -> None:
        self._test_without_arguments(version=2)
        self._test_without_arguments(version=3)

    def test_format(self) -> None:
        output: str = helper.run(
            "rename",
            "--format",
            "${vbox_composer}_${vbox_title}",
            self._get("simple.mscx"),
        )
        target = self._target_path_cwd("Composer_Title.mscx")
        assert os.path.exists(target)
        assert "Composer_Title.mscx" in output
        os.remove(target)

    def test_no_whitespace(self) -> None:
        output: str = helper.run(
            "rename", "--no-whitespace", self._get("meta-real-world.mscx")
        )
        new_name = "Wir-sind-des-Geyers-schwarze-Haufen (Florian-Geyer).mscx"
        target: str = self._target_path_cwd(new_name)
        assert os.path.exists(target)
        assert new_name in output
        os.remove(target)

    def test_alphanum(self) -> None:
        output: str = helper.run(
            "rename", "--alphanum", self._get("meta-all-values.mscx")
        )
        target: str = self._target_path_cwd("vbox title (vbox composer).mscx")
        assert os.path.exists(target)
        assert "vbox title (vbox composer).mscx" in output
        os.remove(target)

    def test_ascii(self) -> None:
        output: str = helper.run("rename", "--ascii", self._get("unicode.mscx"))
        target: str = self._target_path_cwd("Tuetlae (Coempoesser).mscx")
        assert os.path.exists(target)
        assert "Tuetlae (Coempoesser).mscx" in output
        os.remove(target)

    def test_rename_file_twice(self) -> None:
        helper.run("rename", self._get("simple.mscx"))
        output = helper.run("rename", self._get("simple.mscx"))
        target = self._target_path_cwd("Title (Composer).mscx")
        assert "with the same checksum (sha1) already" in output
        os.remove(target)

    def test_rename_same_filename(self) -> None:
        helper.run("rename", "-f", "same", self._get("simple.mscx"))
        helper.run("rename", "-f", "same", self._get("lyrics.mscx"))
        helper.run("rename", "-f", "same", self._get("no-vbox.mscx"))
        assert self._exists_in_cwd("same.mscx")
        assert not self._exists_in_cwd("same1.mscx")
        assert self._exists_in_cwd("same2.mscx")
        assert self._exists_in_cwd("same3.mscx")
        self._rm_in_cwd("same.mscx")
        self._rm_in_cwd("same2.mscx")
        self._rm_in_cwd("same3.mscx")

    def test_rename_skips(self) -> None:
        output: str = helper.run(
            "rename",
            "--skip-if-empty",
            "metatag_composer,metatag_source",
            self._get("simple.mscx"),
        )
        assert "Field “metatag_source” is empty! Skipping" in output

    def test_rename_skip_pass(self) -> None:
        output: str = helper.run(
            "--config-file",
            ini_file,
            "rename",
            "--skip-if-empty",
            "metatag_composer,metatag_work_title",
            self._get("simple.mscx"),
        )
        target: str = self._target_path_cwd("Title (Composer).mscx")
        assert os.path.exists(target)
        assert "simple.mscx -> " in output
        assert "Title (Composer).mscx" in output
        os.remove(target)

    def test_rename_target(self) -> None:
        tmp_dir: str = tempfile.mkdtemp()
        helper.run("rename", "--target", tmp_dir, self._get("simple.mscx"))
        target: str = os.path.join(tmp_dir, "Title (Composer).mscx")
        assert os.path.exists(target)
        os.remove(target)
