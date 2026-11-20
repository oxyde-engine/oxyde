; ===========================================================================
;  ARROYO  -  command set
;  Notation is numpad: 236 = quarter circle forward, 214 = quarter circle
;  back, 623 = dragon punch.  Buttons are x/y/z light-medium-heavy stick and
;  a/b/c light-medium-heavy kick.
;
;  Motion commands open with a release (`~D`) the way chars/kfm/kfm.cmd's
;  header asks for: without it the motion matches while the direction is
;  still being held down and specials fire out of a crouch by accident.
; ===========================================================================

[Remap]
x = x
y = y
z = z
a = a
b = b
c = c
s = s

[Defaults]
command.time = 15
command.buffer.time = 1

; --- the buttons -----------------------------------------------------------
[Command]
name = "x"
command = x
time = 1
[Command]
name = "y"
command = y
time = 1
[Command]
name = "z"
command = z
time = 1
[Command]
name = "a"
command = a
time = 1
[Command]
name = "b"
command = b
time = 1
[Command]
name = "c"
command = c
time = 1
[Command]
name = "start"
command = s
time = 1
[Command]
name = "recovery"
command = x+y
time = 1

; --- held directions and buttons -------------------------------------------
; A held button is how a special picks its strength, and a held direction is
; how a command normal tells itself apart from the plain one.
[Command]
name = "holdfwd"
command = /$F
time = 1
[Command]
name = "holdback"
command = /$B
time = 1
[Command]
name = "holdup"
command = /$U
time = 1
[Command]
name = "holddown"
command = /$D
time = 1
[Command]
name = "hold_x"
command = /x
time = 1
[Command]
name = "hold_y"
command = /y
time = 1
[Command]
name = "hold_z"
command = /z
time = 1
[Command]
name = "hold_a"
command = /a
time = 1
[Command]
name = "hold_b"
command = /b
time = 1
[Command]
name = "hold_c"
command = /c
time = 1

; --- movement ---------------------------------------------------------------
; A dash is a deliberate double tap. A looser window lets the two backward
; halves of a 214-something motion match it as well, so the hop comes out in
; the middle of a special; specials and supers may be cancelled out of a
; dash, which is what makes the overlap harmless when it does happen.
[Command]
name = "FF"
command = F, F
time = 8
[Command]
name = "BB"
command = B, B
time = 8

; --- RIO GRANDE  236236 + HK  (level 3) -------------------------------------
[Command]
name = "rio"
command = ~D, DF, F, D, DF, F, c
time = 40
[Command]
name = "rio"
command = ~D, DF, F, D, DF, F, b
time = 40

; --- OXIDE BOLT  236 + P -----------------------------------------------------
[Command]
name = "bolt"
command = ~D, DF, F, x
time = 18
[Command]
name = "bolt"
command = ~D, DF, F, y
time = 18
[Command]
name = "bolt"
command = ~D, DF, F, z
time = 18

; --- TRES GOLPES  236 + K  (rekka: repeat the motion or just the button) ----
[Command]
name = "tres"
command = ~D, DF, F, a
time = 18
[Command]
name = "tres"
command = ~D, DF, F, b
time = 18
[Command]
name = "tres"
command = ~D, DF, F, c
time = 18

; --- SINAWALI CYCLONE  214 + K  (air OK) -------------------------------------
[Command]
name = "cyclone"
command = ~D, DB, B, a
time = 18
[Command]
name = "cyclone"
command = ~D, DB, B, b
time = 18
[Command]
name = "cyclone"
command = ~D, DB, B, c
time = 18

; --- REDONDO UPPER  623 + P --------------------------------------------------
[Command]
name = "redondo"
command = ~F, D, DF, x
time = 18
[Command]
name = "redondo"
command = ~F, D, DF, y
time = 18
[Command]
name = "redondo"
command = ~F, D, DF, z
time = 18

; --- ARNIS VAULT  214 + P ----------------------------------------------------
[Command]
name = "vault"
command = ~D, DB, B, x
time = 18
[Command]
name = "vault"
command = ~D, DB, B, y
time = 18
[Command]
name = "vault"
command = ~D, DB, B, z
time = 18

; --- throw -------------------------------------------------------------------
[Command]
name = "puno"
command = /$F, z
time = 2

[Command]
name = "throwfwd"
command = /$F, y
time = 2
[Command]
name = "throwback"
command = /$B, y
time = 2

; ===========================================================================
;  [Statedef -1] runs every tick, top to bottom, and the first entry whose
;  triggers hold wins - so the order here is the move priority. Supers first,
;  then specials, then command normals, then normals.
; ===========================================================================
[Statedef -1]

; --- super ------------------------------------------------------------------
[State -1, Rio Grande]
type = ChangeState
value = 3000
triggerall = command = "rio"
triggerall = power >= 3000
triggerall = statetype != A || stateno = [100, 106]
trigger1 = ctrl
trigger2 = stateno = [200, 230]
trigger2 = movecontact
trigger3 = stateno = [1100, 1120]
trigger3 = movecontact

; --- specials ----------------------------------------------------------------
[State -1, Redondo Upper]
type = ChangeState
value = 1300
triggerall = command = "redondo"
triggerall = statetype != A || stateno = [100, 106]
trigger1 = ctrl
trigger2 = stateno = [200, 230]
trigger2 = movecontact
trigger3 = stateno = [400, 430]
trigger3 = movecontact

