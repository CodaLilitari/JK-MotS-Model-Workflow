"""Tests for render_3do.py.

Pure helpers run anywhere. The end-to-end tests need a Python with Blender's `bpy`
5.x (BPY_PYTHON, or the current interpreter if it imports bpy) and a copy of the
Blender-Sith fork (SITH_FORK_ROOT, the directory containing sith/__init__.py);
otherwise they are skipped.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import render_3do  # noqa: E402


def bpy_python() -> str | None:
    candidate = os.environ.get("BPY_PYTHON") or sys.executable
    probe = subprocess.run([candidate, "-c", "import bpy"], capture_output=True)
    return candidate if probe.returncode == 0 else None


FORK = os.environ.get("SITH_FORK_ROOT")
BPY = bpy_python() if FORK and Path(FORK, "sith", "__init__.py").is_file() else None

FIXTURE = r'''
import math, sys
import bpy
fork, out = sys.argv[1], sys.argv[2]
sys.dont_write_bytecode = True
sys.path.insert(0, fork)
import sith
sith.register()
from sith.model import export3do
from sith.model.model3doLoader import Model3doFileVersion
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()
bpy.ops.mesh.primitive_cone_add(radius1=0.2, depth=2.0, location=(0, 0, 0), rotation=(-math.pi / 2, 0, 0))
cone = bpy.context.object
bpy.ops.mesh.primitive_cube_add(size=1.2, location=(1.5, 0, 0))
cube = bpy.context.object
cone.select_set(True)
cube.select_set(True)
bpy.context.view_layer.objects.active = cone
bpy.ops.object.join()
obj = bpy.context.object
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
obj.name = "axisprobe"
obj.sith_model3do_hnode_idx = 0
export3do(obj, out, Model3doFileVersion.Version2_1, False, False, True)
'''

ALPHA = r'''
import json, sys
import bpy
img = bpy.data.images.load(sys.argv[1])
w, h = img.size
px = img.pixels[:]
mass = {"left": 0.0, "right": 0.0, "top": 0.0, "bottom": 0.0}
for y in range(h):
    for x in range(w):
        a = px[(y * w + x) * 4 + 3]
        mass["left" if x < w / 2 else "right"] += a
        mass["top" if y >= h / 2 else "bottom"] += a   # Blender rows run bottom to top
print(json.dumps(mass))
'''


class PureHelpers(unittest.TestCase):
    def test_parse_size(self) -> None:
        self.assertEqual(render_3do.parse_size("1280x960"), (1280, 960))
        for bad in ("12x12", "big", "99999x10"):
            with self.assertRaises(render_3do.RenderError):
                render_3do.parse_size(bad)

    def test_views_have_usable_up_vectors(self) -> None:
        for name, (direction, up) in render_3do.VIEWS.items():
            cross = (direction[1] * up[2] - direction[2] * up[1], direction[2] * up[0] - direction[0] * up[2],
                     direction[0] * up[1] - direction[1] * up[0])
            self.assertGreater(sum(c * c for c in cross), 1e-6, name)

    def test_material_resolution_records_order_and_collisions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp, "a"), Path(tmp, "b")
            a.mkdir()
            b.mkdir()
            (a / "x.mat").write_bytes(b"one")
            (b / "x.mat").write_bytes(b"two")
            (b / "y.mat").write_bytes(b"three")

            def get_path(name, folder):
                path = Path(folder, name)
                return str(path) if path.is_file() else None

            report = render_3do.resolve_materials(["x.mat", "y.mat", "z.mat"], [str(a), str(b)], get_path)
        x, y, z = report
        self.assertTrue(x["selected"].endswith("a/x.mat"))
        self.assertIn("collision", x)
        self.assertTrue(y["selected"].endswith("b/y.mat"))
        self.assertNotIn("collision", y)
        self.assertTrue(z.get("missing"))


@unittest.skipIf(BPY is None, "needs BPY_PYTHON (Blender bpy 5.x) and SITH_FORK_ROOT")
class EndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        cls.model = cls.root / "axisprobe.3do"
        subprocess.run([BPY, "-B", "-c", FIXTURE, FORK, str(cls.model)], check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def render(self, out: str, *extra: str) -> tuple[int, dict]:
        done = subprocess.run([BPY, "-B", str(HERE / "render_3do.py"), str(self.model), "--fork-root", FORK,
                               "--out", str(self.root / out), *extra], capture_output=True, text=True)
        receipt = self.root / out / "receipt.json"
        return done.returncode, (json.loads(receipt.read_text()) if receipt.is_file() else {"stderr": done.stderr})

    def mass(self, png: Path) -> dict:
        done = subprocess.run([BPY, "-B", "-c", ALPHA, str(png)], capture_output=True, text=True, check=True)
        return json.loads(done.stdout.strip().splitlines()[-1])

    def test_axis_convention_front_and_top(self) -> None:
        code, receipt = self.render("axes", "--views", "front,top", "--transparent", "--size", "160x120",
                                    "--samples", "1")
        self.assertEqual(code, 0, receipt)
        self.assertTrue(receipt["fork_source_unchanged"])
        files = {v["view"]: self.root / "axes" / v["file"] for v in receipt["render"]["views"]}
        front, top = self.mass(files["front"]), self.mass(files["top"])
        # the large cube sits at +X: image-left from the front (camera on +Y), image-right from the top
        self.assertGreater(front["left"], front["right"])
        self.assertGreater(top["right"], top["left"])
        # cone tip at +Y points up in the top view, so its wide base sits low
        self.assertGreater(top["bottom"], top["top"])

    def test_receipt_hashes_and_refusals(self) -> None:
        code, receipt = self.render("hashes", "--views", "three-quarter", "--size", "64x48", "--samples", "1",
                                    "--save-blend")
        self.assertEqual(code, 0, receipt)
        self.assertEqual(receipt["native"]["geosets"], 1)
        self.assertIn("unaltered_blend", receipt)
        view = receipt["render"]["views"][0]
        self.assertEqual(render_3do.sha256_file(self.root / "hashes" / view["file"]), view["sha256"])
        code, _ = self.render("hashes")
        self.assertEqual(code, 2)  # output exists
        done = subprocess.run([BPY, "-B", str(HERE / "render_3do.py"), str(self.model), "--fork-root",
                               str(self.root), "--out", str(self.root / "nofork")], capture_output=True, text=True)
        self.assertEqual(done.returncode, 2)


if __name__ == "__main__":
    unittest.main()
