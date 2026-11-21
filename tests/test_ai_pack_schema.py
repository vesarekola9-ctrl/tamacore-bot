"""Generated AI packs must satisfy the actual factory schema."""
import tempfile
import unittest
from pathlib import Path

from tamacore.factory_v3_1.ai_pack_generator import generate_ai_pack
from tamacore.factory_v3_1.pack_inspector import inspect_pack


class GeneratedPackSchemaTests(unittest.TestCase):
    def test_generated_pack_is_valid(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            generate_ai_pack(path)
            self.assertEqual(inspect_pack(path), [])


if __name__ == "__main__":
    unittest.main()
