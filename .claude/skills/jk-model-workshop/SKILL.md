---
name: jk-model-workshop
description: Inspect, render, plan, build, validate and package character, creature, vehicle, player-skin and weapon models for Jedi Knight Dark Forces II and Mysteries of the Sith (3DO, KEY, PUP, MAT), using the Blender-Sith fork headlessly in Claude's cloud workspace, the hierarchy/KEY contract inspector, and Coda's research library. Use when Andrei asks Red to look at, render, fix, convert, re-rig, retexture or plan a JK/MotS model or skin, or to check one against its animations. Excludes level design and COG scripting. Red's Claude fork of Coda's JK/MotS Model Workflow.
metadata:
  version: "0.2.0"
  forked_from: "JK / MotS Model Workflow 1.3 (Andrei and Coda, MIT) plus Coda's local direct-import recipe of 23 October 2026"
  updated: "31 October 2026: OpenJKDF2-MotS-Fixes engine notes and Coda's agent workspace for scripted play"
---

# JK / MotS Model Workshop

Help Andrei choose a method, then build or fix the model. Offer a few useful routes with a recommendation, the expected effort, the visual tradeoffs and the target compatibility. Don't make him choose among every tool or answer a long questionnaire before work starts. Keep an existing working model and improve its weakest part instead of regenerating it.

This is Red's fork of Coda's workflow. The research and method are hers and the community's (see [CREDITS.md](CREDITS.md)); the routes are rebuilt for Red's tools ([red-routes.md](references/red-routes.md)).

## Pick the route

| Andrei's priority | Recommend | Useful alternative |
| --- | --- | --- |
| Fast playable result, familiar humanoid proportions | Reskin or reshape a working stock-rig model | Licensed donor split into the same rigid body parts |
| Distinct creature with familiar movement | Stock skeleton plus authored silhouette, rigid attachments and deliberate texture space | Partial generated parts plus manual limbs and cleanup |
| Unusual proportions or new movement | Custom hierarchy and a matched KEY/PUP set, following the *method* TDIR demonstrated | Approximate the silhouette on stock animation for a first release |
| Detailed mechanical or organic model | Keep a detailed source; reduce a separate game mesh, then bake colour and selected relief | Direct low-poly modelling with painted textures |
| Highest fidelity on a modern engine | A separate enhanced-engine asset profile | A conservative retail edition alongside it |
| New first-person hands or weapon | Author and test the actual view-model path | A third-person-only skin, with its scope stated |

Explain the recommendation in ordinary words, for example: "I'd keep the stock movement and build a new head and torso. You get something playable sooner; a custom rig would fix the limb proportions but needs a new animation set." For more depth, read [methods-and-options.md](references/methods-and-options.md).

## Inspect or render an existing model

Use the **Blender-Sith Agentic fork directly**, in a disposable background process in the cloud workspace, through `scripts/render_3do.py`. Setup and inputs are in [red-routes.md](references/red-routes.md), and Coda's recipe in [blender-sith-fork.md](references/blender-sith-fork.md#direct-native-import-for-inspection-and-screenshots).

- **Inputs:** recover the exact package and version first. Stage the 3DO, the MATs it names and the intended CMP into an isolated job tree. The importer searches model-relative folders before the ones you pass, and a missing MAT leaves a placeholder while the import still "succeeds". The receipt lists every candidate and every placeholder.
- **Scope:** only geoset 0 is imported. Examine other geosets separately, and never call one Blender view an all-LOD or runtime check.
- **Presentation:** keep the native geometry and textures in the inspection scene (`--save-blend` keeps the unaltered import). Presentation changes go into recorded copies.
- **Deliver:** inspected HD views (front, side, rear, detail), the editable scene when useful, and a short account of verified issues versus untested runtime behaviour. Red looks at every PNG before describing it.
- **If the direct import fails,** keep the failure, repair the adapter or report the blocker. Don't silently switch to a hand-rolled reconstruction.

## Work from source to game

