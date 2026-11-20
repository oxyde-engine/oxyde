# Knuckle Up — the belt-scroll brawler mode

Knuckle Up is a beat-'em-up mode in the spirit of *Final Fight* and *Streets of
Rage*, played with the existing roster: one or two players walk a scrolling
stage and clear waves of the roster's own characters as enemies, with bosses,
weapon and health pickups, music and a storyboard.

This document is the design contract for the mode. The rule it exists to keep
is that **Knuckle Up adds no special case to the engine**: it is a
*configuration* of general capabilities, most of which the engine already has,
wired together by a declarative *campaign*. A modder ships a campaign folder,
not an engine patch.

## The one rule: the determinism boundary decides where each feature lives

`Match::step` is a pure function, and that is what buys co-op, replays and
spectating. Every Knuckle Up feature therefore sorts into exactly one bin:

- **Changes the fight's outcome** — damage, position, what spawns, what moves
  exist — lives in **FUSE, inside `step()`**, and is checksummed. Two-player
  online co-op through a whole campaign is then the same two u16s a frame that
  every other deterministic feature already rides on.
- **Only presentation** — music, cutscenes, parallax art, campaign flow — lives
  in **Lua, outside `step()`**.

Put a pickup's healing on the Lua side and co-op desyncs; put it in FUSE and
co-op is automatic. The dependency graph already enforces the split.

## What the engine already has (the 2.5D base)

The depth axis a belt-scroll brawler needs is **already in the simulation**, as
Ikemen-GO-style 2.5D:

- `Player::pos_z` and `vel_z`: a third position axis, integrated every tick
  (`sim.rs`), with no gravity or friction of its own — "a fighter walking into
  the screen is not falling."
- `z_bounds` from `[PlayerInfo] topbound`/`botbound`: the walkable depth strip.
  **Equal bounds pin every fighter to the MUGEN plane**, which is every stage in
  the base archive — so the flat roster is unaffected until a stage opens a
  range.
- Depth-aware hit detection: `depth_reaches` gates a hit on `HitDef
  attack.depth` against the `pos_z` gap, and collapses to always-true when
  nobody has depth (the flat roster again).
- Hits carry Z: `ground.zvelocity`, `air.zvelocity`, `zvel`, `zaccel`.
- Rendering already projects depth to screen (`depth_to_screen`), scales it for
  perspective (`depth_to_scale`), and depth-sorts the scene.

So the brawler's defining axis is not new work; it is **turned on** by a stage
that opens `z_bounds` and one small mode-scoped rule that lets up/down walk it.

## Feature → layer map

| Feature | Layer | Mechanism |
| --- | --- | --- |
| Depth movement (up/down walks the belt) | FUSE / `step()` | mode-scoped `MatchRules.belt`: up/down set `vel_z` when grounded; jump/crouch suppressed while it is on |
| Scenery / stages | MUGEN stage + FUSE stage-logic | campaign lists stages in order; belt camera; parallax from stage BG |
| Stage customization | FUSE stage-logic | hazards, breakable floors, reactive backgrounds, per stage |
| Wave director | FUSE stage-logic | spawn enemies per wave; lock the camera until cleared; then scroll |
| Health / weapon pickups | FUSE / `step()` | one general pickup entity = sprite + effect (heal / weapon / score) |
| Weapons → attacks | FUSE state overlay | a picked-up weapon pushes a temporary moveset overlay; drop/timeout pops it |
| Bosses | roster char + campaign flag | campaign names the boss and scales its stats; the wave gate holds until it falls |
| Special moves (mode-wide) | FUSE universal mechanics | the mode may add a move to every character, as burst/tag/auto-block already do |
| Music | Lua | campaign assigns BGM per stage and boss |
| Storyboard / story | MUGEN storyboard + Lua | intro, interludes, ending; the Lua run declares the campaign's shape |

The genuinely mode-specific primitives are the depth-walk rule, the pickup
entity, the weapon overlay and the belt camera — all general, none
Knuckle-Up-specific; the rest is the stage-logic and universal-mechanics
patterns applied.

## The campaign: one declarative package

A campaign is a folder with a manifest that declares its stages, and per stage
its waves, pickups, boss, music, stage-logic and storyboard. The deterministic
rows (waves, pickups, boss stats, hazards) are handed to `step()` through FUSE;
the presentation rows (music, storyboards, flow) drive the Lua run. Sketch:

```ini
[Campaign "Knuckle Up: Rust City"]
stages = rust_alley, rust_docks, rust_factory

[Stage rust_alley]
  scroll  = belt              ; belt camera + wave gates
  music   = alley.ogg         ; Lua (presentation)
  logic   = rust_alley.fuse   ; hazards / breakables / reactive bg
  intro   = alley_intro.def   ; MUGEN storyboard
  waves   = [ {count:3, pool:[kfm, Mike, Larry]},
              {count:4, pool:[...]},
              {boss:Abigail, life:x2.5, music:boss.ogg} ]
  pickups = [ roast@wave2 (heal 40%), pipe@crate3 (weapon:swing) ]
```

