# Using the focused Blender-Sith fork

Use the focused Blender-Sith Agentic fork by default for importing existing JK/MotS 3DOs into Blender for inspection and screenshots. Also use it when you want Blender's sharp or custom corner normals preserved by direct 3DO export, or when scripted hexadecimal metadata should accept values such as `0xFFFF` reliably. Keep the prepared-export-duplicate route for modifiers and transform cleanup. An independent writer remains useful for precise multi-geoset preservation and file-level model surgery.

The earlier [Blender-Sith audit](blender-sith-audit.md) found no substantive locally modified fork in the historical projects. A new focused fork was subsequently developed at Andrei's request, starting from the actual audited upstream commit [`ecc90131bcfdeabd400225e8a72ce94cbff1ec5c`](https://github.com/smlu/blender-sith/commit/ecc90131bcfdeabd400225e8a72ce94cbff1ec5c). These are two different points in the project's history. The original work is by Crt Vavros / smlu; upstream history and GPL-3.0-or-later licensing are preserved.

The fork's source and tests are distributed through [GitLab](https://gitlab.com/codalilitari/blender-sith) and the [GitHub repository](https://github.com/CodaLilitari/blender-sith). It retains upstream Git history; the GitHub copy is a standalone repository, outside GitHub's upstream fork network. Release identifier `v1.0.1-coda.1` corresponds to extension version `1.0.1`, **Blender Sith (Coda)**. The extension ID remains `sith`; use it as an alternative to upstream in a Blender extension repository.

## Choose the useful route

| Need | Method | Practical cost or limit |
|---|---|---|
| Inspect or render an existing JK/MotS model | Direct fork `sith.model.import3do` call | Supply the resolved MATs and CMP; current scene importer exposes only geoset 0 |
| Direct export of flat faces, sharp edges or existing custom normals | Focused fork | Normal discontinuities create necessary additional 3DO vertices; check the exported budget |
| Bake subdivision, bevels or a weighted-normal modifier into the export | Duplicate the source, apply selected modifiers, then use upstream or fork | Keep the editable original; the fork still reads the base mesh |
| Preserve all existing LOD/geoset structures exactly | Format-aware writer plus structured validation | Blender-Sith's scene importer still exposes only geoset 0 |
| Script KEY priority or node flags without prefix callback errors | Fork's registered properties, followed by readback assertions | Raw ID-property dictionary writes bypass validation |
| Inspect an interactive scene or correct pivots | Blender UI, optionally through an existing MCP connection | This fork adds no new MCP server or Blender-core changes |
| Repeat synthetic export checks or compare two versions | Fork's background CLI regression suite | Synthetic roundtrips do not certify retail or multiplayer runtime behavior |

## Direct native import for inspection and screenshots

The local working checkout observed on 2026-10-23 was Andrei's `Blender-Sith-Agentic` checkout, containing the `sith` package. Verify its current revision and working-tree state before use. When another task is editing the checkout, copy the required add-on source into this job's evidence directory and hash that snapshot; do not pull, reset or modify the shared checkout. Record the snapshot's relationship to the checkout and any uncommitted source changes. An extension label or a source repository URL alone does not prove which code ran.

Use a fresh background Blender process, or a verified Python environment with `bpy`. The working Python route observed on that date was a local Windows Python 3.13 with a private dependency directory on `sys.path`; it loaded `bpy` 5.1.2 with `bpy.app.background == True`. These paths are discovery hints, not assumptions for another machine. Record `sys.executable`, `bpy.__file__`, and `bpy.app.version_string` from the process that performs the import.

In the job script, after resolving exact absolute paths for `fork_root`, `model_path`, `mat_dir` and `cmp_path`, invoke the fork itself:

