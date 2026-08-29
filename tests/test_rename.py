"""
Basic tests for bulk_rename.py.

Run with:
    python -m pytest tests/
or:
    python tests/test_rename.py
"""

import sys
import tempfile
import shutil
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bulk_rename import build_new_name, get_files


class FakeArgs:
    def __init__(self, prefix="", suffix="", find=None, replace="", sequence=None,
                 start=1, padding=3, ext=None):
        self.prefix = prefix
        self.suffix = suffix
        self.find = find
        self.replace = replace
        self.sequence = sequence
        self.start = start
        self.padding = padding
        self.ext = ext


class TestBuildNewName(unittest.TestCase):
    def test_prefix(self):
        args = FakeArgs(prefix="vacation_")
        result = build_new_name(Path("photo.jpg"), 0, args)
        self.assertEqual(result, "vacation_photo.jpg")

    def test_suffix(self):
        args = FakeArgs(suffix="_edited")
        result = build_new_name(Path("photo.jpg"), 0, args)
        self.assertEqual(result, "photo_edited.jpg")

    def test_find_replace(self):
        args = FakeArgs(find="IMG", replace="photo")
        result = build_new_name(Path("IMG_1234.jpg"), 0, args)
        self.assertEqual(result, "photo_1234.jpg")

    def test_sequence(self):
        args = FakeArgs(sequence="photo_", start=1, padding=3)
        result = build_new_name(Path("random_name.jpg"), 0, args)
        self.assertEqual(result, "photo_001.jpg")

        result2 = build_new_name(Path("another.jpg"), 4, args)
        self.assertEqual(result2, "photo_005.jpg")

    def test_change_extension(self):
        args = FakeArgs(ext=".png")
        result = build_new_name(Path("photo.jpg"), 0, args)
        self.assertEqual(result, "photo.png")


class TestGetFiles(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        (self.tmp_dir / "a.txt").touch()
        (self.tmp_dir / "b.txt").touch()
        sub = self.tmp_dir / "subfolder"
        sub.mkdir()
        (sub / "c.txt").touch()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir)

    def test_non_recursive(self):
        files = get_files(self.tmp_dir, recursive=False)
        names = [f.name for f in files]
        self.assertIn("a.txt", names)
        self.assertIn("b.txt", names)
        self.assertNotIn("c.txt", names)

    def test_recursive(self):
        files = get_files(self.tmp_dir, recursive=True)
        names = [f.name for f in files]
        self.assertIn("c.txt", names)


if __name__ == "__main__":
    unittest.main()
