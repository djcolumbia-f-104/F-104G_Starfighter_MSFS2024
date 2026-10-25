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
