# When a player skin comes apart during an idle

A player can stand normally with a saber for several seconds and then lose the whole upper body during a fidget. Before changing a waist seam, trace which numbered joint the fidget animates and which branch that joint carries in the model actually on screen.

## Reproduce the resource combination

Record the profile, model registration and whether the actor is a picker preview, local player, remote player or bot. List the GOBs in search order and identify the selected 3DO, PUP and KEY member paths and hashes. A cosmetic-only level can copy the picker’s visible body but resolve its puppet and fidgets from the base game. A private whole-pack animation test exercises a different combination. Compare both when the same skin is distributed both ways.

For the stock Jedi Knight player, aimed gun mode uses `kystand2` and its second fidget `kyidle2b`. Saber mode uses `kystand1` and `kyidle1b`. Check the selected PUP for the actual mapping. Go through each fidget, including its transition back to standing, and observe from the side and below. A character looking down toward a lower observer can add torso pitch after the KEY blend. In the measured player, half the head pitch went to torso slot 17. Apply that rotation at the same stage when reproducing the pose offline.

## Follow the numeric track to its descendants

A KEY track addresses a numeric node in the 3DO. Its mesh name is a clue to the author’s intent. A meshless node can still move every mesh beneath it. For each suspect track, list its number, the name and geometry expected on the reference player, and the candidate node’s children and mesh-bearing descendants. Compare a character with stock proportions and a clean cosmetic run to isolate the failure.

In the Lilitari R3 case, 91 stock player KEYs were inspected. Four wrote beyond Kyle’s eighteen-node body to optional slot 18. The saber fidget called it `saber`, the gun fidget `gun01`, and `kyfall` and `kysbsabr` called it `Object01`. Kyle has no body subtree there. Lilitari’s picker file put a meshless torso carrier at 18 with the entire upper body beneath it. A cosmetic bundle inherited that file and played the stock fidgets. The same release’s retail world body already used a childless filler at 18.

Measure the torso frame relative to the hip frame so walking or camera motion cannot masquerade as separation. In the measured picker, the maximum translation errors against the working world contract were 0.05454 Jedi units during saber fidget 2 and 0.04765 during gun fidget 2. Regular gun and saber stands gave zero error. Playing only the stand or inspecting a neutral render misses the fault. Small openings due to ordinary rigid-joint rotation are a separate diagnosis. A larger waist cap cannot keep a parent from moving an entire torso away.

## Make both animation contracts fit

Keep stock-driven weapon-only slots free of body children. Also check any extended KEY used by the multiplayer picker. In this pack the shared picker run used slots 51 through 63. Moving the torso carrier to an apparently empty high slot would let a different character’s picker animation move it.

For this body, the repair moved the torso carrier to 48 and reserved 18 as a childless, meshless leaf. To free 48, the existing hip seal’s faces were divided between two mesh chunks already rigidly attached to that same hip, at the same local origin. Check the receiving chunks’ vertex, face and UV budgets. Retain the material, vertex data, corner UVs, winding, flags and normals on each moved face. A seal carried by a different joint or with a different pivot would first need a coordinate conversion. This particular move preserved all 14,811 faces in each of four geosets.

## Prove the failing case and its controls

Compare the old and new body under the same failing KEY, pose, camera, profile and player role. Compare the repaired body to the already working world model under the same motion. Run a regular stand as a negative control, then the gun and saber fidgets, any other clips that own the same slot, and the complete preview run. Check that adjacent visible mesh groups, the weapon attachment and the player’s silhouette maintain their intended relation through blends and aim. A good hierarchy table alone does not prove the game loaded the repaired member.

For this fix, the shared 192-frame picker run was sampled at quarter-frame intervals. Every corresponding active joint transform agreed with the old picker. On the stock fidgets the repaired hip-relative torso matched the working world contract at every sampled frame and half-frame, including selected frames with applied torso pitch between −30° and +30°. This establishes the repaired track ownership for those cases. Other weapon mods and independently authored PUP files need their own slot check.

At a matched low camera angle in the original Jedi Knight 1.01 executable, the old cosmetic bundle’s torso separated during saber fidget 2 at frame 12.12. The corrected bundle kept it seated at frame 12.08 with the same −80° head-aim input. An independent transform comparison across all 91 stock clips and the shared picker run found zero maximum matrix-element error against the intended body motion over 14,568 sampled poses. Matched game captures check what is drawn, while this larger sweep checks the motion of every reattached visible component.

The Blender-Sith fork provides a source-side ownership checker on revisions containing `sith.audit.slotownership`. A stock installation of Blender-Sith 1.3.0 predates that command. Run it against the inspected extraction on an updated checkout. Include COG-triggered KEYs when they can drive the player.

```text
python -m sith.audit.slotownership --reference ky.3do --model dlil.3do --pup ky.pup --key-dir effective-keys --output ownership.json
```

Use the [small-player ghost-node study](ghost-node-player-skins.md) for a related helper collision, and [rigid-joint diagnostics](rigid-joint-and-face-diagnostics.md) when the correct joint is moving but the surfaces at its seat still separate.
