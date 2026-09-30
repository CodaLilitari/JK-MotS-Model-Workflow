# Preserved implementation evidence

These are focused source snapshots for offline inspection of the model workflow's claims. They are not standalone applications, a Comfy installation, or game resources. The seven source artifacts and three license files total **190,496 bytes**. Source comments and license text are retained unchanged; the one OpenJKDF2 function excerpt is explicitly identified below.

The [snapshot manifest](../../references/evidence/source-snapshots.json) records original repository URLs, exact revisions, original paths, retained file sizes and SHA-256 hashes, license locations, and the excerpt's original line range. The [source archive guide](../../references/source-archive.md) covers the broader research library and archived web links.

| Project and revision | Retained source | Why it is useful |
|---|---|---|
| ComfyUI `dec5d9450a5290bcf63430409ea41018e67f41c3` | [nodes_hunyuan3d.py](comfyui/nodes_hunyuan3d.py) | Inspect native Hunyuan conditioning, latent dimensions, decode and extraction. |
| Same ComfyUI revision | [nodes_save_3d.py](comfyui/nodes_save_3d.py) | Inspect SaveGLB and its `3d` output descriptors. |
| Same ComfyUI revision | [server.py](comfyui/server.py) | Inspect exact-class schemas, image upload naming, prompt submission and history routes. |
| trellis.cpp `06fc9000719c912ddc4929d21db075972c26ac3e` (`v0.6.0`) | [preprocess.cpp](trellis-cpp/preprocess.cpp) | Inspect foreground bounds, alpha handling, square cropping and normalization. |
| Same trellis.cpp revision | [trellis_cli.cpp](trellis-cpp/trellis_cli.cpp) | Inspect the `--no-texture` branch and the complete cleanup/export sequence. |
| OpenJKDF2 `0dbd1ea8bb2211c158f6af928b5e4fb14dfa0dac` | [rdKeyframe.c](openjkdf2/rdKeyframe.c) | Inspect KEY allocation and indexed track parsing in this source port. |
| Same OpenJKDF2 revision | [std3D_GetValidDimension-excerpt.c](openjkdf2/std3D_GetValidDimension-excerpt.c) | Exact complete function from `src/Platform/GL/std3D.c`, lines2914–2919; documents the native GL size clamp. This alone does not establish the entire UV path or retail behavior. |

The files are evidence from particular revisions. Their presence does not mean the dependencies they import are installed, that they can run independently, or that a newer version behaves the same way. Follow the workflow's [generation](../../references/local-generation-automation.md) and [compatibility](../../references/compatibility.md) guidance when applying these observations.

## Original licenses and credit

- **ComfyUI and its contributors:** [original GNU GPL version3 license text](comfyui/LICENSE). These retained source files remain under their upstream license. They are separately distributed implementation evidence, not relicensed under the workshop's MIT license.
- **trellis.cpp, Piotr Wilkin:** [original MIT license and copyright notice](trellis-cpp/LICENSE). Its runtime code license does not grant rights to model weights, DINOv3, input images or character designs.
- **OpenJKDF2 contributors:** [original project license and notices](openjkdf2/LICENSE.md). That notice preserves the distinction between OpenJKDF2 code, original game properties and separately licensed third-party libraries. No game assets are included here.

Except for extracting the explicitly marked OpenJKDF2 function and flattening file locations into these project folders, the retained source bytes are unchanged. Full original source is identified by the commit URLs in the manifest. The package updater changes research prose/data only; it does not install or update these source-code snapshots. A refreshed source snapshot ships with a complete versioned package.
