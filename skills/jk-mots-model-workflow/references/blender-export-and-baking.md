# Blender, export and baking: choose the method that fits the job

Use Blender for shape, UV and material work; use a reproducible export copy for the game. Keep the detailed editable master and the native four-LOD 3DO as separate artifacts. This workflow concerns characters, creatures, player skins and other single-player/multiplayer models.

## Choose your control method

| Method | Choose it when | Working pattern |
|---|---|---|
| Blender UI | Sculpting, seam placement, silhouette, manual donor fitting and visual judgment dominate. | Preserve the source file; make a named export collection/copy; inspect neutral front, rear, side and three-quarter views before export. |
| Background Blender Python | You need repeatable import, UV/bake, asset conversion, matched cameras or validation across many files. | Run `blender --background --factory-startup --python job.py -- <job arguments>`. Use an explicit input/output list and save a receipt with versions, hashes and settings. |
| Python with an isolated `bpy` package | An existing tested runtime already runs background Blender jobs without desktop setup. | Use that interpreter and its exact dependency directory. Record `bpy.app.version_string`; verify the actual import location. A successful ordinary Python launch does not prove that the intended Blender package loaded. |
| An existing Blender MCP bridge | Interactive scene inspection or many small edits in an already connected artist session would benefit from it. | Verify the bridge can perform the needed operation; checkpoint the scene, target named objects and verify results. The bridge is transport, not a substitute for a modeling method. |

The historical projects used background Python/`bpy` and project scripts; the initial audit found upstream add-on copies and external adapters. A subsequent [focused Blender-Sith fork](blender-sith-fork.md) adds normal-preservation and metadata fixes with synthetic regressions. Blender itself and an MCP server were not forked. See [the original add-on audit](blender-sith-audit.md) for the prior baseline.

## Choose your export method

| Method | Good fit | Tradeoff / verification |
|---|---|---|
| Prepared export duplicate + Blender-Sith | A mostly manual Blender workflow; deliberate final topology; all required operations can be made explicit. | Apply intended geometry operations to the duplicate, set Sith properties, then independently read back the 3DO. The audited exporter still merges coincident vertices without preserving their normal identity, so applying modifiers alone does not solve every shading case. |
| Existing deterministic 3DO writer | Procedural assembly or a project already has a reviewed writer and format tests. | This route successfully carried our custom hierarchy, per-face modes, MAT contracts and all-LOD checks. Confirm the writer's exact revision and reparse with an independent implementation. Do not assume that an arbitrary writer preserves everything. |
| Focused Blender-Sith fork | You want direct export of existing sharp/custom corner normals or predictable scripted hex metadata. | The tested fork fixes these two issues. Prepare modifiers/transforms separately; shared meshes can still be duplicated. Further exporter changes need their own scoped regressions. |

For the first method, a useful sequence is:

1. Duplicate the final model into a dedicated game-export collection/file. Freeze pose, units, axes and intended modifier settings. Preserve the editable master.
2. Evaluate/apply intended modifiers on that duplicate. Compare evaluated/master and duplicate bounds, silhouette and counts. Any topology-changing operation must be followed by checks of material indices, UVs, light values and Sith face flags.
3. Split and simplify geometry to the target engine's actual per-mesh budget. Count the exported vertices after normal/light splits; source vertex count alone can underestimate it.
4. Preserve the intended numbered rigid hierarchy, parent relationships, pivots and rest transforms. Added hair, teeth or armor usually follow existing joints as rigid children. Do not reorder the stock animation slots to make object names look tidy.
5. Assign texture and lighting modes deliberately. For newly authored perspective-mapped geometry, record texture mode `1` at both mesh and face levels; either field can constrain the effective mode in paths that use it. Preserve an intentionally affine surface when needed. In the audited native OpenGL path, shader interpolation is independent of these legacy 0/1 fields, so changing them alone has no source-supported expected quality gain there. Test the actual target renderer; do not sell this data correction as a general visual fix.
6. Export and parse the complete result independently: each geoset, material name, face index, UV, normal, hierarchy entry, bounds and radius. Import the close LOD into Blender for an actual appearance comparison.
7. Exercise the intended KEY/PUP domain and then run the target game. Keep editor round-trip, isolated animation samples, game rendering and connected multiplayer as separate observations.

Blender's dependency graph distinguishes original geometry from evaluated geometry; an export helper can obtain an evaluated object and temporary mesh, then release that mesh with `to_mesh_clear()`. Persistent copies need an appropriate persistent-mesh path. Check the API documentation for the installed Blender version before writing an adapter. [Blender API: evaluated geometry](https://docs.blender.org/api/5.0/bpy.types.Depsgraph.html)

## Three different meanings of baking

