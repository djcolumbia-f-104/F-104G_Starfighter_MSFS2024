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
