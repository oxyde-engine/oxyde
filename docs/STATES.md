# Common states

Every state number the engine reserves, what it is called, and what it is for.

A MUGEN character inherits these by saying `stcommon = common1.cns`, and in CNS they are bare numbers — `[Statedef 120]` and nothing else. Oxyde's common states are written in FUSE, which lets a state carry a name, so the number has a meaning written next to it rather than remembered.

Read out of `data/common1.fuse` at build time, so it cannot disagree with the states the engine actually ships.

| number | name | what it is for |
|---:|---|---|
| `0` | `Stand` | Standing idle. Where a character returns when nothing else is happening, and what `ChangeState(value: 0, ctrl: 1)` at the end of a move means. |
| `10` | `StandToCrouch` | The crouch is beginning — the transition animation between standing and crouched. |
| `11` | `Crouch` | Crouched and idle. |
| `12` | `CrouchToStand` | Standing back up from a crouch. |
| `20` | `Walk` | Walking, forward or back. The direction comes from the command, not from two separate states. |
| `40` | `JumpStart` | The jump has been input and the fighter is still on the ground in prejump. Jump velocity is applied when this ends. |
| `45` | `AirJumpStart` | An air jump is starting — the second or later jump of a chain. |
| `50` | `JumpUp` | Rising during a jump. |
| `51` | `JumpDown` | Falling during a jump. |
| `52` | `JumpLand` | Landing from a jump, and recovering. |
| `100` | `RunFwd` | Running forward. |
| `105` | `HopBack` | Hopping backwards — the back dash. |
| `106` | `HopBackLand` | Landing from a back hop. |
| `110` | `DodgeBack` | A backward dodge. Not in MUGEN's own set; part of the extended behaviour. |
| `115` | `DodgeFwd` | A forward dodge. |
| `120` | `GuardStart` | Guarding has begun. The engine sends a fighter here when it decides the incoming attack is being blocked, and this state chooses which guard stance follows. |
| `130` | `StandGuard` | Blocking while standing. |
| `131` | `CrouchGuard` | Blocking while crouched. |
| `132` | `AirGuard` | Blocking in the air. |
| `140` | `GuardEnd` | Guard is ending and the fighter is returning to neutral. |
| `150` | `StandGuardHitShake` | The freeze on a standing block, before knockback is applied. |
| `151` | `StandGuardKnockBack` | Being pushed back by a blocked attack while standing. |
| `152` | `CrouchGuardHitShake` | The freeze on a crouching block. |
| `153` | `CrouchGuardKnockBack` | Being pushed back by a blocked attack while crouched. |
| `154` | `AirGuardHitShake` | The freeze on an air block. |
| `155` | `AirGuardKnockBack` | Being pushed back by a blocked attack in the air. |
| `170` | `LosePose` | The losing pose, played after the round is lost. |
| `175` | `DrawPose` | The pose for a draw. |
| `190` | `Intro` | The intro, played before the round starts. |
| `191` | `IntroWait` | Waiting during the intro while the other fighter finishes theirs. |
| `5000` | `HitShake` | Hit while standing — the freeze before the reaction. Every get-hit sequence starts in a shake state. |
| `5001` | `HitStand` | The standing hit reaction proper, after the shake. |
| `5010` | `CrouchHitShake` | Hit while crouching — the freeze. |
| `5011` | `HitCrouch` | The crouching hit reaction. |
| `5020` | `HitAirShake` | Hit in the air — the freeze. |
| `5030` | `HitAirTransition` | Transitioning into the airborne hit reaction. |
| `5035` | `HitAirUp` | Rising after being hit in the air. |
| `5040` | `HitAirRecover` | Recovering in mid-air after a hit, before landing. |
| `5050` | `HitAirFall` | Falling after a hit, with no control. The state a knockdown puts you in. |
| `5070` | `HitTrip` | Tripped — swept off the feet. |
| `5071` | `HitTripFall` | Falling after a trip. |
| `5080` | `HitLieDownShake` | Hit while already lying down — the freeze. |
| `5081` | `HitLieDownFall` | Falling again after being hit while down. |
| `5100` | `FallBounce` | Bouncing off the ground after a hard knockdown. |
| `5101` | `FallBounceUp` | Rising from that bounce. |
| `5110` | `LieDown` | Lying on the ground, before getting up. |
| `5120` | `GetUp` | Getting up from the ground. |
| `5150` | `LieDead` | Lying dead. The round is over for this fighter. |
| `5200` | `FallRecoverGround` | Recovering from a fall by landing on the feet, on the ground. |
| `5201` | `FallRecoverGroundLand` | Landing from a ground recovery. |
| `5210` | `FallRecoverAir` | Recovering from a fall while still in the air. |
| `5500` | `KO` | Knocked out. The transition into defeat. |
| `5900` | `Initialise` | Initialisation. Runs once when the fighter is created, before the first tick of the match. |

