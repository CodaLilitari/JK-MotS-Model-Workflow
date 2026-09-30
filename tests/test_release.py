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
            self.assertEqual(updates["requires_skill_version"], "1.1.0")
            state = json.loads(z.read(base + "research-update-state.json"))
            self.assertEqual(state["research_revision"], release.RESEARCH_REVISION)
            self.assertEqual(state["files"], updates["files"])
            self.assertEqual(len(updates["files"]), 1)
            entry = updates["files"][0]
            self.assertEqual(entry["sha256"], hashlib.sha256(z.read(base + entry["path"])).hexdigest())

    def test_extracted_release_refuses_rollback_and_upgrades_11_research_only(self):
        prefix = "skills/jk-mots-model-workflow/"
        updater_bytes = (MODULE_PATH.parents[1] / prefix / "scripts/research_updates.py").read_bytes()
        research = {"references/method.md": b"Current corrected method.\n",
                    "references/unchanged.md": b"Stable method.\n",
                    "references/evidence/new.json": b'{"new_evidence":true}\n'}
        payloads = {"LICENSE": b"License\n", "CREDITS.md": b"Credits\n",
                    prefix + "SKILL.md": b"Current complete skill instructions\n",
                    prefix + "scripts/research_updates.py": updater_bytes,
                    **{prefix + name: data for name, data in research.items()}}
        for name, data in payloads.items():
            self.source(name, data)
        self.allow(payloads)
        out = self.base / "distribution"
        with mock.patch.object(release, "ROOT", self.root), mock.patch.object(sys, "argv", ["builder", "--output", str(out)]):
            release.main()
        feed = json.loads((out / "research-updates.json").read_text(encoding="utf-8"))
        fresh = self.base / "fresh-skill"
        with zipfile.ZipFile(next(out.glob("*.zip"))) as z:
            source_prefix = "JK-MotS-Model-Workflow-" + release.VERSION + "/" + prefix
            for name in z.namelist():
                if name.startswith(source_prefix):
                    target = fresh / name[len(source_prefix):]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(z.read(name))
        spec = importlib.util.spec_from_file_location("extracted_release_updater", fresh / "scripts/research_updates.py")
        updater = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(updater)
        old_body = b"Previous method.\n"
        old_feed = json.loads(json.dumps(feed))
        old_feed.update(version="1.1.0", research_revision=release.RESEARCH_REVISION - 1)
        for entry in old_feed["files"]:
            if entry["path"] == "references/method.md":
                entry.update(bytes=len(old_body), sha256=updater.sha(old_body))
        calls = []

        def stale_fetch(url, limit):
            calls.append(url)
            self.assertEqual(url, updater.MANIFEST_URL, "A rollback must fail before downloading content")
            return json.dumps(old_feed).encode()

        before = {p.relative_to(fresh).as_posix(): p.read_bytes() for p in fresh.rglob("*") if p.is_file()}
        with self.assertRaisesRegex(ValueError, "downgrade"):
            updater.update(fresh, True, stale_fetch)
        self.assertEqual(calls, [updater.MANIFEST_URL])
        self.assertEqual(before, {p.relative_to(fresh).as_posix(): p.read_bytes() for p in fresh.rglob("*") if p.is_file()})

        # Historical 1.1 packages have a package baseline but no initial update state.
        previous = self.base / "previous-skill"
        existing = {"references/method.md": old_body,
                    "references/unchanged.md": research["references/unchanged.md"],
                    "SKILL.md": b"Existing 1.1 instructions\n",
                    "scripts/research_updates.py": updater_bytes}
        for name, data in existing.items():
            target = previous / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        package = {"version": "1.1.0", "files": [{"path": name, "bytes": len(data), "sha256": updater.sha(data)}
                                                for name, data in existing.items()]}
        package_bytes = json.dumps(package).encode()
        (previous / "PACKAGE-MANIFEST.json").write_bytes(package_bytes)
        calls.clear()

        def candidate_fetch(url, limit):
            calls.append(url)
            if url == updater.MANIFEST_URL:
                return json.dumps(feed).encode()
            content_prefix = updater.BASE + "releases/" + release.VERSION + "/"
            self.assertTrue(url.startswith(content_prefix))
            body = research[url[len(content_prefix):]]
            self.assertEqual(limit, len(body))
            return body

        report = updater.update(previous, True, candidate_fetch)
        self.assertTrue(report["compatible_skill"])
        self.assertTrue(report["applied"])
        self.assertEqual(set(report["changed_files"]), {"references/method.md", "references/evidence/new.json"})
        self.assertEqual(len(calls), 3)  # manifest, changed reference, new reference
        for name, data in research.items():
            self.assertEqual((previous / name).read_bytes(), data)
        for name in ("SKILL.md", "scripts/research_updates.py"):
            self.assertEqual((previous / name).read_bytes(), existing[name])
        self.assertEqual((previous / "PACKAGE-MANIFEST.json").read_bytes(), package_bytes)
        state = json.loads((previous / updater.STATE_NAME).read_text(encoding="utf-8"))
        self.assertEqual(state["research_revision"], release.RESEARCH_REVISION)
        self.assertEqual(state["files"], feed["files"])


if __name__ == "__main__":
    unittest.main()
