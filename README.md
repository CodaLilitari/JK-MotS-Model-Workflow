# JK / MotS Model Workshop

A distributable workflow and Codex skill for **Jedi Knight: Dark Forces II** and **Mysteries of the Sith** character, creature, player-skin and weapon models. It helps you choose a method and build the result: stock-rig remodeling, licensed donor assembly, partial local generation, custom animation, and detailed-source reduction/baking. Single-player and multiplayer integration are covered; level design is outside its scope.

Start with the [method and options guide](skills/jk-mots-model-workflow/references/methods-and-options.md), or let Codex use the [skill](skills/jk-mots-model-workflow/SKILL.md). The [research library](skills/jk-mots-model-workflow/references/research-index.md) explains the choices, including the different lessons of TDIR, JKE and Shred's work.

[GitLab repository](https://gitlab.com/codalilitari/jk-mots-model-workflow) · [GitHub repository](https://github.com/CodaLilitari/JK-MotS-Model-Workflow) · [Portfolio and direct downloads](https://richard-pemberton-research.darkahn.chatgpt.site/projects/jk-mots-model-workflow/)

## What is inside

- Practical choices for manual modeling, stock assets, donor meshes, Hunyuan/TRELLIS parts and ComfyUI workflows.
- Texture painting/generation, authored UVs, color and geometry baking, reduction, normals and game-scale review.
- Blender UI, background scripts, optional MCP and Blender-Sith export methods, including the distinction between wrappers and source patches.
- Rigid hierarchy, KEY/PUP, material/UV interpretation, retail versus enhanced-engine options and reversible packaging.
- ChatGPT Pro advisory and bounded delegation, with a reusable review packet.
- Research references, source credits, small read-only tools and synthetic exporter probes.

The package contains instructions, original analysis and tools. Supply your own game installation, model inputs and optional local model weights. Third-party game/mod assets and private conversations are not bundled.

## Install the skill

Copy `skills/jk-mots-model-workflow` into the personal skills directory used by your Codex installation. In this project's tested desktop setup that directory is `~/.codex/skills`; use the location configured by your own client. Restart or refresh skill discovery if required. No API key or paid model is needed to use the skill.

PowerShell, from an extracted package:

```powershell
Copy-Item -LiteralPath '.\skills\jk-mots-model-workflow' -Destination "$HOME\.codex\skills\jk-mots-model-workflow" -Recurse
```

If that destination already exists, compare versions before replacing it. You can also keep the repository anywhere and ask Codex to read its `SKILL.md` directly.

Example:

> Use $jk-mots-model-workflow. I want a new MotS multiplayer creature with stock movement. Give me a fast route and a higher-detail route, recommend one, and explain which parts could benefit from local generation.

The folder follows the documented skill format of `SKILL.md` plus optional references, scripts and assets. [OpenAI skill documentation](https://developers.openai.com/plugins/concepts/skills).

## Run the lightweight tools

Python 3.10+ is sufficient for the contract inspector and package builder; Blender is needed for Blender scripts. No generation job starts automatically.

```text
python skills/jk-mots-model-workflow/scripts/inspect_contract.py --model candidate.3do --keys idle.key walk.key
python -m unittest discover -s tests -v
python tools/build_release.py --output dist
```

Read each tool's `--help` and the relevant reference before using it. A successful contract check does not certify game behavior.

Release checks and their limits are recorded in [VALIDATION.md](VALIDATION.md). The full ZIP contains the research, skill, tests and package builder; the smaller skill ZIP installs as one folder and retains the same reference library and evidence records.

## Research and compatibility

The research preserves measurements, their source versions and the boundaries of the tests actually performed. TDIR custom rigs, JKE's historical patch requirement, Shred's art choices, OpenJKDF2 behavior and unmodified retail testing answer different questions. Use them to select and troubleshoot a route rather than assuming one universal polygon, node or texture rule.

The Blender-Sith audit found upstream copies plus project-side wrappers and reproducible exporter problems. A source audit is not a bug fix; see [the audit](skills/jk-mots-model-workflow/references/blender-sith-audit.md) for the exact conclusion and future patch criteria.

Direction and project work: Andrei Pemberton. Synthesis and engineering collaboration: Coda (Codex Lily). Source authors and upstream projects are credited in [CREDITS.md](CREDITS.md) and beside the relevant research. See [LICENSE](LICENSE) for this package's original material and the boundaries around cited third-party work.
