# Notice: JK / MotS Model Workshop, Red's fork

Forked from the [JK / MotS Model Workflow](https://gitlab.com/codalilitari/jk-mots-model-workflow) 1.3 (commit `e980010`), which Andrei directed and Coda built. `LICENSE` (MIT, with its scope note) and `CREDITS.md` are upstream's. Community authors, game rights holders and upstream tools keep their own rights, as CREDITS.md and LICENSE explain.

## What changed

- **Verbatim from upstream 1.3:**
  - every file in `references/` and `references/evidence/`, except the two below;
  - `references/smsithlord-validation-lessons.md`;
  - every file in `assets/`, including the licensed research-source snapshots (byte-identical, matching `references/evidence/source-snapshots.json`).
- **From Coda's newer local install (23 October 2026):** `references/blender-sith-fork.md` and `references/blender-export-and-baking.md`, which add the direct-import recipe. Copied from Andrei's computer, read-only; Coda's install was not modified. In `blender-sith-fork.md`, two machine-specific paths are generalized (31 October 2026) so the file can be published.
- **Scripts:** `inspect_contract.py`, `probe_blender_sith.py` and `prepare_finding.py` are unchanged. `test_contract.py` and `test_prepare_finding.py` are upstream's tests, with import paths adjusted to this layout.
- **Edited:**
  - `CREDITS.md`: link paths only, from `skills/jk-mots-model-workflow/…` to this folder's layout.
  - `references/local-generation-automation.md`: a fork note at the top, and its link to `comfy_bridge.py` now points to upstream.
- **New, by Red (MIT):** `SKILL.md` (rewritten), `references/red-routes.md`, `scripts/render_3do.py` and `scripts/test_render_3do.py`.
- **Not included:** `comfy_bridge.py`, `research_updates.py`, `research-update-state.json`, `PACKAGE-MANIFEST.json`, `agents/openai.yaml`.

## The Blender-Sith fork

Red's render script loads Coda's [Blender-Sith Agentic](https://gitlab.com/codalilitari/blender-sith) fork at run time, from a job-local copy of Andrei's checkout. The fork is GPL-3.0-or-later (Crt Vavros, with fork changes by Coda and Andrei) and is **not** bundled in this plugin. `render_3do.py` is separate MIT code that calls the fork's public import function in the same process.
