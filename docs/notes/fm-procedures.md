# F-104G flight manual extract: checklists, procedures, limits, test reference values

Source: T.O. 1F-104G-1 (Change 6), `docs/sources/FlightManual-F-RF-TF-104G.pdf` (scan, not in repo). Extracted
2026-10-27 for the sim test program (pilot + test engineer view). Each item: FM page (PDF page). Values read from
charts are marked ≈. F/RF = single-seat F-104G/RF-104G (our variant). Weight basis for speeds: 16 100 lb unless
stated; **approach/landing speeds +5 kt per 1 000 lb** (FM 2-23).

Not extracted (irrelevant for the sim or for later): cockpit preflight switch lists (FM 2-1..2-11), exterior inspection
(Fig. 2-1), ejection, oxygen, radios, armament, fuel grades (Fig. 2-9), alert procedures. Section IV (autopilot/AFCS,
navigation) still to be read for the cockpit/AP work package.

## 1. Normal procedures (Section II)

### Engine start (FM 2-12, 2-13; PDF 144, 145)
1. Throttle OFF, start switch START (auto-start) - starter max. 1 min continuous, then 2 min cooling.
2. At 10 % rpm: throttle OFF -> beyond IDLE -> back to IDLE detent.
3. Fuel flow at 10-12 % rpm: **400-800 lb/h** (> 800 hot start risk, < 400 hung start).
4. Combustion by 20 % rpm or within 20 s of fuel flow, else false/hung/hot start procedure (throttle OFF, motor).
5. Start switches STOP-START at 40 % rpm (stop air). Max. start time 1 min from first rpm to idle.
6. **Idle checks: nozzle 8.5-9.5, rpm 67 ± 1 %, EGT 320-420 °C** (hot day up to 500, cold down to 120), oil ≥ 12 psi,
   **fuel flow 700-1 600 lb/h**.
- Throttle to OFF unintentionally = immediate flameout; do not reopen (fire hazard).

### After start / pilot-crew chief check (FM 2-15, 2-16; PDF 147, 148)
- Hydraulic No. 2: speed brakes out/in -> drop to ≥ 2 175 psi, max. 3 300 psi, back to normal (≈ 3 000).
- Controls: ailerons (≥ 2 600 psi), stabilizer (≥ 2 700 psi), rudder - full cycle each.
- **Trim check and set to TAKEOFF** (order: aileron, stabilizer, rudder); stick neutral. Takeoff trim light at
  stabilizer takeoff setting. Note: an AP engaged after the trim check may drive the stabilizer away from takeoff
  trim -> recheck (FM 2-18).
- Dampers OFF then ON: ROLL, PITCH, YAW.
- APC check: shaker at AoA indicator 4¼-4¾, kicker at 5 (NOT with gear down); aileron/rudder limiters.
- **Flaps LAND: BLC airflow, extension ≤ 20 s. Flaps TAKEOFF: no BLC.** Not more than one flap cycle at idle;
  repeated cycles need ≥ 85 % rpm.
- Emergency nozzle closure check: idle, handle pull -> nozzle 1.0-3.0 within 1 s, push in -> back to idle area.

### Taxi (FM 2-17, 2-18; PDF 149, 150)
- Nosewheel steering engaged with pedals aligned; no speed brakes while steering/antiskid needed.
- Anti-skid inoperative below 10 kt. Canopy open: taxi ≤ 50 kt.
- Ground clearances (Fig. 2-4): fin tip 13.5 ft, stabilizer 12.6 ft, nose boom 4.13 ft, tip tanks 2.07 ft;
  turning radius outside tip tank 47.7 ft, pitot 48.1 ft, pivot point inside wheel.

### Before takeoff (FM 2-17, 2-18; PDF 149, 150)
Tanks feeding - **flaps TAKEOFF** - harness - **speed brakes IN** - canopy locked - oxygen/radios - **stabilizer takeoff
trim light** - anti-collision lights.

### Engine check on the runway (FM 2-18, 2-19; PDF 150, 151)
1. Throttle burst to Military: **acceleration ≤ 10 s; rpm 100 ± 1 %; EGT 590 ± 10 °C (-11A) / 605 ± 10 (-11B);
   nozzle 1.0-3.5**; fuel flow per Fig. 2-5 (ground, vs. OAT and field elevation, ± 500 lb/h; sea level ≈ 7 000-
   8 400 lb/h); oil pressure ± 2.5 psi steady.