```python
import hashlib
import sys
from pathlib import Path

# fork_root contains sith/__init__.py; it may be a job-local source snapshot.
fork_root = Path(fork_root).resolve()
model_path = Path(model_path).resolve()
mat_dir = Path(mat_dir).resolve()
cmp_path = Path(cmp_path).resolve()
sys.dont_write_bytecode = True
sys.path.insert(0, str(fork_root))
import bpy
import sith
from sith.model import import3do
from sith.model import model3doImporter, model3doLoader

assert bpy.app.background, "Use a disposable process; clearScene clears scenes"
assert Path(sith.__file__).resolve() == fork_root / "sith" / "__init__.py"
assert Path(model3doImporter.__file__).resolve() == (
    fork_root / "sith" / "model" / "model3doImporter.py"
)
assert model_path.is_file() and mat_dir.is_dir() and cmp_path.is_file()
source_hashes = {
    p.relative_to(fork_root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
    for p in sorted((fork_root / "sith").rglob("*"))
    if p.is_file() and p.suffix in (".py", ".toml")
}
sith.register()
native, file_version = model3doLoader.load3do(str(model_path))
import_options = dict(
    mat_dirs=[str(mat_dir)],
    cmp_file=str(cmp_path),
    uvAbsolute_2_1=True,
    importVertexColors=True,
    importRadiusObj=False,
    preserveOrder=True,
    clearScene=True,
)
root = import3do(str(model_path), **import_options)
assert root is not None, "The importer produced no model root"
import_receipt = {
    "python": sys.executable,
    "bpy_module": bpy.__file__,
    "blender": bpy.app.version_string,
    "sith_module": sith.__file__,
    "importer_module": model3doImporter.__file__,
    "source_sha256": source_hashes,
    "model": str(model_path),
    "model_sha256": hashlib.sha256(model_path.read_bytes()).hexdigest(),
    "cmp": str(cmp_path),
    "cmp_sha256": hashlib.sha256(cmp_path.read_bytes()).hexdigest(),
    "mat_directory": str(mat_dir),
    "import_options": import_options,
    "native_geoset_count": len(native.geosets),
    "scene_geoset": 0,
}
# Save this receipt with the job's asset manifest, import log and render settings.
```

For a Blender executable, launch the job with `blender --background --factory-startup --python-exit-code 1 --python job.py -- <job arguments>`. For the isolated `bpy` route, add its verified dependency directory before `import bpy` and run the same job with the explicit Python executable. Do not enable/install the add-on in the user's desktop preferences merely to run a background import.

The importer searches its default model-relative material folders **before** the supplied `mat_dirs`. Extract only the intended package and explicitly resolved dependencies into an isolated job tree, inspect the ordered search folders, and resolve collisions before import. A missing MAT can produce a placeholder while the import still returns successfully. Capture the import log; verify every referenced MAT, decoded image, UV layer and material assignment. Hash the actual MAT files used. Supply the intended CMP for indexed materials; a guessed/default palette can make an intact model look wrong. `uvAbsolute_2_1=True` uses the importer's image-size conversion; compare it with the native model/renderer contract before calling a mismatch a source-model defect.

This call imports geoset 0, native hierarchy and material data; it does not preserve every geoset in the scene or certify animation/game rendering. Check all native geosets with structured diagnostics, keep source problems separate from importer limitations, and inspect actual final images. Any task-local material adapter or display conversion belongs in the receipt with its reason and affected files. Save the unaltered imported scene before optional presentation changes when those changes can hide diagnostic evidence.

## What changes

