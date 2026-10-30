# Measurements in the sim (test bed)

Measured via SimConnect (MCP `simconnect`). Location EDDM, 1 460 ft, 2.9 °C, 28.54 inHg (δ ≈ 0.954, θ ≈ 0.958).
Note: `msfs_get_simvars_bulk` sometimes returned delayed values; `msfs_watch_simvar` is more reliable.
File names `docs/data/flighttest_*.csv` are the raw logs (tools/simlog.py).

## 2026-10-24: static run, parking brake
| Setting | Throttle | N1 / rpm | Thrust (TURB ENG JET THRUST) | Fuel flow | EGT | Target | Verdict |
|---|---|---|---|---|---|---|---|
| Idle (old table) | 0 % | 67.0 % / 4 997 | 1 482 lbf | 1 206 lb/h | 241 °C | ~355 lbf installed (500 uninstalled, Stoelinga) | ✗ -> table corrected |
| Idle (new table) | 0 % | 67.0 % / 4 999 | 610 lbf | 1 202 lb/h | 241 °C | ~355-500 lbf | ~ (cold day: N1c 68.4 % in the steep part of the table) |
| Military | 68 % | 100.3 % / 7 479 | 6 654 lbf | 9 758 lb/h | 337 °C | ~6 670 lbf installed | ✓ thrust; EGT too low (target 590 °C) |
| Max afterburner | 100 % | 100.3 % | 10 516 -> 10 642 lbf | 9 796 lb/h | 338 °C | NASA 11 200 lbf (sea level) x δ 0.954 ≈ 10 690 | ✓ (-0.5 %) |

## 2026-10-24: takeoff run (Claude: brakes/throttle, user: stick)
EDDM runway 26, 1 460 ft, ~3 °C, wind 190°/10 kt (crosswind!), 19 330 lb, CG 6.9 % MAC, flaps TAKEOFF.
- Full afterburner from standstill: steady acceleration ~10 kt/s (175 kt after 19.6 s, 249 kt after 30 s)
  -> net force ~10 150 lbf, matches static thrust 10 640 lbf. **Thrust ok.**
- Liftoff only at ~270-290 kt (expected ~200 kt). The nose responded (user). Suspicion: tail strikes at ~7.5°.
- Gear still down at 292 kt (above the 260/295 kt limit); then uncontrolled flight/crash.
- User: rudder felt "strange" on the takeoff run, aircraft hard to keep on the runway (10 kt crosswind).

## 2026-10-24: lift in flight (deceleration run with autopilot, idle)
16 500 ft, flaps/gear up, data: `docs/data/flighttest_2026-10-24_deceleration.csv`, `tools/analyse_lift.py`.
| IAS | Mach | α | CL sim | CL NASA (TN D-7137) | Ratio |
|---|---|---|---|---|---|
| 485 kt | 0.96 | 0.8° | 0.131 | 0.053 | 2.5 |
| 355 kt | 0.71 | 2.5° | 0.243 | 0.144 | 1.7 |
| 273 kt | 0.56 | 4.6° | 0.374 | 0.249 | 1.5 |
| 229 kt | 0.47 | 6.8° | 0.500 | 0.366 | 1.4 |
| 215 kt | 0.43 | 8.4° | 0.594 | 0.457 | 1.3 |
-> The sim has **more** lift than NASA: offset ~+0.08 at α = 0, slope ~0.060/° instead of ~0.055/°.
Below ~215 kt the autopilot did not hold altitude (α stuck at 8.4°), descent ~1 000 ft, caught with military power.
Idle deceleration from 485 to 215 kt in ~60 s.

## Open items from the 2026-10-24 measurements (status 2026-10-25 in brackets)
- AB fuel flow missing: 9 796 lb/h at full AB instead of ~25 700 lb/h (NASA). [AP-7: solved in flight via gross
  thrust fuel flow; static still -33 %]
- EGT too low: 337 °C at military instead of 590 °C. [solved via egt_peak_temperature]
- Parking brake does not hold full afterburner (aircraft started rolling). Static runs up to military.
- Part throttle between idle and military is only estimated linearly in the thrust table.

## 2026-10-25: T3-A baseline (deceleration run with elevator/trim)
Positioned via MCP (48.25 N 11.0 E, 16 500 ft, heading 270), gear/flaps up, AP altitude + heading, AB to 486 kt,
then idle. Build with `aero_center_lift = 0`. Data: `docs/data/flighttest_2026-10-25_baseline.csv`.
| IAS | Mach | α | CL sim | CL NASA | Elevator | Trim |
|---|---|---|---|---|---|---|
| 394 kt | 0.79 | 1.3° | 0.174 | 0.079 | 0 | 1.8° |
| 322 kt | 0.65 | 2.7° | 0.261 | 0.145 | 0 | 3.4° |
| 267 kt | 0.55 | 4.4° | 0.368 | 0.234 | 0 | 5.4° |
| 227 kt | 0.47 | 6.1° | 0.470 | 0.329 | 0 | 7.4° |
| 199 kt | 0.40 | 8.5° | 0.602 | 0.459 | 0 | 10.0° (stop) |
- **T3-A failed:** mean deviation +0.129 (tolerance 0.03). Reproduces yesterday exactly:
  CL_sim ≈ 0.085 + 1.14 × CL_table (yesterday 0.074 + 1.14).
- **The AP flies with trim only** (elevator stays 0). Trim runs to `elevator_trim_limit = 10` [S] -> below ~200 kt
  the AP cannot pull further, α stays at 8.5°, descent. **Cause of the AP problem.**
- Trim and α correlate 0.999 -> trim vs. table contribution not separable from this run.
- After positioning 2 313 lb of fuel were missing (≈ both tip tanks, 2 × 175 gal); did not recur in later runs.
- At M 0.99 CL matched (0.114 vs. 0.119).

## 2026-10-25: T3-A after AP-1 (modern_fm_only, lift_coef_at_drag_zero = 0, wing_camber 0.1) - INVALID
Same procedure as the baseline; data `docs/data/flighttest_2026-10-25_ap1.csv`. Tip tanks full this time
(19 080 lb instead of 16 690 lb).
- T3-A failed, unchanged: mean deviation +0.129. **Later found invalid**: only the flight was restarted, so the
  old normalization was still active (see below).
- Deviation by α band (baseline / AP-1): 0-1° +0.082/+0.080 · 2-3° +0.115/+0.107 · 4-5° +0.132/+0.131 ·
  6-7° +0.133/+0.141 · 8-9° +0.135/+0.143. Same curve for both runs despite 2 400 lb difference.
- The deviation does not grow with trim: constant ~0.13-0.14 between α 4° and 9° while trim goes 5° -> 10°.

## 2026-10-25: Dev Mode "Debug Aircraft Sim Curves" (normalizer) after AP-1
Screenshot `20261025111743_1.jpg` (Steam), flight at 16 554 ft, M 0.63, α ≈ 3°, 8.4 t.
| Quantity | Raw | Target (Tgt) | Final | Factor |
|---|---|---|---|---|
| Cl at AOA0 | 0.0563 | **0.0910** | 0.0912 | oCl 0.01 |
| dCl/dα at AOA0 (/rad) | 2.7898 | 3.2496 | 3.2516 | nCl 1.27 |
| Cd at AOA0 | 0.0683 | 0.0490 | 0.0489 | nCd 0.68 |
| dCd/dα at AOA0 | 0.7053 | 0.6838 | 0.6833 | dCdf 0.78 |
Further lines: CD0 = 1.0 × 0.0160; k = 0.1941; PlnCd0AOA (with gear, HT, VT, ailerons) 0.0541;
Cd0 shares: wing 0.0272, fuselage 0.0184, HT 0.0069, VT 0.0016. Sim Info: "Cur Cl=0.299 Cd=0.0616".
- **Normalizer target at α = 0 is 0.091, our table says 0.010.** Difference 0.081 = measured offset at small α.
- Target slope 3.25/rad ≈ table × Mach factor -> slope matches.
- "Cur Cl = 0.299" at α ≈ 3° confirms our measurement (table: ~0.16).
- Hypothesis H1: TgtClAOA0 = empty_weight / (q(cruise_speed, sea level density) · S) = 0.0925 ≈ 0.091.

## 2026-10-25: AP-1c test of hypothesis H1 (cruise_speed 490 -> 700) - REFUTED
Screenshot `20261025114445_1.jpg`, on the ground at EDDM after build + flight restart (T1 ✓).
- TgtClAOA0 still 0.0910, all values unchanged -> cruise_speed does not set the target. cruise_speed back to 490.
- Caveat at the time: normalization might only run once per session (confirmed next).

## 2026-10-25: normalizer after a COMPLETE sim restart (build with AP-1 + AP-1b)
Sim start 11:53:59, screenshot via `tools/screenshot.ps1`. On the ground at EDDM, flaps 50 %.
| Quantity | Raw | Target | Final | Factor |
|---|---|---|---|---|
| Cl at AOA0 | -0.0149 | **0.0100** | 0.0100 | oCl 0.01 |
| dCl/dα (/rad) | 3.0182 | 2.9917 | 2.9910 | nCl 1.01 |
| Cd at AOA0 | 0.0358 | 0.0160 | 0.0160 | nCd 0.44 |
| dCd/dα | 0.6850 | 0.4993 | 0.4997 | dCdf 0.65 |
- **Target = table (0.010).** Before (session from ~08:00, build with wing_camber 0 -> internally 1° and FSX legacy
  terms) 0.091.
- **MSFS normalizes only at sim start.** Restarting the flight, a new flight from the menu and package reload
  (Aircraft Selector/Build) all show the old normalization.
- Not separated: camber (0 -> internally 1° vs. 0.1°) or FSX legacy terms.

## 2026-10-25: T3-A after AP-1 + AP-1b WITH sim restart - PASSED
Data `docs/data/flighttest_2026-10-25_ap1b_restart.csv`. Same procedure (16 500 ft, AB to 603 kt / M 1.14, then idle).
- **T3-A passed:** mean deviation -0.001, largest band mean -0.021.
- By α band: 1-2° -0.016 · 2-3° -0.022 · 3-4° -0.013 · 4-5° -0.006 · 5-6° +0.008 · 6-7° +0.010 · 7-8° +0.009 ·
  8-9° +0.005 · 9-10° +0.005 (baseline: +0.08 to +0.14). At M 1.14 (α 1.3°): 0.087 vs. NASA 0.081.
- **The extra lift came from the old normalization**, not from the table.
- New: the jet accelerates much faster with AB (573 kt after 25 s instead of ~490 kt); normalizer nCd 0.44 instead
  of 0.68 -> drag check (new test T3-F).

## 2026-10-25: T3-F drag (evaluation `tools/analyse_drag.py`, no sim)
Flight path balance D = T_net - m·dV/dt - W·sin γ (T_net = TURB_ENG_JET_THRUST, negative at idle = ram drag),
CD = D/(qS), compared with TN D-7137 Table 2 at the same Mach and CL. Idle segment t 3-92 s.
| | M 0.4-0.6 | M 0.6-0.8 | M 0.8-0.95 | M 0.95-1.2 | Mean M 0.4-0.95 |
|---|---|---|---|---|---|
| after AP-1/1b + restart (`..._ap1b_restart.csv`) | 0.93 | 1.04 | 1.05 | 1.05 | **1.00 -> passed** |
| baseline, old normalization (`..._baseline.csv`, t 3-75) | 1.59 | 2.27 | 2.67 | - | 1.91 -> failed |
- The old normalization also had almost double drag.
- At high CL (0.4-0.5, α 8-9°) ratio 0.92 -> induced drag slightly low there, within tolerance.

## 2026-10-25: sim round A (AP-2 all-moving tail, AP-2b trim 11°, AP-5 tail points, AP-7 fuel via gross thrust)
Build 12:13, sim restart 12:24 (T1 ✓). Normalizer: TgtClAOA0 0.0100, Fin 0.0099, nCl 0.98, nCd 0.43.
**T3-C static run** (EDDM, `flighttest_2026-10-25_roundA_static.csv`):
| | N1 | Thrust | Fuel flow | EGT | Target |
|---|---|---|---|---|---|
| Idle | 67.0 % | 427 lbf ✓ | 566 lb/h | 264 °C | 355-500 lbf |
| Military | 100.1 % | 6 628 lbf ✓ | 8 400 lb/h ✓ | 352 °C ✗ | 6 670 lbf, 8 400 lb/h, ~595 °C |
**Afterburner in flight** (`flighttest_2026-10-25_roundA_flight.csv`, 14 500-15 000 ft, full AB):
| M | Thrust sim / NASA Table 3 | FF sim / NASA Table 4 |
|---|---|---|
| 0.96 | 12 804 / 13 007 (-2 %) | 25 773 / 28 898 (-11 %) |
| 1.03 | 13 563 / 13 853 (-2 %) | 27 782 / 31 062 (-11 %) |
| 1.13 | 14 234 / 14 784 (-4 %) | 30 180 / 33 530 (-10 %) |
-> **AB thrust in flight confirmed.** AB fuel flow -11 % -> AB TSFC 2.29 x 1.11 = 2.54.
**T3-A**: passed by band criterion (largest band mean -0.027); single outlier -0.255 from a recovery manoeuvre.
**T3-G**: tail deflection = 1.07 x α (before AP-2: 1.13; CR-96008 expects 0.67-1.05). AP holds altitude to ~214 kt
(trim 11° at the stop, α 10.5°; before 225 kt/10°).
**Cruise** M ~0.87, 30 000 ft: AP oscillated (g 0.7-0.95); point α 4.07° / trim 4.28° matches T3-G.
**T3-E rudder** (8 000 ft, gear/flaps down, 255-275 kt, full deflection, `..._roundA_rudder.csv`, yaw damper off):
rudder only 6-8° (elasticity table), sideslip 5.8-7.9° -> **β/δr ≈ 1.0**, CR-2144 approach 0.32.
Roll-off to 89° bank despite wing leveler. Vertical tail measured in CR-2144 ≈ 38 ft² (= previous estimate).

## 2026-10-25: sim round B (htail_incidence -4.3, rudder_lift_coef 1.6 + yaw damper, EGT factor, AB TSFC 2.54) - ABORTED
Build 12:41, sim restart 12:43 (T1 ✓ incl. systems.cfg/.flt). Normalizer target 0.0100 ✓; the sim reports
"Warning! htail_area = 0.1 sft" (0 becomes 0.1 ft², harmless). Takeoff trim 0.70° ✓ (elevator_trim_neutral works).
- **Yaw damper** OFF after starting from the world map although .flt has YawDamper=True -> switched on with
  `YAW_DAMPER_ON`. The .flt start states are apparently not used when starting from the menu.