| Bake | What it produces | Use for JK/MotS |
|---|---|---|
| Geometry bake / conversion | Real final vertices and faces from modifiers or procedural geometry. | Necessary when the exporter only reads base geometry. It preserves silhouette only insofar as the evaluated geometry is retained. |
| Color/material bake | A UV image sampled from a procedural, projected or composed shader. | Turns Blender-specific box projection and material mixes into portable diffuse images for MAT conversion. |
| High-to-low surface-detail bake | Texture maps transferring detail from dense source to a low-detail target. | Diffuse color and restrained painted depth cues are useful in the base game. Keep silhouette, articulation and important openings in geometry; a normal map is not a native retail MAT feature. Use normal/PBR maps only in a separately verified enhanced renderer lane. |

A polished render of a triplanar shader is a material pilot. It becomes portable only after a UV/image bake and inspection of the result on the delivery mesh. In our skull study, the bone shader was intentionally **not** called an equivalent GLB/MAT because that bake had not happened.

## Option A: bake a composed color shader without extra lighting

Choose this when a good source face, skin image or procedural color mix should be transferred without studio shadows and highlights. Our completed face/skin workflow used a deterministic **Emission** bake. Emission is the baking mechanism here; the result is an ordinary color texture, and the game model need not be fullbright.

1. Retain immutable source images. Keep generated originals separate from derived images, accepted selections and final atlas tiles. A derived output must not become the next run's supposed original input.
2. Finalize target charts around the actual geometry. Our successful head used a retained front chart plus separate side, rear seam, under-chin and neck-cap islands; a single frontal projection did not solve hidden/underside surfaces.
3. Connect the desired color shader to Emission, and create an explicit active Image Texture bake target for each relevant material. Select the intended target UV layer. Save output images explicitly after baking.
4. Control projection conflicts. Hidden eye-support and nostril faces overlapped visible frontal UVs in our model. Their back-facing color could overwrite face pixels. A temporary bake-only copy excluded the occluded/rear-facing contributors; the exported anatomy stayed intact. Use a model-specific visibility rule, not the historical coordinates as universal constants.
5. Record margin, samples, seed, device, color handling, target size and any prefilled pixels. Our repeatable local recipe used CPU Cycles, Emission, one sample, seed 0, 1024-square images and 16-pixel extend margin. These are a demonstrated color-only recipe, not recommended settings for arbitrary AO or lighting bakes.
6. Inspect mapped front/oblique/side/underside views and the final lower-resolution textures. Preserve a measured seam diagnostic if helpful, but require a visual check too.
7. Repeat from the immutable inputs when deterministic reproduction matters. Our recorded repeat produced the same four PNG hashes and retained geometry, normals and topology; it was a historical run, not a promise of bit-identical output across every Blender build or GPU.

For skin matching, a bounded measured color adjustment helped more than repeated generation: quiet face patches supplied median color, the plain-skin field received a limited gain, and the exact transformation was recorded. A texture's useful broad variation should not turn smooth bone into stone or amplify skin grain. Judge appearance at actual game resolution.

## Option B: bake dense donors onto a reduced target

Choose this for a high-detail sculpt or local image-to-3D donor whose large shapes are useful, after final assembly and reduction. First preserve forms that matter in the low mesh: facial profile, rib openings, digit count, hair layers and articulation gaps. No bake can reconstruct a missing outline or make fused geometry articulate.

Use a UV-unwrapped low-detail target with explicit image targets. Select the high sources and make the low target active for Selected to Active. Match their transforms; use a controlled cage or measured ray distance. A custom cage must preserve the target's topology and face order. Bake nearby teeth, limbs or hair in separated groups if cross-projection hits the wrong surface. Test seams and mip levels, then inspect the baked low mesh alone. [Blender manual: Render Baking](https://docs.blender.org/UATEST/manual/en/4.5/render/cycles/baking.html)

A practical choice of passes:

- **Color / Emission:** portable base-color detail, especially when a source image already contains stylized shading.
- **AO or selected broad shading:** a separate adjustable layer for restrained depth cues. Compare it under game lighting before mixing it into diffuse; hard baked shadows can double-darken moving characters.
- **Normal / displacement:** preserve for modern source deliverables or an explicitly supported enhanced path. Native retail delivery still needs its own usable diffuse/geometry result.

The high-to-low procedure is a recommended method from Blender's documented tools. Our retained skull material pilot did not complete a production high-to-low atlas; do not cite it as proof of an executed whole-character bake.

## Option C: surface-aware painted metal from an existing atlas

