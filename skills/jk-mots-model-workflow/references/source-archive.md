# Source archive and offline research

When an original source disappears, use the confirmed snapshot below, the pinned
implementation reference in the [source index](evidence/source-archive-index.json),
or the locally included analysis and licensed code. The workshop download retains
the research. An archived page preserves a historical source; a newer engine or
tool still needs its own compatibility check.

The 30 September 2026 index covers **93 external links** from the research library
and credits. **25 Wayback pages have confirmed working replays.** It records the
original URL, title, purpose, access date, response status and confirmed archive URL
for each source. Twenty-six entries have observed commit pins; all 28 distinct
pin/maintained-alternative URLs checked successfully. Pins preserve a revision's
identity while the host remains available; they are not automatically local copies.

## What remains usable offline

| Need | Included material |
| --- | --- |
| Choose a modeling method without reopening a forum | [Methods and options](methods-and-options.md), [compatibility](compatibility.md), and [JKE/TDIR/Shred research](jke-tdir-shred-research.md) preserve the practical synthesis, attributed historical advice, identified input hashes and measured model examples |
| Reconstruct texture/bake decisions | [Blender export and baking](blender-export-and-baking.md), [textures](textures-and-imagegen.md), and the [Terminator case study](terminator-case-study.md) preserve the recipe and what was actually checked |
| Understand local mesh generation and automation | [Partial generation](partial-generation.md) and [local generation automation](local-generation-automation.md), plus the selected source files below |
| Repeat a meaningful model test | [Testing methods](testing-methods.md), [runtime and packaging](runtime-and-packaging.md), and the bundled runtime-test-plan template |
| Inspect the implementation behind a technical claim | [Licensed source manifest](evidence/source-snapshots.json) and [source bundle guide](../assets/research-sources/README.md) |

The focused implementation bundle contains seven source files or source extracts
and three upstream license texts, totaling 190,496 bytes. It includes ComfyUI's
native Hunyuan nodes, GLB saver and server; trellis.cpp preprocessing and CLI; and
OpenJKDF2 KEY loading plus the studied texture-dimension function. Every entry has
an exact commit, origin, SHA-256, local path and retained license. The small renderer
function is explicitly an extract; it is not the complete graphics implementation.
These files are reading evidence, not standalone installed applications.

Upstream licenses continue to govern those copies. The workshop's MIT license does
not replace GPL or other component terms. The archive contains no commercial game
archives, community model artwork, full forum exports, videos, model weights or
private conversations.

## Short knowledge notes

These original notes preserve decisions that remain useful when a source is
temporarily unreachable. Detailed counts and test limits remain in the linked
research chapters; none of the notes turns a historical author observation into an
universal engine guarantee.

- **Shred18's practical mesh budget:** the August 2005 discussion treats roughly
  500 triangulated faces as an authoring limit and also recognizes a vertex limit.
  Count positions, UV entries and polygon records separately. Splitting for hard
  normals or seams can change export counts even when the visible silhouette does
  not change.
- **The July 2005 mesh-limit discussion:** contributors challenged an asserted
  total-mesh cap and supplied a larger working example. Do not substitute a forum
  recollection for an identified executable's per-mesh and animation constraints.
- **Ruthven's texture method:** several carefully painted 256-square 16-bit tiles
  can support detailed weapons. This offers a practical alternative to making one
  enormous atlas; allocation of useful UV space still matters.
- **The 2005 lighting discussion:** apparent full brightness prompted investigation
  of extra-light data, then a different lighting cause. Inspect the actual face,
  material and scene combination before removing shading from an entire model.
- **Quib Mask's later engine work:** dynamic node manipulation and lighting
  overrides belong to a documented modified-engine feature set. A model relying on
  them must declare that dependency instead of presenting the behavior as stock.