2. Slowly to 80 % (no compressor stall), back to Military, rapidly to IDLE (min. fuel flow 400 lb/h).

### Takeoff (FM 2-20, 2-21, 6-5; PDF 152, 153, 395)
1. Nosewheel steering, Military, brakes release, minimum AB (stabilized light: rpm roll-back then normal, EGT > 600
   then 580-600 °C, nozzle 3.5-5), Maximum thrust (nozzle 7.5-9.5). AB blowout: nozzle < 7, EGT < 500 °C, thrust loss.
2. Back stick 20-25 kt below computed takeoff speed; rotation/nose wheel lift-off 10-20 kt below (5-10 kt for forward
   CG); **takeoff attitude ≈ 5° nose up**. Takeoff speed (Fig. 2-6) **190 KIAS at 20 800 lb** (no stores, F/RF),
   200 KIAS at 23 450 lb (full tip tanks). Minimum-run: -5 kt. Gusty crosswind: +5 KIAS per 10 kt above steady.
3. Full 17° stabilizer only with trim 1-11° LED; takeoff trim 5° LED. Fast stick input = dynamic overshoot, nose may
   fall back ("light stick").
- **After takeoff** (FM 2-22): gear UP when definitely airborne, **up and locked before 260 KIAS**; flaps UP at
  ≥ 260 KIAS (easily controllable nose-up tendency as the flaps retract); throttle as desired; best climb speed.

### Climb / cruise / AB / descent (FM 2-22, 2-23; PDF 154, 155)
- Max-thrust climb is extremely steep (Fig. 6-7); best climb speeds in the appendix.
- Roll SAS OFF before 575 KIAS with tip missiles (structural).
- AB light: if no light within ≈ 3 s (sea level) / 5 s (altitude), back to Military 3-5 s, retry.
- Descent: altimeter, fuel check (sets final approach speed).

### Before landing / pattern (FM 2-23, 2-24, Fig. 2-7; PDF 155, 156, 158, 159)
1. **Autopilot engage switch OFF** - available stick rate is reduced with AP engaged (flare/gusts).
2. Initial: flaps TAKEOFF, 325 KIAS, 1 500 ft AGL.
3. Downwind: gear DOWN < 260 KIAS; flaps LAND below 240 / above 210 KIAS; keep level until flaps + BLC work
   (mild roll transient possible, ≤ 1 in lateral stick).
4. Base: gear down and locked, anti-skid light checked, ≥ 200 KIAS, lose ≤ 500 ft before the final turn.
5. Final: rollout ≥ 6 000 ft from the runway, **not below 190 KIAS** until on final (Fig. 2-7: final **175 KIAS**
   @ 16 100 lb), **rpm ≥ 83 %** (typ. 87-90 %), flat powered approach like ILS/PAR, 700-800 ft/min.
   Heavy weight / hot day: Military may not hold the descent in the final turn -> higher speed. Gusts: +5 KIAS per
   10 kt above steady wind.

### Landing (FM 2-24, 2-25, 2-28; PDF 156, 157, 160)
- BLC lift depends on engine airflow (best > 80 % rpm, low speed, low altitude) -> **smooth power reduction**.
- Flare just short of the runway, thrust smoothly to **82-83 %**, idle as the main gear touches; abrupt power cut =
  roll-off tendency + sink. Speed brakes may be used in the roundout (not needed on the approach).
- **Normal touchdown 155-160 KIAS** (+5/1 000 lb). Holding off slower: lateral stability/control deteriorate, wing
  drop, tail dragging.
- After touchdown: IDLE, nose wheel down, nosewheel steering, **drag chute as soon as the nose wheel is down** (all
  three gear on the ground: nose-down moment). No speed brakes while steering/antiskid needed.
- Crosswind: max. 25 kt (dry); chute OK with 25 kt at 90° or 35 kt at 45° (weather-vanes).
- Heavyweight, minimum-run (TD 140 kt), touch-and-go: see `f104-pilot` skill (FM 2-28).

### Go-around (FM 2-29, Fig. 2-8; PDF 161, 162)
1. **Throttle MILITARY** (Maximum if necessary). 2. **Speed brakes IN.** 3. **Gear UP** when definitely airborne and
   climb established. 4. **Flaps TAKEOFF at ≥ 180 KIAS**, only after a definite climb; expect a nose-up trim change.
   Leave the lever in TAKEOFF 30-60 s (BLC ramp cooling). 5. Flaps UP if desired at ≥ 260 KIAS.
