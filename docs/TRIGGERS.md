# Triggers

Every trigger this engine understands, and how it is written. Read out of the compiler's own table at build time, including the number of arguments each one takes — so a trigger that is here is one the engine will accept, spelled the way it accepts it.

A trigger is an *expression*: it asks the engine a question and gets a number back. That is what separates it from a state controller, which does something. `AnimElem = 3` is a trigger; `ChangeAnim(value: 3)` is a controller.

Usage counted across 300 characters.

| trigger | written as | used by |
|---|---|---:|
| `anim` | `anim` | 300 |
| `animtime` | `animtime` | 300 |
| `attack` | `attack` | 300 |
| `command` | `command("text")` | 300 |
| `const` | `const(name)` | 300 |
| `ctrl` | `ctrl` | 300 |
| `e` | `e` | 300 |
| `id` | `id` | 300 |
| `life` | `life` | 300 |
| `movetype` | `movetype, asserted rather than compared` | 300 |
| `pausetime` | `pausetime` | 300 |
| `physics` | `physics, asserted rather than compared` | 300 |
| `pos` | `pos x   \|   pos y` | 300 |
| `power` | `power` | 300 |
| `rad` | `rad(_)` | 300 |
| `round` | `round(_, _)` | 300 |
| `scale` | `scale x   \|   scale y` | 300 |
| `stateno` | `stateno` | 300 |
| `statetype` | `statetype, asserted rather than compared` | 300 |
| `tan` | `tan(_)` | 300 |
| `time` | `time` | 300 |
| `vel` | `vel x   \|   vel y` | 300 |
| `animelem` | `animelem = n   \|   animelem = n, cmp` | 299 |
| `movecontact` | `movecontact` | 293 |
| `offset` | `offset x   \|   offset y` | 293 |
| `sprpriority` | `sprpriority` | 288 |
| `var` | `var(_)` | 282 |
| `exp` | `exp(_)` | 275 |
| `p2bodydist` | `p2bodydist x   \|   p2bodydist y` | 273 |
| `facing` | `facing` | 272 |
| `p2stateno` | `p2stateno` | 270 |
| `random` | `random` | 263 |
| `movehit` | `movehit` | 261 |
| `name` | `name("text")` | 253 |
| `p2movetype` | `p2movetype, asserted rather than compared` | 247 |
| `p2statetype` | `p2statetype, asserted rather than compared` | 247 |
| `sin` | `sin(_)` | 240 |
| `index` | `index` | 239 |
| `ifelse` | `ifelse(_, _, _)` | 234 |
| `roundstate` | `roundstate` | 233 |
| `float` | `float(_)` | 225 |
| `frontedge` | `frontedge` | 223 |
| `prevstateno` | `prevstateno` | 220 |
| `alive` | `alive` | 219 |
| `animexist` | `animexist(_)` | 219 |
| `numhelper` | `numhelper(0 to 1 arguments)` | 216 |
| `selfanimexist` | `selfanimexist(_)` | 210 |
| `p2dist` | `p2dist x   \|   p2dist y` | 204 |
| `roundno` | `roundno` | 201 |
| `projhit` | `projhit, with a projectile id suffix: projhit2` | 198 |
| `backedge` | `backedge` | 197 |
| `hitover` | `hitover` | 197 |
| `moveguarded` | `moveguarded` | 194 |
| `hitshakeover` | `hitshakeover` | 182 |
| `floor` | `floor(_)` | 177 |
| `sysvar` | `sysvar(_)` | 176 |
| `numexplod` | `numexplod(0 to 1 arguments)` | 173 |
| `animelemtime` | `animelemtime(_)` | 168 |
| `gethitvar` | `gethitvar(name)` | 167 |
| `hitvel` | `hitvel x   \|   hitvel y` | 161 |
| `numproj` | `numproj` | 160 |
| `frontedgebodydist` | `frontedgebodydist` | 157 |
| `backedgebodydist` | `backedgebodydist` | 152 |
| `hitcount` | `hitcount` | 150 |
| `hitfall` | `hitfall` | 140 |
| `backedgedist` | `backedgedist` | 139 |
| `canrecover` | `canrecover` | 139 |
| `win` | `win` | 137 |
| `p2life` | `p2life` | 136 |
| `hitdefattr` | `hitdefattr, asserted rather than compared` | 134 |
| `abs` | `abs(_)` | 131 |
| `frontedgedist` | `frontedgedist` | 130 |
| `timemod` | `timemod = n   \|   timemod = n, cmp` | 124 |
| `attackmul` | `attackmul` | 119 |
| `matchover` | `matchover` | 116 |
| `gametime` | `gametime` | 115 |
| `p2name` | `p2name("text")` | 113 |
| `ishelper` | `ishelper(0 to 1 arguments)` | 108 |
| `screenpos` | `screenpos x   \|   screenpos y` | 108 |
| `fvar` | `fvar(_)` | 102 |
| `angle` | `angle` | 96 |
| `defencemul` | `defencemul` | 96 |
| `lose` | `lose` | 91 |
| `ln` | `ln(_)` | 87 |
| `p4name` | `p4name("text")` | 87 |
| `animelemno` | `animelemno(_)` | 86 |
| `ceil` | `ceil(_)` | 84 |
| `map` | `map(name)` | 82 |
| `winko` | `winko` | 81 |
| `pi` | `pi` | 79 |
| `palno` | `palno` | 72 |
| `log` | `log(_, _)` | 70 |
| `numprojid` | `numprojid(_)` | 70 |
| `numtarget` | `numtarget(0 to 1 arguments)` | 66 |
| `teamside` | `teamside` | 66 |
| `inguarddist` | `inguarddist` | 59 |
| `max` | `max(_, _)` | 58 |
| `projhittime` | `projhittime(_)` | 52 |
| `rootdist` | `rootdist x   \|   rootdist y` | 52 |
| `parentdist` | `parentdist x   \|   parentdist y` | 50 |
| `teammode` | `teammode, asserted rather than compared` | 49 |
| `roundsexisted` | `roundsexisted` | 45 |
| `min` | `min(_, _)` | 44 |
| `authorname` | `authorname("text")` | 43 |
| `projcontact` | `projcontact, with a projectile id suffix: projcontact2` | 42 |
| `hitpausetime` | `hitpausetime` | 40 |
| `numpartner` | `numpartner` | 37 |
| `alpha` | `alpha source \| dest` | 34 |
| `cos` | `cos(_)` | 33 |
| `loseko` | `loseko` | 31 |
| `numenemy` | `numenemy` | 30 |
| `ishometeam` | `ishometeam` | 28 |
| `matchno` | `matchno` | 26 |
| `projguarded` | `projguarded, with a projectile id suffix: projguarded2` | 25 |
| `drawgame` | `drawgame` | 20 |
| `p1name` | `p1name("text")` | 18 |
| `uniqhitcount` | `uniqhitcount` | 18 |
| `playeridexist` | `playeridexist(_)` | 17 |
| `atan` | `atan(_)` | 16 |
| `p3name` | `p3name("text")` | 14 |
| `projcontacttime` | `projcontacttime(_)` | 10 |
| `movereversed` | `movereversed` | 9 |
| `winperfect` | `winperfect` | 9 |
| `dizzy` | `dizzy` | 8 |
| `lifemax` | `lifemax` | 8 |
| `parry` | `parry` | 7 |
| `wintime` | `wintime` | 6 |
| `powermax` | `powermax` | 5 |
| `losetime` | `losetime` | 4 |
| `projcanceltime` | `projcanceltime(_)` | 4 |
| `cond` | `cond(_, _, _)` | 3 |
| `projguardedtime` | `projguardedtime(_)` | 2 |
| `sign` | `sign(_)` | 2 |
| `absorb` | `absorb` | 1 |
| `acos` | `acos(_)` | 1 |
| `deg` | `deg(_)` | 1 |
| `guardbreak` | `guardbreak` | 1 |
| `guardcount` | `guardcount` | 1 |
| `tickspersecond` | `tickspersecond` | 1 |
| `absorbcount` | `absorbcount` | — |
| `absorbpower` | `absorbpower` | — |
| `absorbwindow` | `absorbwindow` | — |
| `ailevel` | `ailevel` | — |
| `ailevelf` | `ailevelf` | — |
| `airjumpcount` | `airjumpcount` | — |
| `analog` | `analog(name)` | — |
| `animelemvar` | `animelemvar(name)` | — |
| `animlength` | `animlength` | — |
| `animplayerno` | `animplayerno` | — |
| `asin` | `asin(_)` | — |
| `atan2` | `atan2(_, _)` | — |
| `bgmvar` | `bgmvar(name)` | — |
| `botboundbodydist` | `botboundbodydist` | — |
| `botbounddist` | `botbounddist` | — |
| `bottomedge` | `bottomedge` | — |
| `camerapos` | `camerapos x   \|   camerapos y` | — |
| `camerazoom` | `camerazoom` | — |
| `clamp` | `clamp(_, _, _)` | — |
| `clsnoverlap` | `clsnoverlap(a mixed list of values and names)` | — |
| `clsnvar` | `clsnvar(a mixed list of values and names)` | — |
| `combocount` | `combocount` | — |
| `consecutivewins` | `consecutivewins` | — |
| `const1080p` | `const1080p(_)` | — |
| `const240p` | `const240p(_)` | — |
| `const480p` | `const480p(_)` | — |
| `const720p` | `const720p(_)` | — |
| `debugmode` | `debugmode` | — |
| `decisiveround` | `decisiveround` | — |
| `displayname` | `displayname("text")` | — |
| `dizzypoints` | `dizzypoints` | — |
| `dizzypointsmax` | `dizzypointsmax` | — |
| `drawpal` | `drawpal group \| index` | — |
| `envshakevar` | `envshakevar(name)` | — |
| `explodvar` | `explodvar(a mixed list of values and names)` | — |
| `fightscreenstate` | `fightscreenstate(name)` | — |
| `fightscreenvar` | `fightscreenvar(name)` | — |
| `fighttime` | `fighttime` | — |
| `firstattack` | `firstattack` | — |
| `gameheight` | `gameheight` | — |
| `gamemode` | `gamemode("text")` | — |
| `gameoption` | `gameoption(name)` | — |
| `gamevar` | `gamevar(name)` | — |
| `gamewidth` | `gamewidth` | — |
| `gethitvar.attr` | `gethitvar.attr, asserted rather than compared` | — |
| `groundangle` | `groundangle` | — |
| `groundlevel` | `groundlevel` | — |
| `guardpoints` | `guardpoints` | — |
| `guardpointsmax` | `guardpointsmax` | — |
| `hasflag` | `hasflag(a mixed list of values and names)` | — |
| `helperindexexist` | `helperindexexist(_)` | — |
| `helpername` | `helpername("text")` | — |
| `helpervar` | `helpervar(name)` | — |
| `hitbyattr` | `hitbyattr(name)` | — |
| `hitdefvar` | `hitdefvar(name)` | — |
| `hitoverridden` | `hitoverridden` | — |
| `ikemenversion` | `ikemenversion(name)` | — |
| `incustomanim` | `incustomanim` | — |
| `incustomstate` | `incustomstate` | — |
| `indialogue` | `indialogue` | — |
| `inputtime` | `inputtime(name)` | — |
| `introstate` | `introstate` | — |
| `isasserted` | `isasserted(name)` | — |
| `isclsnproxy` | `isclsnproxy` | — |
| `ishost` | `ishost` | — |
| `jugglepoints` | `jugglepoints(0 to 1 arguments)` | — |
| `lastplayerid` | `lastplayerid` | — |
| `layerno` | `layerno` | — |
| `leftedge` | `leftedge` | — |
| `lerp` | `lerp(_, _, _)` | — |
| `localcoord` | `localcoord x   \|   localcoord y` | — |
| `memberno` | `memberno` | — |
| `motifstate` | `motifstate(name)` | — |
| `motifvar` | `motifvar(name)` | — |
| `movecountered` | `movecountered` | — |
| `movehitvar` | `movehitvar(name)` | — |
| `mugenversion` | `mugenversion(name)` | — |
| `numplayer` | `numplayer` | — |
| `numstagebg` | `numstagebg(0 to 1 arguments)` | — |
| `numtext` | `numtext(0 to 1 arguments)` | — |
| `outrostate` | `outrostate` | — |
| `oxydeversion` | `oxydeversion(name)` | — |
| `p5name` | `p5name("text")` | — |
| `p6name` | `p6name("text")` | — |
| `p7name` | `p7name("text")` | — |
| `p8name` | `p8name("text")` | — |
| `palfxvar` | `palfxvar(name)` | — |
| `parentexist` | `parentexist` | — |
| `parrycount` | `parrycount` | — |
| `parrykind` | `parrykind, asserted rather than compared` | — |
| `parrywindow` | `parrywindow` | — |
| `playerindexexist` | `playerindexexist(_)` | — |
| `playerno` | `playerno` | — |
| `playernoexist` | `playernoexist(_)` | — |
| `prevanim` | `prevanim` | — |
| `prevmovetype` | `prevmovetype, asserted rather than compared` | — |
| `prevstatetype` | `prevstatetype, asserted rather than compared` | — |
| `projclsnoverlap` | `projclsnoverlap(a mixed list of values and names)` | — |
| `projvar` | `projvar(a mixed list of values and names)` | — |
| `randomrange` | `randomrange(_, _)` | — |
| `receiveddamage` | `receiveddamage` | — |
| `receivedhits` | `receivedhits` | — |
| `redlife` | `redlife` | — |
| `reversaldefattr` | `reversaldefattr, asserted rather than compared` | — |
| `rightedge` | `rightedge` | — |
| `roundswon` | `roundswon` | — |
| `roundtime` | `roundtime` | — |
| `runorder` | `runorder` | — |
| `score` | `score` | — |
| `scoretotal` | `scoretotal` | — |
| `screenheight` | `screenheight` | — |
| `screenwidth` | `screenwidth` | — |
| `selfcommand` | `selfcommand("text")` | — |
| `selfstatenoexist` | `selfstatenoexist(_)` | — |
| `shader` | `shader("text")` | — |
| `soundvar` | `soundvar(a mixed list of values and names)` | — |
| `spriteplayerno` | `spriteplayerno` | — |
| `spritevar` | `spritevar(name)` | — |
| `stagebackedgedist` | `stagebackedgedist` | — |
| `stagebgvar` | `stagebgvar(a mixed list of values and names)` | — |
| `stageconst` | `stageconst(name)` | — |
| `stagefrontedgedist` | `stagefrontedgedist` | — |
| `stagetime` | `stagetime` | — |
| `stagevar` | `stagevar(name)` | — |
| `standby` | `standby` | — |
| `stateowner` | `stateowner` | — |
| `sysfvar` | `sysfvar(_)` | — |
| `teamleader` | `teamleader` | — |
| `teamsize` | `teamsize` | — |
| `timeelapsed` | `timeelapsed` | — |
| `timeremaining` | `timeremaining` | — |
| `timetotal` | `timetotal` | — |
| `topboundbodydist` | `topboundbodydist` | — |
| `topbounddist` | `topbounddist` | — |
| `topedge` | `topedge` | — |
| `winclutch` | `winclutch` | — |
| `winhyper` | `winhyper` | — |
| `winspecial` | `winspecial` | — |
| `xangle` | `xangle` | — |
| `xshear` | `xshear` | — |
| `yangle` | `yangle` | — |
| `zoomvar` | `zoomvar(name)` | — |