- **Sith format references:** a hierarchy node, a mesh record, a KEY allocation and
  a PUP gameplay role are different parts of the model contract. Keep mesh indices
  and parent/child indices consistent, preserve the intended animation-addressed
  slots, and validate roles such as aim/fire separately from geometric appearance.
- **TDIR and JKE:** the preserved research distinguishes a coordinated custom
  character/animation system from detailed familiar-rig construction. TDIR's
  alternative body branches need matching tracks; JKE's rigid detail children do
  not become cloth simulation. Release identity and supported installation matter.
- **Blender's geometry interfaces:** evaluated geometry and source-mesh geometry
  are different inputs. Per-corner normals carry sharp/custom shading distinctions
  that a single averaged vertex normal loses. Bake/export a prepared copy and inspect
  the resulting vertex budget.
- **ComfyUI's protocol:** prompt acceptance supplies a job identifier, not proof of
  a completed mesh. Match per-job history and output descriptors, handle errors,
  and inspect the file before returning success. Pinned implementation snapshots
  preserve the corresponding node and saver contracts.
- **Wine, Xvfb and WSL:** a private graphical display can run an original executable
  without using the main desktop, while a null renderer cannot demonstrate texture
  appearance. Record the actual rendering backend. WSLg's visible GUI support is a
  different route from a private Xvfb test display.