- **Static run** (`..._roundB_static.csv`): idle 425 lbf/564 lb/h/264 °C, military 6 625 lbf/8 403 lb/h/353 °C.
  **egt_tuning_constant 1.39 had no effect** (turbine: EGT = ITT remapped to egt_peak_temperature) -> egt_peak 2187 R.
  Short static AB burst: 10 580 lbf ✓ (NASA 11 200 x δ), FF 17 330 lb/h instead of ~25 700.
- **Crash with htail_incidence -4.3** (`..._roundB_flight.csv`): after positioning g = -0.55, dive from 16 500 ft to the
  ground in 28 s, trim 3.5 -> 6.5° not enough; second attempt at 295 kt crashed despite 11° trim. -> **Sign wrong:
  positive htail_incidence acts like nose-up trim.**
- **AB in flight** (dive, M 1.06-1.29, 11 400-4 000 ft) with AB TSFC 2.54: FF +6..+10 %, thrust +5..+8 % vs. NASA;
  FF/thrust +1..+4 % ✓. The static deviation (-33 %) fits: AB TSFC applies only to the AB thrust increment.

## 2026-10-25: sim round B2 (htail_incidence +4.3, egt_peak 2187 R, rudder_lift_coef 1.6, yaw damper)
Build 12:51, sim restart 12:52 (T1 ✓). Takeoff trim 0.70°, yaw damper via YAW_DAMPER_ON.
- **EGT ✓**: military 593 °C (target 590-600), idle 470 °C (Stoelinga 120-420, slightly high).
- **htail_incidence +4.3** (`..._roundB2_flight.csv`): stable after positioning, trim -0.26° at M ~0.8/16 500 ft;
  AP holds altitude to ~200 kt (trim 7.5°), stop 11° at 193 kt. **T3-A failed: largest band mean +0.057**;
  deviation by α: +0.066 (0-1°) ... +0.047 (4-5°) ... 0.000 (10-11°) ... -0.024 (14-15°), tracks the trim.
  T3-G: deflection = -4.06° + 1.06 x α. At M ~1.15 trim -4.0° (near the lower stop -5°).
  **Interpretation:** MSFS normalizes at α = 0 with the tail at htail_incidence. With 0 (round A) the trimmed flight
  at α = 0 is exactly there (intercept 0.00°) -> lift is right everywhere. With +4.3 the tail load in trimmed flight
  differs -> extra lift. The tutorial rule "cruise trim 0" does not fit trimmed NASA data. -> **htail_incidence 0.**
- **T3-E with rudder_lift_coef 1.6 + yaw damper** (`..._roundB2_rudder.csv`, 9 000 ft, gear/flaps down, 210-230 kt):
  rudder 15°, **β 30°, departure, inverted, crash.** rudder_lift_coef is the lift slope of the whole fin
  (SDK: "yaw stability") -> directional stability halved. -> back to 5.0.
- AP holds altitude with htail 0 to ~214 kt ≈ 1.27 x Vs clean (169 kt) -> realistic for an autopilot; AP-2b closed.

## 2026-10-25: sim round C (htail_incidence 0, takeoff trim 5°, rudder_lift_coef 5.0, rudder_effectiveness 0.32, yaw damper)
Build 13:03, sim restart 13:05 (T1 ✓). Takeoff trim 5.00° ✓.
- **T3-A passed**: band means -0.024 ... +0.009; T3-G -0.05° + 1.08 x α (as in round A).
- **T3-F passed**: CD_sim/CD_nasa 1.04 (M 0.4-0.6: 1.00; 0.6-0.8: 1.05; 0.8-0.95: 1.10).
- AP holds altitude to ~213 kt (as in round A).
- **T3-E**: rudder 5.5-7.9° (as in round A), β 6.6-11.6° -> β/δr 1.2-1.5, roll over inverted, crash.
  rudder_effectiveness 0.32 without measurable effect -> removed again. Yaw damper on at the same time -> not separable.
  SDK: all lateral coefficients of the template (roll_moment_slip_angle, yaw_moment_slip_angle, yaw_moment_delta_rudder,
  side_force_slip_angle, ...) are unused in the modern FM; directional stability and roll due to sideslip come from
  geometry (vertical tail, wing_dihedral, fuselage_lateral_cx).
- **T3-A criterion changed:** acceptance on 1° band means (>= 3 points, |g-1| < 0.15) instead of single points.
  Re-evaluated: baseline ✗ (+0.139), after AP-1b ✓ (-0.021), round A ✓ (-0.027), round B2 ✗ (+0.057), round C ✓ (-0.024).

## 2026-10-25: rudder analysis (no sim) - cause of β/δr ≈ 1 found
Round A (`..._roundA_rudder.csv`, no yaw damper): β follows the rudder exactly (t 16.8 s: 5.82/5.92°;
18.3 s: 5.84/5.87°; 22.8 s: 6.59/6.59°; 24.3 s: 7.09/7.11°). MSFS simulates fin + rudder as ONE surface whose whole
incidence follows the rudder deflection -> equilibrium when the fin is back in line with the airflow: β = δr.
A real flap-type rudder (9 of 47 ft²): effective share Cnδr/Cnβ = 0.32 (CR-2144).
- `rudder_effectiveness` only scales rudder_lift_coef (force of the whole fin) -> does not change the equilibrium
  (hence no effect in round C).