- Slow to accelerate with LAND flaps: decide early, preferably not below **165 KIAS**. Fuel for a go-around in a
  closed pattern ≈ 200-300 lb. Transition to climb may cost > 100 ft (FM 6-16).

### After landing / shutdown (FM 2-29, 2-31; PDF 161, 163)
- Flaps TAKEOFF (≥ 1 min for BLC cooling), speed brakes IN, **trim TAKEOFF**, chute jettison per local rules.
- Shutdown: flaps UP, **3 min at IDLE** for cooling (taxi counts), throttle OFF.

## 2. Emergency procedures (Section III; bold-face = memory items)
- **Abort** (FM 3-6; PDF 172): THROTTLE IDLE - EXTERNAL LOAD JETTISON (if necessary) - DRAG CHUTE DEPLOY - ARRESTING
  HOOK EXTEND. Engine above idle may fail the chute.
- **AB failure on takeoff** (FM 3-6/3-7; PDF 172, 173): blowout = EGT < 500 °C, nozzle < 7, thrust loss. Continue:
  THROTTLE MILITARY, continue at Military; no relight until safe. AB surge: Military, move out of AB.
- **Engine failure on takeoff** (FM 3-7): stop if possible, else eject rather than land on an unprepared surface.
- **Air start** (FM 3-11; PDF 177): START SWITCHES START - THROTTLE OFF - THROTTLE IDLE - monitor, then slowly
  advance. Above 30 000 ft allow 30 s between attempts. RAT out: same glide distance at 245 KIAS TAKEOFF flaps as
  275 KIAS flaps up.
- **Compressor stall** (FM 3-13; PDF 179): EGT 700-800 °C, rpm 70-85 %, nozzle 9-10, bang. Stall clearing = air start
  sequence. Max. rpm 94 % = cold shift -> land with TAKEOFF flaps.
- **Spin recovery** (FM 3-29/3-30, 6-10; PDF 199, 200, 400): THROTTLE IDLE - RUDDER FULL OPPOSITE (turn needle) -
  STABILIZER FULL FORWARD + full nose-down trim - AILERON FULL INTO the spin; retract gear/flaps/speed brakes;
  neutralize when rotation stops, gradual pullout (up to 12 000 ft). Chute (above 25 000 ft) if a stable spin. Eject
  if still rotating at 15 000 ft AGL.
- **SAS failure** (FM 3-30): roll/pitch/yaw switch OFF. **Runaway trim**: selector AUX TRIM, use aux trim, pull TRIM
  CONTROL breaker; F/RF: AP engage (holds), disengage before landing (check auto-trim indicator).
- **BLC malfunction** (strong roll as flaps go to LAND) (FM 3-32; PDF 202): flaps TAKEOFF, minimum safe throttle while
  flaps return, **final ≥ 195 KIAS, touchdown ≥ 165 KIAS** (TAKEOFF flaps).
- **Flameout landing** (FM 3-32..3-35, Fig. 3-7; PDF 202-205): glide **245-260 KIAS** (RAT out, TAKEOFF flaps,
  2 000 lb fuel; +5 kt per 1 000 lb above 2 000), never below 245 before the flare; low key 6 000-8 000 ft AGL;
  final ≥ 1 000 ft AGL ¾ NM out; **flare at 300-500 ft**; **gear only after the flare is assured** (gear down: sink
  7 000 -> 11 000 ft/min).
- **Simulated flameout** (FM 3-33): **83 % rpm, speed brakes OUT, gear UP, flaps TAKEOFF** ≈ dead-engine drag; flaps
  up/gear up/RAT in: 275 KIAS at 84 % rpm with speed brakes out.
- **Partial-power pattern** (FM 3-41; PDF 211): flaps TAKEOFF, 260 KIAS, ≈ 83 % rpm, speed brakes as needed ->
  **≈ 1 800-2 000 ft/min**; 1:2 descent ratio (4 000 ft at 8 NM, 3 000 at 6, 2 000 at 4).
- **Precautionary straight-in** (FM 3-41): flaps TAKEOFF (LAND optional), normal final speed + 20 KIAS.
- **Stuck throttle** (FM 3-41): speed brakes out, TAKEOFF flaps, gear down -> 240 KIAS for LAND flaps (2-3 g);
  **speed brakes + LAND flaps + gear down at Military: flat final ≈ 190-200 KIAS (AB: 230-240)**; fuel OFF at
  touchdown (right roll-off as torque is lost).
