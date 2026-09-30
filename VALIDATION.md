# Release validation — 1.1.0

Checked 2026-09-30. This record concerns the workflow, its small tools and the sources used to write it. It is not a newly built character or a new game-compatibility certification.

## Version 1.1.0 additions

- The full Python suite ran **45 tests: 44 passed, 1 skipped**. The existing native Windows symlink privilege limitation remains; metadata-based file/ancestor reparse cases pass.
- Twelve Comfy bridge cases use a local synthetic HTTP fixture: native-node preflight, exact image mapping, 3D/latent output records, path containment, explicit execution success, error/timeout capture, and no duplicate submission after an uncertain result. Current local Comfy sources and interpreter versions were inspected; no responsive live Comfy endpoint was found and no new inference was run.
- Eleven research-updater cases cover read-only checks, valid updates, digest corruption, local edits/deletions, version requirements, URL/path boundaries, races and handled rollback. An independent adversarial review caught a rollback overwrite of a concurrent edit and Windows filename aliases; both were corrected and independently rechecked.
- Three reporting-helper tests check exact message digest inputs, header injection refusal and decoded `.eml` readback without overwrite. The helper has no email sender/network implementation. No report was emailed; explicit user consent and an available email route remain necessary before a send.
- A single-distribution test confirms the complete ZIP contains the skill's local baseline, notices and research hashes. Copying the nested skill folder supports later research updates.
- The focused Blender-Sith fork's ten synthetic checks return **4 pass / 6 fail on unchanged upstream** and **10 pass / 0 fail on the fork**, using `bpy` 5.1.2. Root independently reviewed the patch, reran the suite, then extracted the exact installable extension ZIP and ran all ten checks again successfully. See [packaged fork evidence](skills/jk-mots-model-workflow/references/evidence/blender-sith-packaged-fork-2026-09-30.json).
- The new testing guide is a source-verified procedure collection. Existing retail, wrapper, camera and source-port results retain their original scope; publishing this guide did not execute a new retail or connected-multiplayer test.

The Blender-Sith fork changes corner-normal preservation and hexadecimal-property handling. It does not fix modifier evaluation, shared-mesh reuse, arbitrary transform semantics or every format version. There is no Blender-core or new MCP-server fork.

## Retained version 1.0.0 checks

- Skill-creator validation accepted the skill frontmatter and structure, using Python UTF-8 mode and PyYAML 6.0.3 in an isolated validation dependency directory. The skill itself has no PyYAML runtime dependency.
- Python unit suite: **18 tests run, 17 passed, 1 skipped**. Tests cover hierarchy/KEY allocation failures, reserved domains, extra but valid KEY tracks, malformed negative tracks, allowlist boundaries, deterministic ZIP contents and readback, preservation of existing archives, and reparse metadata. The native Windows symlink-creation case was skipped because this process lacked that privilege; simulated file and ancestor reparse rejection passed.
- Fresh synthetic Blender-Sith probe on `bpy` 5.1.2 against upstream `ecc90131`: all four observations completed and source hashes stayed unchanged. It reproduced ignored unapplied modifiers, lost sharp-normal identities, duplicated mesh instances and a KEY metadata callback issue. `--require-fixed` correctly failed against this unfixed upstream. See the [probe record](skills/jk-mots-model-workflow/references/evidence/blender-sith-probe-2026-09-30.json).
- Read-only parser corpus: **278 3DO hierarchies and 603 KEY files** parsed without errors. These are separate parser reads, not 881 gameplay tests or model/animation pairings. Specific T80024/custom-TDIR52 pairs passed the narrow checks.
- Two independent scenario exercises confirmed that the skill offers useful alternatives and recommends a bounded route: a stock-motion creature with a successful skull and fused teeth; and an unusual alien for original MotS with optional custom movement/first-person hands.
- A saved ChatGPT Pro advisory contributed independently checked exporter/KEY source findings. That consultation did not execute local game tests.

## Corrections made during review

An inherited recommendation to scale native UVs universally by the texture-size ratio was removed. Current guidance calibrates the actual renderer/export mapping and explains the observed 256-unit normalization counterexample.

The inspector originally ignored malformed negative `NODE` records and falsely rejected valid extra KEY tracks absent from a smaller stock model. Adversarial and original-file cases exposed both; targeted regressions now distinguish them correctly.

The historical Blender-Sith copies were upstream, with external project tools. The new focused fork was developed after that audit and is recorded separately above. Historical source/renderer/runtime findings retain their dates and specific scope in the references.

## Tool scope

`inspect_contract.py` checks declared hierarchy indices, parent cycles, KEY record/allocation consistency and optional detail-domain overlap. It does not inspect full geometry, every child/sibling traversal invariant, PUP inheritance, key timing/interpolation, material content, performance or runtime behavior. Select applicable original-rig reference KEYs before allocation padding when using `--detail-start`.

`build_release.py` packages only the exact `RELEASE_FILES.txt` allowlist, includes per-member sizes/hashes, refuses linked sources and existing archive replacement, and reads back every ZIP member. ZIP integrity is separate from technical correctness and public download availability.

The skill leaves original game data, private project histories, model weights and third-party artwork outside its package. Research measurements and original analysis are portable; other users supply their own permitted inputs and choose their target runtime.
