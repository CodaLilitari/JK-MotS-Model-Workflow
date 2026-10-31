# Red's routes for JK / MotS models

Coda's workflow assumes Windows Blender, local ComfyUI and Codex workers. Red has a different kit: a Linux cloud workspace that can run Blender as a Python module, a Linux shell on Andrei's computer limited to connected folders, his Chrome, computer use on his desktop, and the other collaborators. This page maps the workflow onto that kit.

## Blender in the cloud workspace

Blender's `bpy` module runs headless in the cloud workspace, CPU only.

- **Verified on 26 October 2026:** `bpy` 5.1.2 (the version Coda's fork evidence used) installed into a scratch virtual environment. The Blender-Sith Agentic fork's 10-check background regression suite then passed 10/10, with source hashes unchanged. Cycles CPU renders worked; Workbench produced blank frames (no GPU); EEVEE worked but took about 20× longer than Cycles.
- **Set up once per session** (about 375 MB to download, about 1 GB installed):

  ```text
  python3 -m venv <scratchpad>/bpyenv
  <scratchpad>/bpyenv/bin/pip install bpy==5.1.2
  <scratchpad>/bpyenv/bin/python -c "import bpy; print(bpy.app.version_string, bpy.app.background)"
  ```

  This is a standard package-registry install into Red's own scratch space. Nothing is installed on Andrei's computer.
- **The fork:** Coda's checkout is `Blender-Sith-Agentic`, in one of Andrei's project folders (the public fork is `gitlab.com/codalilitari/blender-sith`).
  - Stage only `sith/**/*.py` and `sith/blender_manifest.toml` (26 files), plus `tests/background_regression.py` when re-running the suite.
  - Copy them into a job-local fork root in the cloud, and record their hashes.
  - Never run Git in, pull, reset, write to, or execute anything inside that checkout. It's a shared working tree that other work may be using.
- **Re-check the fork when it may have changed:** `<bpyenv python> -B tests/background_regression.py --output <new dir>` inside the job-local copy. Expect `passed: 10, failed: 0, addon_source_unchanged: true`.

## Inspecting and rendering a native model

`scripts/render_3do.py` implements Coda's direct-import recipe ([blender-sith-fork.md](blender-sith-fork.md#direct-native-import-for-inspection-and-screenshots)) and adds headless rendering:

```text
<bpyenv python> -B scripts/render_3do.py MODEL.3do --fork-root <job fork> --out <new dir> \
    --mat-dir <job>/mat --cmp <job>/misc/cmp/dflt.cmp --views front,right,rear,three-quarter --save-blend
```

- **Inputs:** stage the exact 3DO, the MATs it names and the intended CMP from Andrei's install or mod package into an isolated job tree. Retail and mod assets stay in Red's scratch space and aren't redistributed.
- **The receipt records:**
  - the Python, `bpy` and fork modules that ran, and the fork's source hashes before and after;
  - the hashes of the model and CMP;
  - native geoset, node and material counts;
  - the importer's ordered MAT search, with every candidate, the file chosen and its hash;
  - missing MATs, placeholder materials and name collisions;
  - mesh counts, camera and light settings, and the hash of each view.
- **Exit 1 means findings to read,** not a crash: missing MATs, placeholders, more than one geoset, no explicit CMP for an indexed model.
- **Axes:** Sith things look along +Y with +Z up, so `front` puts the camera on +Y. An automated test checks this on a synthetic model. A model authored another way will show it in the views.
- **Options:**
  - `--ortho` gives orthographic axis views for reference sheets.
  - `--flat` adds unlit texture-colour material copies, recorded as a presentation adaptation.
  - `--save-blend` keeps the unaltered import before any presentation change.
- **Geoset 0 only.** Check other geosets with structured diagnostics. A render is the imported geoset under recorded inspection lighting, not engine appearance, animation, LOD behaviour or runtime evidence.
- **Looking at the results:** Red reads the PNGs directly. The prop-reference skill's `composite.py` can assemble a labelled board of the views beside source references.

## Other scripts

- `inspect_contract.py` (standard library): hierarchy indices, parent cycles and KEY JOINTS allocation. Runs on the device shell beside the files.
- `probe_blender_sith.py` (needs `bpy`): Coda's synthetic exporter observations. Run it in the cloud with `--addon <job fork>/sith`.
- `prepare_finding.py`: a local draft only, addressed to Coda's findings address. Andrei sends it, or approves sending through an email route he names. Red never sends it on her own.
- **Not included:** `research_updates.py`, Coda's in-place updater. To check for newer research, read the portfolio feed or the GitLab repository, then fold changes into this fork by hand. `comfy_bridge.py` isn't included either; see the note in [local-generation-automation.md](local-generation-automation.md).

## Help that changes the result

Coda's advisory guidance ([advisory-and-delegation.md](advisory-and-delegation.md), [review-packet.md](../assets/review-packet.md)) maps to the **coastline-review** skill. That means Lily for construction, proportions and materials (her Terminator work is credited in CREDITS.md), Ma'at for method audits, and Grok for adversarial checks.

- **Send actual views and references,** not descriptions of them.
- **Windows-only work goes to Coda,** with a handoff file in the project folder: her ComfyUI API bridge and the Windows Blender install.

## Testing in the target game

Red can run OpenJKDF2-MotS-Fixes in her cloud workspace (the **jk-level-workshop** skill's engine route, `references/openmots-linux.md` there), once Andrei supplies his game files. It has two interfaces:

- **A posed still (capture-v1):** shows that the engine loads and draws the model and its MATs under engine lighting, from one camera. It needs an original test room that defines a template for the model. Coda's `new_engine_lighting_fixture.py` in SED shows the pattern; the thing itself is added with SED's `addThing`.
- **Scripted play (Coda's agent workspace, 30 October 2026):** a live single-player session with the model staged as a startup mod, driven through ordinary controls, with read-only state and screenshots, plus JSON scenario recipes and a report. Screenshots taken while walking, crouching or firing show the model animating in the engine. It runs in real time on Red's software renderer, so it isn't frame-exact, retail or GPU evidence, and it doesn't cover sound or multiplayer.

For what neither covers, the routes in order of preference:

1. **Andrei tests,** with Red's [runtime test plan](../assets/runtime-test-plan.json) cases written out exactly: build, mode, character actions, camera cases.
2. **Coda runs her capture or harness tools,** via a handoff file.
3. **Computer use on Andrei's desktop,** when he asks for it. Red launches the game and drives a short scripted case, with screenshots as evidence. Ask first, never while he's playing, and record the exact executable and profile.

Multiplayer claims need separate connected clients, every time.

## Engine changes worth knowing (OpenJKDF2-MotS-Fixes main, 29 October 2026)

Record the engine commit with any OpenJKDF2 result; these fixes change what a model looks like or whether it loads:

- **Translucent faces** (upstream #486). Faces with flag 2 (water, glass, and translucent model faces) were drawn about 65% opaque because the shader inverted their alpha. JK.EXE draws them about 35% opaque, over 65% of what's behind them. Older OpenJKDF2 screenshots overstate translucent faces.
- **Texture cache** (upstream #487). Freed materials left holes in a fixed 4,096-entry texture list, so browsing a few hundred skins (Continuum and SBX together make 282) exhausted it: untextured skins and a crawl. HD textures could also write past a full list. MotS team skins were fixed in the same change.
- **MotS puppet and animation submodes** (upstream #465 and #476): the submode arrays were too small for MotS puppets in runtime builds.
- **World model and sound caches** (fork PRs #2 and #3) now grow without moving records already loaded.

## What Red authors

- **Red does:** inspect, render, validate, convert, and fix technical problems in Andrei's models and in existing mods he supplies (hierarchy, pivots, KEY allocation, UV mapping, normals, materials, packaging); build original creatures and props.
- **Red doesn't:** sculpt or generate new geometry or textures that depict a known franchise character or a real person's likeness, such as a new Leia head.
- **For those, she still does** the planning, source research, contract checks, renders and review. The authoring itself is Andrei's or Coda's.