- **Jon`C's Windows color-error diagnosis:** a conflicting application-compatibility
  database was implicated in a historical JK startup problem. The conditional
  removal command targets that exact custom database; it is not a reason to reduce
  textures to 256 colors or remove unrelated compatibility settings.
- **BodyParts3D and inherited art:** a donor's declared license and the final
  project's rights are separate checks. Preserve source attribution and applicable
  share-alike terms; a portfolio credit alone does not grant redistribution rights.

## Confirmed page snapshots

The dates below identify the archived page, not the date of the original post or
the date this workflow was tested. A release page snapshot does not establish that
its linked downloads were also archived.

| Source | Original | Confirmed replay | Snapshot date |
| --- | --- | --- | --- |
| ChatGPT on the web / ChatGPT Learn | [Original](https://learn.chatgpt.com/docs/web) | [Wayback](https://web.archive.org/web/20260928052335/https://learn.chatgpt.com/docs/web) | 2026-09-28 |
| Depsgraph(bpy_struct) - Blender Python API | [Original](https://docs.blender.org/api/5.0/bpy.types.Depsgraph.html) | [Wayback](https://web.archive.org/web/20260302160941/https://docs.blender.org/api/5.0/bpy.types.Depsgraph.html) | 2026-03-02 |
| Mesh(ID) - Blender Python API | [Original](https://docs.blender.org/api/5.0/bpy.types.Mesh.html#bpy.types.Mesh.corner_normals) | [Wayback](https://web.archive.org/web/20260305051829/https://docs.blender.org/api/5.0/bpy.types.Mesh.html) | 2026-03-05 |
| Jedi Knight Unofficial Specs: PUP | [Original](https://www.massassi.net/jkspecs/pup.htm) | [Wayback](https://web.archive.org/web/20260729000321/https://www.massassi.net/jkspecs/pup.htm) | 2026-07-29 |
| Jedi Knight Sith Engine Specs: Limits | [Original](https://jksith.wikidot.com/limits) | [Wayback](https://web.archive.org/web/20240828100810/http://jksith.wikidot.com/limits) | 2024-08-28 |
| Shred18 on practical 3DO limits | [Original](https://forums.massassi.net/Editing_Forums/Jedi_Knight_and_Mysteries_of_the_Sith_Editing_Forum/thread_34814_page_1.html) | [Wayback](https://web.archive.org/web/20260923112212/https://forums.massassi.net/Editing_Forums/Jedi_Knight_and_Mysteries_of_the_Sith_Editing_Forum/thread_34814_page_1.html) | 2026-09-23 |
| Jedi Knight Unofficial Specs: 3DO | [Original](https://www.massassi.net/jkspecs/3do.htm) | [Wayback](https://web.archive.org/web/20260729000321/https://www.massassi.net/jkspecs/3do.htm) | 2026-07-29 |
| Jedi Knight Enhanced — Massassi release | [Original](https://www.massassi.net/levels/files/3087.shtml) | [Wayback](https://web.archive.org/web/20260729022125/https://www.massassi.net/levels/files/3087.shtml) | 2026-07-29 |
| MotS+ — Massassi release | [Original](https://www.massassi.net/levels/files/3157.shtml) | [Wayback](https://web.archive.org/web/20260728212608/https://www.massassi.net/levels/files/3157.shtml) | 2026-07-28 |
| Community discussion of 3DO mesh limits | [Original](https://forums.massassi.net/Editing_Forums/Jedi_Knight_and_Mysteries_of_the_Sith_Editing_Forum/thread_33977_page_1.html) | [Wayback](https://web.archive.org/web/20260209022116/https://forums.massassi.net/Editing_Forums/Jedi_Knight_and_Mysteries_of_the_Sith_Editing_Forum/thread_33977_page_1.html) | 2026-02-09 |
| Ruthven on high-resolution weapon textures | [Original](https://forums.massassi.net/Editing_Forums/Jedi_Knight_and_Mysteries_of_the_Sith_Editing_Forum/thread_35901_page_1.html) | [Wayback](https://web.archive.org/web/20260416135809/https://forums.massassi.net/Editing_Forums/Jedi_Knight_and_Mysteries_of_the_Sith_Editing_Forum/thread_35901_page_1.html) | 2026-04-16 |
| Model extra-light and lighting discussion | [Original](https://forums.massassi.net/Editing_Forums/Jedi_Knight_and_Mysteries_of_the_Sith_Editing_Forum/thread_35291_page_1.html) | [Wayback](https://web.archive.org/web/20260121085746/https://forums.massassi.net/Editing_Forums/Jedi_Knight_and_Mysteries_of_the_Sith_Editing_Forum/thread_35291_page_1.html) | 2026-01-21 |
| Quib Mask: Quadranscentennial features | [Original](https://forums.massassi.net/Editing_Forums/Jedi_Knight_and_Mysteries_of_the_Sith_Editing_Forum/thread_68242_page_3.html) | [Wayback](https://web.archive.org/web/20250125165345/https://forums.massassi.net/Editing_Forums/Jedi_Knight_and_Mysteries_of_the_Sith_Editing_Forum/thread_68242_page_3.html) | 2025-01-25 |
| The Destruction is Real 1.1 file - ModDB | [Original](https://www.moddb.com/mods/the-destruction-is-real/downloads/the-destruction-is-real-111) | [Wayback](https://web.archive.org/web/20240630145126/https://www.moddb.com/mods/the-destruction-is-real/downloads/the-destruction-is-real-111) | 2024-06-30 |
| ComfyUI Hunyuan3D-2 Examples - ComfyUI | [Original](https://docs.comfy.org/tutorials/3d/hunyuan3D-2) | [Wayback](https://web.archive.org/web/20260914164419/https://docs.comfy.org/tutorials/3d/hunyuan3D-2) | 2026-09-14 |
| ComfyUI Server Routes (HTTP and WebSocket API) - ComfyUI | [Original](https://docs.comfy.org/development/comfyui-server/comms_routes) | [Wayback](https://web.archive.org/web/20260924113622/https://docs.comfy.org/development/comfyui-server/comms_routes) | 2026-09-24 |
| ComfyUI Server Messages (WebSocket API) - ComfyUI | [Original](https://docs.comfy.org/development/comfyui-server/comms_messages) | [Wayback](https://web.archive.org/web/20260924113939/https://docs.comfy.org/development/comfyui-server/comms_messages) | 2026-09-24 |
| 利用許諾 - BodyParts3D / LSDB Archive | [Original](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html) | [Wayback](https://web.archive.org/web/20260905143812/https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html) | 2026-09-05 |
| Run Linux GUI apps with WSL / Microsoft Learn | [Original](https://learn.microsoft.com/en-us/windows/wsl/tutorials/gui-apps) | [Wayback](https://web.archive.org/web/20260825162410/https://learn.microsoft.com/en-us/windows/wsl/tutorials/gui-apps) | 2026-08-25 |
| XVFB(1) manual page | [Original](https://xorg.freedesktop.org/archive/X11R7.0/doc/html/Xvfb.1.html) | [Wayback](https://web.archive.org/web/20211027192109/https://xorg.freedesktop.org/archive/X11R7.0/doc/html/Xvfb.1.html) | 2021-10-27 |
| How do I install Jedi Knight Mysteries of the Sith? – Star Wars Support | [Original](https://support.starwars.com/hc/en-us/articles/360000721246-How-do-I-install-Jedi-Knight-Mysteries-of-the-Sith) | [Wayback](https://web.archive.org/web/20240229042116/https://support.starwars.com/hc/en-us/articles/360000721246-How-do-I-install-Jedi-Knight-Mysteries-of-the-Sith) | 2024-02-29 |
| General - Dege's stuffs | [Original](https://dege.freeweb.hu/dgVoodoo2/ReadmeGeneral/) | [Wayback](https://web.archive.org/web/20260903232733/https://dege.freeweb.hu/dgVoodoo2/ReadmeGeneral/) | 2026-09-03 |
| Jon`C: conflicting Windows compatibility database | [Original](https://forums.massassi.net/Main_Massassi_Forums/Discussion_Forum/thread_67886_page_33.html) | [Wayback](https://web.archive.org/web/20241010090110/https://forums.massassi.net/Main_Massassi_Forums/Discussion_Forum/thread_67886_page_33.html) | 2024-10-10 |
| Windows color-error follow-up | [Original](https://forums.massassi.net/Main_Massassi_Forums/Discussion_Forum/thread_67886_page_34.html) | [Wayback](https://web.archive.org/web/20240909111131/https://forums.massassi.net/Main_Massassi_Forums/Discussion_Forum/thread_67886_page_34.html) | 2024-09-09 |
| Install/Uninstall Custom Databases (Windows 10) - Windows 10 / Microsoft Learn | [Original](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/deployment/compatibility/installing-and-uninstalling-custom-compatibility-databases-in-compatibility-administrator) | [Wayback](https://web.archive.org/web/20260219140010/https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/deployment/compatibility/installing-and-uninstalling-custom-compatibility-databases-in-compatibility-administrator) | 2026-02-19 |

## Sources without a confirmed replay

The full index keeps unsuccessful or unattempted archive checks visible. The TDIR
Massassi landing page has no confirmed replay in this index, while the separately
identified TDIR 1.1 ModDB page does. The SDBINST command-page snapshot was listed by
the archive but its replay was unavailable during this check; it is not counted
among the confirmed pages. The Microsoft database-management page and original
Massassi discussion provide working archived companions.

The Blender baking link containing `/UATEST/` and the ChatGPT Projects page have no
confirmed snapshot here. Several original endpoints denied the automated request,
and some GitHub project links returned anonymous 404 despite maintained GitLab
alternatives. Those statuses do not prove that a project was deleted. Later archive
lookups were rate-limited; no archive-submission queue was treated as a saved page.

For code, prefer a supplied commit pin, a verified maintained alternative, or the
licensed local snapshot. The index retains live release/tag links when no exact
commit was independently established. Media and game-asset download URLs remain
source references; they are not bundled or represented as preserved downloads.

If a source changes a conclusion, record the exact source revision and update the
analysis through the normal [research update/report process](updates-and-reporting.md).
Keep old source identity when it explains an earlier result. A new link or newer
archive should improve the evidence, not silently rewrite which release was studied.