Choose this when an existing native model has useful panel/recess artwork and UVs, and the desired change is a stronger metal finish. **Lilitari / Lily's T-800 Hybrid r2-r4 work** supplies a concrete alternative to generating a replacement atlas or setting up a Blender shader bake. Her retained r4 `bake_body.py` computes an analytical color field directly from native mesh surfaces with NumPy, Pillow, SciPy and Numba. The package's `geometry_r4.py` and `native_io.py` complete the specialized build; it is not a standalone universal Blender plug-in. The source attribution distinguishes **Red's V2 conversion** from **Lily's hybrid and finish work**. [Published inherited attribution](https://github.com/CodaLilitari/T800-Hybrid-JK-MotS/blob/main/docs/INHERITED-ATTRIBUTION.md)

The transferable recipe is:

1. Decode the original material. Its existing panels, recesses and apertures remain the color-detail source. Transform surface positions/normals into a consistent body coordinate space, then rasterize their triangles into the existing UV layout using barycentric samples.
2. Analyze connected parts without welding the delivered mesh. For elongated parts, use the principal component axis to place long highlights along rods/pistons. The historical script classified a part as elongated when its largest covariance eigenvalue exceeded four times the second.
3. At each surface sample, compute a bounded highlight/shadow-band factor from position and normal. Apply the same luminance curve and slightly cool metal palette across regions; reduce body-band contrast so small hardware does not become noisy. This models painted studio-like bands, not physically correct runtime reflection.
4. With mirrored/overlapping UVs, **shade each contributing surface first, then average the resulting color or scalar factors**. Averaging opposite normals before this nonlinear operation can cancel them and create invalid shading. Report the number of contributors and their maximum disagreement; a stable average does not fix incompatible UV ownership.
5. Give the close LOD first claim on a texel. Lower LODs fill still-uncovered samples. Log and skip zero-area UV triangles for coverage; never divide by their zero area. Their native UV coordinates can remain unchanged for a bounded finish-only edit.
6. Dilate valid coverage before downsampling. The r4 recipe used a 1024-square working field, nearest covered-sample fill within twelve pixels, and Lanczos reduction to 256-square native output. Elsewhere it retained the source color. Those dimensions are this project's choices, not new detail recovered from a low-resolution texture.
7. Encode the intended RGB565 mip chain, decode it again, and render the actual native pixels. Preserve a geometry-only comparison alongside the texture-only comparison. Inspect distant LODs as well as the close view.

This method keeps UVs and panel placement stable and costs no image-generation call. A newly painted/generated atlas is the better option when the old artwork or UV layout is the actual bottleneck. A Blender material bake is the better option when the desired surface can be authored more clearly as a shader. Keep all three choices available.

Lily's companion geometry method is useful for proportion corrections: move a rigid skull/jaw/eye group together, compress only the existing neck-support band, keep the field monotone, transform affected normals by the inverse-transpose derivative, and update bounds. Preserve hierarchy, UVs and topology when the request is only a proportion adjustment. The historical r4 validator checked the inverse numerically, mirrored shading and zero-area UV handling; its clean rebuild report compared 17 artifacts. These are retained source-package results, not fresh game tests in this workflow audit. See the [Terminator case study](terminator-case-study.md) for the lineage and later integration lessons.

## Texture layout choices that survive export

- **Several legal small MAT tiles:** a useful retail option, with purposeful UVs and mipmaps. Coherent painting matters more than forcing every character into a single enormous atlas.
- **Large native MAT atlas:** an enhanced option only when the exact executable/patch/renderer is proven to support its dimensions and resource needs.
- **Base MAT plus external PNG replacement:** retain a working fallback MAT and test the replacement system separately. Higher image resolution does not automatically require changing the native MAT's UV contract.

Native 3DO UVs use a pixel-like coordinate domain whose effective normalization must be checked in the target renderer. **Do not multiply UVs merely because a native MAT or replacement image gets larger.** The inspected native OpenGL path clamps its normalization dimension to 256 even when a larger image is uploaded; the inspected Shred 2048-square atlas uses a 256-unit UV period. Scaling that example by eight would repeat/change its mapping. Another path can use a different denominator, so a universal never-scale rule is also wrong. Use an asymmetric numbered grid to calibrate orientation, period and boundaries on the intended renderer, then inspect near/mid/far stored mips. Repacking atlas islands always requires a deliberate mapping update. A source atlas, game MAT and replacement PNG need their own dimensions and tested mapping contract. See [the renderer-specific texture guidance](textures-and-imagegen.md) and [compatibility choices](compatibility.md).

Build gutters around islands and inspect all generated mip levels. In our atlas assembly, sixteen accepted 1024-square regions formed a 4096-square authoring canvas, with explicit twelve-pixel gutters. That was assembled working resolution, not a native 4K generator output. Final base MATs were 256-square indexed or RGB565 with their own mip chain. Preserve those distinctions when offering quality choices.

Finish with the actual renderer and animation. Skin shade depends on source color, palette/CMP, light mode, vertex/sector lighting, gamma and texture format; perspective mode cannot be assumed to cure every color problem. Real geoset LODs lower geometry cost; mipmaps only lower texture sampling cost.

For measured fan precedents and compatibility choices, use the companion model-compatibility research in this workflow. Crt Vavros (smlu) authored Blender-Sith; SMLiberator reported the upstream sharp-edge/shared-mesh issues. The workflow's project adapters and their findings do not transfer that authorship to us.
