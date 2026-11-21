"""Regression coverage for importing generated sprite frames into GDevelop."""
import tempfile
import unittest
from pathlib import Path

from tamacore.factory_v3_1.character_builder import apply_character_animations


class CharacterBuilderTests(unittest.TestCase):
    def test_no_generated_frames_keeps_existing_player(self):
        with tempfile.TemporaryDirectory() as directory:
            player = {"name": "Player", "type": "Sprite", "animations": [{"name": "Original"}]}
            project = {"resources": {"resources": []}}
            apply_character_animations(project, {"objects": [player]}, Path(directory))
            self.assertEqual(player["animations"], [{"name": "Original"}])

    def test_registers_idle_and_walk_frames_once(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / "assets" / "generated" / "player"
            folder.mkdir(parents=True)
            for name in ("player_idle_01.png", "player_walk_01.png"):
                (folder / name).write_bytes(b"image")
            player = {"name": "Player"}
            project = {"resources": {"resources": []}}
            scene = {"objects": [player]}
            apply_character_animations(project, scene, root)
            self.assertEqual([a["name"] for a in player["animations"]], ["Idle", "Walk"])
            resources = project["resources"]["resources"]
            self.assertEqual(len(resources), 2)
            self.assertEqual({r["name"] for r in resources}, {
                "assets/generated/player/player_idle_01.png",
                "assets/generated/player/player_walk_01.png",
            })
            apply_character_animations(project, scene, root)
            self.assertEqual(len(resources), 2)

    def test_unrelated_player_art_is_not_imported_as_animation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            folder = root / "assets" / "generated" / "player"
            folder.mkdir(parents=True)
            for name in ("player_idle_01.png", "player_playful.png", "player_portrait.png", "player_walk_01.png"):
                (folder / name).write_bytes(b"image")
            player = {"name": "Player"}
            project = {"resources": {"resources": []}}
            apply_character_animations(project, {"objects": [player]}, root)
            self.assertEqual([a["name"] for a in player["animations"]], ["Idle", "Walk"])
            self.assertEqual(len(project["resources"]["resources"]), 2)



if __name__ == "__main__":
    unittest.main()
