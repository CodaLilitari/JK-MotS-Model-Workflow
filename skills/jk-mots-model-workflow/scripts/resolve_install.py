#!/usr/bin/env python3
"""Verify the shared current Blender-Sith install; emit JSON, never run Blender.

Python 3.11+ is required. The private manifest is an explicit local selection,
not a release-discovery mechanism or a substitute for actual runtime receipts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import stat
import sys
import tomllib
import zipfile


def default_manifest():
    return Path.home() / ".config" / "blender-sith" / "current-install.json"


def digest_stream(stream):
    result = hashlib.sha256()
    for block in iter(lambda: stream.read(1024 * 1024), b""):
        result.update(block)
    return result.hexdigest()


def digest(path):
    with path.open("rb") as stream:
        return digest_stream(stream)


def nonempty(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a nonempty string")
    return value


def absolute_path(value, label, kind=None, *, preserve_symlink=False):
    path = Path(nonempty(str(value) if isinstance(value, Path) else value, label))
    if not path.is_absolute():
        raise ValueError(f"{label} must be an absolute path (no PATH fallback)")
    # A venv's bin/python may be a symlink: resolving it changes Python's prefix.
    path = Path(os.path.abspath(path)) if preserve_symlink else path.resolve()
    if kind == "file" and not path.is_file():
        raise ValueError(f"{label} is not an existing file: {path}")
    if kind == "directory" and not path.is_dir():
        raise ValueError(f"{label} is not an existing directory: {path}")
    return path


def sha256_value(value, label):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", value):
        raise ValueError(f"{label} must be a SHA-256 hex digest")
    return value.lower()


def checked_hash(path, value, label):
    expected = sha256_value(value, label)
    if digest(path) != expected:
        raise ValueError(f"{label} SHA-256 mismatch: {path}")
    return expected


def member_path(value):
    if (not isinstance(value, str) or not value or "\\" in value or ":" in value
            or "\x00" in value or value.startswith("/")
            or any(part in ("", ".", "..") for part in value.split("/"))
            or PurePosixPath(value).as_posix() != value):
        raise ValueError(f"payload member must be a safe relative POSIX path: {value!r}")
    return value


def bytecode(name):
    return PurePosixPath(name).suffix.lower() in (".pyc", ".pyo")


def expected_payload(value):
    if not isinstance(value, dict) or not value:
        raise ValueError("payload_sha256 must contain every package file")
    result, folded = {}, set()
    for name, checksum in value.items():
        member_path(name)
        if name.casefold() in folded or bytecode(name):
            raise ValueError(f"payload has duplicate casing or packaged bytecode: {name}")
        folded.add(name.casefold())
        result[name] = sha256_value(checksum, f"payload_sha256[{name}]")
    if "__init__.py" not in result or "blender_manifest.toml" not in result:
        raise ValueError("payload must include __init__.py and blender_manifest.toml")
    return result


def compare_payload(actual, expected, label):
    missing = sorted(expected.keys() - actual.keys())
    extra = sorted(actual.keys() - expected.keys())
    changed = sorted(name for name in actual.keys() & expected.keys()
                     if actual[name] != expected[name])
    if missing or extra or changed:
        raise ValueError(f"{label} mismatch; missing={missing}, extra={extra}, changed={changed}")


def archive_payload(archive):
    result, names = {}, set()
    with zipfile.ZipFile(archive) as source:
        for item in source.infolist():
            name = member_path(item.filename[:-1] if item.is_dir() else item.filename)
            if name.casefold() in names:
                raise ValueError(f"archive payload duplicate member: {name}")
            names.add(name.casefold())
            mode = item.external_attr >> 16
            if stat.S_ISLNK(mode):
                raise ValueError(f"archive payload symlink is unsupported: {name}")
            if item.is_dir():
                continue
            with source.open(item) as stream:
                result[name] = digest_stream(stream)
    return result


def generated_cache(name, expected):
    path = PurePosixPath(name)
    match = re.fullmatch(r"(.+)\.cpython-[0-9]+(?:\.opt-[0-9]+)?\.pyc", path.name)
    return (path.parent.name == "__pycache__" and match is not None
            and (path.parent.parent / (match[1] + ".py")).as_posix() in expected)


def installed_payload(addon, expected):
    result, ignored = {}, []
    for path in addon.rglob("*"):
        if path.is_symlink() or getattr(path, "is_junction", lambda: False)():
            raise ValueError(f"installed payload must not contain links: {path}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError(f"installed payload contains a non-file: {path}")
        name = member_path(path.relative_to(addon).as_posix())
        # Only source-paired CPython caches are excluded, never sourceless code.
        if generated_cache(name, expected):
            ignored.append(name)
        else:
            result[name] = digest(path)
    return result, sorted(ignored)


def resolve_install(manifest_path=None, *, regression_output=None):
    """Resolve one explicit manifest. No discovery, imports, writes or execution."""
    manifest = absolute_path(default_manifest() if manifest_path is None else manifest_path,
                             "manifest", "file")
    data = json.loads(manifest.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict) or type(data.get("schema_version")) is not int or data["schema_version"] != 1:
        raise ValueError("manifest schema_version must be 1")
    release = nonempty(data.get("release_tag"), "release_tag")
    version = nonempty(data.get("extension_version"), "extension_version")
    system = data.get("platform_system")
    machine = nonempty(data.get("platform_machine"), "platform_machine")
    if system not in ("Windows", "Linux") or system != platform.system():
        raise ValueError("manifest platform_system does not match this Windows/Linux host")
    if machine.casefold() != platform.machine().casefold():
        raise ValueError("manifest platform_machine does not match this host")
    addon = absolute_path(data.get("addon_dir"), "addon_dir", "directory")
    if addon.name != "sith" or not (addon / "__init__.py").is_file():
        raise ValueError("addon_dir must be named sith and contain __init__.py")
    archive = absolute_path(data.get("archive_path"), "archive_path", "file")
    archive_hash = checked_hash(archive, data.get("archive_sha256"), "archive_sha256")
    expected = expected_payload(data.get("payload_sha256"))
    compare_payload(archive_payload(archive), expected, "archive payload")
    installed, ignored_cache = installed_payload(addon, expected)
    compare_payload(installed, expected, "installed payload")
    extension = tomllib.loads((addon / "blender_manifest.toml").read_text(encoding="utf-8"))
    if extension.get("id") != "sith" or extension.get("version") != version:
        raise ValueError("extension id/version does not match sith and extension_version")
    supported = extension.get("platforms")
    architecture = {"amd64": "x64", "x86_64": "x64", "arm64": "arm64", "aarch64": "arm64"}.get(machine.casefold())
    if supported is not None and (not isinstance(supported, list)
            or f"{system.lower()}-{architecture}" not in supported):
        raise ValueError("extension platforms do not permit this host")

    runtime = data.get("runtime")
    if not isinstance(runtime, dict) or runtime.get("route") not in ("blender", "python"):
        raise ValueError("runtime.route must be blender or python")
    runtime = dict(runtime)
    runtime["executable"] = str(absolute_path(runtime.get("executable"), "runtime.executable", "file",
                                               preserve_symlink=True))
    if "executable_sha256" in runtime:
        runtime["executable_sha256"] = checked_hash(
            Path(runtime["executable"]), runtime["executable_sha256"], "runtime.executable_sha256")
    nonempty(runtime.get("version"), "runtime.version")
    if "bpy_site" in runtime:
        if runtime["route"] != "python":
            raise ValueError("runtime.bpy_site requires the python route")
        runtime["bpy_site"] = str(absolute_path(runtime["bpy_site"], "runtime.bpy_site", "directory"))
    launcher = absolute_path(data.get("launcher_path"), "launcher_path", "file")
    harness = absolute_path(data.get("harness_path"), "harness_path", "file")
    if harness != (launcher.parent.parent / "tests" / "background_regression.py").resolve():
        raise ValueError("harness_path must match the launcher's derived tests/background_regression.py")
    launcher_hash = checked_hash(launcher, data.get("launcher_sha256"), "launcher_sha256")
    harness_hash = checked_hash(harness, data.get("harness_sha256"), "harness_sha256")
    result = {
        "schema_version": 1, "status": "verified", "manifest_path": str(manifest),
        "release_tag": release, "extension_version": version,
        "platform_system": system, "platform_machine": machine,
        "addon_dir": str(addon), "source_root": str(addon.parent),
        "archive_path": str(archive), "archive_sha256": archive_hash,
        "payload_sha256": expected, "runtime": runtime,
        "ignored_generated_bytecode": ignored_cache,
        "launcher_path": str(launcher), "launcher_sha256": launcher_hash,
        "harness_path": str(harness), "harness_sha256": harness_hash,
        "runtime_executed": False,
    }
    if regression_output is not None:
        output = absolute_path(regression_output, "regression_output")
        python = absolute_path(sys.executable, "resolver Python", "file", preserve_symlink=True)
        argv = [str(python), "-B", str(launcher), "--addon", str(addon),
                "--" + runtime["route"], runtime["executable"]]
        if "bpy_site" in runtime:
            argv.extend(["--bpy-site", runtime["bpy_site"]])
        argv.extend(["--output", str(output), "--threads", "2", "--timeout", "300"])
        result["regression_argv"] = argv
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, help="Absolute private manifest; defaults to ~/.config/blender-sith/current-install.json")
    parser.add_argument("--regression-output", type=Path, help="Absolute new external output path; emit argv without executing it")
    args = parser.parse_args(argv)
    try:
        result = resolve_install(args.manifest, regression_output=args.regression_output)
    except (OSError, ValueError, zipfile.BadZipFile, RuntimeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
