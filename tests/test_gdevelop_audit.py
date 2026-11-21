"""Tests for GDevelop export structure auditing."""
import json
import tempfile
import unittest
from pathlib import Path

from tamacore.factory_v3_1.gdevelop_audit import audit_project


class GDevelopAuditTests(unittest.TestCase):
    def test_detects_missing_assets_and_empty_scene(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "game.json"
            project.write_text(json.dumps({
                "resources": {"resources": [{"name": "pet", "file": "pet.png"}]},
                "layouts": [{"name": "Home", "objects": [], "instances": [], "events": []}],
            }), encoding="utf-8")
            errors = audit_project(project)
            self.assertTrue(any("Missing resource" in e for e in errors))
            self.assertTrue(any("no objects" in e for e in errors))
            self.assertTrue(any("no events" in e for e in errors))

    def test_detects_missing_sprite_animation_frame(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "game.json"
            project.write_text(json.dumps({
                "resources": {"resources": []},
                "layouts": [{"name": "Home", "objects": [{
                    "name": "Pet", "animations": [{
                        "directions": [{"sprites": [{"image": "assets/pet_idle.png"}]}]
                    }]
                }], "events": [{"type": "BuiltinCommonInstructions::Standard"}]}],
            }), encoding="utf-8")
            self.assertIn("Missing animation frame: assets/pet_idle.png", audit_project(project))

    def test_rejects_resource_path_traversal(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "game.json"
            project.write_text(json.dumps({
                "resources": {"resources": [{"name": "unsafe", "file": "../secret.png"}]},
                "layouts": [{"name": "Home", "objects": [{"name": "Pet"}],
                             "events": [{"type": "BuiltinCommonInstructions::Standard"}]}],
            }), encoding="utf-8")
            self.assertIn("Unsafe resource path: ../secret.png", audit_project(project))

    def test_accepts_basic_nonempty_structure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pet.png").write_bytes(b"placeholder")
            project = root / "game.json"
            project.write_text(json.dumps({
                "resources": {"resources": [{"name": "pet", "file": "pet.png"}]},
                "layouts": [{"name": "Home", "objects": [{"name": "Pet"}], "events": [{"type": "BuiltinCommonInstructions::Standard"}]}],
            }), encoding="utf-8")
            self.assertEqual(audit_project(project), [])


if __name__ == "__main__":
    unittest.main()