This mirrors the shapes the engine already uses — rulesets as sparse deltas,
the character index as derived facts, Lua Tier B declaring a run on the Act
queue, stage-logic in FUSE. A campaign is those ideas one level up.

### The `knuckleup/` folder

The mode keeps its content in one folder at the game root, apart from what
every other mode shares:

```
knuckleup/
  knuckleup.cfg   the mode's settings ([KnuckleUp]), over oxyde.cfg's
  campaigns/      *.knuckle
  stages/         belt streets — never offered by another mode
  props/          prop characters only this mode parks
  weapons/        weapon pickups
  music/          campaign and boss tracks
  storyboards/    stage intros
  logic/          per-stage FUSE logic
```

A path a campaign names is looked for in `knuckleup/<kind>/` first, then
beside the campaign, then in the shared places it used to live
(`data/campaigns/`, `stages/`, `sound/`, `data/weapons/`, the roster) — so an
install without the folder plays as before, and a campaign that names a
shared stage still gets it. A leading `stages/` or `sound/` in a campaign is
read as "the folder for that kind", which is how content moves in without the
campaign (and its identity, which replays and online peers check) being
edited. `oxtool knuckle migrate <root>` moves an older install's content in;
`oxtool campaign --root <root>` checks every campaign and says where each of
its paths was found. The full rules: [KNUCKLE-UP-CAMPAIGNS.md](KNUCKLE-UP-CAMPAIGNS.md#the-knuckleup-folder).
Tests: `knuckle_home::tests`,
`knuckle_up_lists_the_mode_folder_first_and_each_campaign_once`,
`a_campaign_finds_its_files_in_the_mode_folder_first_and_its_streets_stay_out_of_versus`,
`the_mode_folder_adds_nothing_other_modes_can_pick`,
`a_format_four_tape_finds_its_campaign_after_it_moved_into_the_mode_folder`,
`knuckleup_cfg_overrides_the_main_configs_house_rules_and_takes_the_edits`,
`oxtool`'s `migrate_plans_only_the_modes_own_content_and_keeps_identities` and
`migrate_dry_run_writes_nothing_and_a_real_run_moves_the_content_home`.

## How the mode works, feature by feature

Phase 0 — the mode as a first-class `Mode::KnuckleUp`, one player against three
roster enemies drawn endlessly — rests on the continuous-turns machinery
Team Rumble and Team Tag already use. On top of it:

1. **Depth-walk.** `MatchRules.belt`; up/down drive `pos_z` in
   `apply_physics`, jump/crouch suppressed at the ground state machine and in
   `builtin_command`. Gated so an unopened `z_bounds` (the flat roster) changes
   nothing. Test `belt_scroll_walks_the_depth_instead_of_jumping`.
2. **Camera wave-gate.** In `update_camera`, the view cannot
   scroll past a living enemy and releases on clear.
   Test `belt_camera_holds_until_the_wave_is_cleared`.
3. **Discrete waves.** `perform_substitution` refills the side
   to `on_screen[side]`; backward-compatible (`on_screen=1` modes bring one).
4. **Depth-aware hits.** `belt.hit_depth` floors an attack's
   depth reach so a hit lands when the two are roughly lined up, not exactly.
   Test `belt_hit_depth_lets_roughly_aligned_fighters_connect`.
5. **Pickup entity.** `Pickup`/`PickupKind` (Health, Weapon) in
   the sim, `spawn_pickup` + `collect_pickups` (heals the team-0 player who
   reaches it; a weapon arms them — `weapon_ticks` — for +50% damage while it
   lasts). The wave director drops one on a clear. Tests
   `a_health_pickup_heals_the_player_and_is_consumed`,
   `a_weapon_pickup_arms_the_player_and_runs_out`. `power`, `oneup` and
   `score` pickups come with the run (item 10). **Drawn**
   (`oxyde-render/src/pickupfx.rs`) as rusted OXYDE reward cases,
   re-hued per kind — health green, power blue, 1UP orange, score gold, the
   weapon a crossed wrench and pipe lit into the health case
   (the pickup pipeline writes them; they are embedded in the
   engine). True RGBA, blended with their own alpha: each floats and bobs
   over a soft shadow, a halo and a pillar of its colour breathe, sparks
   twinkle round it, a glint crosses it, and a new one pops in. Taken, a ring
   opens on the floor, rays burst, the case lifts and fades and what it gave
   rises as a label (`+250 HEALTH`, `1UP`, `+2500`). Rendering only — the
   pickup logic is untouched, so every tape verifies — and timed on the
   match's tick. About 0.2 ms a pickup at 1280x720 (`pickup_draw_cost`).
6. **Campaign format + wiring.** `campaign.rs` (model + INI
   parser + `validate`), demo at `knuckleup/campaigns/rust_city.knuckle`, and
   `oxtool campaign <file>` to check one. The full key-by-key reference for
   content authors is [KNUCKLE-UP-CAMPAIGNS.md](KNUCKLE-UP-CAMPAIGNS.md). The
   parsed campaign **is** wired into the match flow: `game.rs`
   `resolve_knuckle_campaign` seeds the enemies and `knuckle_life_mult`,
   `build_knuckle_plan` flattens stages→waves→boss, and `perform_substitution`
   spawns each wave at `on_screen[side]`, scales the boss, and drops the wave's
   campaign pickup. A picker reads `OXYDE_KNUCKLE_CAMPAIGN` or defaults to the
   demo.
7. **Presentation.** Each campaign stage opens on a card (`title`,
   `story1`…) that the round's intro waits for, and plays its own
   `music`, a `boss.music` when the boss walks in, and an `intro` storyboard.
8. **Bosses and balance.** The campaign's
   `boss = name, mult` drives `knuckle_life_mult`, applied in
   `perform_substitution`, and the camera holds on the final wave until the boss
   falls (clear-to-advance). Roster-wide brawler balance (reach, damage curves
   across 1,051 enemies) is a matter of tuning rather than engine code.

9. **Co-op.** `Mode::KnuckleUpCoop` fields two heroes on
   one team against the same waves (`drives: [row(Human(0), Human(1)), row(Cpu,
   Cpu)]`, `on_screen: [2, 3]`), sharing the solo mode's whole belt/campaign
   logic through `Mode::is_knuckle()`. Test
   `knuckle_up_coop_fields_two_heroes_against_the_waves`; headless render 97.6%
   painted; `1051 unchanged`. The determinism fold for online play:
   `room_setup_hash` folds the run identity — the campaign definition
   (`Campaign::identity`) plus each resolved enemy's content hash — into the
   handshake whenever the mode `is_knuckle`, so two peers on a different run or a
   different version of an enemy are refused rather than desynced
   (`fold_knuckle_run_identity`). Online co-op seating:
   `OnlineMode::Coop` seats a joiner (and couch+online hybrid heroes) on
   team 0 through `net_layout`, and two peers converge in tests
   (`online_coop_seats_two_players_and_converges`,
   `an_online_knuckle_run_with_a_couch_seat_converges`). Online co-op does not
   yet carry the run itself: it fields its waves inside
   `step()` and does not carry the lives, props or placement that item 10
   adds, and a live two-machine WAN/NAT run is unproven (localhost and
   loopback only — see [KNUCKLE-UP-FLOW.md](KNUCKLE-UP-FLOW.md)). See
   [BYOC.md](BYOC.md) for the content-identity pattern this reuses.

10. **The run.** What makes it a beat-'em-up rather than a
    gauntlet, in `crates/oxyde-app/src/knuckle.rs`:
    - **Floating enemy bars.** Every enemy carries a slim bar with its name over
      its head, longer for more life (`bar_width`); the boss gets a wide bar
      along the bottom instead. (Restyled, with a power gauge, in item 12.)
    - **Varied life.** Grunts fight on the campaign's (or stage's) `life`, or
      their own `name*0.35`; a boss on its own multiple. Applied to the first
      wave of a stage as well as to the waves that walk in later. On top of
      that every grunt is dealt a toughness from the run's seed
      (`knuckle_toughness`): a pushover at 0.65–0.75 of that life one time in
      four, as written (0.9–1.1) half the time, tough (1.3–1.5) one in five and
      heavy (1.7–1.9) one in twenty. A boss keeps the campaign's figure.
    - **Lives.** `[Campaign] lives`. A knocked-out player with a life left lies
      there for `REVIVE_DELAY` ticks while the round holds, then drops back in on
      full life, untouchable for `RESPAWN_INVULN` ticks. `oneup` pickups add one.
    - **Score.** Damage, knockouts, the boss and props, shown with the lives
      on the hero's plate (item 12).
    - **Stages.** When the next wave belongs to another campaign stage, the run
      moves to that stage's set (a fresh round; the player's life carries over)
      behind its card.
    - **Props.** `prop1 = car2, 2, random` parks a bonus-game character for a
      wave. It stands on the enemy team so attacks land, but `Player::prop`
      keeps it out of the camera's wave gate and it is nobody's team member, so
      the wave never waits for it. Breaking it pays a reward drawn from the run's
      seed. A prop is scenery: it takes no part in push resolution, so fighters
      walk past it, and nothing it or its helpers swing or fire reaches anyone
      (`a_parked_prop_neither_blocks_nor_hurts_the_hero`).
    - **Facing.** On the belt a fighter turns only to an enemy still in the
      fight, never to one lying knocked out or to a prop; with nobody left the
      hero turns to the way they walk.
    Tests: `knuckle::tests` (score, prop payout, rewards, revive, card, bar
    width), `campaign::tests` (the new keys), and in the simulation
    `power_one_up_and_score_pickups_reach_the_gauge_and_the_run` and
    `a_prop_on_the_enemy_team_does_not_hold_the_wave_gate`. Local only, like
    the app-side waves it sits on: online co-op fields its waves in `step` and
    has no lives or props yet.

