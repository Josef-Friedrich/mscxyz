"""Test submodule “rename.py”."""

from __future__ import annotations

from mscxyz.fields import FieldsManager


class TestClassFieldsManager:
    def test_property_names(self, fields: FieldsManager) -> None:
        assert fields.names == (
            "title",
            "abspath",
            "basename",
            "dirname",
            "extension",
            "filename",
            "relpath",
            "relpath_backup",
        )

    def test_method_get(self, fields: FieldsManager) -> None:
        assert fields.get("title") == "Title"
