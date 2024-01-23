"""Test submodule “rename.py”."""

from __future__ import annotations

import os
import re

from mscxyz.fields import FieldsManager


class TestClassFieldsManager:
    def test_property_names(self, fields: FieldsManager) -> None:
        assert fields.names == (
            "title",
            "subtitle",
            "composer",
            "lyricist",
            "vbox_title",
            "vbox_subtitle",
            "vbox_composer",
            "vbox_lyricist",
            "metatag_arranger",
            "metatag_audio_com_url",
            "metatag_composer",
            "metatag_copyright",
            "metatag_creation_date",
            "metatag_lyricist",
            "metatag_movement_number",
            "metatag_movement_title",
            "metatag_msc_version",
            "metatag_platform",
            "metatag_poet",
            "metatag_source",
            "metatag_source_revision_id",
            "metatag_subtitle",
            "metatag_translator",
            "metatag_work_number",
            "metatag_work_title",
            "version",
            "version_major",
            "path",
            "backup_file",
            "json_file",
            "dirname",
            "filename",
            "basename",
            "extension",
        )

    def test_method_export_to_dict(self, fields: FieldsManager) -> None:
        result = fields.export_to_dict()
        for key in result:
            value = result[key]
            if isinstance(value, str) and value.startswith(os.path.sep):
                value = re.sub(f"^{os.path.sep}.*{os.path.sep}", "/../..", value)
            result[key] = value
        if "dirname" in result:
            result["dirname"] = "dir"
        assert result == {
            "title": "Title",
            "composer": "Composer",
            "vbox_title": "Title",
            "vbox_composer": "Composer",
            "metatag_composer": "Composer",
            "metatag_msc_version": "4.20",
            "metatag_platform": "Linux",
            "metatag_work_title": "Title",
            "version": 4.20,
            "version_major": 4,
            "path": "/../..score.mscz",
            "backup_file": "/../..score_bak.mscz",
            "json_file": "/../..score.json",
            "dirname": "dir",
            "basename": "score",
            "extension": "mscz",
            "filename": "score.mscz",
        }

    def test_method_get(self, fields: FieldsManager) -> None:
        assert fields.get("title") == "Title"

    def test_method_set(self, fields: FieldsManager) -> None:
        new = "New Title"
        fields.set("title", new)
        assert fields.get("title") == new

    def test_distribute(self, fields: FieldsManager) -> None:
        fields.set("title", "We are the champions - Queen")
        fields.distribute("title,composer", "$title - $composer")
        assert fields.get("title") == "We are the champions"
        assert fields.get("composer") == "Queen"