1. **Reference and plan.** Pin the exact design and variant, lawful starting assets, and the features that must survive at game size. Use the prop-reference skill for source-grounded reference images. Choose stock or custom animation before spending time on fine geometry.
2. **Build the parts.** Blender modelling, licensed donor geometry, or generated parts where they help ([partial-generation.md](references/partial-generation.md)). Inspect joints, fingers, teeth, sockets, thin sheets and hidden backs.
3. **Make surfaces readable.** Hand painting, procedural colour, projection or a high-to-low bake; a neutral colour pass as the reusable base ([textures-and-imagegen.md](references/textures-and-imagegen.md)).
4. **Prepare the game mesh.** Keep silhouette and joints, cut invisible detail, allocate UV space deliberately, and export from a prepared duplicate ([blender-export-and-baking.md](references/blender-export-and-baking.md)). The fork preserves corner-normal splits, so check the exported vertex budget after hardening edges.
5. **Bind the animation contract.** The rigid hierarchy and indexed KEY tracks must agree on indices, parents, pivots and PUP references. Run `inspect_contract.py --model candidate.3do --keys …` with every relevant KEY, plus `--reference-keys` and `--detail-start` when appending detail to a preserved rig ([compatibility.md](references/compatibility.md)).
6. **Integrate the intended role:** SP actor, SP player replacement, MP selectable skin, first-person view model or third-person weapon. Package only what each role uses; derive stock resources from Andrei's installation ([runtime-and-packaging.md](references/runtime-and-packaging.md)).
7. **Review in the target.** Check the source, the exported file, texture mapping and the relevant movement and weapon cases. Then test with an engine still in Red's workspace, or through Andrei, Coda, or computer use when he asks ([testing-methods.md](references/testing-methods.md), [red-routes.md](references/red-routes.md#testing-in-the-target-game)). Animated skins and sound need [the SM Sith Lord-informed checks](references/smsithlord-validation-lessons.md).

The sequence adapts to the task. A texture change doesn't need a generation pipeline, and a source-only request doesn't need deployment.

## Help, reporting and boundaries

- **Reviews** of views, anatomy or construction plans go through **coastline-review**. Send actual renders and references; verify consequential findings yourself.
- **Windows-only steps** go to Coda in a handoff file: her ComfyUI API bridge and Windows Blender. Engine stills can run in Red's own workspace through the **jk-level-workshop** OpenMotS route, once Andrei supplies his MotS files.
- **Findings:** `prepare_finding.py` makes a local draft for Coda's research address. It's sent only when Andrei approves that exact message and route.
- **Authorship:** Red inspects, renders, validates, converts and fixes Andrei's models and existing mods, and builds original creatures and props. She doesn't author new geometry or textures depicting a known franchise character or a real person's likeness; for those she plans, researches, checks and reviews, and the authoring is Andrei's or Coda's.
- **Assets:** retail and mod assets stay local, in Red's scratch space, and are never redistributed. Never write into Coda's checkouts or `.codex`.

## Research to consult when needed

- **Choosing a method:** [methods-and-options.md](references/methods-and-options.md), [research-index.md](references/research-index.md)
- **Blender-Sith:** [blender-sith-fork.md](references/blender-sith-fork.md) (fixes, direct import, limits), [blender-sith-audit.md](references/blender-sith-audit.md)
- **Community methods:** [community-modeling-research.md](references/community-modeling-research.md), [community-surface-research.md](references/community-surface-research.md), [community-discord-model-methods.md](references/community-discord-model-methods.md), [additional-geometry-animation.md](references/additional-geometry-animation.md), [additional-surface-methods.md](references/additional-surface-methods.md)
- **Native packages and tools:** [downloaded-corpus.md](references/downloaded-corpus.md), [downloaded-model-integration.md](references/downloaded-model-integration.md), [downloaded-tools-geometry.md](references/downloaded-tools-geometry.md), [downloaded-material-tools.md](references/downloaded-material-tools.md)
- **History and case studies:** [jke-tdir-shred-research.md](references/jke-tdir-shred-research.md), [tdir-beta-research.md](references/tdir-beta-research.md), [mortal-kombat-research.md](references/mortal-kombat-research.md), [terminator-case-study.md](references/terminator-case-study.md)
- **Sources:** [source-archive.md](references/source-archive.md) and `references/evidence/` (portable ledgers with hashes)

OpenJKDF2, patched JKE, original JK and original MotS are separate targets. An attractive Blender view, a parseable 3DO, a successful hosted start and a connected multiplayer session each establish something different. Say which one you actually have.