**Normal preservation.** The upstream exporter merged coincident vertices using position and color and wrote a BMesh vertex normal. The fork reads Blender's per-corner normals and includes the normal in the merge key. Flat-face, sharp-edge and custom normal splits survive. Texture coordinates keep their separate indexing. A smooth cube stays at eight vertices; a flat or all-sharp cube exports 24. Blender's [corner-normal API](https://docs.blender.org/api/5.0/bpy.types.Mesh.html#bpy.types.Mesh.corner_normals) defines the source data used by the fix.

Credit SMLiberator's [upstream issue 13](https://github.com/smlu/blender-sith/issues/13) for the earlier report of sharp-edge loss, automatic merging and the resulting vertex-budget tradeoff. This patch supplies normal-aware merging and synthetic regression coverage; it does not implement the report's suggested optional merge-control UI.

**Hexadecimal metadata.** Four-digit fields accept bare or `0x`-prefixed hexadecimal input, normalize it, and reject negative or overflowing values while retaining the previous value. The registered getter returns declared defaults when unset: `FFFF` for KEY high-priority types and `01` for hierarchy node type. This corrects the previous empty-string getter behavior; it is a deliberate default change. Saved explicit values remain explicit.

Use readback assertions in scripts:

```python
bpy.context.scene.sith_key_types = "0xFFFF"
assert bpy.context.scene.sith_key_types == "FFFF"
model_root.sith_model3do_hnode_type = "0x0001"
assert model_root.sith_model3do_hnode_type == "01"
```

Do not infer a KEY animation failure merely from the historical callback error. The earlier probe showed the assignment could still read back correctly. The patch eliminates the callback problem and fixes range/default behavior; animation playback remains a separate test.

## Repeat the checks

From the fork repository, with a compatible Blender executable:

```text
blender --background --factory-startup --python-exit-code 1 --python tests/background_regression.py -- --output regression-results
```

Or use an existing Python environment providing compatible `bpy`:

```text
python tests/background_regression.py --output regression-results
python tests/background_regression.py --addon /path/to/upstream/sith --output upstream-results
```

The output directory must be new. The suite creates synthetic meshes and an animation in a disposable process, serializes 3DO 2.1 and KEY files, parses them back, checks normals and other fields, and writes `regression.json`. It verifies add-on source hashes and source mesh snapshots remain unchanged. Exit 0 means these checks pass; it is not a game compatibility certificate.

On the observed `bpy` 5.1.2 runtime, the identical ten checks produced four passes and six failures on upstream, and ten passes on the patched candidate. Fixed failures cover disconnected sharp-normal seams, flat and sharp cubes, custom normals, mixed n-gon/disconnected faces, and hexadecimal metadata. Passing regression controls cover smooth normals, UV seams, absolute image-size UV conversion, byte-color behavior, face material/flags/modes, hierarchy offsets and an animated KEY roundtrip. The upstream minimum is Blender 5.0; the executed test runtime was 5.1.2.

The exact installable extension ZIP was extracted and independently passed the same ten checks. Its [packaged-artifact evidence](evidence/blender-sith-packaged-fork-2026-09-30.json) records the ZIP hash and source commit `0f401e672f9e28818bc7304407bf1cb781e65b70`. Source archives use exact Git blobs; raw working-tree hashes can differ when a checkout normalizes line endings. Installing through Blender's desktop extension UI was not part of that process-local test.

## Remaining work and model release checks

- Apply non-uniform or negative scales on a prepared export duplicate, then inspect winding, normals, bounds and hierarchy offsets. The patch does not replace the upstream transform/radius code; its normal fixtures use unit scale.
- Shared mesh datablocks still produce separate mesh records for separate hierarchy objects. Safe reuse would have to account for scale and object-specific properties.
- The additional 3DO 2.2 experiment found an existing RGB face-extra-light writer/reader disagreement. Upstream documents that format as IJIM RGB. The focused passing matrix covers JK/MotS 2.1; it does not claim 2.2 was repaired.
- Exported byte-color handling follows upstream's existing sRGB byte-layer behavior. This change is not a color-management redesign.
- Modifier evaluation, retail rendering, animation blending, multiplayer interoperability and material resolution remain independent checks. Follow [runtime and packaging](runtime-and-packaging.md) and [compatibility](compatibility.md).

See [Blender export and baking methods](blender-export-and-baking.md) for prepared duplicates, native atlases, analytical chrome baking and high-to-low alternatives. The fork is the default native import route; export and preservation methods still depend on the task.