- **Flap failure / no-flap landing** (FM 3-36; PDF 206): TE fail -> fuel low (< 3 000 lb), flat final ≥ 5 NM from
  1 000 ft AGL, gear down, **≥ 230 KIAS**, ≈ 800 ft/min (200 ft/NM), APC ≤ 2.5, **sink never > 2 000 ft/min**
  (recovery needs 400 ft), **touchdown ≥ 190 KIAS**, chute at idle only. LE fail only: normal speeds; TE only to
  TAKEOFF: final ≥ 195, TD ≥ 165.
- **Maximum glide** (FM 3-38/3-39, Fig. 3-8; PDF 208, 209): TAKEOFF flaps **245 KIAS** (= flaps up 275 KIAS, but
  ≈ 1 000 ft/min more sink), gear up, RAT out, no wind: **9 NM per 10 000 ft** (10k: 9, 20k: 18, 30k: 28, 40k: 38,
  50k: 48, 60k: 54, 70k: 61 NM); gear down 5.5 NM per 10 000 ft; without RAT +2 NM per 10 000 ft.
- **Nose gear flat tire / nose gear up** (FM 3-38): hold nose off, lower at ≥ 130 KIAS, chute after nose contact.
- **Belly landing** (FM 3-32): abandon rather than belly land.

## 3. Limits (Section V)
- Airspeed (Fig. 5-2; PDF 378): **750 KEAS** engine limit (low altitude), Mach 2.0 limit Mach number; engine inlet
  temperature limit varies with ambient temperature.
- **Gear: transient 260 KIAS, down and locked 295 KIAS. Flaps LAND 240 KIAS, TAKEOFF per Fig. 5-7..5-9 (370 KIAS for
  extension, FM 3-36). Drag chute MB-7G 180 / BS-4000 205 KIAS (140 KIAS min. recommended).** (FM 5-4/5-5; PDF 378/379)
- RAT: ≤ 550 KIAS; above 30 000 ft ≥ 350 KIAS.
- EGT (Fig. 5-3; PDF 379): continuous 600 °C (-11A) / 615 °C (-11B); up to 750 °C for 3 s; start limits separate.
- T2 reset (high Mach AB): rpm 103.5 ± 1 %.
- Load factor (Fig. 6-3): 7.33 g (F/RF, no stores, 17 000 lb); 2.0 g above M 1.6 with yaw SAS off (TF).
- Rolls (FM 5-14/5-15; PDF 388, 389): flaps up, entry ≥ 0.5 g: full-deflection rolls ≤ 360°; < 0.5 g: full rolls
  prohibited; below 1 g with pitch or yaw SAS off: full 360° rolls prohibited. Maneuvering flaps: ≤ 360°, one SAS
  required, no rolls below 1 g entry. Prohibited: intentional pitch-up and spins; prolonged negative g (flameout).
- Roll SAS off before 575 KIAS with tip stores (wing torsion).

## 4. Flight characteristics (Section VI) - what the sim should show
- Net dihedral effect ≈ 5-10° equivalent positive (fin + T-tail ≈ 15-20°, anhedral -10°) (FM 6-2; PDF 392).
- SAS: subsonic oscillations damp without SAS; supersonic lightly damped (Fig. 6-1; PDF 393).
- Controls (FM 6-3): ailerons ±9.75° gear up / ±20° gear down; rudder ±6° gear up / ±20° gear down, trim ±4°.
- **Stall/APC** (FM 6-5..6-8; PDF 395-398): pitch-up beyond the kicker; shaker then kicker; **kicker inoperative with
  LAND flaps or gear down**. Clean 15 200 lb: buffet 225 kt, heavy 215, **shaker < 200**, lateral instability 190,
  **kicker 175 kt**. TAKEOFF flaps: shaker 170, min. control 160, kicker 160. LAND flaps (BLC power): no buffet,
  shaker 150 (25 000 ft, 100 %), **min. control 140 kt**.
- **Minimum operating speeds (Fig. 6-4; PDF 399)**, sea level-10 000 ft, no tip stores, 1.0 g, shaker speed
  (min. control speed):

  | Weight lb | Gear+flaps up | TAKEOFF flaps | LAND flaps (power on) |
  |---|---|---|---|
  | 23 500 | 245 (220) | 210 (200) | 170 (165) |
  | 21 500 | 235 (210) | 200 (190) | 165 (160) |
  | 19 500 | 225 (200) | 190 (180) | 155 (150) |
  | 15 000 | 195 (175) | 170 (160) | 135 (130) |
  Bank 40° (1.3 g) / 60° (2.0 g) columns in the figure.