[State -1, Oxide Bolt]
type = ChangeState
value = 1000
triggerall = command = "bolt"
triggerall = statetype != A || stateno = [100, 106]
trigger1 = ctrl
trigger2 = stateno = [200, 230]
trigger2 = movecontact
trigger3 = stateno = [400, 430]
trigger3 = movecontact

[State -1, Tres Golpes]
type = ChangeState
value = 1100
triggerall = command = "tres"
triggerall = statetype != A || stateno = [100, 106]
trigger1 = ctrl
trigger2 = stateno = [200, 230]
trigger2 = movecontact
trigger3 = stateno = [400, 430]
trigger3 = movecontact

[State -1, Sinawali Cyclone]
type = ChangeState
value = 1200
triggerall = command = "cyclone"
trigger1 = ctrl
trigger1 = statetype = S
trigger2 = ctrl
trigger2 = statetype = A
trigger3 = stateno = [200, 230]
trigger3 = movecontact

[State -1, Arnis Vault]
type = ChangeState
value = 1400
triggerall = command = "vault"
triggerall = statetype = S
trigger1 = ctrl

; --- throw --------------------------------------------------------------------
[State -1, Throw]
type = ChangeState
value = 800
triggerall = command = "throwfwd" || command = "throwback"
triggerall = statetype = S
triggerall = ctrl
triggerall = stateno != 100
trigger1 = p2bodydist X < 8
trigger1 = (p2statetype = S) || (p2statetype = C)
trigger1 = p2movetype != H

; --- dashes ---------------------------------------------------------------------
[State -1, Run]
type = ChangeState
value = 100
trigger1 = command = "FF"
trigger1 = statetype = S
trigger1 = ctrl

[State -1, Back Dash]
type = ChangeState
value = 105
trigger1 = command = "BB"
trigger1 = statetype = S
trigger1 = ctrl

; --- command normal ------------------------------------------------------------------
[State -1, Puno Cross]
type = ChangeState
value = 230
triggerall = command = "puno"
trigger1 = statetype = S
trigger1 = ctrl

; --- standing normals ------------------------------------------------------------------
; Chains run light to heavy: a jab that connected may be cancelled into a
; medium, and a medium into a heavy.
[State -1, 5HK]
type = ChangeState
value = 225
triggerall = command = "c"
triggerall = command != "holddown"
trigger1 = statetype = S
trigger1 = ctrl
trigger2 = stateno = [200, 215]
trigger2 = movecontact

[State -1, 5HP]
type = ChangeState
value = 220
triggerall = command = "z"
triggerall = command != "holddown"
trigger1 = statetype = S
trigger1 = ctrl
trigger2 = stateno = [200, 215]
trigger2 = movecontact

[State -1, 5MK]
type = ChangeState
value = 215
triggerall = command = "b"
triggerall = command != "holddown"
trigger1 = statetype = S
trigger1 = ctrl
trigger2 = stateno = [200, 205]
trigger2 = movecontact

[State -1, 5MP]
type = ChangeState
value = 210
triggerall = command = "y"
triggerall = command != "holddown"
trigger1 = statetype = S
trigger1 = ctrl
trigger2 = stateno = [200, 205]
trigger2 = movecontact

[State -1, 5LK]
type = ChangeState
value = 205
triggerall = command = "a"
triggerall = command != "holddown"
trigger1 = statetype = S
trigger1 = ctrl
trigger2 = stateno = 200
trigger2 = movecontact

[State -1, 5LP]
type = ChangeState
value = 200
triggerall = command = "x"
triggerall = command != "holddown"
trigger1 = statetype = S
trigger1 = ctrl

; --- crouching normals -------------------------------------------------------------
[State -1, 2HK]
type = ChangeState
value = 430
triggerall = command = "c"
triggerall = command = "holddown"
trigger1 = statetype = C
trigger1 = ctrl

[State -1, 2MP]
type = ChangeState
value = 410
triggerall = command = "y" || command = "z" || command = "b"
triggerall = command = "holddown"
trigger1 = statetype = C
trigger1 = ctrl
trigger2 = stateno = 400
trigger2 = movecontact

[State -1, 2LK]
type = ChangeState
value = 400
triggerall = command = "x" || command = "a"
triggerall = command = "holddown"
trigger1 = statetype = C
trigger1 = ctrl

; Ground normals are listed above the air ones on purpose. The two sets
; are mutually exclusive - one wants `statetype = S`, the other
; `statetype = A` - so the order changes nothing in play, but the move
; list the engine reads out of this file takes the first entry a button
; leads to, and the useful answer for a button pressed on the ground is
; the standing normal.
; --- air normals -----------------------------------------------------------------
[State -1, j.HP]
type = ChangeState
value = 620
triggerall = command = "z" || command = "c"
trigger1 = statetype = A
trigger1 = ctrl

[State -1, j.LP]
type = ChangeState
value = 600
triggerall = command = "x" || command = "y" || command = "a" || command = "b"
trigger1 = statetype = A
trigger1 = ctrl

; --- taunt ---------------------------------------------------------------------------
[State -1, Taunt]
type = ChangeState
value = 195
trigger1 = command = "start"
trigger1 = statetype != A
trigger1 = ctrl
