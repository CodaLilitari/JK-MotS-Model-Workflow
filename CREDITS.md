# Credits and source lineage

**Andrei Pemberton** directed the projects, supplied and selected inputs, judged appearance, and requested this portable collection. **Coda (Codex Lily)** assembled the workflow and research, implemented local integration and tests, and coordinated independent checking. These are contributor credits; they do not replace the original asset or tool authors.

**Lilitari / Lily**, working in ChatGPT, contributed Terminator hybrid construction, proportions, eye geometry/materials and surface-aware chrome work, plus later source/visual advisory. **Red**, working through Claude, contributed the retained Terminator conversion checkpoint and a later eye-face extra-light idea. The [Terminator case study](skills/jk-mots-model-workflow/references/terminator-case-study.md) separates their actual inherited work, reported methods, and Coda's subsequent changes. Earlier input authorship is retained; similarity or a later repair does not erase it.

## Community and upstream work

**Shred18 is a central artistic and technical reference for this workshop.** His
JKE characters, weapons and original creature work informed the guide's treatment
of silhouette, rigid body parts, texture-space allocation, detail attached to an
existing rig and levels of detail. His [hierarchy instructions](https://forums.massassi.net/Editing_Forums/Jedi_Knight_and_Mysteries_of_the_Sith_Editing_Forum/thread_32931_page_1.html)
also teach an explicit parent-chain, pivot-placement and insertion-height procedure.
Crt Vavros's [2022 Blender-Sith announcement, preserved by Brian](https://www.massassi.net/news_archive_2022-5.html),
credits Shred with early in-game model-export testing. Those contributions predate
this workflow; our synthesis and measurements do not replace his authorship.

The inspected TDIR 1.1 manual names **Shred18** as project lead, lead modeler and
lead skinner; **Gsusnme** as a skinner; **Burn** as lead animator/keyer; and
**Jenny Kitty** for modeling/skinning and conversion to the new animation system.
Together with the wider TDiR Team, they supplied the coordinated character and
animation work from which this guide's custom-rig route learns. The comparative
research distinguishes measured release assets from statements about earlier builds.

| Author/project | Contribution used in this research | Source |
| --- | --- | --- |
| Shred18 | JKE characters, modeling/texture examples, TDIR contributions and public technical advice | [Jedi Knight Enhanced](https://www.massassi.net/levels/files/3087.shtml), [3DO limits discussion](https://forums.massassi.net/Editing_Forums/Jedi_Knight_and_Mysteries_of_the_Sith_Editing_Forum/thread_34814_page_1.html) |
| TDiR Team, Shred18, Gsusnme, Burn, Jenny Kitty and credited collaborators | Original character/animation work; multiple rig-size precedent | [The Destruction Is Real](https://www.massassi.net/levels/files/2727.shtml) |
| Shimstock and separately credited MotS+ contributors | Distribution context and authorship records for later creature examples | [MotS+](https://www.massassi.net/levels/files/3157.shtml) |
| ZeqMacaw and historical patch contributors | JKE-supported patch context and resource-limit distinctions | JKE's included notices; see the [comparative research](skills/jk-mots-model-workflow/references/jke-tdir-shred-research.md) |
| Ruthven, ProdigyOddigy, Emon, JediKirby, scelestus, Quib Mask and forum contributors | Attributed texture, model-limit, lighting and version-specific technique discussions | Individual original posts linked in the [comparative research](skills/jk-mots-model-workflow/references/jke-tdir-shred-research.md) |
| Mike “LikWid” Watson, Ping_Me, PJB, CosmoDNA, F-Body, Hell Raiser, BoBo_Fett, Nikumubeki, darthslaw, Stormtrooper, Edward, Xzero, zagibu and other credited participants | Character construction, pivots, animation events/blending, skin selection and first-person methods, including corrections and reported failures | [Community character methods](skills/jk-mots-model-workflow/references/community-modeling-research.md) and its source ledger |
| EvanC, Z@NARDI, GuNbOY, XDelusion, CaptBevvil, Sige, Jim14, MikeC, SG-fan, Descent_pilot, Alco, SavageX378, RogerSpruce, Jon`C and the other source authors | Texture conversion, palette/mipmap behavior, model UVs, shading and practical exporter investigations | [Community surface methods](skills/jk-mots-model-workflow/references/community-surface-research.md) and its source ledger |
| Crt Vavros (smlu) | Blender-Sith add-on | [Source and GPL license](https://github.com/smlu/blender-sith) |
| SMLiberator | Existing normal-preservation and mesh-reuse issue reports | [Issue 13](https://github.com/smlu/blender-sith/issues/13), [issue 12](https://github.com/smlu/blender-sith/issues/12) |
| Mr. X, Discman 13, Monkey torp, and Darth Slaw / Colin Hurley | Historical Mortal Kombat skin releases, credited assistance/testing, and the recovered MK2 character models | [Historical skin research](skills/jk-mots-model-workflow/references/mortal-kombat-research.md) preserves individual package credits and contents |
| Shred, Urgon, Stormtrooper, SMLiberator, LadyEebs and other individually cited Discord participants | Dated modeling, animation, exporter, material and resource-budget methods, with hypotheses separated from measured results | [Earlier community methods](skills/jk-mots-model-workflow/references/community-discord-model-methods.md), [recent model discussion](skills/jk-mots-model-workflow/references/community-discord-research.md) |
| shinyquagsire23 and OpenJKDF2 contributors | Engine implementation used for specific source comparisons | [OpenJKDF2](https://github.com/shinyquagsire23/OpenJKDF2) |
| Massassi Temple and Sith format-documentation contributors | Preserved releases, primary discussions and format reference | [Massassi](https://www.massassi.net/), [Sith engine specs](https://jksith.wikidot.com/) |
| Jonn / Sketchfab_apk_gratis | Declared source of the ported T-800 input | [T 800 low poly (PORT/P3D)](https://sketchfab.com/3d-models/t-800-low-poly-portp3d-ce8c971d7b4240229bbebed9b53198b6) |
| Tencent Hunyuan, Comfy contributors, Microsoft TRELLIS and trellis.cpp contributors | Optional local-generation architectures and runtimes | [Hunyuan3D-2](https://github.com/Tencent-Hunyuan/Hunyuan3D-2), [ComfyUI](https://github.com/Comfy-Org/ComfyUI), [TRELLIS](https://github.com/microsoft/TRELLIS), [trellis.cpp](https://github.com/pwilkin/trellis.cpp) |
| Database Center for Life Science | BodyParts3D anatomical donor reference | [Publisher and license](https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html) |

Original LucasArts game data and all associated third-party characters/trademarks remain with their respective rights holders. The source T-800 is described as a port: its declared license is recorded, while earlier mesh authorship and franchise permissions are not independently established. No model artwork, commercial game files, donor meshes or neural weights are bundled here.

The **Red** byline on the historical Massassi tutorial is credited in the surface guide as a separate source author. No identity relationship with this project's Claude collaborator Red has been established.

The package includes original analysis and synthetic tools. Citing an author does not grant redistribution rights to that author's assets. Keep the original notices and component-level permissions when using any linked material in a new model.

## Retained implementation sources

The [offline source snapshot guide](skills/jk-mots-model-workflow/assets/research-sources/README.md) and [source manifest](skills/jk-mots-model-workflow/references/evidence/source-snapshots.json) preserve selected ComfyUI, trellis.cpp and OpenJKDF2 implementation evidence at exact revisions. ComfyUI contributors retain their GNU GPL notices; Piotr Wilkin and trellis.cpp contributors retain the MIT notice; OpenJKDF2 retains its original permissive notice. Complete source files and a labeled function excerpt are identified individually, with their upstream licenses, byte counts and hashes. These are research inputs, not newly authored workflow code or standalone applications.

The [source archive index](skills/jk-mots-model-workflow/references/source-archive.md) keeps original URLs, verified archive references and local research pointers. Archived community statements retain their original authorship.

## Additional downloaded-corpus contributions

Shred's [KeyEd discussion](https://forums.massassi.net/Editing_Forums/Jedi_Knight_and_Mysteries_of_the_Sith_Editing_Forum/thread_28662_page_1.html) adds two concrete lessons: his converted Yoda exposed idle flinches that led Hell Raiser to revise differential handling, and his invisible torso/hip control-node suggestion preserves semantic roles while changing visible geometry. His reports also motivate fresh-scene exporter comparisons, weapon-origin checks when changing pivots, and explicit comparison of geosets after a legacy re-export. These are credited contributions and historical observations; later source checks and our measurements retain separate provenance.

The additional [native package research](skills/jk-mots-model-workflow/references/downloaded-model-integration.md) credits Anthony Piggott, Al MacDonald, Galen Starfield, Alfred The Ewok, JM, Robban, Rulefreak, Andy/Darth Dude and each package's named collaborators. Milhouse's actor adaptations retain the donor credits to Al MacDonald, Red and the Skinners, and Eeth Koth. KnightSpider, Elyas Machera, Matrix__Apoc and Zymotico contribute the inspected texture/skin examples.

The additional [geometry and animation research](skills/jk-mots-model-workflow/references/additional-geometry-animation.md) credits Hell Raiser, Sige, Mr. Xeinsane, Lilguy, Jeff Walters, Pax, Darth DarKal, EvanC, molotov42 and SavageX for specific methods and counterexamples. The Tynar, CosmoDNA and Rosebud supply distinct painting and texture-repair approaches. BoBo Fett, Craig Urquhart/UGG, bahstrike, Alexei Novikov and Code Alliance, PJB, Jereth Kok, Frank Krueger, Curtis Brazzell and Ecki81 retain their tool, manual and implementation credit. The [new community diagnostics](skills/jk-mots-model-workflow/references/additional-discord-model-methods.md) preserve individual contributions by Shred, Urgon, Stormtrooper, SMLiberator, KnightCop and shimstock.
