# Methods and options

This is a decision guide for making models, not a prescribed sequence of tools. Choose the smallest combination that can deliver the requested appearance and behavior. Effort estimates below are relative; source quality and animation scope can change them substantially.

## Five useful starting routes

| Route | Best fit | Main work | Relative effort | Tradeoff |
| --- | --- | --- | --- | --- |
| Texture replacement | Existing shape already fits | Repaint/project/bake textures; preserve hierarchy and animation | Low | Cannot fix silhouette or proportions |
| Stock-rig remodel | Humanoids with conventional movement | Replace rigid mesh parts while preserving the working joint contract | Medium | Extreme proportions may clip or place weapons poorly |
| Donor or generated-part assembly | Anatomy or mechanical pieces would be costly from scratch | Acquire a permitted donor or generate a few parts, fit them, simplify and author the missing precision | Medium to high | Source seams, topology and inconsistent style need real cleanup |
| Detailed source to reduced game model | High visual ambition with reusable editable source | Retopology/reduction, silhouette decisions, UVs and baking | High | More pipeline work; much source detail becomes texture rather than geometry |
| Custom rig and animation set | New limb layout, posture or movement | Design hierarchy, author/retarget KEYs and PUP states, integrate model role | Highest | Most control, largest animation and integration scope |

The routes combine. A skull might come from Hunyuan, hands from manual modeling, torso from a licensed donor, and cloth from low-poly Blender modeling. The export mesh can use a stock skeleton even when every visible surface is new.

## Choose the target early

**Original retail first:** begin with a conservative known-working rig, materials appropriate to the intended renderer, and manageable per-mesh counts. Test the actual game executable and renderer. Prefer this route for maximum historical reach or when the user explicitly says unmodified/vanilla retail.

**Enhanced engine first:** use its verified capabilities for larger textures, additional geometry or improved rendering. Keep a distinct profile so its appearance does not become an accidental retail promise. “JKE-style quality” is an art target; JKE's historical package dependency is a separate technical choice.

**Two editions:** share the detailed source and author separate game exports. Differences may include mesh partitioning, texture dimensions/encoding, mipmaps, material mapping and effects. This costs more checking but avoids forcing every user into one renderer.

TDIR shows why a custom animation route is an option. It does not show that its high-index animated branches can be dropped into a stock player's animation set. See [the comparative research](jke-tdir-shred-research.md).

## Choose geometry tools by the problem

- **Blender UI:** fastest for sculptural judgment, reference alignment, selecting bad faces and fixing local topology.
- **Blender background Python/CLI:** best for reproducible assembly, bake setup, export preparation, matched views and repeated checks. Pin the executable/add-on versions and keep the editable source.
- **Blender MCP:** useful for interactive scene inspection and short tool-mediated changes when a trusted server is already available. It is an optional transport, not a requirement or evidence that the add-on was patched. Bind the exact scene/output scope; inspect the result in Blender.
- **Custom format writer:** useful when it demonstrably preserves an invariant the add-on loses or needs deterministic packaging. It carries maintenance and format-validation work. Re-import and compare its output rather than trusting the writer to validate itself.
- **Exporter patch/fork:** justified when there is a reproducible upstream defect, a concrete fix, licensing compliance and a regression test. A diagnosis or external preparation script alone is not a fixed fork.

## Choose a surface method

| Method | Choose it for | Watch for |
| --- | --- | --- |
| Hand-painted atlas | Strong stylization, precise anatomy/decals | Time cost, seams and uneven density |
| Procedural material to color bake | Bone, metal, cloth with repeatable art direction | Generic noise and lighting baked unintentionally |
| GPT image generation/edit | Reference design, material studies, atlas components and guided local revisions | Invented geometry, asymmetric views, misplaced highlights and inconsistent UV placement |
| Local ComfyUI generation | Controlled seeds, reusable graphs, batch studies with available hardware | Exact node/model versions, model licenses, VRAM and graph inputs |
| Photo/donor projection | Specific appearance with authorized references | Perspective distortion, occlusion and baked shadows |
| Detailed-source bake | Transfer surface color and selected geometric cues to a smaller mesh | Cage misses, self-occlusion, wrong active image, triangulation and normal changes |

For classic materials, a normal map or PBR setup in Blender is not automatically a game feature. Preserve important depth in silhouette/geometry, and convert chosen small cues to the supported color/material representation. Avoid crushing every detail into dark AO. Inspect at gameplay size and in motion.

## Example recommendations

**“Make a new multiplayer soldier quickly.”** Start from an appropriate working stock hierarchy, remodel the distinctive helmet and equipment, and paint/bake a few coherent material regions. Offer a texture-only first version if time is tight. Test model selection, idle/move/fire/death and separate-client visibility.

**“Make a gaunt creature with an unusual head.”** Recommend a partial skull donor or Hunyuan study, then manual jaw/teeth/sockets and deliberate hair/cloth masses. Keep stock movement for the first playable edition if acceptable. Offer a custom rig if limb proportions and posture are central to the design.

**“Match a detailed mechanical character.”** Keep the detailed source, simplify repeated internals and small fasteners, preserve silhouette-critical parts, bake material cues, and model the required hand poses intentionally. Inspect the actual weapon view models: a third-person body replacement may leave stock first-person hands visible.

**“I want TDIR-like movement.”** Offer the full custom KEY/PUP route. Establish the hierarchy and representative movement first, then spend time on the final surface. An alternative is a stock-animation prototype to judge the visual design before funding the animation work.

**“Make the model look as convincing as Shred's.”** Compare readable silhouette, material regions, joint placement, mip behavior and game-sized screenshots. Increasing triangle count is only one possible tool and often not the first useful change.