11. **Side-scrolling levels.** The authoring guide is
    [KNUCKLE-UP-STAGES.md](KNUCKLE-UP-STAGES.md).
    - **Placement along the street.** `waveN.at`, `waveN.from`, `prop = name,
      at X, reward` and `boss.at` place a stage's fights by stage x. A placed
      wave waits until the leading player reaches it (a GO sign shows, the
      round clock holds), walks in from ahead or behind, and the screen locks
      where it was met (`Match::belt_arena`) until it is down. A placement past
      where a fighter can walk fires at the edge. Unplaced waves keep the
      sequential behaviour. Positions are in the stage file's own coordinates,
      so a `localcoord = 1280,720` stage places its waves in its own pixels.
    - **Props stand where they are parked**: a prop is exempt from the screen
      clamp and from the camera's framing, so one up the street waits there.
    - A computer-driven hero (co-op partner, headless run) walks on when the
      screen is clear.
    - The campaign's `logic`, `music`, `boss.music` and `intro` are wired; a
      campaign `stage` may be a `.def` by path, outside `select.def`.
    - **Campaign list** on the menu when more than one is installed.
    - `oxtool props` measures which bonus props can stand in a street, and
      `oxtool campaign --root` checks a campaign against an installation.
    - The example street `knuckleup/stages/knuckle_rust_street.def` and the first stage
      of `rust_city.knuckle` use all of it.
    Tests: `a_stage_places_waves_props_and_the_boss_along_the_street`,
    `a_placement_behind_the_last_is_noted_and_a_bad_side_refused`,
    `placing_things_moves_the_identity_and_a_sequential_campaign_keeps_its_own`,
    `a_belt_arena_holds_the_camera_and_a_parked_prop_stands_off_screen`,
    `a_hero_alone_on_the_belt_walks_on_up_the_street`,
    `knuckle_up_asks_which_campaign_when_there_is_a_choice`,
    `a_campaign_stage_brings_its_own_logic_and_music`.

