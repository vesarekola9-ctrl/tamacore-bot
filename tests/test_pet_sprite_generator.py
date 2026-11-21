"""Procedural pet PNG and GDevelop animation integration tests."""
import struct
import tempfile
import unittest
from pathlib import Path

from tamacore.factory_v3_1.pet_sprite_generator import STATES, generate_pet_sprites, render_pet
from tamacore.factory_v3_1.character_builder import apply_character_animations


class PetSpriteGeneratorTests(unittest.TestCase):
    def test_png_signature_and_dimensions(self):
        for species in ("bunny", "cat", "dog"):
            data = render_pet(species, "idle", 0)
            self.assertEqual(data[:8], b"\\x89PNG\\r\\n\\x1a\\n")
            self.assertEqual(struct.unpack(">II", data[16:24]), (128, 128))

    def test_generate_ten_frames_and_preserve_custom_art(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            frames = generate_pet_sprites(root, "cat")
            self.assertEqual(len(frames), 2 * len(STATES))
            self.assertTrue(all(path.is_file() for path in frames))
            frames[0].write_bytes(b"custom artist art")
            generate_pet_sprites(root, "dog")
            self.assertEqual(frames[0].read_bytes(), b"custom artist art")

    def test_gdevelop_registers_all_five_animation_states(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            generate_pet_sprites(root, "bunny")
            player = {"name": "Player"}
            project = {"resources": {"resources": []}}
            apply_character_animations(project, {"objects": [player]}, root)
            self.assertEqual([item["name"] for item in player["animations"]],
                             ["Idle", "Walk", "Sleep", "Eat", "Play"])
            self.assertEqual(len(project["resources"]["resources"]), 10)


if __name__ == "__main__":
    unittest.main()
