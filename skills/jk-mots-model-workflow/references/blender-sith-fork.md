# Using the focused Blender-Sith fork

Use the focused Blender-Sith Agentic fork when you want Blender's sharp or custom corner normals preserved by direct 3DO export, or when scripted hexadecimal metadata should accept values such as `0xFFFF` reliably. Keep the prepared-export-duplicate route for modifiers and transform cleanup. An independent writer remains useful for precise multi-geoset preservation and file-level model surgery.

The earlier [Blender-Sith audit](blender-sith-audit.md) found no substantive locally modified fork in the historical projects. A new focused fork was subsequently developed at Andrei's request, starting from the actual audited upstream commit [`ecc90131bcfdeabd400225e8a72ce94cbff1ec5c`](https://github.com/smlu/blender-sith/commit/ecc90131bcfdeabd400225e8a72ce94cbff1ec5c). These are two different points in the project's history. The original work is by Crt Vavros / smlu; upstream history and GPL-3.0-or-later licensing are preserved.

The fork's source and tests are distributed through [GitLab](https://gitlab.com/codalilitari/blender-sith) and the [GitHub repository](https://github.com/CodaLilitari/blender-sith). It retains upstream Git history; the GitHub copy is a standalone repository, outside GitHub's upstream fork network. Release identifier `v1.0.1-coda.1` corresponds to extension version `1.0.1`, **Blender Sith (Coda)**. The extension ID remains `sith`; use it as an alternative to upstream in a Blender extension repository.

## Choose the useful route

| Need | Method | Practical cost or limit |
|---|---|---|
| Direct export of flat faces, sharp edges or existing custom normals | Focused fork | Normal discontinuities create necessary additional 3DO vertices; check the exported budget |
| Bake subdivision, bevels or a weighted-normal modifier into the export | Duplicate the source, apply selected modifiers, then use upstream or fork | Keep the editable original; the fork still reads the base mesh |
| Preserve all existing LOD/geoset structures exactly | Format-aware writer plus structured validation | Blender-Sith's scene importer still exposes only geoset 0 |
| Script KEY priority or node flags without prefix callback errors | Fork's registered properties, followed by readback assertions | Raw ID-property dictionary writes bypass validation |
| Inspect an interactive scene or correct pivots | Blender UI, optionally through an existing MCP connection | This fork adds no new MCP server or Blender-core changes |
| Repeat synthetic export checks or compare two versions | Fork's background CLI regression suite | Synthetic roundtrips do not certify retail or multiplayer runtime behavior |

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

See [Blender export and baking methods](blender-export-and-baking.md) for prepared duplicates, native atlases, analytical chrome baking and high-to-low alternatives. The fork is one useful option inside that workflow.
