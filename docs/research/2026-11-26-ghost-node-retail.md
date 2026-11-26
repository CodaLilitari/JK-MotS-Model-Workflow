# Stock animations and standing collision on short player models

**November 26, 2026.** In the original *Jedi Knight: Dark Forces II* 1.01 executable, Biddy Blas and Lilivane each matched Kyle on all eleven standing projectile probes. Each selected avatar also activated stock animation tracks for standing, receiving a hit, walking forward and crouching forward. This follow-up tests the released R2 world models with the original Kyle puppet. SMLiberator's unfinished NPC pack supplied the ghost-node technique that prompted the comparison. [Original NPC pack post](https://discord.com/channels/881034839401328680/881749278811377695/1575533495005220946) · [Hierarchy and pose study](../../skills/jk-mots-model-workflow/references/ghost-node-player-skins.md)

## The standing target

Kyle, Biddy and Lilivane were selected in separate original-game sessions. The test used the same world, spawn location, aim points and stock `ky.pup`. The player origin at rest was (0, 0.168, 0.120114) in game units. Each player reported collision type 1, a hit radius of 0.065 and a movement radius of 0.065.

| Projectile aim point | Kyle | Biddy | Lilivane |
| --- | --- | --- | --- |
| Center, inner left, inner right, inner upper, inner lower, inner diagonal | 6 hits | 6 hits | 6 hits |
| Outer left, outer right, outer upper, outer diagonal, high above | 5 misses | 5 misses | 5 misses |

The eleven positions scored in the same order gave hit mask **427** for every avatar. That establishes agreement at the sampled standing points, including near misses around the visible body. The study did not sample a complete collision surface.

## What the engine played

Readback identified the original `ky.pup` and four stock clips on each selected avatar: `kystand0.key`, `kyhit0.key`, `kywalkf.key` and `kycrchgn.key`. The researchers drove walking and crouching **after** the projectile series. Biddy's event-driven position log did not sample his crouched origin; the crouch evidence for him is the active track. Crouching projectile boundaries, joint trajectories, peer saber contact, SBX, slot 18 and the remaining retail clips and phases are outside this test.

For an author choosing a rig, these results separate two questions. Stock tracks can play on the released R2 models while the standing shots agree with Kyle. The visible soles and off-hand grip still need pose-by-pose review. The earlier [crouch and staff measurements](../../skills/jk-mots-model-workflow/references/ghost-node-player-skins.md#what-happened-on-biddy-and-lilivane) show where those rigs benefit from private clips.

## Tested resource fingerprints

| Resource | SHA-256 |
| --- | --- |
| Original 1.01 executable | `4509cd690634ba20e132bd16e713f91e144b17e2beaaad5e678f1ddb189b51d9` |
| Stock `ky.pup` | `4717bd702e83deb91a7fd4c8fbd580cb75dadc2056022284cd9a532a05e3082b` |
| Test world | `d3669463e6c8471d7cc0d7c491d11802735a68b1af776a65973e38b4fe1580e8` |
| Selected `ky.3do` | `8e86e367df0198960d301db385c429a991e86cefbbe026918534ebbfe8540140` |
| Selected `biddybl.3do` | `a6ffa675fccf461e5d3998f86a23861f3d979e5dbce74110c243139cda789435` |
| Selected `lvane.3do` | `1ef1ad3f7fe9f0aa1fcddb2df2e308e825db30c9affa87dd4ec257fdfd1af4ee` |

The consolidated three-session evidence record has SHA-256 `45a19a9b37ceac39ab3c982dbf31a538ff2d02aa10d3a91b6fd4dd7b0ad029bc`.

## Two additional original-game checks

**The Ugnaught's collision center.** A fourth session selected `kyug.3do` and its `kyug.snd` sound class directly from SMLiberator's unchanged 281-entry NPC pack (SHA-256 `d135544795d7d53b4418fc0a1f0a4811c54b65f55af77fc128f3c9a6da283ec1`). The Ugnaught played the same four stock clips, reported the same 0.065 hit and movement radii, and scored the same mask of 427 on projectiles aimed relative to its own origin. On the same floor its standing Z was **0.101000**, putting its collision center **0.019114 game units lower** than Kyle's 0.120114. Matching the radius and an origin-relative shot pattern still leaves a measurable difference in world space.

**What the stock crouch looked like.** A separate original-game session used `SetThingModel` to switch the actual local player among Kyle, Biddy R2 and Lilivane R2. The camera kept the same offset from the actor and each capture used the same crop. In the forward-crouch images, Biddy's and Lilivane's lower bodies visibly sank into the floor while Kyle's legs remained visible. These frames provide a visual comparison. They do not yield individual joint coordinates or a measured boot depth.
