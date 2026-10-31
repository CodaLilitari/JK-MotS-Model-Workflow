#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Import a JK/MotS 3DO through the Blender-Sith fork and render inspection views headlessly.

This follows Coda's direct-import recipe (references/blender-sith-fork.md): the
fork's own `sith.model.import3do`, a disposable background process, exact MAT
and CMP inputs, and a receipt of what actually ran. Rendering is Red's addition
for Claude's cloud workspace, where Blender's `bpy` module runs without a GPU.

    python render_3do.py MODEL.3do --fork-root FORK --out NEW_DIR [--mat-dir DIR ...] [--cmp FILE]
        [--views front,right,rear,three-quarter] [--size 1280x960] [--samples 32]
        [--ortho] [--flat] [--transparent] [--save-blend] [--no-render] [--no-uv-absolute]

FORK is the directory containing `sith/__init__.py` (a job-local copy of Coda's
Blender-Sith Agentic checkout, never her working tree). Run with a Python that
imports `bpy` 5.x (`bpy.app.background` must be true).

Outputs in NEW_DIR (must not exist): one PNG per view, receipt.json, import.log
and, with --save-blend, imported-unaltered.blend saved before any presentation
change. Exit 0 = imported (and rendered, unless --no-render); 1 = imported with
findings (missing MATs, placeholder materials, more geosets than the one imported);
2 = refused or failed.

Axis convention: Sith things look along +Y with +Z up, so "front" puts the camera
on +Y and "right" on +X. Confirm on the render; a model authored another way
will show it. The scene imports geoset 0 only. A render shows the imported
geoset under recorded presentation settings, not engine lighting, animation or
any LOD other than 0.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import math
import sys
from pathlib import Path
from typing import Any

