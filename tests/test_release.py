"""Public-package boundary tests using only disposable synthetic sources."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock
import zipfile


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "build_release.py"
SPEC = importlib.util.spec_from_file_location("workflow_build_release", MODULE_PATH)
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)


class ReleaseBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="jk-mots-release-test-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "source"
        self.root.mkdir()

    def source(self, name, data):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def allow(self, names):
        (self.root / "RELEASE_FILES.txt").write_text("\n".join(names) + "\n", encoding="utf-8")

    def test_rejects_traversal_absolute_and_ambiguous_paths(self):
        self.source("ok.txt", b"allowed")
        (self.base / "outside.txt").write_bytes(b"outside the source")
        for invalid in ("../outside.txt", "nested/../../outside.txt", "/outside.txt",
                        "C:/outside.txt", r"C:\outside.txt", r"nested\ok.txt",
                        "./ok.txt", "nested//ok.txt", "nested/"):
            with self.subTest(path=invalid):
                self.allow([invalid])
                with self.assertRaisesRegex(ValueError, "Unsafe allowlist path"):
                    release.selected_files(self.root)
        self.assertEqual((self.base / "outside.txt").read_bytes(), b"outside the source")

    def test_rejects_duplicate_and_case_colliding_entries(self):
        self.source("Readme.txt", b"public")
        for entries in (["Readme.txt", "Readme.txt"], ["Readme.txt", "README.TXT"]):
            with self.subTest(entries=entries):
                self.allow(entries)
                with self.assertRaisesRegex(ValueError, "Duplicate/case-colliding"):
                    release.selected_files(self.root)

    def test_rejects_reparse_metadata_on_file_or_ancestor(self):
        payload = self.source("nested/payload.txt", b"public")
        self.allow(["nested/payload.txt"])
        real_lstat = Path.lstat
        for refused in (payload, payload.parent):
            with self.subTest(refused=refused.name):
                def marked_lstat(path, *args, **kwargs):
                    result = real_lstat(path, *args, **kwargs)
                    if path == refused:
                        return SimpleNamespace(st_mode=result.st_mode,
                                               st_file_attributes=getattr(result, "st_file_attributes", 0) | 0x400)
                    return result
                with mock.patch.object(Path, "lstat", marked_lstat):
                    with self.assertRaisesRegex(ValueError, "Linked/reparse source"):
                        release.selected_files(self.root)

    def test_rejects_real_symlink_source_when_supported(self):
        outside = self.base / "outside.txt"
        outside.write_bytes(b"not public")
        link = self.root / "linked.txt"
        try:
            os.symlink(outside, link)
        except (OSError, NotImplementedError) as exc:
            code = getattr(exc, "winerror", None) or getattr(exc, "errno", None)
            self.skipTest(f"Host cannot create symlinks: {type(exc).__name__}, OS error {code}")
        self.allow(["linked.txt"])
        with self.assertRaisesRegex(ValueError, "Linked/reparse source"):
            release.selected_files(self.root)
        self.assertEqual(outside.read_bytes(), b"not public")

    def test_rejects_empty_missing_and_directory_sources(self):
        self.allow(["# intentionally no public files"])
        with self.assertRaisesRegex(ValueError, "Empty release allowlist"):
            release.selected_files(self.root)
        self.allow(["missing.txt"])
        with self.assertRaises((OSError, ValueError)):
            release.selected_files(self.root)
        (self.root / "folder").mkdir()
        self.allow(["folder"])
        with self.assertRaisesRegex(ValueError, "Missing or escaped source"):
            release.selected_files(self.root)

    def test_deterministic_archive_exact_members_and_manifest_readback(self):
        expected = {"README.md": b"Public text\r\n", "data/example.bin": bytes(range(256))}
        for name, data in expected.items():
            self.source(name, data)
        self.source("private-secret.txt", b"never in the allowlist")
        self.allow(["# public package", "data/example.bin", "README.md"])
        files1 = release.selected_files(self.root)
        first = self.base / "first.zip"
        receipt1 = release.archive(first, files1, "package")
        self.allow(["README.md", "data/example.bin"])
        os.utime(self.root / "README.md", (1_000_000, 1_000_000))
        second = self.base / "second.zip"
        receipt2 = release.archive(second, release.selected_files(self.root), "package")
        self.assertEqual(first.read_bytes(), second.read_bytes())
        self.assertEqual(receipt1["sha256"], receipt2["sha256"])
        self.assertEqual(receipt1["sha256"], hashlib.sha256(first.read_bytes()).hexdigest())
        with zipfile.ZipFile(first) as archive:
            names = archive.namelist()
            expected_members = {"package/" + name for name in expected} | {"package/PACKAGE-MANIFEST.json"}
            self.assertEqual(set(names), expected_members)
            self.assertEqual(len(names), len(expected_members))
            self.assertIsNone(archive.testzip())
            manifest = json.loads(archive.read("package/PACKAGE-MANIFEST.json"))
            self.assertEqual(manifest["version"], release.VERSION)
            self.assertEqual({entry["path"] for entry in manifest["files"]}, set(expected))
            for entry in manifest["files"]:
                data = archive.read("package/" + entry["path"])
                self.assertEqual(data, expected[entry["path"]])
                self.assertEqual(entry["bytes"], len(data))
                self.assertEqual(entry["sha256"], hashlib.sha256(data).hexdigest())
        for name, data in expected.items():
            self.assertEqual((self.root / name).read_bytes(), data)

    def test_existing_archive_is_preserved(self):
        existing = self.base / "keep.zip"
        original = b"An existing user file; need not even be a ZIP."
        existing.write_bytes(original)
        with self.assertRaisesRegex(ValueError, "Refusing to replace"):
            release.archive(existing, [("README.md", b"public")], "package")
        self.assertEqual(existing.read_bytes(), original)

    def test_single_download_contains_installable_skill_and_research_baseline(self):
        prefix = "skills/jk-mots-model-workflow/"
        names = ["LICENSE", "CREDITS.md", prefix + "SKILL.md", prefix + "references/method.md"]
        for name in names:
            self.source(name, ("Example " + name + "\n").encode())
        self.allow(names)
        out = self.base / "distribution"
        with mock.patch.object(release, "ROOT", self.root), mock.patch.object(sys, "argv", ["builder", "--output", str(out)]):
            release.main()
        archives = list(out.glob("*.zip"))
        self.assertEqual(len(archives), 1)
        with zipfile.ZipFile(archives[0]) as z:
            root_name = "JK-MotS-Model-Workflow-" + release.VERSION + "/"
            base = root_name + prefix
            manifest = json.loads(z.read(base + "PACKAGE-MANIFEST.json"))
            for entry in manifest["files"]:
                body = z.read(base + entry["path"])
                self.assertEqual(hashlib.sha256(body).hexdigest(), entry["sha256"])
                self.assertEqual(len(body), entry["bytes"])
            self.assertIn(base + "LICENSE", z.namelist())
            self.assertIn(base + "CREDITS.md", z.namelist())
            updates = json.loads((out / "research-updates.json").read_text())
            self.assertEqual(len(updates["files"]), 1)
            entry = updates["files"][0]
            self.assertEqual(entry["sha256"], hashlib.sha256(z.read(base + entry["path"])).hexdigest())


if __name__ == "__main__":
    unittest.main()
