# JK / MotS Model Workshop

A distributable workflow and Codex skill for **Jedi Knight: Dark Forces II** and **Mysteries of the Sith** character, creature, player-skin, weapon and environment-prop models. It helps you choose a method and build the result: stock-rig remodeling, licensed donor assembly, partial local generation, custom animation, and detailed-source reduction/baking. Single-player and multiplayer model integration are covered. Environment props hand off to the separate level and COG workflows for sectors, placement, doors/lifts and multiplayer behavior.

Start with the [method and options guide](skills/jk-mots-model-workflow/references/methods-and-options.md), or let Codex use the [skill](skills/jk-mots-model-workflow/SKILL.md). The [research library](skills/jk-mots-model-workflow/references/research-index.md) explains the choices, including the different lessons of TDIR, JKE and Shred's work.

[GitLab repository](https://gitlab.com/codalilitari/jk-mots-model-workflow) · [GitHub repository](https://github.com/CodaLilitari/JK-MotS-Model-Workflow) · [Portfolio and direct downloads](https://richard-pemberton-research.darkahn.chatgpt.site/projects/jk-mots-model-workflow/)

Version **1.6.0** adds the shared current-install resolver and updates the [Blender-Sith workflow](skills/jk-mots-model-workflow/references/blender-sith-fork.md) for extension **1.1.0 / v1.1.0-coda.1**. Use explicit API modules and JKDF2/MOTS animation targets, export inspected baked-image MATs with a real CMP, retain recovery diagnostics, and account for current normals, linear colors, UV units and numeric precision. Verified integration/CI, published assets, installed copies and game acceptance remain separate states. Research revision is **2026111301**; this feed requires the complete **1.6.0** skill because a research-only update cannot install its new resolver or helper.

Version 1.5.0 added measured Tripo topology ledgers and [environment-prop authoring](skills/jk-mots-model-workflow/references/environment-props-to-jk.md) from Red and Wren's recent work, plus a separate level/resource handoff study from Dot Lilitari's Kestrel Relay. That research is preserved: distinguish requested quads, mixed polygon outputs, triangulated counts and final native budgets; preserve accepted UV layouts and inspect actual placement dimensions. The historical 1.0.4 radius/pivot evidence remains attributed and separate from the new integration's tests.

Version 1.4.1 adds [same-name material editions](skills/jk-mots-model-workflow/references/same-name-material-editions.md): a measured historical example of separate indexed and RGB565 packages retaining one internal character identity. TIE's original statement, exact archive comparisons and source-supported loading behavior remain separate from the real mixed-client tests needed for a new release.

Version 1.4.0 added the current [Blender-Sith GitHub fork and install route](skills/jk-mots-model-workflow/references/blender-sith-fork.md), [Red’s hosted Tripo conversion methods](skills/jk-mots-model-workflow/references/tripo-to-jk.md), and [Lily/Red/Andrei’s Suno character-voice method](skills/jk-mots-model-workflow/references/generated-character-voice.md). It also preserves the newer direct textured-import instructions from the installed skill. No new game test or generation run is implied.

Version 1.3 added [research from the downloaded material collection](skills/jk-mots-model-workflow/references/downloaded-corpus.md): a hash-checked inventory of 2,308 JK/MotS packages, selected native model/material/animation analysis, original tool manuals/source, and attributed community methods. The package includes the portable evidence ledgers; original third-party game/mod binaries remain separate.

## What is inside

- Practical choices for manual modeling, stock assets, donor meshes, Hunyuan/TRELLIS parts and ComfyUI workflows.
- Texture painting/generation, authored UVs, color and geometry baking, reduction, normals and game-scale review.
- Blender UI, background scripts, optional MCP and Blender-Sith export methods, including the distinction between wrappers and source patches.
- Rigid hierarchy, KEY/PUP, material/UV interpretation, retail versus enhanced-engine options and reversible packaging.
- ChatGPT Pro advisory and bounded delegation, with a reusable review packet.
- Research references, source credits, small read-only tools and synthetic exporter probes.
- Attributed community methods for 3DO construction, hierarchy/pivots, animation events, POV hands, MAT/palette conversion, UVs, mipmaps and shading diagnosis.
- Historical TDIR / DBZ 4.0 and Mortal Kombat skin investigations, with verified archive contents, exact recovery leads and unresolved findings kept distinct.
- Original-retail Windows and WSL/Wine test methods, hidden graphical and headless source-port tests, idle-camera captures, 8-bit material and renderer matrices, and conditional launch/wrapper repairs.
- A local ComfyUI bridge, portfolio research-update checker, and optional findings-report drafts with explicit per-message sending consent.

The package contains instructions, original analysis and tools. Supply your own game installation, model inputs and optional local model weights. Third-party game/mod assets and private conversations are not bundled.

## Install the skill

Download and extract **JK-MotS-Model-Workflow-1.6.0.zip**. This one package contains the workflow, complete research, installable Codex skill, tools and tests. Copy its `skills/jk-mots-model-workflow` folder into the personal skills directory used by your Codex installation. That folder includes `SKILL.md`, all references, scripts, notices and the generated update baseline. In this project's tested desktop setup the personal directory is `~/.codex/skills`; use the location configured by your own client. Restart or refresh skill discovery if required. No API key or paid model is needed to use the skill. Installing this workflow does not itself install Blender-Sith or create the private current-install manifest.

PowerShell, from an extracted complete release ZIP:

```powershell
Copy-Item -LiteralPath '.\skills\jk-mots-model-workflow' -Destination "$HOME\.codex\skills\jk-mots-model-workflow" -Recurse
```

If that destination already exists, compare versions before replacing it. You can also keep the source repository anywhere and ask Codex to read its `SKILL.md` directly; source checkouts can check research updates but should install a release ZIP to obtain the generated update baseline before applying them.

Example:

> Use $jk-mots-model-workflow. I want a new MotS multiplayer creature with stock movement. Give me a fast route and a higher-detail route, recommend one, and explain which parts could benefit from local generation.

The folder follows the documented skill format of `SKILL.md` plus optional references, scripts and assets. [OpenAI skill documentation](https://developers.openai.com/plugins/concepts/skills).

## Run the lightweight tools

Python 3.10+ is sufficient for the contract inspector and package builder; the current-install resolver requires Python 3.11+ for manifest parsing. Blender is needed for Blender scripts. No generation job starts automatically.

```text
python skills/jk-mots-model-workflow/scripts/inspect_contract.py --model candidate.3do --keys idle.key walk.key
python -m unittest discover -s tests -v
python -m unittest discover -s skills/jk-mots-model-workflow/scripts -p test_resolve_install.py -v
python tools/build_release.py --output /absolute/external/release-output
```

Read each tool's `--help` and the relevant reference before using it. A successful contract check does not certify game behavior.

Release checks and their limits are recorded in [VALIDATION.md](VALIDATION.md). One ZIP contains the research, skill, tests and package builder. The optional Blender-Sith extension is a separate add-on installed into Blender.

**The ZIP includes the complete research corpus for local Codex use.** Readable portfolio pages and external source links supplement those files. The [update/reporting guide](skills/jk-mots-model-workflow/references/updates-and-reporting.md) explains automatic checks when the skill is used, optional research-only updates, and optional reports to the source. Nothing is emailed automatically.

## Research and compatibility

The research preserves measurements, their source versions and the boundaries of the tests actually performed. TDIR custom rigs, JKE's historical patch requirement, Shred's art choices, OpenJKDF2 behavior and unmodified retail testing answer different questions. Use them to select and troubleshoot a route rather than assuming one universal polygon, node or texture rule.

The original Blender-Sith audit found unchanged upstream copies plus project-side wrappers. Workflow 1.1.0 introduced the focused fork; workflow 1.6.0 documents the later add-on 1.1.0 integration of upstream `01ff4bd` with retained Coda fixes and automation. These workflow and add-on version numbers are separate. The [original audit](skills/jk-mots-model-workflow/references/blender-sith-audit.md) remains dated evidence, while the [current guide](skills/jk-mots-model-workflow/references/blender-sith-fork.md) explains changed APIs and remaining limits. Blender itself is not forked.

Direction and project work: Andrei Pemberton. Synthesis and engineering collaboration: Coda (Codex Lily). Source authors and upstream projects are credited in [CREDITS.md](CREDITS.md) and beside the relevant research. See [LICENSE](LICENSE) for this package's original material and the boundaries around cited third-party work.


## Lessons credited to SM Sith Lord

See [the original integration and validation notes](skills/jk-mots-model-workflow/references/smsithlord-validation-lessons.md) for lessons
from SM Sith Lord / COG Factory applied to this project. Source inspection,
automated authoring checks and actual game observations remain separate.