11. **The arcade rules.**
    - **Projectiles keep a row.** A projectile takes its firer's `pos_z` when
      it is launched, is drawn there, and on the belt hits only what is
      roughly lined up with it, by the same `hit_depth` rule as a punch.
      Before, it had no depth and hit every row. Test
      `on_the_belt_a_fireball_hits_only_the_row_it_was_thrown_on`.
    - **Continues.** With every life spent, a CONTINUE? screen counts ten
      seconds; a button brings the lives back and drops the heroes in where
      they fell, so the stage, the wave and the boss — his life included — are
      untouched. The score is kept (the genre's other habit, halving or zeroing
      it, punishes the player for a feature they were offered). Test
      `a_continue_brings_the_lives_back_and_leaves_the_boss_as_he_was`.
    - **Time over costs a life**, not the round; the clock starts again. It
      used to end the round on the banner with nothing to start the next.
    - **Extra lives by score** (default 20,000, then every 50,000).
    - **Only so many attack at once** (`belt.max_attackers`, default 2): the
      rest wait their turn at a distance. Test
      `on_the_belt_only_so_many_enemies_close_in_at_once`.
    - **Bonus stages between stages**: now and then the run stops for a
      sixty-second bonus. It is drawn from the installed
      bonus games (the ten OXYDE ones, the car, barrels, bricks and bag) and
      played **on the bonus game's own stage** (`game/knuckle_bonus.rs`),
      or from a list, or — `bonusgames = street`, and every older tape — a
      prop parked in the street just cleared. Clearing it pays
      `bonusreward`: by default a mystery reward drawn from the run's seed
      over the original four and the newer continue, invincibility, double
      points, power surge, weapon, full heal and jackpot. See
      [KNUCKLE-UP-CAMPAIGNS.md](KNUCKLE-UP-CAMPAIGNS.md#bonus-stages-between-stages).
    - **Options → KNUCKLE UP**: continues, lives, extend, enemy life,
      attackers at once, wave size, bonus props, friendly fire; all folded into
      the run identity. See [CONFIGURATION.md](CONFIGURATION.md#knuckle-up).
    - **A fighter taken off the stage lets go**: anyone in its custom state is
      released and anything bound to it unbound, at once rather than after the
      five-second abandoned-state rescue.
    - **Two headless traces** for chasing what a run does: `OXYDE_KNUCKLE_TRACE=1`
      prints the run line and every fighter's life each half second, and
      `OXYDE_ORPHAN_TRACE=1` reports anything still drawn whose owner has left
      the match (`Match::orphans`) and any afterimage trailed for ten seconds.

12. **The screens and the HUD.** The run's own screens and HUD — a modern Game
    Over, well-positioned lives and score, a stage summary, and no P2 life bar
    for the opponents. All of it is drawing and app-side
    counting, in `crates/oxyde-app/src/knuckle_ui.rs` and the stats in
    `knuckle.rs`; nothing writes into the `Match`, so `oxtool regress` is
    unchanged.
    - **No P2 bar.** The enemies are a wave from an endless reserve, so the
      versus-style P2 life bar, gauge, name and portrait are gone (screenpack
      and engine HUD alike). In Knuckle Up Co-op the second hero has that
      corner instead.
    - **Floating bars with power.** Each enemy's bar is a slim sheared bar with
      its damage trail draining behind it, its name over it and its power gauge
      under it (gold for each banked 1,000, a notch between levels), so the
      enemy about to throw a super is visible. Props and fighters with no
      gauge get no power line. The boss keeps his wide bar along the bottom,
      on a BOSS plate, with his gauge under it.
    - **The hero's plate**, under their own bars: a life token and `X2`, then
      the score in seven digits that counts up as points arrive (ember while
      counting, the leading zeros dimmed). The plate's foot fills in gold
      towards the next extra life; the token flashes on a 1UP or a revive.
    - **The street's plate**, in the top-right corner the P2 bar left (under
      the clock in co-op): `STAGE 1/3`, one pip per wave of the stage (ember
      once cleared, the live one breathing, the boss's wide and red) and
      `LEFT n`, the enemies still standing. It replaces `KO 0 LEFT 64`, which
      counted the endless reserve.
    - **STAGE n COMPLETE.** Clearing a campaign stage puts up a summary before
      the next stage's card: stage score, knockouts, props broken, best combo,
      damage taken, time, lives left and total score, arriving row by row,
      and a rank (S/A/B/C/D, `StageStats::grade`: lives and continues cost the
      most, damage a point per 50 life, a long combo and props earn some back).
      Five seconds, or a button after the first second. It holds the next
      stage's intro the way the card does, and is local only, like the card.
    - **CONTINUE?** slams in over a darker field, with the seconds in a ring
      that drains (red for the last three) and the credits under it.
    - **GAME OVER / CAMPAIGN COMPLETE.** The run ends on one screen: the
      campaign's name, the headline, the stage reached, the final score
      counting up, the whole run's table and, for each cleared stage, its rank.
      A replay offer line sits above PRESS START. The generic arcade CONTINUE?
      act that used to follow a lost local run is gone: the run's own CONTINUE?
      already offered the house's continues, and the second one ignored the
      KNUCKLE UP option.
    - **"X WINS"** (every mode): the winner's name is the headline, about a
      tenth of the window tall over the fighters' heads, with WINS in gold
      under it on a band that sweeps open. The built-in theme hands its win
      text to this banner with `[Round] win.style = banner`, an Oxyde key
      MUGEN ignores; other screenpacks keep their own `win.text`.
    - `OXYDE_KNUCKLE_SHOW=summary|gameover|complete|continue|win` puts one of
      these screens up at the end of a headless run, for a `--shot`.
    Tests: `knuckle::tests` (`a_stage_counts_its_knockouts_props_combo_damage_and_clock_without_touching_the_match`,
    `the_summary_holds_then_a_button_moves_it_on_but_not_at_once`,
    `the_rank_rewards_a_clean_stage_and_punishes_lives_and_continues`,
    `the_hud_score_counts_up_and_the_lives_flash_on_a_change`),
    `knuckle_ui::tests` (`the_run_plates_never_overlap_the_bars_each_other_or_the_edge`,
    `the_street_plate_takes_the_free_corner_or_sits_under_the_clock`),
    `hud::tests::the_winners_name_is_the_headline_over_the_fighters_heads`,
    `fight::tests::a_pack_can_hand_its_win_message_to_the_engines_banner`.

13. **Replays of a whole run.** See
    [Saving and sending a replay](#saving-and-sending-a-replay) below. Tests
    `a_knuckle_up_run_replays_across_a_stage_change`,
    `skipping_the_stage_card_is_recorded_and_replayed`,
    `a_run_whose_campaign_is_missing_or_changed_is_refused`,
    `a_knuckle_up_run_survives_a_round_trip`,
    `a_format_three_knuckle_up_tape_rebuilds_the_run`.

14. **Two players, their own lives, and enemies that get hit.** Both players
    select at the same time, with separate lives and scoring and a shared
    continue counter; opponents take damage while blocking; and there is no
    versus screen or "Player 2 wins".
    - **One roster, both players at once.** Knuckle Up's select screen gives
      each player their own cursor in their own half: player two joins a solo
      run with START (B before picking leaves again) and picks while player
      one does; player one alone starts at once, as before. Two heroes make
      the run Knuckle Up Co-op (the menu's Co-op expects player two). The
      screenpack says P2 PRESS START where player two's name would go.
    - **No versus screen**, and the five-second freeze before the street is
      gone: confirm → first stage frame was 4.1–4.7 s of `start_match` plus a
      240-tick (4 s) VS screen; it is now 0.39–0.51 s and straight to the
      stage card. The campaign's 280 fighters load on a background thread
      while the card and the first wave play (`Assets::preload_in_background`;
      a wave that walks in first loads its fighter on the spot, as it always
      could), the replay's content hashes are worked out on the same thread
      and filled in before a tape is written (`Game::complete_tape`), and the
      campaign's wave plan is built once instead of twice, with each name
      looked up once. Online co-op keeps the full preload before frame 1.
    - **Each player's own lives and score; the continues are shared.** Each
      seat (`knuckle::Seat`) has its lives, score, extends and CONTINUE?. A
      player out of lives while the other fights on is asked on their own
      plate (CONTINUE? 9…0), spending the run's shared continue with any
      button; letting it run out drops them out of the run (START brings them
      back while a continue is left). Alone, or with both out, the CONTINUE?
      holds the screen as before; with nothing left the run ends on GAME OVER,
      whose table (and every STAGE COMPLETE summary) lists PLAYER 1 and
      PLAYER 2 with their scores and lives. Points go to whoever struck the
      blow (`gethit.attacker`), a score or 1UP pickup to the hero nearest it.
    - **YOU LOSE, never PLAYER 2 WINS.** A lost run says YOU LOSE as it falls
      and GAME OVER on its screen; the enemies are nobody's player two.
    - **No round clock.** A street is untimed unless its campaign sets a
      `time` ([KNUCKLE-UP-CAMPAIGNS.md](KNUCKLE-UP-CAMPAIGNS.md)): the options'
      99 seconds used to run on every wave, and a long one called TIME OVER in
      the middle of the street and took a life for it.
    - **Enemies block less, and not forever.** Measured first, headless, Long
      Run, three heroes × two seeds, 18,000 frames each, the computer hero at
      AI 8 and a scripted button-masher (`OXYDE_KNUCKLE_MASH=1`): 16.7% of the
      computer hero's contacts and 24.8% of the masher's were blocked (Ryu's
      masher up to 46%), the enemies in a guard state 5.0% / 9.1% of the
      time. Damage was already 98% from clean hits — what read as "always
      blocking" was the strings. Now (`[KnuckleUp] enemyguard`, default 50,
      and `guardbreak`, default 3): an enemy decides **once per attack**
      whether to block it, at half the chance its difficulty gave it, scaled
      by its toughness tier and its own lean (`Player::guard_bias`, from the
      run's seed); one that does not is mostly caught standing. Four blocks in
      a row (five for a brute; a campaign boss seven since ku8 —
      `guardbreakboss`, below) and the next hit breaks the guard:
      it lands clean, under a GUARD BREAK! burst over the enemy's head. After:
      11.8% (computer hero) and 13.6% (masher) blocked, guard time 5.0% /
      4.9%, 98.6% / 99.1% of the damage clean, 9 / 10 guards broken; the
      computer hero landed 1,078 clean hits for 51,368 damage against 727 for
      39,701. Both knobs are Knuckle-Up-only belt rules (`BeltRules::guard`,
      `guard_break`); Versus and Arcade never read them.
    - **Replays.** Format 5 records the two guard rules. A format 4 run reads
      them as CLASSIC/off and keeps the options' clock and (in co-op) the one
      shared pool of lives it was recorded with, so its simulation is
      untouched: a Long Run tape re-simulates to the same final checksum
      on this engine as on the one before it.
    Tests: `knuckle::tests` (`each_player_scores_their_own_hits_and_earns_their_own_extends`,
    `a_player_out_of_lives_is_asked_while_the_other_fights_on_and_continues_are_shared`,
    `a_player_who_let_the_countdown_run_out_drops_out_and_start_brings_them_back`,
    `one_player_plays_exactly_as_before`, `an_older_co_op_tape_keeps_its_one_pool_of_lives`),
    `knuckle_up_heroes_are_picked_side_by_side_and_player_two_can_join`,
    `on_the_belt_an_enemy_that_blocks_too_often_has_its_guard_broken`,
    `a_format_four_run_reads_as_classic_guarding_and_format_five_keeps_its_own`,
    `a_street_is_untimed_unless_the_campaign_gives_it_a_clock`.

15. **Further belt rules and pickups.**
    - **The camera leads after a wave** (`[KnuckleUp] cameralead`, default
      on; `BeltRules::camera_lead` = 0.35 of the half view). With nothing left
      to fight, the view eases ahead of the leading hero — 7% of the
      gap a tick, at most seven units — until they stand about a third of the
      way in from the left, so "you don't have to move on the very edge" to
      scroll on. Forward only, held back while an enemy is on screen, never
      past the hero furthest back, and inside `update_camera`, so it is
      simulation state and deterministic. Test
      `camera_lead_runs_ahead_of_the_hero_once_the_screen_is_clear`.
    - **Pickups** (`[KnuckleUp] pickups`, default `full`). Eight new engine
      kinds — `Heal` (percent), `FullHealth`, `Charge` (percent), `FullPower`,
      and four timed ones on `Player::powerups`: `Boost` (POWER UP, hits ×1.5),
      `Speed` (walking ×1.5, both axes), `Shield` (damage taken ×0.5) and
      `Magnet` (pickups within 260 units drift in). A cleared wave the campaign
      named nothing for draws from `knuckle::WAVE_TABLE`, and one fallen grunt
      in five drops from `KO_TABLE`, both keyed by the run's seed. A campaign
      may now name every kind (and `random`); under `full` its `power`,
      `score` and `oneup` drops come out as themselves — under `classic`, as
      before, anything but a weapon came out as health, which is how Rust
      City's `power, 6, 1000` used to heal for 1,000. Art: the same rusted
      OXYDE cases (from the pickup pipeline) — half-lit emblem for the
      partial heal and charge, white-hot with a MAX plate for the full ones,
      a stopwatch on the 1UP case for the timed four — with the same idle
      and flourish (`pickupfx.rs`), plus an aura on whoever runs a timed one.
      Tests `the_ku8_pickups_heal_charge_and_time_their_boosts`,
      `the_drop_tables_are_drawn_from_the_seed_and_cover_every_kind`,
      `a_campaign_names_every_pickup_and_random_is_the_table`.
    - **RAPID FIRE** (rapidfire round, standing in for weapons until there are
      any). A fifth timed pickup, `PickupKind::RapidFire` on
      `Player::powerups.rapid` (12 s): once a move has let its projectile go —
      a `Projectile` controller, or a helper the hero made in that state that
      becomes a travelling attacker — the rest of the state plays at double
      speed (`Match::rapid_fire_recovery`: the current state's controllers run
      a second time a tick, then its animation and `Time` advance again, so
      every tick the state is written against is still visited once), and the
      gauge is held full. Never the startup, never whether a move may fire: a
      character's `NumProjID` guard still holds. `[KnuckleUp] droptable =
      rapidfire` (default) puts it where the tables had the weapon — street
      props' prizes, the mystery draw — and into a cleared wave's table
      (`WAVE_TABLE_RAPID`); a campaign naming `weapon` still gets the weapon.
      On the tape as format 10. See CHANGELOG-rapidfire.md.
    - **Walking on the depth axis looks like walking.** A fighter walking up
      or down the street from a stand would otherwise slide on their stand. The
      simulation counts those ticks (`Player::depth_walk`, out of the
      checksum) and the renderer draws the walk, action 20, from the first
      step (`scene::drawn_action`), heroes and computer enemies alike. It is
      presentation only — the fight's animation, boxes and checksum are the
      stand's — so no replay changes. Test
      `walking_the_depth_from_a_stand_is_counted_for_the_walk_animation`.
    - **Guard break for bosses** (`guardbreakboss`, default 6: the seventh
      block breaks; `guardbreakrest`, default 3 s, during which a broken
      enemy's blocks count for nothing). The boss is marked
      (`Player::belt_boss`) as it walks on. Test
      `a_boss_guards_on_its_own_count_and_a_break_does_not_chain`.
    - **Replays: format 8** carries the four settings above (four bytes after
      WAVE VARIETY); a format 4 to 7 tape reads `legacy_ku8` — bosses as
      brutes, no rest, the tension camera, the classic drops — so it simulates
      exactly as before. Test
      `the_ku8_settings_ride_in_format_eight_and_an_older_run_reads_the_old_rules`.
    - **A headless run does not write `replays/last-run.oxr`** — otherwise a
      scripted run in the game root would replace the player's own last run.
      `--keep-last-run` asks for it; `--save-replay <f>` still writes the tape
      where it is told. Test `a_headless_run_does_not_overwrite_the_last_run`.
    - **Headless aids.** `--shot-at 600,1200` writes `<shot>-000600.png` and
      so on from one run; `OXYDE_KNUCKLE_PICKUPS=<frame>` lays every floor
      pickup out on that frame (`Game::debug_spawn_pickups`);
      `OXYDE_KNUCKLE_TRACE=<n>` traces every n-th frame and now adds the
      camera, the hero's x, the arena lock, the lead, who is walking the
      depth and the guard breaks; `OXYDE_RT_PARTS=1` adds the checksum by
      part to `OXYDE_REPLAY_TRACE`. And the headless `--ai` no longer seats
      the computer on a parked prop: its presses were not on the tape, so a
      headless run that never broke the car saved a replay that "diverged" on
      its last frame (the fight itself was identical).

Every engine piece above is gated on `belt.enabled`, and `oxtool regress` is
`1051 unchanged` — the MUGEN plane is untouched. What is additive on this core
(Lua presentation, online co-op, roster-wide balance) is content and tuning
rather than engine code.

## Saving and sending a replay

A Knuckle Up run is recorded from the first wave to the last frame as **one
tape** — across every stage change, bonus prop, revive and continue — and that
tape reproduces the run exactly when played back. It is the bug report: send
the file, and whoever receives it re-simulates the run frame for frame.

**Saving one, at the cabinet:**

- **Mid-run:** press **Start** to pause (the move list page opens over the
  frozen fight). Its first row is **SAVE REPLAY** — press **A** on it, or
  **Select** anywhere on the page. The run so far is written and the row says
  `SAVED <file>`; the run carries on when you press **B** or **Start**.
- **When the run ends** — GAME OVER, the CONTINUE? countdown running out, or
  CAMPAIGN CLEAR — the result screen offers **SELECT TO SAVE THE REPLAY**, as
  every mode's does. With `[Replay] record = auto` it is saved without asking.
- **Afterwards:** the most recent run is always kept as
  `replays/last-run.oxr`, overwritten by the next one. It is written when a run
  ends, when one is quit (Start + B, Escape, closing the window) and at every
  stage change, so a bug you only think to report later is still on disk.
  `[Replay] record = off` turns all of this off.

Saved replays go in the `replays/` folder of the game (`[Replay] dir`), named
for when, what and who — `2026-10-10_1426_knuckleup_mech-sagat_rust-city_stage2.oxr`
(see [MODES.md](MODES.md#replays) for the naming rule).

**What the tape carries** beyond the inputs (replay format 4, format 5's two enemy-guard rules, format 6's bonus settings — `bonusgames` and `bonusreward` — format 7's `wavevariety`, one byte, format 8's `guardbreakboss`, `guardbreakrest`, `cameralead` and `pickups`, four bytes, format 9's `streetprops`, one byte, and format 10's `droptable`, one byte; a tape from before format 7 plays its waves as the campaign wrote them, one from before format 8 on the old boss guard, the tension camera and the classic drops, one from before format 9 its streets undressed, and one from before format 10 on the drop tables with the weapon): the campaign by
path *and* by content (`Campaign::identity`), the `[KnuckleUp]` house rules
and round time it was played under, and the two decisions the app takes outside
the step — every fighter's `AILevel` as it changes, and a button that cut a
stage card or an entrance short. Playback refuses, by name, a run whose
campaign is not installed (`CAMPAIGN ... IS NOT INSTALLED`) or has been edited
since (`... IS A DIFFERENT VERSION FROM THE ONE RECORDED`); drop the sender's
`.knuckle` into `knuckleup/campaigns/` and it is found there. A tape names its
campaign by the path it had when recorded; one recorded before the campaign
moved into `knuckleup/` (`data/campaigns/rust_city.knuckle`) finds it by file
name in the folder, or by identity among everything installed. A tape from before
format 4 names no campaign; playback recognises it by its enemy line-up — the
installed campaign whose plan deals exactly the recorded side-two fighters.
Nor does it carry `AILevel` or the intro skips: the levels are worked out from
*this* install's difficulty and `[Arcade]` ramp (so play it back on the
sender's `mugen.cfg`), and a skipped stage card is inferred from the first
frame anybody pressed anything — the computer's seats act the moment control is
handed over. A format-3 tape of 40,528 frames with a continue in it reproduces
this way to its recorded checksum on the 0.36.0 engine that recorded it. An
engine fix that changes what happens in that run means it plays to its last
frame and ends on another checksum on a later engine; the reconstruction is
what is pinned (test
`a_format_three_knuckle_up_tape_rebuilds_the_run`). A tape reproduces on the
engine that recorded it — an engine fix that changes a fight changes its
replays too.

**Re-simulating one, as a developer:**

```bash
oxtool replay info  replays/last-run.oxr          # campaign, house rules, stage reached
oxtool replay verify . replays/last-run.oxr       # fighters, stage and campaign present here?
OXYDE_KNUCKLE_TRACE=1 OXYDE_ORPHAN_TRACE=1 \
  oxyde --headless --replay replays/last-run.oxr --frames 100000
```

`oxtool replay scan . replays/last-run.oxr` plays the tape with the sweep's
detectors watching and prints each finding with its tape frame;
`OXYDE_SCAN_DIR=dir` on the headless run writes a frame-by-frame log of every
fighter, helper and prop (and PNGs with `OXYDE_SCAN_EVERY`/`OXYDE_SCAN_AT`).

The headless run prints `replay  reproduced exactly`, or the frame and
checksum it diverged at (and exits 1). A scripted run can be written out with
`--save-replay <file>`:

```bash
OXYDE_KNUCKLE_CAMPAIGN=rust_city \
  oxyde --headless --mode knuckleup --p1 chars/mech_sagat/mech_sagat.def \
        --frames 20000 --seed 7 --ai 8 --save-replay run.oxr
```