- `rudder_maxangle_scalar` scales the effective deflection (SDK: "< 1, effective deflection aligned with the overall
  vtail and rudder chord") -> **0.32** (round D). `elevator_maxangle_scalar` stays 1 (all-moving tail).
- Prediction for round D: β/δr ≈ 0.32 (δr = deflection after the elasticity table); less sideslip -> less roll-off.
- Open: whether RUDDER_DEFLECTION reports the scaled or unscaled angle (read in round D).

## 2026-10-25: sim round D (only change: rudder_maxangle_scalar 0.32) - T3-E PASSED
Build 13:48, sim restart 13:54 (T1 ✓). Data `docs/data/flighttest_2026-10-25_roundD_rudder.csv`
(gear/flaps down, 240-255 kt, ~9 000 ft, yaw damper on, AP wing leveler).
- RUDDER_DEFLECTION reports the **unscaled** command: 9.6-11.3° (elasticity at ~245 kt). Sideslip β 3.7-3.9°
  -> **β/δr = 0.34** (target Cnδr/Cnβ = 0.32 per CR-2144, ±30 %) ✓. β again equals the *effective* deflection
  (11.2° × 0.32 = 3.6°), confirming the single-surface explanation.
- **Roll-off remains**: with β ≈ 3.8° constant the jet rolls at ~15-20°/s through inverted; the AP wing leveler
  does not counter it. Estimate with CR-2144 (approach): Cl = Clβ·β = 0.175 × 0.066 = 0.0116; steady roll rate
  without aileron p = Cl·2V/(|Clp|·b) ≈ 85°/s; aileron to hold wings level δa = Clβ·β/Clδa ≈ 17°.
  -> **Strong roll due to sideslip is real F-104 behaviour** (FM 6-2: "relatively large rolling moment in a sideslip
  condition"). The sim rolls slower than the estimate. Criterion "no roll-off" was wrong -> new test T3-E2: steady
  heading sideslip with opposite aileron (closed loop), measure aileron required vs. ~17° (approach config).
- Positioning lesson: after a sim restart the AP is OFF; positioning with gear/flaps down at ~300 kt (above the
  240 kt flap limit) led to a dive from 9 000 to 2 000 ft. Procedure: AP on first, position clean at ≤ 225 kt IAS,
  extend gear/flaps only after the AP has stabilized.

## 2026-10-25: round D part 2 - yaw damper problem and first T3-E2 (closed loop sideslip)
- Positioning at 9 000 ft failed twice (dive to the ground in ~18 s ≈ free fall): positioning sets α = 0 and the
  AP may only raise the nose at 2°/s (`max_pitch_velocity_lo_alt = 2`). At 16 500 ft the jet then rolled to 66° bank
  with **2.5° rudder from the yaw damper** (no rudder input) and fell from 16 500 to ~7 500 ft. After `YAW_DAMPER_OFF`
  the AP wing leveler rolled it back level immediately (60° -> 5° in 12 s). -> **yaw damper with my estimated gain 1.0
  is destabilizing; disabled** (`yaw_damper_gain = 0`, systems.f104.cfg) until tuned (T3-J).
- **T3-E2 with `tools/sideslip_test.py`** (yaw damper off, gear/flaps down, 263-338 kt, ~9 700 ft,
  `docs/data/flighttest_2026-10-25_roundD_sideslip.csv`): the script found the axis signs itself (aileron +4000 ->
  bank +2.1°, elevator +3000 -> pitch +4.0° = nose down) and held both axes without abort.
  Full rudder: rudder 5.9° (elasticity at ~300 kt), **β 1.86° -> β/δr = 0.32 ✓** (without yaw damper, confirms
  round D); aileron to stop the roll **-2.4°** (AILERON_AVERAGE_DEFLECTION, command ~35 %), steady bank ~14° (P-only
  roll loop). CR-2144 estimate for this β: δa = Clβ·β/Clδa = 0.175 × 0.0325/0.039 ≈ 8.5°.
  -> together with the free roll rate (15-20°/s vs. ~85°/s estimated) the **roll due to sideslip in the sim is weaker
  than the CR-2144 estimate** (or roll damping/aileron power stronger). Data quality limited (speed drifted +75 kt,
  P-only loop, approach-config derivatives applied at 300 kt) -> repeat with PI roll loop, AILERON_LEFT_DEFLECTION and
  constant speed; compare with CR-2144 cruise derivatives (flight conditions 1-10, PDF 55-65).

## 2026-10-25: round E - T3-E2 repeated (clean, constant speed) - PASSED, roll due to sideslip matches CR-2144
Build + full sim restart with yaw damper off (T1 ✓, TgtClAOA0 0.0100 ✓, T2 ✓). Data
`docs/data/flighttest_2026-10-25_roundE_sideslip.csv` (clean, ~15 600 ft, 325-344 kt IAS ≈ M 0.67, PI roll loop).
- Full rudder: RUDDER_DEFLECTION -5.76° (elasticity at ~335 kt), **β 1.83° -> β/δr = 0.32 ✓**.
- Aileron to hold the bank **-2.25°** (AILERON_LEFT_DEFLECTION), steady bank -2.8° (PI loop holds it constant).
- **Corrected reference** (CR-2144 Table III-9, lateral dimensional derivatives, PDF 62): solve the steady
  sideslip balance with p = r = 0 for δr = 1:
  N'β·β + N'δa·δa + N'δr = 0 and L'β·β + L'δa·δa + L'δr = 0. The earlier estimates (8.5°, 17°) ignored the
  **rolling moment of the rudder itself** (L'δr: tall fin above the CG), which cancels most of the roll due to sideslip.

  | F/C | H, M | β/δr | δa/δr |
  |---|---|---|---|
  | 1 (approach) | SL, 0.257 | 0.32 | 0.27 |
  | 2 | SL, 0.80 | 0.42 | 0.39 |
  | 4 | 15 000 ft, 0.90 | 0.33 | 0.47 |
  | **sim round E** | 15 600 ft, 0.67 | **0.32** | **0.39** |

  -> sim within the CR-2144 range for both ratios, assuming CR-2144 δa is the deflection of one aileron (not
  checked yet: if it is the sum of both, the reference halves to 0.13-0.23 and the sim needs ~2x too much aileron).
  **No change to roll due to sideslip.** AP-6 rudder
  and T3-E2 done; the free roll-off in round D is plausible (no aileron, β 3.8° with rudder roll included).
- Observation: positioned at 16 500 ft / 330 kt TAS clean, the jet again sank to 9 900 ft (AP 2°/s) and reached
  543 kt IAS. GEAR_DOWN and FLAPS_DOWN at ~217 kt moved the handles, but gear stayed 0 % and flaps 0° (no damage
  flags) - cause unknown, possibly the AP climb at ~8 000 ft/min pushed the speed over the limits. Test then flown clean.
- The F-104 has fuselage speed brakes; not modelled yet (all spoiler values 0) -> new work package.

## 2026-10-25: T3-D takeoff, runs 1-4 (scripted, `tools/takeoff_test.py`) - liftoff 20 kt too fast -> AP-10 flaps
EDDM runway 26L start position (true heading 263.4°): lat 48.34472, lon 11.80386 (re-usable with
`msfs_set_aircraft_position(on_ground=true)`). Wind ~250°/21 kt (headwind; IAS unaffected, ground roll shorter).
Reference FM Fig. A2-3 (PDF 457, "Takeoff Airspeed Schedule"): normal liftoff ≈ 155 + 4.43 kt per 1 000 lb above
14 000 lb -> **174 kt at 18 155 lb** (max. performance ~5 kt less, 50 ft ≈ +35 kt). Rotation ~20 kt below (FM 6-5).
- Run 1: rudder axis sign wrong (positive AXIS_RUDDER_SET = nose LEFT) -> abort at 94 kt, jet in the grass.
- Run 2: control loop only 2.3 Hz (each SimConnect read waits for a sim frame, ~70 ms) -> pitch loop oscillated,
  crash after liftoff. Gains retuned for ~3 Hz.
- Run 3 (`..._T3D_takeoff_run3.csv`, Vr 165, gentle pull): nose only 6-7° on the ground, liftoff 227-242 kt.
- Run 4 (`..._T3D_takeoff_run4.csv`, 18 155 lb, Vr 157, θ target 10.5°): **liftoff 194 kt at θ 10.6°**, ground
  roll 2 736 ft (headwind), max θ on ground 10.6° (tail at 12.3° ✓). Heading ±0.2° ✓. After liftoff the AP handover
  with `AP_ALT_HOLD_ON` held the *current* altitude (39 ft) and put the jet back on the runway at 335 kt (script
  error, fixed: VS mode +4 000 ft/min).
- Analysis: CL at liftoff = 18 155/(127.6 psf x 196.1) = 0.725 (incl. tail download); FM liftoff needs CL 0.90.
  Cause found in the SDK flap formula: ΔCL = lift_coef_flaps x lift scalar x deflection **in radians**, and
  `add incidence` (default 0.5) applies only half of it at α 0. With lift_coef_flaps 0.62: TAKEOFF ≈ 0.13 at 10°,
  LAND ≈ 0.28 at α 2.3° instead of the intended 0.62.
- FM 1-73: TAKEOFF = leading and trailing edge flaps 15°, LAND = LE 30° / TE 45°, BLC only in LAND.
- **AP-10 change (needs Build All + full restart):** per-position values in `[FLAPS.0]` with add incidence 1;
  LAND lift/drag scalar 1.273 (ΔCL 0.62, ΔCD 0.12 as derived from CR-2144), TAKEOFF lift scalar 1.847 (ΔCL 0.30,
  from FM liftoff speed: 0.90 - 0.565 at θ 10.6°). Prediction for the next run: liftoff ≈ 175-180 kt at θ ≈ 10.5°.

## 2026-10-25: T3-D run 5 - flaps never extended (systems), fixed
Build 15:38 with the AP-10 flap scalars, sim restart 15:42 (T1 ✓), 19 006 lb (FM liftoff 177 kt).
`docs/data/flighttest_2026-10-25_T3D_takeoff_run5.csv`: first liftoff **193.6 kt at θ 10.6°** - identical to run 4,
the flap change had no effect. Then a short touchdown, sustained liftoff 211 kt; the script crashed at the AP handover
(`AP_VS_ON` not in the Python-SimConnect catalog -> None). Recovered by repositioning to 16 500 ft.
- **Cause:** with the flap lever at TAKEOFF, TRAILING/LEADING_EDGE_FLAPS_LEFT_ANGLE stayed 0°. `[FLAPS.0] system_type = 1`
  (hydraulic, my estimate) but the test-bed systems.cfg has no hydraulic system (`normal_pressure = 0`); the same for
  `gear_system_type = 1` (gear did not extend in flight, round E). **The flaps have never moved in any test so far**
  (round D "gear/flaps down" was in fact flaps up; β/δr does not depend on flaps).
- Fix: flaps `system_type = 0` (electric, FM 1-73 "two ac motor powered actuators", template circuit Flaps_Motor);
  gear `gear_system_type = 0` (test-bed solution via circuit Gears_Motor; real gear is hydraulic). T0 rules AP-10 added.
  `takeoff_test.py` now checks the real flap angle before the run, reports the first liftoff, maps AP_PANEL_VS_ON
  directly and stops if an event is missing. Needs Build All + full restart.

## 2026-10-25: T3-D run 6 - PASSED (flaps finally extended)
Build 15:57 (electric flaps/gear, English comments), full sim restart 16:01 (T1 ✓). preflight: flaps trailing edge
**15.00°** ✓, 19 337 lb -> FM Fig. A2-3 liftoff **179 kt**. `docs/data/flighttest_2026-10-25_T3D_takeoff_run6.csv`.
- First liftoff 170 kt at θ 8.2° (the controller over-rotated: θ 6° while the command was 4°; FM 6-5 warns that a quick
  stick input gives a "dynamic" nose-up), short touchdown, **sustained liftoff 185 kt** at θ 9-12°, ground roll
  2 668 ft (~20 kt headwind). Max. θ on the ground 9.5° (tail 12.3°) ✓.
- **185 kt vs. 179 kt = +3.4 % -> T3-D passed (±5 %)**; first liftoff -5 %. Before the flap fixes: 194 kt (runs 4/5).
- AP handover in VS mode (AP_PANEL_VS_ON) worked: climb 3 150 ft/min. After the script (military + ALT hold at
  1 500 ft AGL) the jet accelerated to 600 kt IAS at ~3 000 ft -> throttle reduced by hand. To do: reduce power
  in the script after the handover.

## 2026-10-25: T3-H excess thrust / climb potential vs. NASA TN D-6398 (level max-AB accelerations)
Same sim session as T3-D run 6 (flown on after the takeoff). Ambient ~ISA-1 °C, weight 18 100 -> 16 200 lb (corrected
to 18 000 lb via induced drag). Reference `docs/data/nasa_d6398_excess_thrust_lbf.csv` (read from Fig. 6(a)/(b),
±300 lbf). New tool `tools/analyse_climb.py` (energy balance Fn,ex = W/g·dV/dt + W·sin γ). Logger reached only
~0.7 Hz with 24 SimVars (asked for 3 Hz) - enough for band means.
- **10 000 ft** (`..._T3H_accel10k.csv`, M 0.49 -> 1.23 in 65 s, AP drifted up to 11 300 ft): Fn,ex sim/NASA
  M 0.56-1.05: 0.81-1.15, mostly 0.86-1.07 (band means within ±10 % except M 0.70: 0.84) ✓;
  **M 1.07-1.19: 0.74-0.91 (about -800 lbf)**.
- **20 000 ft** (`..._T3H_accel20k.csv`, M 0.67 -> 1.48, altitude held 19 900-20 000 ft): M 0.70-1.25: 0.88-1.09 ✓;
  **M 1.30-1.40: 1.16-1.33 (about +500..+800 lbf)**.
- Decomposition with `analyse_drag.py` (thrust is logged): supersonic drag at 10 000 ft +3..+7 % vs. D-7137, net
  thrust at M 1.15 about -1.5 % -> the two small errors add up to -800 lbf of excess thrust (excess thrust is the small
  difference of ~16 000 lbf thrust and ~13 000 lbf drag: 5 % of thrust = 25 % of excess thrust).
- The supersonic deviations have **opposite signs at 10 000 and 20 000 ft**, so no single drag or thrust factor fixes
  both; the model stays consistent with D-7137 (thrust ±1-4 %, drag 1.00-1.07). D-6398 itself states that predicted
  climb potential matches the measurement only within 10 %, and its 20 000 ft data dip around M 1.4-1.5 (T2 reset).
- **Verdict T3-H: subsonic/transonic passed (M 0.6-1.05 at 10 000 ft, M 0.7-1.25 at 20 000 ft); supersonic outside
  ±10 % but within ±800 lbf (≤ 5 % of thrust) -> accepted for now, no change.** Revisit with T3-I (Mach 2 at
  35 000-40 000 ft), where the D-6398 30 000/40 000 ft data (Fig. 6(c)/(d), PDF 29) can be added.

## 2026-10-25: round F prepared (not flown yet)
Changes (cfg value comparison against the previous commit: only these keys): speed brakes as spoilers
(`spoiler_limit`/`air_spoiler_limit` 52, `spoiler_handle_available` 1, `spoiler_extension_time` 2,
`drag_coef_spoilers`/`drag_coef_air_spoilers` 0.046, lift 0); systems: `yaw_damper_gain` 0.3,
`yaw_damper_rudder_gain` 1.0, `max_pitch_velocity_lo_alt`/`hi_alt` 5/4 °/s. The clean flight model is unchanged
(spoilers only act when extended, the yaw damper only after YAW_DAMPER_ON). takeoff_test.py ends with throttle 7000
instead of military; simlog.py logs SPOILERS_HANDLE_POSITION and AMBIENT_TEMPERATURE.

## 2026-10-25: round F flown - speed brakes PASSED, AP pitch rate OK, Dutch roll too fast (new finding)
Build + full restart (T1 ✓, T2 ✓). Positioned at 16 500 ft / 520 kt TAS: with AP pitch rate 5°/s the jet now sank
only ~1 400 ft (before: up to 6 500 ft) ✓.
- **S11e speed brakes** (`..._roundF_speedbrake.csv`, ~490 -> 420 KIAS, M 0.97 -> 0.84, throttle constant):
  fully out **ΔCD 0.046** steady (mean incl. extension 0.040) vs. target 0.042 ±20 % -> **PASSED**. Deceleration
  +0.3 kt/s -> -3.5 kt/s. The "CD_sim/CD_nasa 1.48" points right after SPOILERS_OFF are the retraction transient
  (handle already 0, surface still moving) - not a flight model error.
- **T3-J Dutch roll** (`tools/doublet_test.py`, 7 Hz, ~420 KIAS, 15 000 ft, AP ALT + wing leveler):
  yaw damper off (`..._doublet_ydoff.csv`): β peaks -2.13/+0.98/-0.67/+0.41°, **period ≈ 0.87 s**, amplitude ratio
  per cycle ≈ 0.31 (ζ ≈ 0.19); yaw damper on, gain 0.3 (`..._doublet_ydon.csv`): practically identical (ratio 0.33),
  no roll-off (bank -1..-4°) ✓.
  CR-2144 F/C 4 (15 000 ft, M 0.9): N'β = 9.91 -> ωn ≈ 3.1 rad/s -> **period ≈ 2.0 s**, ζ ≈ (|N'r|+|Y'v|)/(2ωn) ≈ 0.11.
  -> **The sim's directional stiffness is ~5x too high** (ωn ≈ 7.2 rad/s) although β/δr was correct (ratio of two
  equally too strong moments). Suspect: `rudder_lift_coef` 5.0 on vtail_area 38 ft² ([S]) and/or fuselage
  contribution; yaw inertia (59 669 slug ft², CR-2144) is plausible. **New work package AP-11** (see plan).

## 2026-10-26: AP-11 iteration 1 prepared (Dutch roll)
Correction of round F: CR-2144 Table III-12 (PDF 65, SAS off) gives the Dutch roll directly: F/C 4 (15 000 ft,
M 0.9) **period 1.41 s**, 1/C(1/2) 1.24 (0.81 cycles to half amplitude); F/C 2 (SL, M 0.8) 1.40 s. The earlier 2.0 s
(ωn = sqrt(N'β) only) was too crude. Sim 0.87 s -> directional stiffness about **2.6x** too high (not 5x); damping in
the sim (ratio 0.31/cycle) is close to CR-2144 (0.43/cycle).
Changes (value diff: exactly these 5 keys): fin of the G vtail_area 38 -> 50, vtail_span 5.5 -> 7.3, vtail_sweep
40 -> 45 (D-6398 three-view, RM SL56H06 V3, historicalfighters.com); rudder_lift_coef 5.0 -> 1.7; rudder_maxangle_scalar
0.32 -> 0.24 (keep β/δr 0.32). Test: doublet (period target 1.4 s ±15 %), T3-E2 sideslip (β/δr 0.32, δa/δr 0.27-0.47).

## 2026-10-26: AP-11 PASSED - Dutch roll, sideslip (iterations 1 and 2, aircraft reload only)
**Workflow finding: lateral cfg changes take effect after Build All + reloading the aircraft - no full sim restart
needed** (iteration 1: build 18:25, sim started 18:16, period changed 0.87 -> 1.6 s). Normalization (lift) still
assumed to need a full restart.
All at 15 000 ft, M 0.90, ~460 KIAS = CR-2144 F/C 4; AP ALT + wing leveler; `tools/doublet_test.py`, `sideslip_test.py`.

| | round F (5.0 / 0.32, fin 38) | it. 1 (1.7 / 0.24, fin 50) | **it. 2 (2.0 / 0.32, fin 50)** | CR-2144 |
|---|---|---|---|---|
| Dutch roll period | 0.87 s | 1.6 s | **1.48 s** (+5 %) | 1.41 s |
| amplitude ratio per cycle | 0.31 | 0.54 | 0.57 | 0.43 |
| β/δr (full rudder) | 0.32 | 0.26 | **0.35** | 0.32-0.42 |
| δa/δr (opposite aileron) | 0.39 | 0.33 | **0.41** | 0.27-0.47 |

Values: rudder_lift_coef / rudder_maxangle_scalar, fin area ft². Logs `flighttest_2026-10-26_AP11_it1_*`, `_it2_*`.
Damping slightly weaker than CR-2144 (SAS off) - the yaw damper (T3-J) can add it. Pitfall: in iteration 2 the
first AP_MASTER toggle did not leave the AP on after the reload -> the jet dived to 6 100 ft; always read
AUTOPILOT_MASTER after positioning.

## 2026-10-26: T3-J yaw damper - not usable, switched off
After AP-11 (fin 50 ft², rudder_lift_coef 2.0), 15 000 ft, M 0.90, doublets with YAW_DAMPER_ON:
- gain 0.3 (`..._T3J_yd03.csv`): period 1.39 s, ratio 0.62/cycle (off: 0.57) -> no effect.
- gain 1.0 (`..._T3J_yd10.csv`): period 1.48 s, ratio 0.58/cycle -> no effect in the doublet, bank stable for 30 s.
  **~15 s later the jet departed by itself** (next log `..._T3J_yd10b.csv` starts at β -42°, bank 132°, yaw rate
  267°/s; crashed). Same behaviour as round D (yaw damper rolled the jet to 66°). RUDDER_DEFLECTION read 0 during the
  free oscillation (the yaw damper rudder command does not show in this SimVar, or it is not applied).
- **Decision: yaw damper OFF** (`yaw_damper_gain` 0). The natural damping (0.57/cycle, about 0.9 cycles to half
  amplitude) is close to the F-104A without SAS (CR-2144 Table III-12: 0.43/cycle, 0.81 cycles to half). A real SAS
  ("completely damped", FM 6-3) would need own control logic (WASM or XML), later work package.

## 2026-10-26: T3-I level max-AB acceleration at 40 000 ft (Mach 0.92 -> 1.80 in 240 s)
Same session (AP-11 build, yaw damper off). Climb to 39 000-40 200 ft, **ambient -57 °C = ISA**, 18 240 lb (NASA 18 000).
Log docs/data/flighttest_2026-10-26_T3I_accel40k.csv (~1 Hz). D-6398 Fig. 6(c)/(d) (30 000/40 000 ft) added to
docs/data/nasa_d6398_excess_thrust_lbf.csv; nalyse_drag.py now has supersonic bands up to M 2.1.
- **Net thrust vs. D-7137 Table 3** (interpolated to the flown altitude): 0.977-1.009 for M 0.9-1.8 ✓.
- **Drag vs. D-7137 Table 2:** M 0.95-1.2: 1.07, M 1.2-1.4: 0.94, M 1.4-1.6: 0.96, M 1.6-1.8: 0.98 ✓.
- Excess thrust vs. D-6398 (flight-measured): M 1.25-1.5: 0.85-1.06 ✓; M 1.6-1.8: 0.69-0.80; transonic M 0.9-1.15 noisy
  (only ~1 000-2 000 lbf excess: 0.55-1.76). Since thrust and drag both match D-7137, the remaining difference is
  between the two NASA reports (D-7137 prediction vs. D-6398 measurement), not a sim error -> no change.
- Mach 2: not reached within the 240 s limit (M 1.80, excess thrust ~2 400 lbf, ~45 s more needed) -> reachable.
- Trim: 9.7° at M 1.0, 5.7° at M 1.08, 2.0° at M 1.8 (nose up positive) - far from the 5° nose-down stop at 40 000 ft.
**Verdict T3-I: thrust/drag up to M 1.8 passed; Mach 2 reachable; excess thrust vs. D-6398 within -30 % (source difference).**

## 2026-10-26: S12 supersonic trim at 16 500 ft - PASSED (first run with the f104 MCP server)
Build with yaw damper off (T1 ✓), aircraft reload. position + ccel_run (M 0.86 -> 1.30 in 70 s, 16 400 ft,
OAT -11 °C ≈ ISA+8, 19 200 lb). Log docs/data/flighttest_2026-10-26_S12_trim16k.csv.
- Trim (nose up +): M 0.87 3.0°, M 1.07 1.9°, M 1.18 1.5°, M 1.27 1.2° -> far from the 5° nose-down stop. The round A
  concern (-4° at M 1.15) predates the htail_incidence/elevator fixes; with 2.0° at M 1.8 / 40 000 ft (T3-I) S12 is done.
- Regression after AP-11 (same log): T3-F drag 1.05 (M 0.4-0.95) ✓, 0.99 at M 1.2-1.4; T3-G tail deflection
  1.10 × α ✓; T3-A largest band mean -0.032 (tolerance 0.03, mean -0.018) - marginal, within scatter (AP-11 changed
  only lateral values).
- Note: after position the AP wing leveler did not hold a -20° bank; AP_HDG_HOLD_ON rolled the jet level ->
  position(lateral='hdg') is the safer default for longitudinal tests.

## 2026-10-26: T3-L approach configuration, run 1 (too slow) - LAND flap pitching moment too strong
Positioned 8 000 ft, gear down at 247 KIAS, LAND flaps at 226 KIAS, military (64 % lever, N1 95-98 %).
Log docs/data/flighttest_2026-10-26_T3L_approach.csv (30 s with flaps/gear): **177 KIAS, 18 400 lb: α 9.45°, CL 0.887,
CD 0.382, trim at the 11° nose-up stop, elevator 0 (the MSFS AP flies with trim only), flight path -8°** -> AP could not
hold the altitude; recovered with flaps up + AB.
- Flown too slow: FM (Fig. A8-2/2-7) final approach at 18 400 lb ≈ 200 KIAS; 177 kt is near touchdown speed.
- Still, relative to CR-2144 (approach CL 0.735 at α 2.3°, CLα 3.44/rad -> CL 0.887 at α ≈ 4.8°) the sim needs ~4.6°
  more α, and CR-2144 trims with δs -7.1° (nose up) while the sim runs out of trim -> the flap lift acts too far aft
  (large nose-down moment, large tail download). Change: LAND dd aft feet 0 -> +3.5 [S] (flap lift centre forward).
  Retest at FM final approach speed (≈ 200 KIAS at 18 400 lb), ~88 % rpm, target trim < 11°, α ≈ 5°.

## 2026-10-26: T3-L approach run 2 (add aft feet 3.5, at 16 500 -> 12 300 ft) - flap lift too low
New sim_actions.py approach (idle + speed brakes, gear < 255, LAND flaps < 230 KIAS, throttle loop, no AB).
Log ..._T3L_approach2.csv, 19 000 lb: 218 KIAS α 8.8° CL 0.86 trim 9.5°; 189 KIAS α 8.8° CL 0.91 trim 9.0° (better
than run 1, trim no longer at the stop at these speeds); military not enough at 12-16 000 ft -> slowed to 157-177 KIAS,
α 10.6°, CL 1.00, CD 0.40, trim 11° (stop), descent -7°.
CR-2144 extrapolated to α 8.8°: CL ≈ 1.12 -> effective LAND increment ≈ 0.39 instead of 0.62 (same shortfall as
TAKEOFF before AP-10's empirical factor) -> LAND lift scalar 1.273 -> 2.0 [M]. T0 target updated (nominal 0.97).
Also: position at 8 000 ft / 250 kt TAS dived to 1 300 ft AGL (ALT hold apparently not active) -> watchdog on
AUTOPILOT_ALTITUDE_LOCK added; approach tests at >= 12 000 ft until verified.

## 2026-10-26: T3-L approach run 3 (lift scalar 2.0, add aft feet 3.5) - worse
Log ..._T3L_approach3.csv, 19 000 lb, from 14 000 ft: CL 0.82 at α 10.2°, CD 0.50, trim at the 11° stop already at
223 KIAS, flight path down to -22°, aborted at 2 900 ft AGL. More flap lift = more nose-down moment (flap lift centre far
aft of the CG) = more tail download, net CL even lower. Run 1 -> 2 showed ~2° trim per 3.5 ft -> add aft feet 3.5 -> 7
(flap lift centre near the CG). Note: the MSFS AP only trims (elevator stays 0), a pilot would add stick.

## 2026-10-26: T3-L runs 2-4 invalid for the flap changes - lift normalization needs a FULL sim restart
Screenshot of "Debug Aircraft Sim Curves" with LAND flaps out (run 4 state): **TgtClAOA0 0.9832** (= 0.01 + new flap
ΔCL 0.97 from the cfg) but **FinClAOA0 0.2233**, RawClAOA0 0.0116, nCl 1.98. The sim had been started before all
of today's flap changes (add aft feet 3.5/7, lift scalar 2.0) and was only reloaded -> flaps still used the old
normalization. Lateral values (AP-11) do take effect on reload, lift/flap values do NOT.
Stall debug window with flaps out: "Middle wing AOA -14.2°" (flap section). Drag check: with
lift_coef_at_drag_zero_flaps default 0 the polar gives CD 0.263 at CL 0.735 incl. gear = CR-2144 exactly -> keep.
Next: full sim restart, check FinClAOA0 with flaps in the debug window, then repeat the approach (≈ 200 KIAS).

## 2026-10-26: T3-L run 5 (after a full restart) and root cause of the LAND flap problem
Full restart did not change anything (FinClAOA0 0.2233 again, approach as run 4: CL 0.92 at α 11.3°) -> the
normalization hypothesis was wrong. Comparison with TAKEOFF flaps at 226 KIAS (debug screenshots): TAKEOFF RawClAOA0
0.159, TgtClAOA0 0.3093, **FinClAOA0 0.3095 ✓**, flapped "middle" wing section incidence +17.1° (Cl0AOA 17.8°).
LAND: middle section Cl0AOA 60°, wing AOA -14.2°, RawClAOA0 0.0116 -> **MSFS turns flap angle x lift scalar into an
incidence increment of the flapped section (~0.62 x angle x scalar); at LAND (45° x 1.273..2.0 = +35..60°) the
section is fully stalled** -> no flap lift, high drag, nose-down moment. This explains runs 1-5.
Change (needs full restart): TE flaps TAKEOFF 0.84 / LAND 0.6 (+~17°), new LE flaps [FLAPS.1] (type 2, 15°/30°,
span 0.95, system lift scalar 1.01, drag scalar 0); targets TAKEOFF 0.30, LAND 0.62 unchanged; add aft feet back to 0.
New T0 rule: TE LAND angle x lift scalar <= 30. Re-test T3-D (takeoff) and T3-L after the restart.

## 2026-10-26: T3-L run 6 - LAND flap lift PASSED (TE + LE flap split), T3-D re-check
Build + full restart (T1 ✓, preflight ✓). Takeoff re-check (..._T3D_takeoff_run7.csv, 19 004 lb, FM 177 kt): first
liftoff 173 kt at 7.6°, sustained 187 kt at 10.6°, ground roll 3 049 ft - same as run 6 (TAKEOFF split unchanged).
Approach (..._T3L_approach6.csv, 18 400 lb, from 15 500 ft): altitude held (-1 100 ft instead of -9 000 ft).
| IAS | α | CL sim | CL CR-2144 (0.735 @ 2.3°, 3.44/rad) | trim | CD |
|---|---|---|---|---|---|
| 186 kt | 4.1° | 0.855 | 0.845 ✓ | 5.6° | 0.27 (polar 0.30) |
| 155 kt | 9.3° | 1.145 | 1.155 ✓ | 11° | 0.38 |
Debug "Sim Curves" with LAND flaps: TgtClAOA0 0.6286, **FinClAOA0 0.6156** (-2 %), nCl 2.19 ✓.
At 14 000-15 000 ft military is not enough for ~200 KIAS with gear + LAND flaps (speed decays to 155 kt); the FM
approach (~88 % rpm) is at low altitude - a low-altitude approach/landing test is still open.
**Verdict T3-L (approach configuration): lift and trim passed.** Open: landing at low altitude, landing distance.

## 2026-10-26: T3-L landing 1 (scripted, 	ools/landing_test.py) - first landing, distance plausible
Start 6 NM out on a 3° glide path (aim 1 000 ft past the threshold), gear + LAND flaps, AP HDG (bug steered by the
cross-track error) + AP VS (glide path) + throttle loop on the FM final approach speed (17 859 lb -> 184 KIAS).
Log ..._T3L_landing1.csv (2.1 Hz). Flare at 50 ft AGL; **touchdown 162 KIAS** (FM Fig. A8-2 normal 166-171, -2.5 %),
sink 565 ft/min, pitch 8.0°, 399 ft past the threshold, 78 ft right of the centreline. **Ground roll 3 158 ft**
(speed brakes, full wheel brakes only below 150 KIAS). FM Fig. A8-4 (no chute, LAND flaps, anti-skid, hard braking):
≈ 2 850 ft at 17 900 lb, 1 500 ft field, std temp, no wind -> +11 % (later braking) ✓.
Approach quality: IAS oscillated 160-220 kt and the jet was up to 570 ft below the path (throttle loop too slow, AP VS
lag) -> tune the script (throttle gain, earlier configuration) before using touchdown values as a strict test.

## 2026-10-27: FM landing distance charts read carefully (grid at 200 dpi)
17 900 lb, 1 500 ft pressure altitude, 12 °C (standard), no wind, dry hard runway, anti-skid, hard braking:
**Fig. A8-4 without chute ≈ 3 130 ft, Fig. A8-3 with 18-ft chute ≈ 2 760 ft (-12 %)**; the sample arrows of both charts
give the same ratio (2.74/3.07 = 0.89). (Yesterday's quick estimate of 2 850 ft without chute was too low; landing 1
with 3 158 ft matches.) The chute drag estimate ΔCD 0.65 (18-ft ring-slot, CD 0.5) would be far too strong; energy
balance with mean q ≈ half the touchdown q gives ΔCD ≈ 0.10-0.15 -> drag_coef_spoilers 0.76 -> 0.21 before building.

## 2026-10-27: landing 3 - belly landing (gear not down), procedure from the FM
..._T3L_landing3.csv: approach clean (path error +3 ft at the flare, 192 KIAS on target with the PI throttle), but
touchdown 184 KIAS, pitch 2.3°, sink 803 ft/min, ground roll 3 091 ft - **gear 0 %** afterwards: positioning in the air
retracts the gear and the script had extended it before set_pos. Landings 1 and 3 were belly landings -> their ground
rolls are invalid. Script fixed (gear/flaps after positioning, gear check 2 NM out -> go-around, softer flare from
100 ft, 80 % rpm), speeds per FM Fig. 2-7 (final 175 / touchdown 155 KIAS @ 16 100 lb), glide 2.5° (700-800 ft/min),
chute 1 s after touchdown. FM landing procedure summarised in the project skill .claude/skills/f104-pilot.

## 2026-10-27/28: landing script rebuilt (dry runs 1-15) - details in docs/notes/test-cards/T3-L-landing.md
Root causes found on the way: set_pos retracts the gear, drops AP modes, starts at α 0, speed argument ≈ IAS; the
MSFS AP flies pitch by trim only (~0.13°/s) and locks the trim while engaged; `pitch_use_elevator_only` resets the trim
to 0 (tried, reverted); a trim run-down after AP disconnect came from the sim settings (fixed by pete). The script now
flies by hand (elevator PI on vertical speed + pitch damping, aileron PID on a localizer bank target, PI throttle),
incl. a hand-flown FM go-around (dry run 15: 30 ft height loss). B5 evidence: level flight in landing configuration
at Military, 6 500 ft MSL, 19 180 lb only 168 KIAS steady (α ≈ 7°, CL ≈ 1.02, CD ≈ 0.32) - FM Fig. 6-8 suggests a
positive climb margin -> test B5 at low altitude.

## 2026-10-28: F2 normal landing PASSED (landing 7, ..._T3L_landing7.csv)
16 786 lb, EDDM 26L (1 487 ft, OAT 10 °C, light wind), 2.5° glide path hand-flown by the script: level 1 065-1 120 ft
AGL, glide path -5..+25 ft, 177-183 KIAS (target 178), bank ±3.6°. Flare from 117 ft. **Touchdown 162 KIAS** (FM Fig.
2-7: 158-163 KIAS at 16 786 lb ✓), sink 83 ft/min, pitch 1.5°, +4 ft from the centreline, 3 979 ft past the threshold
(long float). Chute at 160 KIAS (≤ 180 ✓), hard braking. **Ground roll 2 850 ft**; FM Fig. A8-3 (chute) 2 760 ft at
17 900 lb and its schedule touchdown speed (≈ 165 KIAS) -> scaled by (162/165)² ≈ 2 660 ft -> **+7 % ✓** (±10 %).
Drag chute ΔCD (`drag_coef_spoilers` 0.21) confirmed. Next: F3 without chute (A8-4: 3 130 ft).
Approach of landing 7 (real altitude, ≈ 1 950 ft MSL, 16 570 lb, 179 KIAS, 2.5° glide, steady 33 samples):
**N1 91.1 %** (FM Fig. 2-7: 87-90 % at 16 100 lb, 175 KIAS -> sim ≈ 1-4 % high -> B5: slightly too much drag or too
little part-power thrust), sink 785 ft/min (FM 700-800 ✓), α 3.5°, trim 5.2° with elevator ≈ 0.2° (trim preset
right). **Fuel flow 8 270 lb/h at 5 170 lbf net thrust** - almost the validated military fuel flow (8 400 lb/h) at
about half the thrust: TSFC on gross thrust (≈ 6 600 lbf incl. ram drag) ≈ 1.25 vs. J79 part power ≈ 0.85-0.9 ->
**part-power fuel flow probably too high (test plan D5, pete's observation 2026-10-27)**.

## 2026-10-28: F3 landing without chute PASSED (landing 8, ..._T3L_landing8_nochute.csv)
Refuelled via SimVars (FUEL_TANK_CENTER/CENTER2_QUANTITY, 4 145 lb, CG 8.9 % MAC) instead of a reload. 19 243 lb at
the start, ≈ 18 700 lb at touchdown. Approach: glide path -14..+35 ft, 179-204 KIAS. **Touchdown 173 KIAS** (FM 171-176
✓), 241 ft/min, pitch 2.7°, -3 ft. **Ground roll 3 511 ft** without chute; FM Fig. A8-4 3 130 ft at 17 900 lb and
≈ 166.5 KIAS schedule touchdown -> scaled (173/166.5)² -> ≈ 3 380 ft -> **+4 % ✓**.
Both landings normalised to 166.5 KIAS: with chute 3 010 ft (+9 % vs. 2 760), without 3 250 ft (+4 % vs. 3 130);
chute effect -7 % in the sim vs. -12 % FM -> chute slightly weak, both within ±10 % -> no change (change control).

## 2026-10-28: B6 / B5 landing configuration at Military - FAILED, drag too high (tools/config_test.py)
Card docs/notes/test-cards/B5-B6-landing-config.md. Gear down, LAND flaps, trim 5.2°, Military, hand-flown.
- B6 build-up 10 000 ft (..._B6_climb10k.csv): steady 9 100 ft, 18 780 lb, 167 KIAS: **-690 ft/min** (Fig. 6-8
  extrapolated ≈ 0..+100). Aborted by a false AGL 0 read (fixed).
- **B6 4 500 ft** (..._B6_climb4500.csv): steady 25-119 s, mean 5 140 ft, 18 280 lb, OAT 3 °C, 173 KIAS, α 5.4°,
  N1 100 %, net thrust 6 377 lbf, FF 9 823 lb/h: **+389 ft/min**. FM Fig. 6-8 (3 000 ft curve, scaled for weight and
  altitude, colder day) ≈ 1 200-1 400 ft/min -> deficit ≈ 850-900 ft/min ≈ 850 lbf excess thrust ≈ ΔCD 0.043 at q 101 psf.
- **B5 4 500 ft, speed brakes out** (..._B5_level4500_sb.csv): level, 17 400 lb, settles at **164 KIAS** (α 6.25°,
  net thrust 6 489 lbf); FM 3-41: speed brakes + LAND flaps + gear at Military -> flat ≈ 190-200 KIAS -> at 195 KIAS
  the sim drag is ≈ 930 lbf above the thrust ≈ **ΔCD 0.037**.
- Thrust check: Military net thrust at M 0.29 / 5 000 ft ≈ 6 700 lbf expected (NASA max-AB table x validated static
  Military/AB ratio 6 670/11 200) vs. 6 377 sim (-5 %, as validated before) -> explains ≤ 300 lbf only.
- Source conflict: the LAND flap + gear ΔCD 0.142 comes from NASA CR-2144 (approach CD 0.263 at CL 0.735; the sim
  reproduces that polar), but three FM points (Fig. 6-8, FM 3-41, Fig. 2-7 approach rpm 87-90 % vs. 91 %) agree on
  ≈ 0.04 less drag. FM = flight-tested performance -> proposal: LAND flap drag ΔCD 0.12 -> ≈ 0.08 (flaps-position.2
  drag scalar 1.273 -> ≈ 0.85), gear unchanged. Needs a FULL sim restart and regression: B5/B6, T3-L approach config,
  F2/F3 landings (ground roll will lengthen a few %, chute effect -7 % vs. FM -12 % could then be raised), T3-D.

## 2026-10-28: regression after LAND flap drag 1.273 -> 0.85 (Build All + full sim restart)
- **B6 4 500 ft** (..._B6_climb4500_r2.csv): mean 5 634 ft, 18 800 lb, OAT 3 °C, 177 KIAS: **+1 061 ft/min** (was +389;
  FM Fig. 6-8 scaled ≈ 1 050-1 250) **✓**.
- **B5 4 500 ft speed brakes** (..._B5_level4500_sb_r2.csv): level at **194 KIAS** (was 164; FM 3-41 190-200) **✓**.
- Both flown with live weather (≈ 14 kt wind at altitude) - steady wind does not change IAS/ROC, light turbulence only.
- **F2 landing 9** (with chute, 17 900 lb): approach OK (path -38..+21 ft), but bank oscillation ±6° and in the flare
  at 42 ft a gust (IAS 181 -> 191 KIAS in 1 s, bank -7 -> -22°, ailerons at the ±4000 limit) -> go-around at 25 ft
  (lowest 6 ft AGL), FM go-around flown fine. Live weather: 14 kt from 325° (crosswind for 26L) with gusts.
  -> test configuration: no live weather, calm wind, ISA (test plan section 2); aileron limit ±4000 -> ±8000.
- **Dry run 16** (clear skies, wind 1 kt, ISA; aileron limit ±8000): bank ±1.3° in the approach (was ±6° in live
  weather), path -7..+32 ft, TD 177 KIAS (FM 171-176, +1 kt), 384 ft/min, +2 ft ✓. **cfg bug found in the go-around:**
  the TAKEOFF flaps stuck at 15° up to 545 KIAS - `damaging-speed = 240` applies to every extended flap position (SDK),
  the FM go-around accelerates with TAKEOFF flaps beyond 240 (TAKEOFF limit 370 KIAS, FM 3-36) -> flaps damaged.
  Fixed: damaging-speed 370, blowout 400, position limits TAKEOFF 370 / LAND 240 (both flap systems); scripts retract
  the TAKEOFF flaps at 340 KIAS latest. (Earlier takeoff tests retracted at 400 ft AGL - possibly damaged then too,
  without effect on the liftoff measurement.)

## 2026-10-28: landings in calm weather (clear skies, wind 1 kt, ISA, after the flap fixes) - ground roll too long
- Dry run 17 ✓ (TD 175 KIAS, 497 ft/min, -2 ft; go-around: flaps retracted to 0° ✓ after the damaging-speed fix).
- **F2 landing 10 (chute)**, 18 634 lb: TD 173 KIAS (FM 168-173 ✓), 21 ft/min, +6 ft; **ground roll 3 701 ft** ->
  scaled to 166.5 KIAS 3 428 ft vs. FM A8-3 2 760 ft = **+24 % ✗**.
- **F3 landing 11 (no chute)**, 19 771 lb: TD 178 KIAS (FM 173-178 ✓); **ground roll 4 292 ft** -> scaled 3 755 ft vs.
  FM A8-4 3 130 ft = **+20 % ✗**. Chute effect -9 % (FM -12 %).
- Landings 7/8 (+9/+4 %) were flown in live weather - a headwind of ≈ 8 kt explains ≈ -10 %; calm weather is the valid
  FM condition. Mean deceleration (no chute) 0.33 g vs. FM 0.39 g; brake share ≈ 0.29 vs. 0.35 g ->
  **toe_brakes_scale 0.68 (template) -> 0.82** (systems.f104.cfg [BRAKES]); Build All + aircraft reload; regression F2/F3.

## 2026-10-28: brakes 0.82 - regression F3/F2 in calm weather
- **F3 landing 12 (no chute)**, 19 339 lb: TD 175 KIAS ✓, roll 3 782 ft -> scaled 3 423 ft vs. FM 3 130 = **+9.4 % ✓**
  (brakes x1.2 gave -9 %, not the computed -17 %: friction/transition limited).
- **F2 landing 13 (chute)**, 20 287 lb (refuel script left 116 gal in the tip tanks - fixed: tools/refuel.py, tips
  empty, 4 080 lb fuselage): TD 180 KIAS ✓, roll 3 868 ft -> scaled 3 310 ft vs. FM 2 760 = **+20 % ✗**.
- Deceleration vs. speed (rollout logs): no chute 11-14 ft/s², chute only +1..1.5 ft/s² at 100-160 kt -> effective
  chute ΔCD ≈ 0.066 of the configured 0.19 (≈ 1/3) -> `drag_coef_spoilers` 0.21 -> 0.43 (provisional value, marked
  "to be calibrated with the landing test"). Full sim restart + F2 regression (F3 unaffected: no chute).
- Both landings: the first band after touchdown (180 -> 160 kt) only ≈ 6.4 ft/s² - engine still at ≈ 84 % N1
  (≈ 3 300 lbf) and nose up for several seconds; FM charts likely include a shorter transition. Watch, no change.

## 2026-10-28: NOTE - all tests until 2026-10-28 afternoon were flown in LIVE (real) weather
pete: the sim ran with real weather in every session until clear skies were set (after landing 9). Wind, non-ISA
temperature/pressure and turbulence were therefore present in all earlier rounds (A-F, T3-A ... T3-L, B5/B6 incl. the
regression runs; e.g. 14 kt and 1 028 hPa on 2026-10-28). Assessment:
- Likely still valid: T3-A lift and T3-G trim (analysed with the measured density and IAS; steady wind has no effect),
  T3-D liftoff IAS, landing touchdown IAS.
- **To re-verify in ISA / calm**: T3-F drag and T3-H/I excess thrust (wind shear biases dV/dt; NASA thrust is standard
  day), thrust/fuel-flow comparisons, B5/B6 (1 028 hPa ≈ +1-2 % thrust), spot checks T3-E2 / T3-J (turbulence).
- Invalid and already replaced: landings 7-9 (headwind / gusts).
Valid test results from now on only with the test configuration of docs/test-plan.md section 2 (clear skies, calm, ISA).

## 2026-10-29: F2 regression with drag_coef_spoilers 0.43 (clear skies, wind 1 kt, ISA) - chute lever ineffective
Landing 14 (..._T3L_landing14.csv), 19 180 lb (refuel.py standard): approach path -6..+20 ft, bank ±1.2°; TD 176 KIAS
(FM 170-175, +1 kt ✓), 275 ft/min, -6 ft; chute at 175 KIAS. **Ground roll 3 628 ft -> scaled 3 247 ft vs. FM A8-3
2 760 = +17.6 % ✗** (with 0.21: +20 %). Deceleration bands (ft/s²) no chute / chute 0.21 / chute 0.43:
160-180 kt 6.4/6.4/5.8, 140-160 11.3/14.3/14.9, 120-140 14.2/13.7/13.8, 100-120 14.1/15.5/14.8, 80-100 14.1/15.4/15.7,
below 80 ≈ 13-14 for all -> **doubling the ground spoiler drag changes nothing measurable**: the MSFS ground spoiler
drag is not a usable drag chute. No native drag chute in the MSFS 2024 SDK (only parachute SimObjects). The first
≈ 2 s after touchdown show almost no deceleration (small bounce, nose lowering), then ≈ 15 ft/s² (0.46 g).
Verdict: F3 (no chute, brakes 0.82) ✓ +9.4 %; **F2 with chute = known deviation +17.6 %** until a real drag chute is
modelled with own system logic (test plan H5). drag_coef_spoilers stays 0.43 (harmless, no measurable effect).

## 2026-10-29: B6/B5 re-verified in ISA (clear skies, wind 1 kt, 1013.25 hPa, OAT 9 °C at 4 500 ft ≈ ISA+3)
- **B6** (..._B6_climb4500_isa.csv): mean 5 373 ft, 18 984 lb, 176 KIAS, Military: **+905 ft/min** (FM Fig. 6-8
  scaled ≈ 850-1 000) **✓**. Live-weather run (1 028 hPa, 3 °C) gave 1 061 - consistent with the extra thrust.
- **B5** (..._B5_level4500_sb_isa.csv): 18 881 lb, speed brakes out, Military, level: **182.8 KIAS** (card 180-210 ✓;
  FM 3-41 190-200 without weight -> lower edge). Live weather (18 158 lb, more thrust) gave 194.

## 2026-10-29: ISA re-verification of T3-A/F/G and T3-H (clear skies, calm, 1013.25 hPa, ≈ ISA+3)
- **Deceleration run** (`tools/decel_test.py`, new; ..._T3AF_decel_isa.csv; 16 000 ft, 18 750 lb, OAT -12.5 °C, idle
  from M 1.15 / 596 KIAS to 229 KIAS): **T3-A lift ✓** (mean -0.012, largest band -0.028, tolerance 0.03);
  **T3-G** tail = -0.01° + 1.08 α ✓ (as before); **T3-F drag mean 1.04 ✓** but bands M 0.4-0.6 0.97, **M 0.6-0.8 1.06,
  M 0.8-0.95 1.09**, M 0.95-1.2 1.02 (live weather 2026-10-25: 1.00-1.04).
- **T3-H 10 000 ft** (MCP accel_run, ..._T3H_accel10k_isa.csv, M 0.70 -> 1.20 in 55 s, OAT -1.2 °C, 18 470 lb):
  Fn,ex sim/NASA M 0.75 0.76, 0.80 0.82, 0.85 0.87, 0.90 0.96, 0.95 1.00, 1.00 0.94, 1.05-1.20 0.75-0.84 -> ✗ subsonic
  (live weather: mostly 0.86-1.07); supersonic unchanged (-20 %, accepted before). Drag split of the same run:
  CD/NASA M 0.6-0.8 1.08, M 0.8-0.95 1.11. Few points per band (≈ 1 Hz logger, n = 2) and the run started right
  after positioning (AP still climbing back 350 ft).
- Consistent picture: in ISA the subsonic drag at M 0.6-0.95 is ≈ 6-11 % above D-7137 (T3-F still within ±10 %), which
  becomes -13..-24 % excess thrust. Candidate cause: Oswald factor / induced drag at higher CL or the transonic
  rise start - **no change yet**; to investigate with a dedicated repeat (longer bands, logger at higher rate,
  20 000 ft run too). Earlier "T3-F ✓ 1.00-1.04" and "T3-H subsonic ✓" were live-weather results.
- **T3-J doublet in ISA** (MCP doublet, 16 500 ft, M 0.89, 18 000 lb): period **1.60 s**, amplitude ratio **0.55**/cycle.
  CR-2144 F/C 4 (15 000 ft, M 0.9): 1.41 s / 0.43; scaled to the test point (density, speed) ≈ 1.53 s -> +5 % ✓
  (live weather 2026-10-26: 1.48 s / 0.57).
- **T3-E2 sideslip in ISA** (MCP sideslip, 15 000 ft, ≈ 350-381 KIAS, M ≈ 0.7): **β/δr 0.34, δa/δr 0.43** ✓
  (CR-2144 0.32-0.42 / 0.27-0.47; round E 0.32 / 0.39).

## 2026-10-29: B4 glide (tools/config_test.py glide mode, ISA, 22 000 -> 13 000 ft, idle, gear up)
- Run 1 (TAKEOFF flaps): aborted at pitch -21° (controller start too aggressive) -> VS command starts at the current VS,
  slower speed integrator, gains scaled with 1/q.
- **TAKEOFF flaps, 245 KIAS** (..._B4_glide_to2.csv, 19 175 lb): α 4.4°, idle net thrust -549 lbf (≈ windmilling ram
  drag): glide ratio (energy) **5.15 = 8.5 NM per 10 000 ft**; aerodynamic L/D (thrust removed) 6.04.
- **Flaps up, 275 KIAS** (..._B4_glide_clean.csv): α 7.2°, idle net thrust -803 lbf: glide ratio **6.42 = 10.6 NM per
  10 000 ft**; aerodynamic L/D 8.78 (desk check from the polar 8.6 ✓).
- FM Fig. 3-8: both configurations give the same distance; 9 NM with RAT, ≈ 11 NM without RAT (the sim has no RAT) ->
  **clean -4 % ✓, TAKEOFF -23 % ✗** -> TAKEOFF flap drag too high (same pattern as the LAND flaps on 2026-10-28, both
  from the scaled CR-2144 estimate): **TAKEOFF drag scalar 1 -> 0.42** (flap ΔCD 0.031 -> 0.013). FULL restart;
  regression: B4 TAKEOFF glide (expect ≈ 10.5-11 NM), T3-D takeoff liftoff speed (drag only, should be unchanged).
- **Regression after the change (Build All + FULL restart, ISA, wind 1 kt, trim-hold check ✓):**
  - B4 TAKEOFF flaps 245 KIAS (..._B4_glide_to_reg.csv, 19 140 lb): α 4.3°, idle net thrust -596 lbf: glide ratio
    (energy) **5.94 = 9.8 NM per 10 000 ft** (was 8.5); aerodynamic L/D 7.29. vs. FM ≈ 11: **-11 %**, just outside ±10 %;
    sim TAKEOFF/clean = 0.92 (FM 1.0). Accepted as ◐: the "≈ 11 NM without RAT" reference is itself an estimate (FM text:
    RAT costs about 2 NM), so a further scalar cut would chase reading accuracy. No further change.
  - T3-D takeoff (MCP takeoff, 18 938 lb, θ 10.5°): liftoff **170 kt**, pitch 8.9°, ground roll 2 627 ft / 17.0 s.
    FM Fig. A2-3 174 kt at 18 155 lb + 4.43 kt per 1 000 lb -> 177.5 kt: **-4.2 % ✓** (±5 %). Run 6 (2026-10-25) was
    185 kt (+3.4 %), but it was flown in live weather and BEFORE the LE flaps were added (T3-L, 2026-10-26, more lift
    in TAKEOFF too); the flap drag change cannot lower the liftoff speed -> new reference value 170 kt. The ground roll
    is the first data point for D1b (FM Fig. A2-4, still to read).

## 2026-10-29: D5 cruise fuel flow vs. FM Fig. A6-1 (drag index 0) - FAILED, part-power fuel flow +79..86 %
Card docs/notes/test-cards/D5-fuel-flow.md, new `tools/cruise_test.py` (AP ALT/HDG hold, throttle PI on Mach, 60 s steady
average). Clear skies, calm, 1013.25 hPa, ISA+3. FM chart: NM per 1 000 lb x δ vs. true Mach, W/δ parameter, data
basis flight test (J79-GE-11A); FF_FM = TAS / NMPP.
| Point | alt | M | W/δ | N1 | net thrust | FF sim | gross = FF/1.26 | FF FM | sim/FM |
|---|---|---|---|---|---|---|---|---|---|
| A | 11 898 ft | 0.700 | 29 450 | 83.8 % | 2 156 lbf | 6 148 lb/h | 4 880 lbf | 3 427 lb/h | **1.79** |
| B | 19 602 ft | 0.801 | 39 306 | 84.7 % | 2 081 lbf | 5 825 lb/h | 4 623 lbf | 3 124 lb/h | **1.86** |
| C | 29 499 ft | 0.853 | 59 509 | 85.4 % | 1 906 lbf | 4 816 lb/h | 3 822 lbf | 2 616 lb/h | **1.84** |
- Point A was evaluated from the simlog (t 150-236 s, steady ±5 ft, M 0.700) because the script aborted on a wrong VS unit
  (Python-SimConnect returns VERTICAL_SPEED in ft/min; fixed).
- Chart reading ±1.5 units ≈ ±2 %; error is ~40x that. Also seen in passing: 6 100 ft, M 0.82: 9 320 lb/h at 2 950 lbf
  net thrust.
- Cause: FF = TSFC 1.26 x GROSS thrust (AP-7, calibrated statically at Military, M 0). In flight the gross thrust
  includes the ram drag (here ≈ 1 900-2 700 lbf, airflow ≈ 100 lb/s - physically plausible with ram pressure), so a
  constant gross TSFC overstates part-power cruise fuel. The FM implies FF/gross ≈ 0.68-0.70 at M 0.7-0.85 vs. 1.26
  static; the error does NOT depend on altitude (1.79-1.86 from 12 000 to 29 500 ft) -> it is a Mach (ram) effect, so
  `JET_density_on_FF_table` alone cannot fix it. FM-implied net TSFC 1.37-1.59.
- Consequences: endurance/range in the sim ≈ 55 % of the real jet (pete's observation 2026-10-27 confirmed).
- **No change yet** - fix options and a further reference point at low Mach (FM Part 5 endurance, sea level) are
  planned in the D5 card; the validated AB fuel flow (AP-7) and static Military FF are affected by every option.
- **Endurance points** (FM Fig. A5-1 maximum endurance, sheets 1/2 PDF 513/515, DI 0, 18 500 lb read: 5 000 ft M 0.50
  106 NM per 1 000 lb, 10 000 ft M 0.555 119 NM per 1 000 lb; FF scaled with weight): 5 000 ft M 0.500, 18 921 lb, N1 80.9 %,
  net 1 998 lbf: **5 210 vs. 3 132 lb/h = 1.66**; 10 000 ft M 0.556, 18 645 lb, N1 81.5 %, net 1 968 lbf: **5 085 vs.
  3 000 = 1.70** (logs ..._D5_endur_5k/_10k). The error grows with Mach (1.66 at M 0.5 -> 1.86 at M 0.8), consistent
  with the ram drag in the gross thrust.
- Options evaluated on all 5 points (needed FF/gross 0.676-0.757, FF/net 1.37-1.59): (b) gross TSFC 0.72 -> -4.9 /
  -3.1 / +2.5 / +6.5 / +5.2 %; (c) net TSFC 1.50 -> -4 / -2 / -6 / 0 / +9 % but a mode switch with untested AB
  behaviour and negative idle net thrust in flight. **Chosen (b): ThrustSpecificFuelConsumption 1.26 -> 0.72**
  (same mechanism, one value). Known deviation: static Military ≈ 4 800 lb/h instead of the ≈ 8 400 estimate (ground
  runs only; takeoff uses AB). Needs Build All + aircraft reload (engine value).
- AB fuel flow must be re-calibrated (FF_AB = TSFC x dry gross + AB TSFC x AB increment). Reference before the change
  (ISA accel 10 000 ft, ..._T3H_accel10k_isa.csv, full AB): M 0.70 22 895, 0.80 27 833, 0.90 31 654, 1.00 34 870,
  1.10 37 702, 1.20 40 849 lb/h (these match D-7137 Table 4 via round A/B). Plan: same accel run after the change ->
  dry gross G = ΔFF / 0.54 -> AB increment -> new AB TSFC that restores the reference FF.

## 2026-10-29: regression after TSFC 1.26 -> 0.72 (Build All + reload; MSFS crashed once, then full restart)
- MSFS crashed (hung, "not responding") right after an MCP `position` from the ground (engine idle on the runway).
  After the restart: positioning only from the air (takeoff first). A position with throttle 5 000 at 19 600 ft gave
  a dive to 9 500 ft at -22° pitch (AP too slow) -> repositioned with throttle 8 000, fine (use ≥ 7 000).
- Engine start ✓ (39 -> 67 % N1, combustion, no flameout), ground idle FF ≈ 240-280 lb/h (known: was ≈ 566).
- **T3-D** (..._T3D_takeoff_tsfc072.csv, 19 340 lb, FM 178.7 kt): first liftoff 171 kt (-4.3 %), short touchdown,
  sustained 185 kt (+3.5 %) ✓ (AB thrust unchanged; same pattern as run 6).
- **AB fuel flow unchanged** (..._AB_accel10k_tsfc072.csv vs. ..._T3H_accel10k_isa.csv, full AB, 10 000 ft):
  FF new/old M 1.00 0.996, 1.05 1.002, 1.10 1.004, 1.15 1.007, 1.20 1.007 -> with full AB MSFS uses the AB TSFC only;
  **no AB re-calibration needed**. (M 0.80-0.95 bands differ because the new run started at M 0.79 during the AB light-up;
  net thrust was lower there too.)
- **D5 regression** (cruise_test.py, same points): B M 0.80 / 19 600 ft **1.07** (3 395 vs. 3 180 lb/h, predicted
  1.065), C M 0.85 / 29 500 ft **1.04** (2 834 vs. 2 725), E1 M 0.50 / 5 000 ft **0.96** (2 975 vs. 3 112) ✓ (±10 %).
  Sim range now 146-178 NM per 1 000 lb (FM 156-185).
- **Idle in flight** (5 000 ft, 35 s): N1 67 %, FF ≈ 300 lb/h, net -800..-1 150 lbf, combustion stays on ✓; Military
  after idle: 99.3 % N1, 6 648 lbf, 6 407 lb/h at ≈ 215 KIAS ✓.
- Open: approach N1/FF (next landing run), A/E2 not re-flown (bracketed by B/E1).

## 2026-10-30: approach N1/FF (last D5 regression item) and F3 regression - PASSED
Session start checks ✓ (T1, preflight, wind 1 kt / 1013.25 hPa, trim hold; fresh load again had 87 gal per tip ->
refuel.py). Takeoff first (T3D_takeoff_day4: first liftoff 171 kt, sustained 185 kt, 19 009 lb - same as 2026-10-29),
refuel in the air, then `landing_test.py ... 6 2.5 0 nochute` (landing 15).
- **Approach** (glide path 2.5°, 40 samples, ≈ 2 100 ft MSL, 18 918 lb, 190.5 KIAS, -866 ft/min, α 3.6°):
  **N1 89.5 %** (FM Fig. 2-7: 87-90 % at 16 100 lb / 175 KIAS) ✓; **FF 4 311 lb/h** at 4 546 lbf net (landing 7 with
  TSFC 1.26: 8 270 lb/h at 5 170 lbf). No FM fuel-flow value for the approach -> plausibility only.
- **F3 landing 15** (no chute): TD 174 KIAS (FM 170-175 ✓), 44 ft/min, -4 ft; ground roll 3 730 ft -> scaled to
  166.5 KIAS 3 416 ft vs. FM A8-4 3 130 = **+9.1 % ✓** (landing 12: +9.4 %).
- D5 regression complete.

## 2026-10-30: flap travel coupling found (LE TAKEOFF 15 -> 10°), takeoff climb-out fault, B7 clean
- **Flap coupling**: MSFS drives all flap systems with ONE travel fraction and stops when the first system reaches its
  stage: UP->TAKEOFF gave TE 15° / LE 10° (TE stage 15/45 = 1/3 reached first), LAND->TAKEOFF gave TE 22.6° / LE 15°
  (LE stage 15/30 = 1/2 reached first). FLAPS_INCR/FLAPS_1/DECR all show it (handle index 1, percent 0.5 both times).
  Every validated takeoff/B4 run used the extending path (TE 15 / LE 10) -> **LE TAKEOFF stage 15 -> 10°** (same
  physics as validated, no hysteresis); flown TAKEOFF ΔCL is 0.246, not the design 0.30 (T0 target updated).
  Needs Build All + FULL restart; regression: T3-D (extend path), LAND->TAKEOFF retract check, B4 TAKEOFF optional.
- **Takeoff climb-out fault** (pete's question; log ..._T3D_takeoff_day4b.csv): after the AP handover at 30 ft the
  trim-based AP held the jet at 21-34 ft for 12 s while it accelerated 204 -> 321 kt; gear UP only at 50 ft ≈ 330 KIAS
  (FM: when definitely airborne, up before 260 KIAS), TAKEOFF flaps UP at 400 ft ≈ 376 KIAS (limit 370; FM: up at
  ≥ 260 KIAS). Liftoff values (measured before) stay valid; no damage flags set. Fix in `takeoff_test.py`: hand-flown
  climb-out (pitch 15°, half gains scaled with (185/IAS)², wings level by aileron), gear up at 20 ft when definitely
  airborne then Military, flaps up at ≥ 260 KIAS / 300 ft, fallback to the old AP handover if unstable.
- **B7 clean** (`config_test.py slow`, 19 000 lb, 1 kt/s level deceleration; card B7-minimum-speeds.md):
  run 1 (10 000 ft, to 200 KIAS): α 9.0° @ 242, 10.7° @ 227, 12.2° @ 212, 13.9° @ 202 KIAS - consistent with the lift
  table. Run 2 (15 000 ft): α stuck at 16.2° below ≈ 183 KIAS - script elevator clamp (-12 000 = 12.45°), invalid for
  the limit. **Run 3** (full elevator): elevator reaches the 17° stop, **α still limited to ≈ 16.2°**, load factor
  0.91 g at 180 KIAS -> effective trimmed CLmax ≈ 0.80 -> **minimum level speed ≈ 188-190 KIAS**; below that the jet
  mushes (sink > 2 000 ft/min), wings level, no pitch-up, no departure. FM Fig. 6-4 at 19 000 lb: shaker ≈ 222, min.
  control ≈ 197 KIAS; FM 6-5 kicker/pitch-up scaled ≈ 196 KIAS -> sim ≈ 4 % below the FM minimum control speed ✓
  (±5 %), but the behaviour differs (mush instead of pitch-up) -> pitch-up/APC shaker-kicker = test plan H2.

## 2026-10-30: after the LE flap change (Build All + FULL restart): flap path, new climb-out, B7 TAKEOFF/LAND
- **Flap path** (ground): UP->TAKEOFF TE 15.0 / LE 10.0, ->LAND 45.0 / 29.9, LAND->TAKEOFF **15.0 / 10.0** ✓ (hysteresis gone).
- **T3-D + new climb-out** (..._T3D_takeoff_climbout1.csv, 19 007 lb, FM 177.6 kt): first liftoff 169 kt, sustained
  188 kt (+5.9 %; the last four runs 184-188 kt, the sustained value depends on the short bounce after the first
  liftoff; mean +4.3 %) ✓ unchanged by the LE stage. Climb-out: gear up at ≈ 222 KIAS / 24 ft ✓ (< 260), Military,
  max 243 KIAS, bank ±0.1°, steady climb to 1 500 ft ✓; pitch drifts from 15° to ≈ 19.5° (no integral term) and the
  TAKEOFF flaps stay out because 260 KIAS is not reached (FM-correct) -> cosmetic, open.
- **B7 TAKEOFF flaps** (19 000 lb): to 180 KIAS (10 000 ft) α 11.2° / CL 0.86 at 182 KIAS; to the limit (15 000 ft):
  elevator 17° stop at ≈ 160 KIAS, α max ≈ 15.8°, 0.91-0.95 g at 158-161 KIAS -> CL_eff ≈ 1.05 -> **min. level speed
  ≈ 165-168 KIAS vs. FM min. control ≈ 178 (-6..-7 %)** ◐, mush, no departure.
- **B7 LAND flaps + gear** (19 000 lb): to 150 KIAS (10 000 ft) α 11.1° / CL 1.23 at 152 KIAS (T3-L consistent); to the
  limit (12 000 ft): elevator 17° stop at ≈ 137 KIAS, α max ≈ 15.5°, 0.93 g at 136 KIAS -> CL_eff ≈ 1.44 -> **min. level
  speed ≈ 141-144 KIAS vs. FM min. control ≈ 148 (-3..-5 %)** ✓.
- **B7 summary**: in all three configurations the sim's minimum level speed is set by elevator authority (17° stop,
  α ≈ 15.5-16.2°), 3-7 % below the FM minimum control speeds (clean -4 %, TAKEOFF -6..-7 %, LAND -3..-5 %); the jet
  mushes wings-level instead of pitching up (clean/TAKEOFF) -> pitch-up, APC shaker/kicker = H2 (own logic). The
  sim stall-speed values in the cfg (full_flaps_stall_speed 121) are never reached in level flight.

## 2026-10-30: T3-H subsonic investigation - explained (reference conflict D-7137 vs. D-6398), no change
- **Steady-level drag** from the D5 cruise/endurance logs (unaccelerated, D = T cos α - W sin γ; best drag data we
  have, no dV/dt noise): CD_sim/CD_D-7137 = M 0.50 1.04, 0.555 1.05, 0.70 1.05, 0.80 1.06/1.07, 0.85 1.03 (CL 0.2-0.3)
  -> **subsonic drag +3..+7 %, mean ≈ +5 %** ✓ (the accel/decel band values 1.06-1.11 carry dV/dt noise).
- **AB net thrust** (ISA accel 10 000 ft vs. D-7137 Table 3): M 0.8 -2.6 %, 0.9 +0.7 %, 1.0 +1 % ✓.
- **Reference check**: D-7137's own thrust-minus-drag model (Table 3 - Table 2, 18 000 lb) vs. the D-6398 measured
  excess thrust: 10 000 ft M 0.70-0.85 **0.86-0.90**, 20 000 ft **1.03-1.12** (M 0.95-1.2 at 20 000 ft 1.01-1.13, M 1.3-1.4
  1.25-1.50). A perfect D-7137 replica therefore shows -10..-14 % at 10 000 ft and +3..+12 % at 20 000 ft vs. D-6398 -
  the same opposite-sign pattern found supersonically on 2026-10-25 and at 40 000 ft (T3-I).
- **New ISA run 20 000 ft** (..._T3H_accel20k_isa.csv, M 0.63 -> 1.30 in 80 s, 18 920 lb, OAT -20.8 °C): Fn,ex
  sim/D-6398 M 0.65 0.88 (n = 2, AB light-up), M 0.70-1.25 **0.97-1.08** ✓; drag (accel) 1.04/1.08/1.03 (M 0.6-0.8/
  0.8-0.95/0.95-1.2).
- **Verdict T3-H ◐ explained**: the sim follows D-7137 (thrust -3..+1 %, drag +3..+7 %); the remaining 10 000 ft
  deficit (-13..-24 % in ISA, of which ≈ -10..-14 % is the reference conflict and ≈ -5 % the drag/thrust residual plus
  n = 2 band noise) is not a sim error. No change (a drag cut would improve 10 000 ft and worsen 20 000 ft).

## 2026-10-30: D1b takeoff ground run vs. FM Fig. A2-5 (PDF 458) - +10 % (tolerance edge)
- Chart: "Takeoff ground run distance - maximum thrust, normal performance, hard surface level runway" (data basis
  flight test, J79-GE-11A); note: ground run changes 5.5 % per 5 kt deviation from the normal takeoff speed.
  Reading method calibrated on the FM sample problem (PDF 453: 21 020 lb, 3 000 ft, 40 °C -> 4 800 ft; my trace of the
  21 000 lb line on that row: 4 740 ft, -1 %). **Our condition 19 000 lb, 1 500 ft, 15 °C, zero wind/slope: ≈ 2 630 ft**
  (±150 ft).
- `takeoff_test.py` new option `fm` (FM 2-20 technique: Military against the brakes -> release -> AB). Run
  ..._D1b_takeoff_fm1.csv (19 008 lb, wind 1 kt): first liftoff 171 kt after 2 690 ft, sustained 188 kt after 3 253 ft -
  identical to the AB-against-brakes runs (the sim's AB lights almost at once). Normalised to the FM normal takeoff
  speed 177.6 kt (V² / the 5.5 %-per-5 kt rule): **≈ 2 900-2 920 ft vs. FM 2 630 = +10 %** ◐ (2026-10-29 run: 2 627 ft
  to 170 kt at 18 938 lb -> 2 860 ft, +9..10 %). Mean acceleration sim ≈ 15.4 ft/s² vs. FM ≈ 17 ft/s².
- Candidate causes (not changed): low-speed AB thrust (D-7137 Table 3: 11 200 static -> 13 640 at M 0.4; the sim's AB
  thrust was validated at M ≥ 0.7 in flight and statically), rolling friction, the rotation technique (FM attitude
  ≈ 5°, script 10.5° with a bounce). Next: log thrust in takeoff_test.py and compare with D-7137 M 0-0.3.
- **Follow-up (thrust-logged takeoff, ..._D1b_takeoff_thrust.csv + _fm2.csv)**: same result (170 kt after 2 678 ft,
  187 kt after 3 224 ft). AB net thrust on the roll vs. D-7137 Table 3 (interpolated to 1 460 ft, M 0-0.24):
  **0.969-0.979** at every speed up to 150 KIAS (static 10 365 lbf). Mid-roll acceleration 26.7 -> 151.5 KIAS in
  12.4 s = 17.0 ft/s²; T/m 19.1 minus ≈ 2.1 ft/s² for drag (≈ 780 lbf at q ≈ 40 psf with gear/flaps) and rolling friction
  (≈ 380 lbf) -> consistent. The +10 % = ≈ +3 % from the -2.5 % thrust plus the rotation phase (script pulls to 10.5°
  from 157 kt -> high induced drag; FM attitude ≈ 5°) and the first 3 s after brake release (14 ft/s²).
  **D1b ◐ accepted, no cfg change**; technique (rotation attitude/timing) to refine with the takeoff script later.

## 2026-10-30: D3 level acceleration 35 000 ft vs. FM Fig. A9-1 (PDF 561) - time ✓, fuel +20 %
- FM Fig. A9-1 (maximum thrust level flight acceleration, 35 000 ft, no external stores, data basis flight test),
  standard day, from M 0.9 to M 1.8 (x axis runs to M 2.0): 18 000 lb 2.55 min / 37 NM / 880 lb; 20 000 lb 3.2 min /
  41 NM / 1 010 lb -> **at 18 986 lb ≈ 2.87 min, ≈ 39 NM, ≈ 945 lb**.
- Sim (..._D3_accel35k.csv, MCP accel_run, 34 950-35 100 ft, OAT -50.8 °C ≈ ISA+3.5, 18 986 lb at M 0.9):
  **3.10 min (+8 % ✓), 40.2 NM (+3 % ✓), 1 137 lb (+20 % ✗)**.
- AB fuel flow vs. D-7137 Table 4 (interpolated in δ between 30 000/40 000 ft): M 1.0 +2 %, 1.2 +3 %, 1.4 +9 %, 1.6 +15 %,
  1.8 +20 %; at 10 000 ft (ISA accel) M 0.8-1.2: 0.94-1.01. -> the AB fuel flow error grows with Mach, not altitude:
  FF = AB TSFC x AB gross-thrust increment, which contains the ram drag (same mechanism as the dry cruise FF, D5). The SDK
  has no Mach-dependent FF factor; `AfterBurnThrustSpecificFuelConsumption` would trade the validated M ≈ 1 values
  against M 1.8. **Known deviation, no change** (+9..+20 % AB fuel at M 1.4-1.8).
- Both 35 000 ft runs stopped at the 740 KIAS script limit (FM 750 KIAS, Fig. 5-2): at 33 000-35 000 ft that is
  M ≈ 1.77-1.82 (supersonic pitot), so Mach 2.0 is only reachable higher up (D4 at 40 000 ft). First suspected a
  spurious read; accel_run now requires the stop condition on two consecutive reads anyway.

## 2026-10-30: D4 top speed - Mach 2.05 at 40 000 ft ✓; finding: MSFS indicated airspeed reads high supersonic
- **Sim IAS supersonic**: AIRSPEED_INDICATED showed 740 kt at M 1.77 / 33 000 ft. Pitot with the normal shock
  (Rayleigh) gives ≈ 680 KCAS, EAS ≈ 604 kt; the isentropic formula without the shock gives ≈ 746 kt = the sim value.
  -> MSFS computes IAS without the normal shock ahead of the pitot: ≈ +60 kt at M 1.8, growing with Mach. The FM limit
  is 750 KEAS (Fig. 6-6: M 2.0 / 750 KEAS). The accel_run stop (740 "KIAS") had therefore ended the D3 and two D4 runs
  at M 1.77-1.90 -> accel_run now stops on EAS = TAS x sqrt(σ) > 740. Later (cockpit, AP-9): our own ASI gauge must use
  the Rayleigh pitot formula, the sim variable is not usable above M 1.
- **D4** (..._D4_mach2_40k_c.csv; positioned at 44 000 ft, sank to ≈ 38 000 ft, then AB with the AP climbing back to
  40 150 ft; 18 976 lb, OAT -53.1 °C = ISA): M 1.25 -> **2.056 in 222 s**; dM/dt 0.21-0.26 per min up to M 1.8,
  still 0.18 per min at M 1.96 (while climbing ≈ 1 000 ft/min) -> thrust-wise Mach 2 is reachable with margin, as the FM
  says (the limit is the engine inlet temperature 121 °C, reached at M ≈ 1.98 at -53 °C; 136 °C at M 2.05). Net thrust
  11 100 lbf at M 1.96 (T3-I: thrust ✓ vs. D-7137 to M 1.8). **D4 ✓**. The sim has no inlet temperature limit/warning
  (real aircraft: pilot limit, FM 5) -> cockpit/systems later.
- Positioning at 35 000-44 000 ft with Military: the jet sinks ≈ 4 000-5 000 ft (α 0 after set_pos) -> position
  ≈ 4 000 ft above the target altitude.

## 2026-10-30: incidents - unattended belly landing, bad respawn; tools fixed
- After the D4 run accel_run set the throttle to IDLE; the jet stayed in AP ALT hold at idle, sank unattended and
  belly-landed ≈ 230 NM west of EDDM (48.40 N 7.51 E, gear up, no crash flagged). Fix: accel_run ends at throttle 9000.
- `runway_start` from that state: set_pos with the gear UP put the jet down at belly height, GEAR_DOWN afterwards pushed
  it up -> it bounced on the runway (pete) and the next takeoff was invalid (..._T3D_takeoff_day4c.csv: liftoff 125 kt,
  13.2° on the ground > 12.3° tail contact). Fix: gear down first, then set_pos, then wait until the jet sits still
  (on ground, |VS| < 30, pitch -0.5..1.5°, gear 100 %; one re-position), else "NOT SETTLED"; takeoff_test.py aborts if
  the jet is not settled. Verified: runway_start from the belly-landed state -> settled; takeoff 170 / 187 kt normal.

## 2026-10-30: D7 maximum thrust climb at M 0.90 vs. FM Fig. A3-7 (PDF 480) - PASSED
- FM Fig. A3-7 "Maximum thrust climb control, climb speed Mach 0.90" (data basis flight test; schedule M 0.90 at all
  altitudes, SL 595 / 20 000 ft 425 / 35 000 ft 310 KIAS). Lines only for drag index 20-80 -> DI 0 extrapolated linearly
  from DI 20/40 (nearly straight in this range). 19 000 lb, standard day; altitude lines identified on a 260 dpi zoom with
  labels (a first reading had taken the 37 500/42 500 ft dashed lines for 35 000/40 000 ft): time from SL 10 000 ft
  0.20, 20 000 ft 0.52, 25 000 ft 0.69, 30 000 ft 0.97, **35 000 ft 1.33 min** (DI 20: 0.22 ... 1.46).
- New `tools/climb_test.py` (set_pos 9 000 ft ≈ M 0.9, full AB, elevator holds the Mach via an integrated VS command,
  aileron heading hold, round-off from 33 000 ft, Military at 35 000 ft, AP ALT hold at the end). Run
  ..._D7_climb_m090.csv: 19 005 lb, OAT 0.1 °C at 9 000 ft (≈ ISA+3), mean M 0.90-0.93 (0.945 in the first 5 000 ft),
  pitch up to 50° (FM Fig. 6-7: 40-50°): **10 000 -> 35 000 ft in 1.09 min (FM DI 0 1.13, -4 %)**, 20 000 -> 35 000 ft
  0.82 min (FM 0.81, +1 %), 25 000 -> 35 000 ft 0.59 min (FM 0.64, -8 %) ✓ (reading ±5 %).

## 2026-10-30: D7 military climb at M 0.85 vs. FM Fig. A3-10 (PDF 486) - PASSED; climb_test.py hardened
- FM Fig. A3-10 "Military thrust climb control, climb speed Mach 0.85" (flight test; SL 565 / 20 000 ft 400 / 35 000 ft
  290 KIAS). DI 20-80 lines only -> DI 0 extrapolated from DI 20/30 (the lines fan out strongly at the top: least
  certain above 25 000 ft). 19 000 lb, standard day; altitude lines by pixel scan/track: time from SL 10 000 ft 0.80,
  20 000 ft 1.70, 25 000 ft 2.27, 30 000 ft 2.82, 35 000 ft ≈ 4.16 min (DI 20: ... 35 000 ft 5.72).
- Run 1: aborted at once (pitch 71°): set_pos gave M ≈ 1.1 instead of ≈ 0.85 and the large Mach error became a huge VS
  command. Run 2 (..._D7_climb_mil085.csv): started at M 0.93, zoomed 10 -> 20 000 ft in 14 s at 67°, then M 0.77-0.82
  (below the schedule) -> evaluated by energy height only: 20 -> 35 000 ft ratio 1.11 (segments up to 1.33) - off schedule.
- **climb_test.py fixes** (script change -> regression): proportional term limited to ±8 000 ft/min, VS cut above 55°
  pitch, start speed scaled with the target Mach, wait for plausible attitude after set_pos, and an **idle pre-phase**
  holding ≈ 9 000 ft until the Mach is on the schedule (set_pos does not reliably take the speed: one regression attempt
  appeared at M 1.27 / 735 KIAS after a high-altitude flight -> pitch 72° abort).
- **Regression max thrust** (..._D7_climb_m090_reg.csv): 10 000 -> 35 000 ft **1.09 min** again (identical intervals) ✓.
- **Military run 3** (..._D7_climb_mil085b.csv, 19 002 lb, ISA+3, pre-phase 24 s, **M 0.850 throughout**, pitch ≤ 19°):
  10 -> 20 000 ft 0.87 min (FM 0.90, -3 %), -> 25 000 ft 1.48 (1.47, +1 %), -> 30 000 ft 2.28 (2.02, +13 %), **-> 35 000 ft
  3.50 min (FM 3.36, +4 %)** ✓. The 30 000 ft mark is where the DI 0 extrapolation is least certain.
  Energy-height evaluation of the max thrust run: 10 -> 35 000 ft ratio 1.03.

## 2026-10-30: CG check (pete's input "CG limits 0.07-0.164 MAC from CR-2144") - not limits; CG travel reversed
- CR-2144 PDF 40 (F-104A): **0.070 c̄ and 0.164 c̄ are the CG positions of the two analysed configurations, not limits**:
  nominal (clean, 750 rounds, 50 % internal fuel, 16 300 lb) c.g. 0.070 c̄; power approach (clean, 20 % internal fuel,
  flaps 45° + BLC, gear down, 14 126 lb) c.g. 0.164 c̄. The FM gives no numeric CG limits (2026-10-25). The cfg comment
  "CR-2144: 0.07 (combat) to 0.164 (approach)" at CG_forward_limit is correct as positions, not as limits.
- **Sim CG vs. fuel** (SimVar CG_PERCENT, tips empty, Center2 drains first): full internal 5 887 lb 12.4 %, 70 % (test
  standard) 9.6 %, 50 % (Center2 empty) 11.1 %, 20 % 7.7 %, zero fuel 5.1 % MAC -> **the sim CG moves FORWARD as fuel
  burns; the F-104A moves AFT** (7.0 % at 50 % -> 16.4 % at 20 %).
- Cause: `empty_weight_CG_position` = 0.07 MAC was taken from the CR-2144 nominal case (which includes 50 % fuel and
  ammunition), and the tanks were then moved aft (first +6/+11 ft gave -4.8 % MAC, now Center1 -1.6 ft) to reach ≈ 7-10 %
  at the test fuel state (AP-8 matched one point only).
- Desk fit to both CR-2144 points with our weights (zero fuel 14 930 lb, Center1 only at 20 %): Center1 ≈ +9.9 ft ahead
  of the datum (≈ F.S. 353, between cockpit and wing - plausible for the F-104 fuselage cells), zero-fuel CG ≈ +0.1 ft
  (≈ 24 % MAC). Consequence: at the test standard (70 %, Center2 ahead of Center1) the CG would be ≈ 1 % MAC instead of
  9.6 %.
- **Not changed** (big change to validated values: T3-A normalization, T3-G trim gradient, takeoff/landing trim, all
  flown at 9.6 %; F-104A data for a G with a different nose and an auxiliary tank). Proposed work package: get F-104G
  weight-and-balance data (FM Section V loading/CG chart, D-6398/D-7137 test-aircraft CG, a G weight report), then one
  change round with full regression (T3-A/F/G, T3-D, T3-L, B5/B6, landings).

## 2026-10-30: CG rework (pete's decision: correct now) - change, regression pending
- Key detail: the two CR-2144 configurations differ in ammunition too - nominal "clean, 750 rounds", power approach
  "clean" -> 16 300 - 14 126 = 2 174 lb = 30 % fuel (1 747 lb) + ≈ 427 lb ammunition. Fit in the F-104A frame (zero-fuel
  weight without ammo 12 961 lb, ammo at ≈ 13 ft [S], auxiliary cell drains first): main-cell centroid **6.2 ft**
  (≈ F.S. 398, around the inlet ducts), zero-fuel CG 0.34 ft -> empty CG without pilot ≈ **0 ft = 25 % MAC**.
- Change (needs Build All + FULL restart): `empty_weight_CG_position` 1.7 -> 0.0; Center1 -1.6 -> 6.2 ft; Center2
  5.0 -> 15.0 ft (ahead of the forward main cell [S]); CG limits -0.05 / 0.25 [S]; `tools/refuel.py` standard state now
  as in flight: auxiliary cell EMPTY, 4 080 lb in the main cells (was Center2 full + 3 150 lb).
- Predicted CG (G weights): full internal ≈ 0.4 %, test standard 4 080 lb ≈ 8.7 % (was 9.6 %), 50 % ≈ 11.8 %, 20 % ≈ 17.5 %,
  zero fuel ≈ 22 % MAC -> aft travel with fuel burn as the real aircraft; the test standard moves only ≈ 1 % MAC.
- Regression plan: CG at the fuel states (CG_PERCENT), trim-hold check, T3-D takeoff (incl. new climb-out), T3-A/F/G
  deceleration, B6 climb, B7 clean (elevator-limited α), T3-L approach trim + F3 landing; low-fuel approach (20 %) as a
  new check (CG ≈ 17.5 %: trim and stability).

## 2026-10-30: regression after the CG rework (Build All + FULL restart)
- **CG in the sim** (CG_PERCENT): full internal 0.85 %, test standard 4 080 lb main cells 9.23 % (was 9.56 %), 50 % 12.35 %,
  20 % 18.08 %, zero fuel 22.65 % MAC (desk 0.4 / 8.7 / 11.8 / 17.5 / 22) -> aft travel with fuel burn ✓. Pitfall: setting all
  tanks to 0 for the zero-fuel point flamed the engine out (N1 9 %, first takeoff attempt "90 s without liftoff") ->
  ENGINE_AUTO_START.
- **T3-D** (..._T3D_takeoff_cg.csv): liftoff 170 kt after 2 664 ft, NO bounce this time (FM 177.6, -4.3 %) ✓. pete: "it
  oscillates a lot on takeoff" -> climb-out pitch limit cycle 1° <-> 21° (≈ 1.5 s): the airborne loop of the new
  hand-flown climb-out runs at only ≈ 1.3 Hz; gains 400/150 too high (already ±3° in the first climb-out run). Gains
  -> 200/60: ..._T3D_takeoff_cg_gains.csv pitch 9 -> 15° smooth, no oscillation, liftoff 170 kt ✓ (a few seconds at
  10-20 ft before the climb builds - sluggish but within the gear limit).
- **T3-A/F/G** (..._T3AF_decel_cg.csv, 16 500 ft): T3-G -0.02° + 1.08 α (identical) ✓; T3-F mean 1.03 (0.97/1.05/1.08/1.03)
  ✓; T3-A largest band -0.031 (tolerance 0.03; ISA run -0.028, S12 -0.032 - same scatter) ✓.
- **B6** (..._B6_climb4500_cg.csv): first attempt aborted (pitch 23°): set_pos gave 223 instead of 185 KIAS -> config_test.py
  climb/level now has an idle pre-phase until IAS ≤ target + 5. Retry: **+982 ft/min** at 181 KIAS (ISA run +905; FM
  850-1 000) ✓.
- **B7 clean** (..._B7_clean_cg.csv): α max 16.2°, mush below ≈ 185-188 KIAS - unchanged ✓.
- **F3 landing** (no chute): landing 16 TD 174/175 KIAS ✓, approach α 3.6°, trim unchanged; **ground roll 3 955 ft ->
  scaled 3 580 vs. 3 130 = +14 %**; landing 17 with a firmer nose-down push (10 000; the elevator only goes from -4.2° to
  the -5° stop) 4 238 ft -> +24 % -> push reverted. Before the CG change: landings 12/15 +9.4/+9.1 %. Rollout bands
  (simlog only 2 points per 20 kt) show the same 12-15 ft/s² mid-roll; the difference sits in the first seconds after
  touchdown (160-180 kt band 8.6-9 ft/s², nose slightly up). **F3 ◐ open**: either the CG shift changed the gear load
  split (static pitch on the runway 0.8° vs. 0.4° before) or it is run-to-run scatter -> investigate with a
  high-rate rollout log (brake force, gear loads, pitch) before any change.

## 2026-10-30: F3 ground roll investigation - the "+14 %" was skipping after touchdown, not braking
- New `tools/rollout_log.py` (13 SimVars, ≈ 2 Hz, only below 500 ft AGL; gear compression via CONTACT_POINT_COMPRESSION:n
  reads 0 - not usable in this form). Landing 18 (..._T3L_landing18_*): first touch 175 KIAS at 22-60 ft/min, then
  **two skips** (≈ 3.5 s airborne, ≈ 1 000 ft) before the final touchdown at 164 KIAS. Ground roll from the FINAL
  touchdown 3 025 ft -> scaled (166.5/164)² **-0.3 %** ✓; mid-roll deceleration 12-15 ft/s² as before. The old evaluation
  counted from the first touch (+15 %). The CG change only moved the nose-gear load share from 12.3 to 12.6 % - not the cause.
- `landing_test.py`: ground roll now from the final touchdown (reset while airborne), skips counted and reported.
  Landing 19: 3 skips, 2 717 ft from 159 KIAS -> **-4.8 %** ✓. High-rate log: porpoising pitch +4.8 <-> -2.4° (≈ 1 s) right
  after the touch - triggered by the script's instant nose-down push (-4.2°, near the 5° stop) at ≈ 175 kt.
- Fix (technique, not cfg): nose-down push ramped over 3 s, wheel brakes only once the nose is down (pitch < 1°, FM).
  Landing 20: **1 skip** (2.3 s), 2 853 ft from 161 KIAS -> **-2.6 %** ✓. Remaining skip: first touch at 174 KIAS with
  22 ft/min and 0.9-1.7° pitch, the nose rises to 4.4° after the main-gear contact and the wing (LAND flaps) still flies.
- **F3 ✓** (-0.3 / -4.8 / -2.6 % with the corrected measurement). Open (separate item): touchdown dynamics - flare too soft
  (≈ 20-60 ft/min) and the nose-up after main-gear contact; candidates: flare target sink (≈ 150-250 ft/min), gear
  spring/damping (compression ratio 1.5, damping 0.7 [S]), main-gear x position vs. the corrected CG.

## 2026-10-30: touchdown skip and takeoff rotation - findings, open items
- **Touchdown** (landing 20, simlog): during the flare the controller PULLS (elevator +1.0..1.5°); after the first touch
  at 174 KIAS / 22 ft/min the jet floats up to 7 ft for ≈ 5 s (VS +75..+170 ft/min) before the final touchdown at 158 KIAS.
  Lift at 174 KIAS with LAND flaps in ground effect still carries the jet: `lift_coef_ground_effect_mach_table` is the SDK
  template value (≈ ×1.08 lift at M 0.26) - unvalidated for the F-104 (low aspect ratio), no source yet -> not changed.
- Flare target -150 -> **-250 ft/min** (landing 21, ..._T3L_landing21_*): TD 178 KIAS at 279 ft/min, still 1 skip; ground roll
  from the final touchdown (173 KIAS) 3 448 ft -> scaled **+2 %** ✓. Even a firm touchdown skips -> gear spring/damping
  [S] (compression ratio 1.5, damping 0.7) and/or the template ground effect are the candidates (open, needs a source or
  a dedicated test: drop/touchdown test at fixed sink rates).
- **Takeoff rotation** (pete: "pulls too early and too hard"): FM 2-20/6-5 back stick 20-25 kt below takeoff speed, nose wheel
  lift-off 10-20 kt below, attitude ≈ 5°, "fast stick input = dynamic overshoot, nose may fall back". The script (feed-forward
  5000 + attitude ramp 3°/s from 157 kt) overshoots (8.9° at liftoff with 5° commanded) and the jet often lifts at ≈ 170 kt,
  touches again and lifts for good at 185-191 kt. Trial 3000 + 2°/s (..._T3D_takeoff_softrot.csv): same overshoot on the ground
  (5.3° at 2.8° commanded), weak climb-out (5-7° pitch at 5-7 ft up to 230 kt) -> reverted. Note: with the calibrated TAKEOFF
  flap lift the sim cannot lift off at a 5° attitude below ≈ 200 kt, so the FM "≈ 5°" is probably a different reference
  (attitude indicator / initial rotation). **Open: redesign the rotation as a pitch-rate command (≈ 2°/s) with a proper
  build-up**, then re-check T3-D (liftoff speed, no bounce) and D1b.
- **Pitch-rate rotation, first try** (..._T3D_takeoff_qrot1.csv, now option `qrot`, NOT default): the nose rose ≈ 6°/s at
  164-169 kt, the P term on the rate error PUSHED (cmd +1 600), pitch fell 5.1 -> -0.8° right after the first liftoff at 169 kt;
  the climb-out fallback (pitch < 0°) handed over to the trim-based AP at 4 ft AGL and set the elevator to 0 -> the jet
  bounced along the runway at 180-230 kt (sustained liftoff 203 kt after 3 747 ft) and drifted off the centreline (pete:
  "neben der Piste"). Recovered by the AP climb (no damage). Fixes: default back to the old attitude rotation; fallback only
  above 100 ft AGL. Lesson: a new takeoff control law needs a build-up first (e.g. a high-speed taxi run with the rotation
  only up to nose-wheel lift-off and throttle idle, or the law tested in the air at the same speed with gear/flaps down).
- **Taxi build-up for rotation law v2 FAILED - live testing stopped** (..._T3D_taxi_qrot2.csv): (1) `runway_start` put the
  jet down at 273.1° true instead of 263.4° (cause unknown - new gear-first/settle code or the set_pos heading; the takeoff
  script holds the heading found at brake release -> it rolled diagonally, pete: "du rollst schief weg"); (2) the rotation
  law v2 reached 3.9° at 167 kt (taxi end criterion), but the stop routine did not keep the jet on the ground: airborne at
  ≈ 170 kt, pitch up to 28° at idle, then -9.8°, hard touchdown, heading 25° off, stopped at 48.3461 N 11.7809 E, heading
  299° (probably off the runway), gear 100 %, engine idle, no crash flag. To analyse OFFLINE before any further sim test:
  the runway_start heading, why the pitch rose after the taxi-end (elevator command/sign in the stop loop, trim 5° at idle
  ≈ 170 kt), and a safer taxi criterion (stop at nose-wheel lift-off speed - 15 kt, not at 3° pitch).
- Offline analysis and script fixes (not yet flown): (a) the taxi stop routine ramped the elevator from 0 to a push over
  3 s - with the 5° nose-up takeoff trim and TAKEOFF flaps at ≈ 170 kt neutral elevator is enough to lift off and pitch up
  -> the stop now holds 0° pitch actively (3 000 + 2 500 per degree, up to the full nose-down stop); (b) takeoff_test.py
  uses the runway heading 263.4° as reference and refuses to start if the jet is more than 2° off (the 273° placement
  remains unexplained). Next session: re-run the taxi build-up only after reviewing these changes; criterion taxi end
  ≤ 165 kt.
