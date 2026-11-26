# Biddy’s snout and Lilivane’s left boot during stock player fidgets

The six-body R4 cosmetic GOB registered each player directly from its root `3do/` member and inherited Jedi Knight’s stock player puppet. Two bodies used hierarchy slot 18 for visible anatomy. All four stock clips that write this optional equipment track were affected. They are the saber and gun second fidgets (`kyidle1b.key`, `kyidle2b.key`), the fall (`kyfall.key`) and the underwater saber action (`kysbsabr.key`). Both Mandalorians and the T-800 in the same archive had no comparable findings across the 62 distinct puppet clips tested. The R4 Lilitari cosmetic included the earlier torso fix.

| R4 cosmetic root | 3DO SHA-256 | What slot 18 controlled |
| --- | --- | --- |
| `3do/biddybl.3do` | `19e8c34ebb8502d16e5139d01aca99c66c6d97e33a0905d9e3448f2be965d1dc` | Snout mesh on the head |
| `3do/lvane.3do` | `d3a61473cb8313678fbb8cfacf1314b9d79a42b451519bffc3132cf184036678` | Helper above the canonical left calf and foot, slots 3 and 4 |

## Biddy Blas

In the affected cosmetic, an equipment track moved a visible facial mesh. Specifying `--body-node bb_snout` classified the movement as body motion. The R5 candidate put the same snout on 27 and a meshless leaf on 18. All 17 visible meshes retained their geometry, pivots and material assignments. Under the four formerly conflicting clips, the original snout’s largest origin differences from its intended head attachment were 0.05082, 0.02818, 0.03946 and 0.00631 game units, respectively.

Native KEY sampling on the candidate found zero head-relative snout drift through 91 stock clips (13,800 quarter-frame samples). Every other visible mesh retained its exact original motion. All 17 meshes matched the original picker on its actual run (768 samples). The candidate SHA-256 is `742352b00842e3ab9e8d389b8a6f99ad9734adb8c9d0a83e6dfe05d6fdcd7a19`. Original-game captures at matched phases around frame 12 showed the old snout crossing the scarf in the saber fidget and leaving an opening below the helmet in the gun fidget. The replacement snout remained seated in both views.

The retail gameplay body already held the snout at 19. In SBX the face is at 21, with a legitimate secondary grip at 19. Across 91 effective private retail keys and 171 effective SBX keys from seven puppet styles and their additional action calls, the face retained its bind relation to the head in the sampled frames. For these checks the original profile rig is the animation reference. For the stock cosmetic the reference is the original Kyle rig.

The original engine’s rendered foot vertices exposed a separate problem. On a flat floor at zero, R4 Biddy’s median sole height was +0.00020 JKU standing, −0.02626 crouched, and −0.02671 crouch-walking. Kyle’s corresponding medians were +0.00010, −0.00139 and −0.00151. The crouched actor origin was +0.075 for both. The face repair preserved the leg poses, including this crouch error.

Biddy’s private movement fix uses only two crouch clips on the revised cosmetic body. The source private-world crouch had already been animated against 17 helper nodes. Their names and neutral offsets identified the corresponding slots in the cosmetic file. Remapping those numeric tracks retained every visible mesh transform from the authored private crouch. Forward and backward now have their own private KEY names in a per-skin PUP. The original stock PUP and movement assets can continue to serve every ordinary Kyle. Across a quarter-frame sweep, the transformed sole of the private forward crouch was within 0.00052 game units of floor zero and the backward crouch within 0.00043.

The complete original retail profile supplied the native calibration for that retarget. On the released world body, its existing private forward crouch produced measured median sole heights of +0.00022 JKU stationary and +0.00030 moving. Both values came from the original executable’s rendered foot matrices.

The same original-game fixture then explicitly assigned `r5bb.pup` to the revised cosmetic body. The median sole heights were +0.00017 stationary (26 samples), +0.00030 moving forward (73) and +0.00032 moving backward (70). Readback confirmed execution of both privately named clips. Stand and walk still used the stock keys, and the measured collision radius was 0.065. This tests the selected puppet’s behavior. Automatic per-skin selection in a particular arena is an integration test of its own.

## Lilivane

Trace the two protected limb nodes back to their parents. In the R4 cosmetic both descended from the helper at slot 18. In the separate full-retail world member, a meshless leaf occupied 18 and the calf helper occupied 19. Testing that world member against the stock player puppet cleared the four ownership conflicts. That test alone could not establish correct stride or sole position.

The revised picker/cosmetic body moved the calf helper to 39. Its children still include the left calf and downstream foot. Lilivane’s SBX rig has a different contract again. It intentionally keeps the calf helper on slot 18, driven by 108 private animation files, and the secondary grip on 19. A replacement that put a dummy at 18 in every file would discard her intended SBX leg motion.

Comparing the same R4 retail world body on raw stock versus private animation illustrates the distinction. On both second fidgets the left foot’s position relative to the hips agreed within 0.00000001 JKU. Its world-space origin differed by about 0.00442 JKU, reaching 0.04827 JKU during a fall. These are joint-origin measurements. Measuring the lowest transformed boot vertices and testing the actual drawn character can answer whether her sole meets the floor.

On the same original-game flat-floor fixture, the R4 cosmetic’s stock stationary crouch put Lilivane’s sole at a median −0.02989 JKU. Her complete retail world model playing its own private crouch gave −0.00255 stationary and −0.00190 moving. The original model, model registration, puppet, stance and renderer jointly define the measured case.

The revised cosmetic preserved all 14,370 faces and their corner data in each of four detail levels. Across 91 stock clips plus the picker run, 14,660 quarter-frame samples including clip endpoints matched the intended visible part transforms. The separate private crouch fix retained the stock limb rotations. Two helper roots received the same frame-dependent vertical correction calculated from the soles. The native engine explicitly assigned the resulting `r5lv.pup` to the repaired body. Stationary crouch gave a median −0.00014 game units over 26 readings, forward and reverse each gave −0.00010 over 73 and 69 readings. All of those readings fell between −0.00029 and +0.00007.

The prior [standing projectile study](https://github.com/CodaLilitari/JK-MotS-Model-Workflow/blob/53dfbf06a3ece492691b56b3584191eb614ce1a0/docs/research/2026-11-26-ghost-node-retail.md) measured the stock player collision envelope at eleven points. It exercised another condition. The [ownership checker](https://github.com/CodaLilitari/blender-sith/blob/291a2367ca5c1e040845ee6b2509b2c5ec9acddf/docs/audits/slot-ownership.md) accepts a named part on either an extracted 3DO or a complete path inside a GOB, and reports its resolved slot and hashes.