- Pitch-up/spin (FM 6-10; PDF 400): > 2 000 lb fuel spin resistant; spins right (engine gyro); 1 800-2 000 ft and
  5-6 s per turn, ≈ 18 000 ft/min.
- Ground effect (FM 6-8): no buffet/lateral instability at recommended speeds.
- Thrust/drag (Fig. 6-5) and envelope (Fig. 6-6; PDF 401-403): military envelope to ≈ 45 000 ft; max thrust to
  ≈ M 2.0 / 750 KEAS; 1 g stall line ≈ 20 000 ft at M 0.4.
- Climb angle at best climb Mach (Fig. 6-7; PDF 404): steep with max thrust (≈ 40-50° subsonic at low altitude).
- **Go-around capability (Fig. 6-8; PDF 405)**, Military, landing configuration: sea level 14 500 lb 60 °F ≈ 3 000
  ft/min max.; **20 500 lb 60 °F ≈ 1 400 ft/min max at ≈ 165-175 KIAS**, ≈ 0 at ≈ 205 KIAS; 3 000 ft 20 500 lb
  60 °F ≈ 800 ft/min. Marginal: straight-in with TAKEOFF flaps.
- **Pitch trim (Fig. 6-9; PDF 406)**: stabilizer for level flight ≈ 4° at M 0.6, falling to ≈ 1.5° near M 1.2, ≈ 1°
  at M 2.0 (S12 measured 1.2° at M 1.27, 2.0° at M 1.8). Mild nose-down trim change at M 0.88-0.90; slight nose-down
  M 1.05-1.5 then nose-up.
- Lateral-directional oscillation ≈ 0.5 Hz at M 0.94-0.98 above 25 000 ft (FM 6-17; PDF 407).
- Level flight acceleration (Fig. 6-10; PDF 407): best at 35 000 ft (Fig. 6-11).
- Maneuvering (FM 6-19): no adverse yaw, rudder not needed above 300 KIAS; rudder must not pick up a low wing (high
  rudder rolls the wrong way). Max. constant-speed load factor ≈ 2 g at 35 000 ft (Fig. 6-14). Not PIO prone.
- Tip tank oscillation ≈ 4 Hz below 5 000 ft at ≈ M 0.80 with 400-800 lb per tip tank (yaw damper).

## 5. Test reference values (candidates for test cards)
| Test idea | Configuration | FM reference | Page |
|---|---|---|---|
| Engine idle / Military check | ground | idle 67 %, EGT 320-420, FF 700-1 600; Mil 100 %, 590 °C, accel ≤ 10 s | 2-13, 2-19 |
| Takeoff | AB, TAKEOFF flaps | 190 KIAS @ 20 800 lb; attitude 5° | Fig. 2-6, A2 |
| Glide L/D (T3 glide) | gear up, TAKEOFF flaps, idle (RAT not modelled -> no-RAT +2 NM/10k) | 9 (+2) NM per 10 000 ft at 245 KIAS; flaps up 275 KIAS same distance | Fig. 3-8 |
| Glide gear down | gear down, TAKEOFF flaps | 5.5 NM per 10 000 ft | Fig. 3-8 |
| Simulated flameout drag | 83 %, speed brakes out, gear up, TAKEOFF flaps | ≈ dead-engine glide | 3-33 |
| Partial-power descent | TAKEOFF flaps, 260 KIAS, 83 % | 1 800-2 000 ft/min | 3-41 |
| Landing-config drag | speed brakes + LAND flaps + gear, Military | level/flat ≈ 190-200 KIAS (AB 230-240) | 3-41 |
| Go-around climb | landing config, Military, 20 500 lb | ≈ 1 400 ft/min at 165-175 KIAS (sea level, 60 °F) | Fig. 6-8 |
| Minimum speeds / stall | clean, TAKEOFF, LAND; 1 g and 40°/60° bank | Fig. 6-4 table | 6-9 |
| Trim vs. Mach | level flight | Fig. 6-9 | 6-16 |
| Approach / landing | LAND flaps | final 175 KIAS @ 16 100 lb, TD 155-160, A8 distances | Fig. 2-7, A8 |
| Lateral oscillation transonic | M 0.94-0.98 > 25 000 ft | ≈ 0.5 Hz, undamped (SAS off) | 6-17 |
