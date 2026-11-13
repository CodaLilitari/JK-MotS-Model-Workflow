"""Synthetic Blender-Sith export observations; no game files or model assets.

Run in a fresh background Blender process, or Python with an existing bpy
installation. The output directory must not exist. Exit 0 means the probes
completed, not that the add-on is defect-free. --require-fixed returns 1 when
any known defect remains. Deliberate rejection of an unapplied modifier is
reported separately from silently exporting its base mesh. No add-on file or
desktop preference is changed. This is not the full core/application test suite.
"""
from __future__ import annotations

import argparse
import contextlib
from datetime import datetime, timezone
import hashlib
import importlib
import importlib.util
import io
import json
from pathlib import Path
import sys


def source_hashes(folder):
    return {
        p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(folder.rglob("*"))
        if p.is_file() and "__pycache__" not in p.parts
        and p.suffix in (".py", ".toml")
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--addon", type=Path, required=True,
                        help="Package directory containing __init__.py and model/")
    parser.add_argument("--output", type=Path, required=True,
                        help="New directory for synthetic 3DO fixtures and JSON")
    parser.add_argument("--bpy-site", type=Path,
                        help="Optional existing dependency directory containing bpy")
    parser.add_argument("--require-fixed", action="store_true")
    argv = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else sys.argv[1:]
    args = parser.parse_args(argv)
    addon_dir = args.addon.resolve()
    if not (addon_dir / "__init__.py").is_file():
        parser.error("--addon must identify an extracted extension package")
    if args.bpy_site:
        sys.path.insert(0, str(args.bpy_site.resolve()))
    sys.dont_write_bytecode = True
    import bpy
    from mathutils import Vector
    if not bpy.app.background:
        parser.error("Run in a fresh background process, not an interactive scene")
    out_dir = args.output.resolve()
    out_dir.mkdir(parents=True, exist_ok=False)
    before = source_hashes(addon_dir)
    package_name = "sith_workflow_probe"
    spec = importlib.util.spec_from_file_location(
        package_name, addon_dir / "__init__.py",
        submodule_search_locations=[str(addon_dir)])
    addon = importlib.util.module_from_spec(spec)
    sys.modules[package_name] = addon
    spec.loader.exec_module(addon)
    addon.register()
    exporter = importlib.import_module(package_name + ".model.model3doExporter")
    loader = importlib.import_module(package_name + ".model.model3doLoader")
    report = {
        "schema": "blender-sith-synthetic-probes-v2",
        "utc": datetime.now(timezone.utc).isoformat(),
        "blender": bpy.app.version_string,
        "python": sys.version,
        "scope": "Synthetic fixtures only; no animation/game/MAT compatibility verdict",
        "addon_files_sha256": before,
        "exporter_module": exporter.__file__,
        "loader_module": loader.__file__,
        "harness_completed": False,
        "tests": {},
    }
    tests = report["tests"]
    try:
        # Reset only this disposable process, never an open artist scene.
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False)
        vertices = [(0,0,0),(1,0,0),(0,1,0),(0,0,0),(0,0,1),(1,0,0)]
        mesh = bpy.data.meshes.new("splitprobe")
        mesh.from_pydata(vertices, [], [(0,1,2),(3,4,5)])
        mesh.update()
        obj = bpy.data.objects.new("splitprobe", mesh)
        bpy.context.scene.collection.objects.link(obj)
        obj.sith_model3do_hnode_idx = 0
        fixture = out_dir / "splitprobe.3do"
        exporter.export3do(obj, str(fixture), loader.Model3doFileVersion.Version2_1,
                          False, False, False)
        parsed, _ = loader.load3do(str(fixture))
        exported = parsed.geosets[0].meshes[0]
        wrong = []
        for face_id, face in enumerate(exported.faces):
            original = mesh.polygons[face_id]
            for source_id, target_id in zip(original.vertices, face.vertexIdxs):
                expected = Vector(mesh.vertices[source_id].normal)
                actual = Vector(tuple(exported.normals[target_id]))
                if (expected-actual).length > 1e-6:
                    wrong.append({"face":face_id,"input_vertex":source_id,
                                  "export_vertex":target_id,
                                  "expected":list(expected),"actual":list(actual)})
        tests["split_normals"] = {
            "input_vertices":len(mesh.vertices),
            "output_vertices":len(exported.vertices),
            "wrong_normal_corners":len(wrong), "details":wrong,
            "defect_observed":bool(wrong),
            "fixture_sha256":hashlib.sha256(fixture.read_bytes()).hexdigest(),
        }
        root = bpy.data.objects.new("sharedroot", None)
        bpy.context.scene.collection.objects.link(root)
        native_root = bpy.data.objects.new("sharedjoint", None)
        bpy.context.scene.collection.objects.link(native_root)
        native_root.parent = root
        native_root.sith_model3do_hnode_idx = 0
        obj.parent = native_root
        obj.sith_model3do_hnode_idx = 1
        second = bpy.data.objects.new("sharedcopy", mesh)
        bpy.context.scene.collection.objects.link(second)
        second.parent = native_root
        second.location = (2,0,0)
        second.sith_model3do_hnode_idx = 2
        shared = exporter.makeModel3doFromObj("shared.3do",root,sync_mesh_list=False)
        tests["shared_mesh"] = {
            "input_mesh_datablocks":1, "input_mesh_objects":2,
            "output_meshes":len(shared.geosets[0].meshes),
            "output_nodes":len(shared.meshHierarchy),
            "defect_observed":len(shared.geosets[0].meshes)!=1,
        }
        errors = io.StringIO()
        prefixed = {"assignment_returned":False}
        try:
            with contextlib.redirect_stderr(errors):
                bpy.context.scene.sith_key_types = "0xFFFF"
            prefixed = {"assignment_returned":True,
                        "readback":bpy.context.scene.sith_key_types}
        except Exception as exc:
            prefixed["exception"] = type(exc).__name__ + ": " + str(exc)
        bpy.context.scene.sith_key_types = "FFFF"
        tests["key_metadata"] = {
            "prefixed_assignment":prefixed,
            "canonical_readback":bpy.context.scene.sith_key_types,
            "callback_reported_error":bool(errors.getvalue()),
            "defect_observed":bool(errors.getvalue()) or not prefixed["assignment_returned"],
            "interpretation":"Metadata callback only; no animation failure inferred",
        }
        bpy.ops.mesh.primitive_cube_add()
        cube = bpy.context.active_object
        cube.name = "modifierprobe"
        cube.sith_model3do_hnode_idx = 0
        mod = cube.modifiers.new("ProbeSubdivision", "SUBSURF")
        mod.subdivision_type = "SIMPLE"
        mod.levels = mod.render_levels = 1
        bpy.context.view_layer.update()
        evaluated_obj = cube.evaluated_get(bpy.context.evaluated_depsgraph_get())
        evaluated_mesh = evaluated_obj.to_mesh()
        try:
            expected = {"vertices":len(evaluated_mesh.vertices),
                        "faces":len(evaluated_mesh.polygons)}
        finally:
            evaluated_obj.to_mesh_clear()
        rejection = None
        actual = None
        try:
            model = exporter.makeModel3doFromObj("modifier.3do",cube,sync_mesh_list=False)
        except ValueError as exc:
            # Only the expected policy rejection completes this observation.
            # An unrelated export failure must retain a failed harness receipt.
            if str(exc) != f"Apply visible mesh modifiers on '{cube.name}' before 3DO export":
                raise
            rejection = str(exc)
        else:
            exported = model.geosets[0].meshes[0]
            actual = {"vertices":len(exported.vertices),"faces":len(exported.faces)}
        tests["unapplied_modifier"] = {
            "base":{"vertices":len(cube.data.vertices),"faces":len(cube.data.polygons)},
            "evaluated":expected,"exported":actual,
            "outcome":"rejected_unapplied_modifier" if rejection else "exported",
            "rejection":rejection,
            "modifier_retained_on_source":len(cube.modifiers)==1,
            "defect_observed":rejection is None and actual!=expected,
        }
        report["harness_completed"] = True
    finally:
        report["addon_source_unchanged"] = source_hashes(addon_dir)==before
        report["known_defect_count"] = sum(bool(v["defect_observed"]) for v in tests.values())
        (out_dir / "probe-results.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    if not report["addon_source_unchanged"]:
        raise RuntimeError("Add-on source hashes changed during the probe")
    print(json.dumps({k:report[k] for k in
                      ("blender","harness_completed","known_defect_count","addon_source_unchanged")},indent=2))
    return 1 if args.require_fixed and report["known_defect_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
