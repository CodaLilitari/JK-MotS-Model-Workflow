"""Focused, runtime-free checks for the shared Blender-Sith install resolver."""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import platform
import sys
import tempfile
import unittest
from unittest import mock
import zipfile


SPEC = importlib.util.spec_from_file_location(
    "resolve_install", Path(__file__).with_name("resolve_install.py"))
resolver = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(resolver)


def sha(data):
    return hashlib.sha256(data).hexdigest()


class ResolveInstallTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="sith-install-resolver-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.addon = self.root / "installation" / "sith"
        self.addon.mkdir(parents=True)
        self.payload = {
            "__init__.py": b"# Synthetic fixture; never imported.\n",
            "model/loader.py": b"# Fixture source.\n",
            "LICENSE": b"Fixture license.\n",
            "blender_manifest.toml": b'id = "sith"\nversion = "1.0.4"\n',
        }
        for name, data in self.payload.items():
            path = self.addon / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        self.archive = self.root / "sith-fixture.zip"
        with zipfile.ZipFile(self.archive, "w") as output:
            for name, data in self.payload.items():
                output.writestr(name, data)
        self.launcher = self.root / "validation" / "scripts" / "run_regression.py"
        self.harness = self.root / "validation" / "tests" / "background_regression.py"
        for path in (self.launcher, self.harness):
            path.parent.mkdir(parents=True)
            path.write_text("raise AssertionError('Must not execute fixture code')\n", encoding="utf-8")
        self.runtime = self.root / "runtime" / "blender"
        self.runtime.parent.mkdir()
        self.runtime.write_bytes(b"Not an executable: resolver must not launch it.\n")
        self.manifest = self.root / "current-install.json"
        self.data = {
            "schema_version": 1,
            "release_tag": "v1.0.4-coda.1",
            "extension_version": "1.0.4",
            "platform_system": platform.system(),
            "platform_machine": platform.machine(),
            "addon_dir": str(self.addon),
            "archive_path": str(self.archive),
            "archive_sha256": sha(self.archive.read_bytes()),
            "payload_sha256": {name: sha(data) for name, data in self.payload.items()},
            "runtime": {"route": "blender", "executable": str(self.runtime), "version": "5.1.2"},
            "launcher_path": str(self.launcher),
            "launcher_sha256": sha(self.launcher.read_bytes()),
            "harness_path": str(self.harness),
            "harness_sha256": sha(self.harness.read_bytes()),
        }
        self.save()

    def save(self):
        self.manifest.write_text(json.dumps(self.data), encoding="utf-8")

    def resolve(self, output=None):
        return resolver.resolve_install(self.manifest, regression_output=output)

    def test_positive_full_package_and_no_runtime_execution(self):
        result = self.resolve()
        self.assertEqual(result["source_root"], str(self.addon.parent))
        self.assertEqual(result["addon_dir"], str(self.addon))
        self.assertEqual(result["payload_sha256"], self.data["payload_sha256"])
        self.assertEqual(result["runtime"], self.data["runtime"])
        self.assertFalse(result["runtime_executed"])
        self.assertNotIn("regression_argv", result)

    def test_changed_missing_and_extra_payload_rejected(self):
        for mode in ("changed", "missing", "extra", "extra_non_source"):
            with self.subTest(mode=mode):
                original = self.addon / "model/loader.py"
                extra = self.addon / ("extra.py" if mode == "extra" else "unlisted.dat")
                if mode == "changed":
                    original.write_bytes(b"changed")
                elif mode == "missing":
                    original.unlink()
                else:
                    extra.write_bytes(b"unexpected")
                with self.assertRaisesRegex(ValueError, "payload"):
                    self.resolve()
                original.write_bytes(self.payload["model/loader.py"])
                if extra.exists():
                    extra.unlink()

    def test_only_generated_bytecode_excluded(self):
        cache = self.addon / "model" / "__pycache__"
        cache.mkdir()
        (cache / "loader.cpython-313.pyc").write_bytes(b"generated")
        result = self.resolve()
        self.assertEqual(result["ignored_generated_bytecode"],
                         ["model/__pycache__/loader.cpython-313.pyc"])

    def test_sourceless_or_unrecognized_bytecode_is_unexpected_payload(self):
        for name in ("module.pyc", "old.pyo", "model/__pycache__/orphan.cpython-313.pyc",
                     "model/__pycache__/injected.py", "model/__pycache__/loader.pyc"):
            with self.subTest(name=name):
                extra = self.addon / name
                extra.parent.mkdir(parents=True, exist_ok=True)
                extra.write_bytes(b"unattested executable bytes")
                with self.assertRaisesRegex(ValueError, "payload"):
                    self.resolve()
                extra.unlink()

    def test_extension_manifest_wrong_platform_rejected(self):
        content = self.payload["blender_manifest.toml"] + b'platforms = ["macos-arm64"]\n'
        self.payload["blender_manifest.toml"] = content
        (self.addon / "blender_manifest.toml").write_bytes(content)
        self.data["payload_sha256"]["blender_manifest.toml"] = sha(content)
        with zipfile.ZipFile(self.archive, "w") as output:
            for name, data in self.payload.items():
                output.writestr(name, data)
        self.data["archive_sha256"] = sha(self.archive.read_bytes())
        self.save()
        with self.assertRaisesRegex(ValueError, "extension platforms"):
            self.resolve()

    def test_wrong_platform_and_machine_rejected(self):
        for key, wrong in (("platform_system", "Linux" if platform.system() == "Windows" else "Windows"),
                           ("platform_machine", "not-this-machine")):
            with self.subTest(key=key):
                old = self.data[key]
                self.data[key] = wrong
                self.save()
                with self.assertRaisesRegex(ValueError, "platform"):
                    self.resolve()
                self.data[key] = old
        self.save()

    def test_missing_runtime_launcher_and_harness_rejected(self):
        for path in (self.runtime, self.launcher, self.harness):
            with self.subTest(path=path.name):
                content = path.read_bytes()
                path.unlink()
                with self.assertRaises(ValueError):
                    self.resolve()
                path.write_bytes(content)

    def test_optional_runtime_executable_hash_verified(self):
        self.data["runtime"]["executable_sha256"] = sha(self.runtime.read_bytes())
        self.save()
        self.assertEqual(self.resolve()["runtime"]["executable_sha256"],
                         self.data["runtime"]["executable_sha256"])
        self.runtime.write_bytes(b"changed executable bytes")
        with self.assertRaisesRegex(ValueError, "runtime.executable_sha256 SHA-256"):
            self.resolve()

    def test_archive_launcher_and_harness_hashes_rejected(self):
        for path in (self.archive, self.launcher, self.harness):
            with self.subTest(path=path.name):
                content = path.read_bytes()
                path.write_bytes(content + b"changed")
                with self.assertRaisesRegex(ValueError, "SHA-256"):
                    self.resolve()
                path.write_bytes(content)

    def test_manifest_cannot_attest_different_harness(self):
        other = self.root / "other-harness.py"
        other.write_bytes(self.harness.read_bytes())
        self.data["harness_path"] = str(other)
        self.save()
        with self.assertRaisesRegex(ValueError, "harness_path"):
            self.resolve()

    def test_manifest_payload_must_match_archive(self):
        (self.addon / "LICENSE").write_bytes(b"mutated install")
        self.data["payload_sha256"]["LICENSE"] = sha(b"mutated install")
        self.save()
        with self.assertRaisesRegex(ValueError, "archive payload"):
            self.resolve()

    def test_archive_unexpected_entry_rejected(self):
        with zipfile.ZipFile(self.archive, "a") as output:
            output.writestr("extra.txt", "unexpected")
        self.data["archive_sha256"] = sha(self.archive.read_bytes())
        self.save()
        with self.assertRaisesRegex(ValueError, "archive payload"):
            self.resolve()

    def test_archive_path_escape_rejected(self):
        with zipfile.ZipFile(self.archive, "a") as output:
            output.writestr("../escape.py", "unsafe")
        self.data["archive_sha256"] = sha(self.archive.read_bytes())
        self.save()
        with self.assertRaisesRegex(ValueError, "relative"):
            self.resolve()

    def test_declared_extension_version_must_match_payload(self):
        self.data["extension_version"] = "9.9.9"
        self.save()
        with self.assertRaisesRegex(ValueError, "extension_version"):
            self.resolve()

    def test_relative_paths_and_wrong_addon_name_rejected(self):
        for key in ("addon_dir", "archive_path", "launcher_path", "harness_path"):
            with self.subTest(key=key):
                old = self.data[key]
                self.data[key] = "relative/path"
                self.save()
                with self.assertRaisesRegex(ValueError, "absolute"):
                    self.resolve()
                self.data[key] = old
        other = self.addon.with_name("not-sith")
        self.addon.rename(other)
        self.data["addon_dir"] = str(other)
        self.save()
        with self.assertRaisesRegex(ValueError, "named sith"):
            self.resolve()

    def test_exact_blender_regression_argv(self):
        output = self.root / "results"
        result = self.resolve(output)
        self.assertEqual(result["regression_argv"], [
            str(Path(sys.executable).absolute()), "-B", str(self.launcher),
            "--addon", str(self.addon), "--blender", str(self.runtime),
            "--output", str(output), "--threads", "2", "--timeout", "300"])
        self.assertFalse(output.exists())

    def test_exact_python_regression_argv_and_bpy_site(self):
        site = self.root / "bpy-dependencies"
        site.mkdir()
        self.data["runtime"].update(route="python", bpy_site=str(site))
        self.save()
        output = self.root / "results"
        self.assertEqual(self.resolve(output)["regression_argv"], [
            str(Path(sys.executable).absolute()), "-B", str(self.launcher),
            "--addon", str(self.addon), "--python", str(self.runtime),
            "--bpy-site", str(site), "--output", str(output),
            "--threads", "2", "--timeout", "300"])

    def test_invalid_runtime_and_relative_output_rejected(self):
        with self.assertRaisesRegex(ValueError, "absolute"):
            self.resolve(Path("relative-results"))
        self.data["runtime"]["executable"] = "blender"
        self.save()
        with self.assertRaisesRegex(ValueError, "absolute"):
            self.resolve()
        self.data["runtime"]["executable"] = str(self.runtime)
        self.data["runtime"]["route"] = "ambient"
        self.save()
        with self.assertRaisesRegex(ValueError, "route"):
            self.resolve()

    def test_runtime_symlink_spelling_preserves_virtualenv_route(self):
        link = self.root / "venv" / "bin" / "python"
        link.parent.mkdir(parents=True)
        try:
            link.symlink_to(self.runtime)
        except OSError as exc:
            self.skipTest(f"Host cannot create symlinks: {exc}")
        self.data["runtime"].update(route="python", executable=str(link))
        self.save()
        result = self.resolve(self.root / "results")
        self.assertEqual(result["runtime"]["executable"], str(link))
        position = result["regression_argv"].index("--python")
        self.assertEqual(result["regression_argv"][position + 1], str(link))

    def test_cli_explicit_manifest_and_exact_argv(self):
        output = self.root / "results"
        stdout = io.StringIO()
        with mock.patch.object(Path, "home", return_value=self.root / "unconfigured-home"):
            with contextlib.redirect_stdout(stdout):
                self.assertEqual(resolver.main([
                    "--manifest", str(self.manifest), "--regression-output", str(output)]), 0)
        self.assertEqual(json.loads(stdout.getvalue()), self.resolve(output))

    def test_default_manifest_and_missing_default_no_fallback(self):
        default = self.root / "home" / ".config" / "blender-sith" / "current-install.json"
        default.parent.mkdir(parents=True)
        default.write_bytes(self.manifest.read_bytes())
        with mock.patch.object(Path, "home", return_value=self.root / "home"):
            self.assertEqual(resolver.default_manifest(), default)
            self.assertEqual(resolver.resolve_install()["manifest_path"], str(default))
            default.unlink()
            with self.assertRaises(ValueError):
                resolver.resolve_install()


if __name__ == "__main__":
    unittest.main()