VIEWS = {
    # name: (camera direction from the model's centre, up vector)
    "front": ((0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
    "rear": ((0.0, -1.0, 0.0), (0.0, 0.0, 1.0)),
    "right": ((1.0, 0.0, 0.0), (0.0, 0.0, 1.0)),
    "left": ((-1.0, 0.0, 0.0), (0.0, 0.0, 1.0)),
    "top": ((0.0, 0.0, 1.0), (0.0, 1.0, 0.0)),
    "three-quarter": ((0.62, 0.78, 0.42), (0.0, 0.0, 1.0)),
    "rear-three-quarter": ((-0.62, -0.78, 0.42), (0.0, 0.0, 1.0)),
}


class RenderError(Exception):
    pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fork_hashes(fork_root: Path) -> dict[str, str]:
    return {p.relative_to(fork_root).as_posix(): sha256_file(p)
            for p in sorted((fork_root / "sith").rglob("*"))
            if p.is_file() and p.suffix in (".py", ".toml") and "__pycache__" not in p.parts}


def parse_size(text: str) -> tuple[int, int]:
    try:
        w, h = (int(v) for v in text.lower().split("x"))
    except ValueError:
        raise RenderError(f"--size must look like 1280x960: {text!r}") from None
    if not (16 <= w <= 8192 and 16 <= h <= 8192):
        raise RenderError("--size out of range (16..8192)")
    return w, h


def resolve_materials(names: list[str], search_dirs: list[str], get_path) -> list[dict[str, Any]]:
    """Mirror the importer's ordered search and record every candidate, so collisions are visible."""
    report = []
    for name in names:
        candidates = []
        for folder in search_dirs:
            found = get_path(name, folder)
            if found:
                candidates.append(str(Path(found).resolve()))
        unique = list(dict.fromkeys(candidates))
        entry: dict[str, Any] = {"name": name, "search_order": search_dirs, "candidates": unique,
                                 "selected": unique[0] if unique else None}
        if unique:
            entry["sha256"] = sha256_file(Path(unique[0]))
            if len(unique) > 1:
                entry["collision"] = "several folders hold this name; the first in search order was used"
        else:
            entry["missing"] = True
        report.append(entry)
    return report


def scene_bounds(bpy, mathutils) -> tuple[Any, float]:
    points = [o.matrix_world @ mathutils.Vector(corner)
              for o in bpy.context.scene.objects if o.type == "MESH" for corner in o.bound_box]
    if not points:
        raise RenderError("the import produced no mesh objects to render")
    lo = mathutils.Vector((min(p.x for p in points), min(p.y for p in points), min(p.z for p in points)))
    hi = mathutils.Vector((max(p.x for p in points), max(p.y for p in points), max(p.z for p in points)))
    return (lo + hi) / 2.0, max((hi - lo).length / 2.0, 1e-4)


def mesh_summary(bpy) -> tuple[list[dict[str, Any]], list[str]]:
    meshes, placeholders = [], set()
    for obj in sorted(bpy.context.scene.objects, key=lambda o: o.name):
        if obj.type != "MESH":
            continue
        mats = []
        for slot in obj.material_slots:
            mat = slot.material
            if mat is None:
                continue
            has_image = bool(mat.node_tree is not None and any(
                n.type == "TEX_IMAGE" and n.image is not None for n in mat.node_tree.nodes))
            mats.append({"name": mat.name, "has_image": has_image})
            if not has_image:
                placeholders.add(mat.name)
        meshes.append({"object": obj.name, "parent": obj.parent.name if obj.parent else None,
                       "vertices": len(obj.data.vertices), "faces": len(obj.data.polygons),
                       "uv_layers": [uv.name for uv in obj.data.uv_layers], "materials": mats})
    return meshes, sorted(placeholders)


def flat_copies(bpy) -> list[str]:
    """Presentation-only: texture colour as emission on material copies, like a fully-lit game face."""
    changed = []
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH":
            continue
        for slot in obj.material_slots:
            mat = slot.material
            if mat is None or mat.node_tree is None:
                continue
            image_nodes = [n for n in mat.node_tree.nodes if n.type == "TEX_IMAGE" and n.image is not None]
            if not image_nodes:
                continue
            copy = mat.copy()
            copy.name = mat.name + ".flat"
            nodes, links = copy.node_tree.nodes, copy.node_tree.links
            tex = next(n for n in nodes if n.type == "TEX_IMAGE" and n.image is not None)
            out = next((n for n in nodes if n.type == "OUTPUT_MATERIAL"), None) or nodes.new("ShaderNodeOutputMaterial")
            emission = nodes.new("ShaderNodeEmission")
            links.new(tex.outputs["Color"], emission.inputs["Color"])
            links.new(emission.outputs["Emission"], out.inputs["Surface"])
            slot.material = copy
            changed.append(copy.name)
    return sorted(set(changed))


def add_camera(bpy, mathutils, name: str, center, radius: float, direction, up, ortho: bool,
               aspect: float) -> dict[str, Any]:
    cam_data = bpy.data.cameras.new(name)
    cam = bpy.data.objects.new(name, cam_data)
    bpy.context.scene.collection.objects.link(cam)
    d = mathutils.Vector(direction).normalized()
    if ortho:
        cam_data.type = "ORTHO"
        cam_data.ortho_scale = 2.0 * radius * 1.12 * max(1.0, aspect)
        distance = radius * 4.0
    else:
        cam_data.lens = 50.0
        half_fov = math.atan((cam_data.sensor_width / 2.0) / cam_data.lens)
        if aspect < 1.0:
            half_fov = math.atan(math.tan(half_fov) * aspect)
        distance = radius * 1.12 / math.sin(half_fov)
    cam.location = center + d * distance
    forward = (center - cam.location).normalized()
    right = forward.cross(mathutils.Vector(up))
    if right.length < 1e-6:
        raise RenderError(f"view {name}: up vector is parallel to the viewing direction")
    right.normalize()
    true_up = right.cross(forward)
    # camera axes: X = image right, Y = image up, Z = backwards (cameras look along -Z)
    cam.rotation_euler = mathutils.Matrix((right, true_up, -forward)).transposed().to_euler()
    cam_data.clip_start = max(distance - radius * 3.0, radius * 0.001)
    cam_data.clip_end = distance + radius * 3.0
    return {"camera_location": [round(v, 6) for v in cam.location], "looks_at": [round(v, 6) for v in center],
            "direction_from_model": list(direction), "up": list(up), "type": cam_data.type,
            "lens_mm": None if ortho else cam_data.lens,
            "ortho_scale": round(cam_data.ortho_scale, 6) if ortho else None}


def add_lights(bpy) -> list[dict[str, Any]]:
    rig = [("key", (0.75, 0.25, 0.55), 3.0), ("fill", (0.95, 0.0, -0.9), 1.2), ("rim", (2.3, 0.0, 3.1), 1.5)]
    out = []
    for name, rotation, energy in rig:
        light = bpy.data.objects.new(name, bpy.data.lights.new(name, "SUN"))
        light.data.energy = energy
        light.rotation_euler = rotation
        bpy.context.scene.collection.objects.link(light)
        out.append({"name": name, "type": "SUN", "rotation_euler": list(rotation), "energy": energy})
    return out


def run(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    sys.dont_write_bytecode = True
    model = Path(args.model).expanduser().resolve()
    fork_root = Path(args.fork_root).expanduser().resolve()
    out = Path(args.out).expanduser().resolve()
    if not model.is_file():
        raise RenderError(f"model not found: {model}")
    if not (fork_root / "sith" / "__init__.py").is_file():
        raise RenderError("--fork-root must contain sith/__init__.py")
    if out.exists():
        raise RenderError(f"output directory exists: {out}")
    if not out.parent.is_dir():
        raise RenderError(f"output parent does not exist: {out.parent}")
    mat_dirs = [Path(d).expanduser().resolve() for d in (args.mat_dir or [])]
    for d in mat_dirs:
        if not d.is_dir():
            raise RenderError(f"--mat-dir is not a directory: {d}")
    cmp_path = Path(args.cmp).expanduser().resolve() if args.cmp else None
    if cmp_path is not None and not cmp_path.is_file():
        raise RenderError(f"--cmp not found: {cmp_path}")
    width, height = parse_size(args.size)
    views = [v.strip() for v in args.views.split(",") if v.strip()]
    unknown = [v for v in views if v not in VIEWS]
    if unknown:
        raise RenderError(f"unknown views {unknown}; choose from {', '.join(VIEWS)}")

    before = fork_hashes(fork_root)
    sys.path.insert(0, str(fork_root))
    import bpy  # noqa: E402
    import mathutils  # noqa: E402
    import sith  # noqa: E402
    from sith.model import import3do, model3doImporter, model3doLoader  # noqa: E402
    from sith.utils import getDefaultMatFolders, getFilePathInDir  # noqa: E402

    if not bpy.app.background:
        raise RenderError("run in a disposable background process (bpy.app.background is false)")
    if Path(sith.__file__).resolve() != fork_root / "sith" / "__init__.py":
        raise RenderError(f"imported sith from {sith.__file__}, not the requested fork root")

    out.mkdir()
    receipt: dict[str, Any] = {
        "schema": "red-jk-model/render-3do/v1",
        "python": sys.executable,
        "bpy_module": bpy.__file__,
        "blender": bpy.app.version_string,
        "sith_module": sith.__file__,
        "importer_module": model3doImporter.__file__,
        "fork_source_sha256": before,
        "model": {"path": str(model), "sha256": sha256_file(model)},
        "cmp": {"path": str(cmp_path), "sha256": sha256_file(cmp_path)} if cmp_path else None,
        "mat_dirs": [str(d) for d in mat_dirs],
        "findings": [],
        "adaptations": [],
    }
    sith.register()
    native, file_version = model3doLoader.load3do(str(model))
    receipt["native"] = {
        "file_version": str(file_version),
        "geosets": len(native.geosets),
        "scene_geoset": 0,
        "hierarchy_nodes": len(native.meshHierarchy),
        "materials": list(native.materials),
        "geoset0_meshes": len(native.geosets[0].meshes) if native.geosets else 0,
    }
    if len(native.geosets) > 1:
        receipt["findings"].append(f"{len(native.geosets)} geosets; only geoset 0 is imported and shown. "
                                   "Inspect the others separately.")
    search = [str(Path(p).resolve()) for p in getDefaultMatFolders(str(model))] + [str(d) for d in mat_dirs]
    receipt["materials"] = resolve_materials(list(native.materials), search, getFilePathInDir)
    missing = [m["name"] for m in receipt["materials"] if m.get("missing")]
    if missing:
        receipt["findings"].append(f"MAT files not found for {missing}; the importer leaves placeholders")
    collisions = [m["name"] for m in receipt["materials"] if m.get("collision")]
    if collisions:
        receipt["findings"].append(f"MAT name collisions for {collisions}; check which file was used")
    if str(file_version).endswith("2_1") and cmp_path is None and native.materials:
        receipt["findings"].append("3DO 2.1 imported without an explicit --cmp; the importer may fall back "
                                   "to a default or found palette, and indexed MATs can look wrong")

    import_options = dict(mat_dirs=[str(d) for d in mat_dirs], cmp_file=str(cmp_path) if cmp_path else "",
                          uvAbsolute_2_1=not args.no_uv_absolute, importVertexColors=True,
                          importRadiusObj=False, preserveOrder=True, clearScene=True)
    log = io.StringIO()
    with contextlib.redirect_stdout(log):
        root = import3do(str(model), **import_options)
    (out / "import.log").write_text(log.getvalue(), encoding="utf-8")
    receipt["import_options"] = import_options
    if root is None:
        raise RenderError("the importer produced no model root (see import.log)")
    bpy.context.view_layer.update()
    meshes, placeholders = mesh_summary(bpy)
    receipt["scene"] = {"root": root.name, "meshes": meshes,
                        "total_vertices": sum(m["vertices"] for m in meshes),
                        "total_faces": sum(m["faces"] for m in meshes)}
    if placeholders:
        receipt["findings"].append(f"materials without a loaded image (placeholders): {placeholders}")
    if args.save_blend:
        path = out / "imported-unaltered.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(path), copy=True)
        receipt["unaltered_blend"] = {"file": path.name, "sha256": sha256_file(path)}

    if not args.no_render:
        scene = bpy.context.scene
        if args.flat:
            receipt["adaptations"].append({"flat_emission_material_copies": flat_copies(bpy),
                                           "reason": "texture colour without scene lighting (presentation only)"})
        center, radius = scene_bounds(bpy, mathutils)
        receipt["bounds"] = {"center": [round(v, 6) for v in center], "radius": round(radius, 6)}
        receipt["lights"] = add_lights(bpy)
        world = bpy.data.worlds.new("inspection-world")
        world.color = (0.18, 0.18, 0.2)
        scene.world = world
        scene.render.engine = "CYCLES"
        scene.cycles.device = "CPU"
        scene.cycles.samples = args.samples
        scene.render.resolution_x, scene.render.resolution_y = width, height
        scene.render.resolution_percentage = 100
        scene.render.film_transparent = bool(args.transparent)
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_mode = "RGBA" if args.transparent else "RGB"
        receipt["render"] = {"engine": "CYCLES", "device": "CPU", "samples": args.samples,
                             "size": [width, height], "transparent": bool(args.transparent),
                             "orthographic_axis_views": bool(args.ortho), "views": []}
        aspect = width / height
        for view in views:
            direction, up = VIEWS[view]
            ortho = args.ortho and view not in ("three-quarter", "rear-three-quarter")
            info = add_camera(bpy, mathutils, f"cam-{view}", center, radius, direction, up, ortho, aspect)
            scene.camera = bpy.data.objects[f"cam-{view}"]
            target = out / f"{model.stem}-{view}.png"
            scene.render.filepath = str(target)
            with contextlib.redirect_stdout(io.StringIO()):
                bpy.ops.render.render(write_still=True)
            receipt["render"]["views"].append({"view": view, "file": target.name, "sha256": sha256_file(target), **info})

    after = fork_hashes(fork_root)
    receipt["fork_source_unchanged"] = after == before
    if after != before:
        receipt["findings"].append("fork source files changed during the run")
    receipt["limits"] = [
        "Geoset 0 only; other geosets and LODs are not shown.",
        "Inspection lighting, not engine lighting; no animation, no runtime or multiplayer evidence.",
        "Material appearance depends on the MAT/CMP actually resolved; see materials and import.log.",
    ]
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return (1 if receipt["findings"] else 0), receipt


def main(argv: list[str] | None = None) -> int:
    raw = sys.argv[sys.argv.index("--") + 1:] if argv is None and "--" in sys.argv else argv
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("model")
    parser.add_argument("--fork-root", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--mat-dir", action="append")
    parser.add_argument("--cmp")
    parser.add_argument("--views", default="front,right,rear,three-quarter")
    parser.add_argument("--size", default="1280x960")
    parser.add_argument("--samples", type=int, default=32)
    parser.add_argument("--ortho", action="store_true", help="orthographic cameras for the axis views")
    parser.add_argument("--flat", action="store_true", help="also show texture colour unlit (material copies)")
    parser.add_argument("--transparent", action="store_true")
    parser.add_argument("--save-blend", action="store_true", help="save the unaltered import before presentation")
    parser.add_argument("--no-render", action="store_true")
    parser.add_argument("--no-uv-absolute", action="store_true", help="pass uvAbsolute_2_1=False to the importer")
    args = parser.parse_args(raw)
    try:
        code, receipt = run(args)
    except (RenderError, OSError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": f"{type(exc).__name__}: {exc}"}), file=sys.stderr)
        return 2
    summary = {"ok": True, "findings": receipt["findings"], "out": str(Path(args.out).resolve()),
               "native": receipt["native"], "faces": receipt["scene"]["total_faces"],
               "views": [v["file"] for v in receipt.get("render", {}).get("views", [])]}
    print(json.dumps(summary, indent=2))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
