#!/usr/bin/env python3
"""Build deterministic public ZIPs using the exact RELEASE_FILES.txt allowlist."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = "1.1.0"
RESEARCH_REVISION = 2026093001


def selected_files(root):
    entries = (root / "RELEASE_FILES.txt").read_text(encoding="utf-8").splitlines()
    files = []
    seen = set()
    for name in entries:
        if not name or name.startswith("#"):
            continue
        pure = PurePosixPath(name)
        if pure.is_absolute() or "\\" in name or ":" in name or any(p in (".", "..", "") for p in name.split("/")):
            raise ValueError("Unsafe allowlist path: " + name)
        if name.casefold() in seen:
            raise ValueError("Duplicate/case-colliding allowlist entry: " + name)
        seen.add(name.casefold())
        path = root
        for part in pure.parts:
            path = path / part
            mode = path.lstat()
            if stat.S_ISLNK(mode.st_mode) or getattr(mode, "st_file_attributes", 0) & 0x400:
                raise ValueError("Linked/reparse source refused: " + name)
        if not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
            raise ValueError("Missing or escaped source: " + name)
        files.append((name, path.read_bytes()))
    if not files:
        raise ValueError("Empty release allowlist")
    return sorted(files)


def archive(path, files, prefix):
    manifest = [{"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
                for name, data in files]
    members = files + [("PACKAGE-MANIFEST.json", (json.dumps({"version": VERSION, "files": manifest}, indent=2) + "\n").encode())]
    if path.exists():
        raise ValueError("Refusing to replace an existing archive; choose a fresh output directory")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name, data in sorted(members):
            info = zipfile.ZipInfo(prefix + "/" + name, (2026, 9, 30, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            z.writestr(info, data)
    with zipfile.ZipFile(path) as z:
        for name, data in members:
            if z.read(prefix + "/" + name) != data:
                raise ValueError("ZIP readback mismatch")
    return {"name": path.name, "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "source_files": len(files)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    files = selected_files(ROOT)
    args.output.mkdir(parents=True, exist_ok=True)
    skill_prefix = "skills/jk-mots-model-workflow/"
    skill = [(name[len(skill_prefix):], data) for name, data in files if name.startswith(skill_prefix)]
    skill += [(name, data.replace(b"skills/jk-mots-model-workflow/", b"") if name == "CREDITS.md" else data)
              for name, data in files if name in ("LICENSE", "CREDITS.md")]
    # One complete download includes a copyable skill with its baseline/notices.
    skill_manifest = {"version": VERSION, "files": [{"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
                                                     for name, data in skill]}
    full = list(files) + [(skill_prefix + name, data) for name, data in skill if name in ("LICENSE", "CREDITS.md")]
    full.append((skill_prefix + "PACKAGE-MANIFEST.json", (json.dumps(skill_manifest, indent=2) + "\n").encode()))
    receipts = [archive(args.output / f"JK-MotS-Model-Workflow-{VERSION}.zip", full, f"JK-MotS-Model-Workflow-{VERSION}")]
    research = {"schema_version": 1, "scope": "research-only", "version": VERSION,
                "requires_skill_version": VERSION, "research_revision": RESEARCH_REVISION,
                "files": [{"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
                          for name, data in skill if name.startswith("references/") and name.endswith((".md", ".json"))]}
    research_bytes = (json.dumps(research, indent=2) + "\n").encode()
    (args.output / "research-updates.json").write_bytes(research_bytes)
    research_receipt = {"name": "research-updates.json", "bytes": len(research_bytes), "sha256": hashlib.sha256(research_bytes).hexdigest()}
    (args.output / "SHA256SUMS.txt").write_text("".join(f"{r['sha256']}  {r['name']}\n" for r in receipts + [research_receipt]), encoding="utf-8")
    (args.output / "release-manifest.json").write_text(json.dumps({"version": VERSION, "artifacts": receipts, "research_manifest": research_receipt}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipts, indent=2))


if __name__ == "__main__":
    main()
