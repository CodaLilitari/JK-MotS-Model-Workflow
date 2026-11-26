# Small player skins on stock animations

A short player can keep Kyle's multiplayer collision and inherit the movement of his stock rig. Those choices solve different problems. SMLiberator's ghost nodes help place the visible head, hands and feet on a body with different proportions. Kyle's player template and world insertion height govern the collision comparison. For **Biddy Blas and Lilivane R2**, keep the released private puppets and clips as the reference. Substituting stock clips on those rigs produced measurable crouch errors. A different rig could improve on that result.

## What SMLiberator built

SMLiberator shared his unfinished Jedi Knight NPC skin pack in the Massassi showcase. Its 281 archive entries include 43 world models and no KEY, PUP or COG replacements. Thirty-two models have 34 hierarchy nodes. Max (`kymx.3do`), Pic (`kypi.3do`) and the Ugnaught (`kyug.3do`) each retain the numbered body slots 0–17 and add sixteen meshless `PIVOT_*` nodes. The Blender-Sith importer read sixteen visible meshes in each of those three models. The archive SHA-256 is `d135544795d7d53b4418fc0a1f0a4811c54b65f55af77fc128f3c9a6da283ec1`. [SMLiberator's original post](https://discord.com/channels/881034839401328680/881749278811377695/1575533495005220946)

Follow the **parent indices**, even if a parent appears later in the file. In these three models, left calf 3 parents a meshless helper at 32, and helper 32 parents left foot 4. A stock track still drives the joint at its original number. The helper's fixed transform moves the joint's frame relative to its parent, so the foot follows the calf from the new location throughout the motion. Record the pivot, translation, rotation and all descendants before deciding which body part a helper actually affects.

Inspect the complete puppet before assigning helper slots. Four clips referenced by retail `ky.pup` author motion at slot 18. On the three example models, 18 is `PIVOT_TORSO` and carries the upper body.

| Stock clip | Track name at 18 |
| --- | --- |
| `kyfall.key` | `Object01` |
| `kyidle1b.key` | `saber` |
| `kyidle2b.key` | `gun01` |
| `kysbsabr.key` | `Object01` |

The OpenJKDF2 playback code associates a track with its numbered slot. A name mismatch is a useful diagnostic. In the fork's single-layer, full-weight Ugnaught evaluation, including the four tracks in the order above displaced the head origin by up to 0.0373, 0.0495, 0.1077 and 0.1157 game units compared with omitting only slot 18. These are pose comparisons. Actual puppet priorities, blends and original-executable behavior require gameplay tests. For a new stock-compatible rig, reserve the full set of authored slots across the intended PUP before assigning load-bearing helpers. Check both the highest authored index and each KEY's declared joint allocation against the complete hierarchy. RED reports these as separate findings. [Blender-Sith audit](https://github.com/CodaLilitari/blender-sith/blob/f56fd81eeee4acc6c6ac4457684ad4a0388912cc/docs/audits/ghost-nodes.md) · [RED hierarchy guide](https://github.com/CodaLilitari/RED/blob/613b19b752fc3279dbbc320755fbe101125aa68d/docs/model_hierarchy.md#small-players-with-stock-animations)

## What happened on Biddy and Lilivane

Both released R2 world models have 64 hierarchy nodes and preserve Kyle's `INSERT OFFSET` Z of 0.120114 game units. Biddy uses `bb_ky.pup` and Lilivane uses `lv_ky.pup`. The comparison applied original KEY bytes to the existing models in memory. It measured the lowest vertex on the left and right foot meshes (nodes 4 and 10) against Kyle's feet at the same animation phase. A small character's head height would be a poor substitute for this measurement.

| Phase-matched sole comparison, game units | Biddy | Lilivane |
| --- | ---: | ---: |
| Forward crouch with unmodified stock KEY, largest absolute difference | 0.03291 | 0.03276 |
| Same crouch with released private KEY, largest absolute difference | 0.00907 | 0.00418 |
| Best fixed translation shared by torso and hip carriers, largest remaining difference across eight grounded clips | 0.018566 | 0.016695 |

The eight clips covered standing, walking forward, running, forward and backward crouch, both strafes and turning left. The fit used 1,072 half-frame samples and minimized the worst sole error. Matching a single standing frame left larger errors during the crouch. An additional fit gave each existing extra ancestor of the feet an independent translation and minimized ankle-position error against the released clips. Even fitting all eight clips left ankle RMS errors of 0.02344 for Biddy and 0.00686 for Lilivane. These fits allow changes to limb proportions and do not adjust foot orientation. Their limits apply to the tested rig and those fitted parameters. A differently placed or rotated joint, a redesigned hierarchy, or a hybrid using private clips for specific movements is a separate experiment.

### SBX lightstaff grip

Test the second hand against the solid handle as the weapon moves. In a separate offline mesh comparison using Biddy's integrated SBX model and the original SBX KEYs, the support hand touched the double-ended staff handle on 0 of 121 quarter-frame samples in `ls_stand`, 0 of 17 in `ls_sabrf`, and 0 of 39 in `ls_sabrr1`. The sample sets contain the phases where Kyle held the handle. Peak clear gaps were 0.02172, 0.03229 and 0.04405 game units. Biddy's released private aliases restored contact on all 121, 17 and 39 samples. An apparently close grip in a standing screenshot can conceal a larger loss of contact in a swing.

Lilivane's hands behaved differently. Original and released aliases gave identical results in the same phases: 121/121, 15/17 and 17/39 intersections, with maximum clearances of 0, 0.00014 and 0.00140 game units. For those three moves this metric gives no grip advantage to the private aliases. A triangle intersection can also mean a hand penetrates the handle. Inspect depth, finger placement and transitions before making a visual judgment.

## Preserve Kyle's gameplay collision

When describing a candidate, distinguish three practical choices. The first plays the original KEY bytes. The second keeps the stock movement tracks but gives a privately named copy enough joint allocation for the larger hierarchy. The third adjusts private movement tracks to fit the character. Record which path each stance, crouch and attack actually uses. Private copies can preserve shared stock assets for Kyle and other players.

Compare the exact player template, inheritance, `size`, `movesize` and collision mode in the same map. The stock player radius and movement radius used here were both 0.065. Compare the grounded player origin as well: the R2 insertion height matches Kyle's, while the inspected Max, Pic and Ugnaught models have insertion heights of 0.0720, 0.1045 and 0.1010 respectively. A matching radius alone leaves room for a vertically shifted target. Keep necessary visual offsets on model-only helpers and compare actual standing and crouching target positions.

Earlier original Jedi Knight multiplayer tests on the **released R2 setup** compared projectile hits and misses with Kyle and recorded peer saber damage. Those observations cover its private animation paths. This stock-animation study produced hierarchy, import and sampled-pose evidence. Original-executable playback with unmodified stock clips and peer hit tests for a new rig remain open.

## A repeatable review

1. Resolve the selectable player's world model and active PUP, enumerate the distinct KEYs, and list authored indices, declared joint allocation and attachment roles. Compare retail and any supported mod independently.
2. Inspect at least one helper chain from animated parent to visible mesh. Check for cycles, shared descendants, body-pivot motion on equipment tracks, and off-hand grip when the right hand carries a weapon.
3. Compare the original stock motion, the released character's private motion and any proposed calibration at matched phases. Include stance changes, crouch travel, left/right stride, jump/fall/land, idle flourishes and attacks. Measure sole positions and foot slip at the intended speed. Check separately for penetration because a sole below the floor can satisfy a simple distance-based contact test.
4. In the target game, record the active PUP and KEY, grounded player origins, and matching pairs of projectile hits and near misses against Kyle. Add crouching and a second player's saber attack where relevant. Record visual continuity, grip and measured collision as separate results.
