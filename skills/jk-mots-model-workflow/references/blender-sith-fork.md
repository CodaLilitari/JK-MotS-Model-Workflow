# Using the Blender-Sith Agentic fork

Use Blender-Sith Agentic by default for importing existing JK/MotS 3DOs into Blender for inspection and screenshots. Its focused fixes also preserve corner normals, make scripted metadata predictable, repair indexed MAT cel reading, and correct native KEY export. Keep a prepared export duplicate for modifiers and transform cleanup. An independent writer remains useful for precise multi-geoset preservation and file-level model surgery.

The earlier [Blender-Sith audit](blender-sith-audit.md) found no substantive locally modified fork in the historical projects. A new focused fork was subsequently developed at Andrei's request, starting from the actual audited upstream commit [`ecc90131bcfdeabd400225e8a72ce94cbff1ec5c`](https://github.com/smlu/blender-sith/commit/ecc90131bcfdeabd400225e8a72ce94cbff1ec5c). These are two different points in the project's history. The original work is by Crt Vavros / smlu; upstream history and GPL-3.0-or-later licensing are preserved.

The public [GitHub repository](https://github.com/CodaLilitari/blender-sith) now belongs to [smlu/blender-sith](https://github.com/smlu/blender-sith)'s fork network; the former standalone arrangement is historical. [GitLab](https://gitlab.com/codalilitari/blender-sith) remains a source-distribution link, but verify each host's actual revision before treating copies as equivalent. A release is an exact source snapshot: later upstream refactors and pull requests require a separate comparison and are not implicitly included.

## Public release and installation

The November 2026 update targets **v1.0.4-coda.1**, extension version **1.0.4**,
named **Blender Sith (Coda)**. Its publication and exact-package validation are
recorded in the [GitHub release](https://github.com/CodaLilitari/blender-sith/releases/tag/v1.0.4-coda.1)
and [GitLab mirror](https://gitlab.com/codalilitari/blender-sith/-/releases/v1.0.4-coda.1).
Keep the exact version, platform, archive hash and runtime in the job receipt.

1. Use Blender **5.0 or newer** and choose [Windows x64](https://github.com/CodaLilitari/blender-sith/releases/download/v1.0.4-coda.1/sith-1.0.4-windows-x64.zip), [Linux x64](https://github.com/CodaLilitari/blender-sith/releases/download/v1.0.4-coda.1/sith-1.0.4-linux-x64.zip), [macOS Apple Silicon](https://github.com/CodaLilitari/blender-sith/releases/download/v1.0.4-coda.1/sith-1.0.4-macos-arm64.zip), or [universal](https://github.com/CodaLilitari/blender-sith/releases/download/v1.0.4-coda.1/sith-1.0.4-universal.zip).
2. Compare the download with the release's [SHA-256 checksums](https://github.com/CodaLilitari/blender-sith/releases/download/v1.0.4-coda.1/SHA256SUMS.txt). Per-package receipts record source and normalized file hashes.
3. In Blender, open **Edit > Preferences > Add-ons > Install from Disk**, select the ZIP and enable the extension. The ID remains `sith`; use one edition in a given extension repository.

These are Python extensions, not Blender executables. The optional MCP companion
is separate. Background inspection can load a verified snapshot without changing
desktop preferences. The universal package removes a manifest restriction; it
does not expand the validated architecture/runtime matrix. macOS means Apple
Silicon: this Blender-5.0-minimum release does not claim Intel Mac support.

The preceding [v1.0.3-coda.2 release](https://github.com/CodaLilitari/blender-sith/releases/tag/v1.0.3-coda.2)
already supplied a separately validated Apple Silicon package. Earlier statements
that no Mac 1.0.3 asset existed described v1.0.3-coda.1 and are historical.

## Choose the useful route

| Need | Method | Practical cost or limit |
|---|---|---|
| Inspect or render an existing textured JK/MotS model | Direct fork `sith.model.import3do` call below | Supply resolved MATs and CMP; scene import exposes only geoset 0 |
| Direct export of flat faces, sharp edges or existing custom normals | Focused fork | Normal discontinuities create necessary additional 3DO vertices; check the exported budget |
| Bake subdivision, bevels or a weighted-normal modifier into the export | Duplicate the source, apply selected modifiers, then use upstream or fork | Keep the editable original; the fork still reads the base mesh |
| Preserve all existing LOD/geoset structures exactly | Format-aware writer plus structured validation | Blender-Sith's scene importer still exposes only geoset 0 |
| Script KEY priority or node flags without prefix callback errors | Fork's registered properties, followed by readback assertions | Raw ID-property dictionary writes bypass validation |
| Export keyed returns to zero or quaternion turns through the wrap boundary | Version 1.0.3 KEY exporter | Key enough quaternion samples to express the turn; explicit Euler winding is retained |
| Inspect an interactive scene or correct pivots | Blender UI, optionally through a verified general Blender connection | The optional format-specific companion is not an interactive scene editor |
| Summarize a native file or make a geometry-only `.blend` | Optional local MCP companion | Conversion omits MAT/CMP lookup and imports only geoset 0; it is not the textured inspection route |
| Repeat synthetic checks or compare two versions | Bounded background launcher and regression suite | Serialized fixtures do not certify retail or multiplayer runtime behavior |

## Direct native import for inspection and screenshots

Resolve a verified source checkout or snapshot containing `sith/__init__.py`. Record its revision and any local source changes before using it. When another task is editing the checkout, copy the required add-on source into an external job evidence directory and hash that snapshot; do not pull, reset or modify the shared checkout. Serialize any necessary Git inspection with the checkout's coordinator. An extension label or repository URL alone does not identify the code that ran. A release ZIP places `__init__.py` at its root; extract it into a job-local directory named `sith` if using the source-root import layout below, and record the archive hash and adaptation.

Use a fresh background Blender process or an isolated Python environment with compatible `bpy`. The direct-import workflow observed on 2026-10-23 used `bpy` 5.1.2 with `bpy.app.background == True`; that is historical runtime evidence, not a required personal installation path. Record `sys.executable`, `bpy.__file__`, and `bpy.app.version_string` from the actual import process. Keep runtimes, dependencies, copied source, assets and outputs physically outside Git checkouts, with no junctions or symlinks back into them.

In the job script, resolve exact absolute paths for `fork_root`, `model_path`, `mat_dir` and `cmp_path`, then invoke the fork itself:

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

For a Blender executable, launch the job with `blender --background --factory-startup --offline-mode --threads 2 --python-exit-code 1 --python job.py -- <job arguments>` under an actual process deadline that can terminate the owned process tree. Use isolated Blender user configuration. For the `bpy` route, add its verified dependency directory before `import bpy` and run the same job with the explicit Python executable and a bounded supervisor. These settings do not constitute an OS sandbox. Do not install or enable the add-on in desktop preferences merely to run a background import.

The importer searches its default model-relative material folders **before** supplied `mat_dirs`. Extract only the intended package and explicitly resolved dependencies into an isolated job tree, inspect the ordered search folders, and resolve collisions before import. A missing MAT can produce a placeholder while import still succeeds. Capture the import log; verify every referenced MAT, decoded image, UV layer and material assignment. Hash the actual MAT files used. Supply the intended CMP for indexed materials; a guessed palette can make an intact model look wrong. `uvAbsolute_2_1=True` uses image-size conversion; compare it with the native renderer contract before diagnosing a source-model defect.

This call imports geoset 0, native hierarchy and material data. Check all native geosets with structured diagnostics and keep source defects separate from importer limitations. Inspect the actual final images. Record any task-local material adapter or display conversion and its affected files. Save the unaltered imported scene before optional presentation changes that could hide diagnostic evidence. A reconstructed mesh or the companion's geometry-only conversion can supplement diagnosis; neither substitutes for a requested textured fork import.

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

**Material fixes added in 1.0.2.** Darth Martyr's [material-table separator repair](https://github.com/sithmartyr/blender-sith/commit/a25543f5ba45c5ad203a65ba11193c640b37e255) retains its original author and source-commit attribution. Long MAT filenames remain separated from their numeric index. A separate Coda fix consumes indexed MAT mip payloads even without a CMP palette, keeping later cel headers aligned and rejecting truncated skipped data. Missing palettes still yield placeholders; this is not recovery of the intended colors. See the [dated source audit](https://github.com/CodaLilitari/blender-sith/blob/v1.0.4-coda.1/docs/fork-audit-2026-11-01.md).

**KEY export corrected in 1.0.3.** A keyed location or rotation component can now return to explicit zero without retaining its earlier nonzero value. Quaternion samples choose equivalent continuous pitch/yaw/roll values before native differentials are written, avoiding an unintended long reverse turn across the wrap boundary. Authored Euler winding remains intact, including sparse multi-turn Euler keys. See the [correction notes](https://github.com/CodaLilitari/blender-sith/blob/v1.0.4-coda.1/docs/key-export-corrections.md) and [exporter source](https://github.com/CodaLilitari/blender-sith/blob/v1.0.4-coda.1/sith/key/keyExporter.py).

Keep quaternion samples close enough to express the intended direction: orientation samples alone cannot distinguish an omitted revolution or a turn exceeding 180 degrees between samples. Bake or key an adequate sampling density when needed. This change does not bake unkeyed constraints, modifiers or Blender interpolation curves. Its tests inspect serialized KEYs and synthetic interpolation; actual game playback is still a separate check.

## Radius and native pivots corrected in 1.0.4

Red's saved build used a conservative radius of **0.133282** after the old
exporter produced **0.081336**. Re-export of that unchanged Blender file
reproduced the problem. Its assembled native rest geometry requires about
**0.120722308**, so the repaired exporter writes **0.120722** at six-decimal
format precision. The fix measures exported hierarchy geometry about the native
origin, including ancestor translations/rotations and each node's pivot; it
does not apply scale or INSERT OFFSET twice. An explicitly authored larger
radius remains authoritative. Rest-pose containment is distinct from bounds
for every animation pose.

A separate archived check found native pivots lost through import/export.
Baking a pivot into vertices can preserve visible surfaces while changing the
joint matrix used to attach a weapon. The cited hand pivot explains an
approximately **0.01096 JKU** attachment shift. New imports preserve pivot
metadata; export restores native vertices and pivots, with explicit authored
PivotConstraint behavior kept separate. Check attachment matrices as well as
surface positions. The fix cannot infer pivots already erased from older saved
Blender files: re-import a source 3DO retaining its hierarchy, or perform a
separately verified rig repair. Existing KEY location semantics are preserved.

Credit Red's report, workaround and archived verifier leads; Coda reproduced
the defects, checked native engine semantics and implemented the add-on repair.
This update ships synthetic tests, not the private character source. It does not
turn geoset-zero Blender import into a complete LOD-preserving round trip.

## Optional local MCP companion

The fork now offers a separate [local stdio companion](https://github.com/CodaLilitari/blender-sith/blob/v1.0.4-coda.1/docs/MCP.md). The normal Blender extension does not start it or require its dependencies. Its five tools report configuration (`server_info`), summarize an allowlisted native file (`inspect_3do`), create a geometry-only scene (`convert_3do_to_blend`), run synthetic checks (`run_regression`), and package the companion checkout's add-on (`build_extension`).

`inspect_3do` summarizes all parsed geosets. Conversion imports **geoset zero with placeholders**, disables neighboring MAT/CMP lookup, and cannot normalize JK 2.1 UVs using absent texture dimensions. Use the direct recipe above for textured inspection. `build_extension` does not publish or install; when configured with a Blender executable it also validates the exact ZIP. A Python-plus-`bpy` configuration cannot substitute for Blender CLI extension validation.

Configure trusted runtime/source paths, exact authorized read roots, and an external job directory. The companion serializes bounded jobs and rejects paths outside its configured scope; it is a trusted-user local tool, not an OS security sandbox. Preserve its limits and receipts. Its SDK environment should be separate from a general Blender MCP server's environment. The companion documentation's example pairing with Blender Lab is not evidence of a tested joint session or official endorsement.

## Repeat the checks

Prefer the fork's [bounded launcher](https://github.com/CodaLilitari/blender-sith/blob/v1.0.4-coda.1/docs/platform-builds.md). Supply verified executable/source paths and a **new external output directory**. Adapt these placeholders to the machine:

```powershell
python C:\src\blender-sith\scripts\run_regression.py `
  --blender C:\runtimes\blender\blender.exe `
  --output C:\builds\sith-regression-001 --threads 2 --timeout 300
```

```sh
python3 /src/blender-sith/scripts/run_regression.py \
  --blender /opt/blender/blender \
  --output /srv/sith-jobs/regression-001 --threads 2 --timeout 300
```

The launcher isolates preferences, bounds the subprocess lifetime and thread count, verifies the completed report and source hashes, and refuses output inside Git checkouts. Keep dependency environments, build/capture trees and generated fixtures physically external too, with no junctions or symlinks into source checkouts. Use `--addon` to select an extracted exact package for comparison. Existing compatible Python-plus-`bpy` environments are supported through `--python` and optional `--bpy-site`; the launcher does not install dependencies.

The direct harness entry points remain available for established automation with equivalent supervision:

```text
blender --background --factory-startup --python-exit-code 1 --python /src/blender-sith/tests/background_regression.py -- --output /srv/sith-jobs/direct-001
python /src/blender-sith/tests/background_regression.py --addon /path/to/upstream/sith --output /srv/sith-jobs/upstream-001
```

The suite creates synthetic geometry, animations and material fixtures in a disposable process, checks serialized native data and writes `regression.json`. Preserve the launcher receipt and detailed results, including failures and skips. A successful report establishes the tested contracts, not game compatibility.

### Current release evidence: 1.0.4

The exact runtime matrix, native-platform receipts and check totals are retained
in the [release validation record](https://github.com/CodaLilitari/blender-sith/releases/download/v1.0.4-coda.1/VALIDATION.md).
Each new release must be checked against its own package hashes; the earlier
16-case 1.0.3 results cannot validate changed 1.0.4 bytes. The new synthetic
coverage includes origin-centered radius, accumulated transforms and pivots,
import/export attachment preservation and unchanged source data. Actual game
rendering, animation blending and connected multiplayer remain separate checks.

### Historical baseline: September 2026 / 1.0.1

The original identical ten-check comparison on `bpy` 5.1.2 gave upstream four passes and six failures, and the focused candidate ten passes. Its fixes covered disconnected normal seams, flat/sharp/custom normals, mixed faces and hexadecimal metadata. Controls covered smooth geometry, UV/material/color channels, hierarchy and a simple animated KEY roundtrip. Those totals describe that historical harness, not today's full matrix.

The original installable extension ZIP was extracted and independently passed those same ten checks. Its [packaged-artifact evidence dated 2026-09-30](evidence/blender-sith-packaged-fork-2026-09-30.json) records the archive hash and source commit `0f401e672f9e28818bc7304407bf1cb781e65b70`. Source archives use exact Git blobs; working-tree hashes can differ with line-ending normalization. Installing through the desktop extension UI was not part of that process-local test.

## Remaining work and model release checks

- Apply non-uniform or negative scales on a prepared export duplicate, then inspect winding, normals, bounds and hierarchy offsets. The radius/pivot repairs follow exported native coordinates; they do not establish arbitrary shear, modifier or animation-transform fidelity.
- Shared mesh datablocks still produce separate mesh records for separate hierarchy objects. Safe reuse would have to account for scale and object-specific properties.
- The additional 3DO 2.2 experiment found an existing RGB face-extra-light writer/reader disagreement. Upstream documents that format as IJIM RGB. The focused passing matrix covers JK/MotS 2.1; it does not claim 2.2 was repaired.
- Exported byte-color handling follows upstream's existing sRGB byte-layer behavior. This change is not a color-management redesign.
- Modifier evaluation, retail rendering, animation blending, multiplayer interoperability and material resolution remain independent checks. Follow [runtime and packaging](runtime-and-packaging.md) and [compatibility](compatibility.md).

See [Blender export and baking methods](blender-export-and-baking.md) for prepared duplicates, native atlases, analytical chrome baking and high-to-low alternatives. The fork is the default native import route; export and preservation methods still depend on the task.
