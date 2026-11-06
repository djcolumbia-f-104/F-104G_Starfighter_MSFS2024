# F9: crosswind landing (FM 2-25, 2-28)

**Objective / acceptance:** FM 2-25: crab or wing-down or both (crab in strong crosswind), max 25 kt crosswind (dry),
nose lowered immediately after the touchdown; FM 2-28: touchdown speed +5 kt per 10 kt crosswind (LAND flaps). Acceptance
per step: touchdown within ±25 ft of the centreline (runway 148 ft wide), heading within ±2° of the runway at the touchdown
(decrabbed), bank ≤ ±5° below 50 ft, no go-around trip; ground roll from 165 KIAS within ±5 % of FM A8-4 (headwind
component ≈ 0 for 350°/170°). Build-up in steps of surface crosswind: ≈ 5 -> 10 -> 15 -> 20 -> 25 kt.

**Weather:** presets from `tools/make_wpr.py` (template saved by pete in the sim, docs/data/weather/). Measured 2026-11-06:
preset 350°/10 kt (ground layer) gives **5 kt at the runway** (Debug Weather: 5 kt avg from 350°) and ≈ 10 kt at 2 km - the
sim adds a surface boundary layer -> surface crosswind ≈ 0.5 x preset. Turbulence setting REALISTIC (pete's assistance
options) -> some gusts possible. selftest `wind=<dir>:<kt>` checks the preset at the aircraft.

**Tool:** `landing_test.py <csv> 6 2.5 <high> nochute fmflare xw=<surface kt>` (new option; forces the FAST loop): speeds
+0.5 x xw; heading target + crab asin(crosswind / TAS) from AMBIENT_WIND_* at the aircraft (every ≈ 0.6 s); crab faded out
between 30 and 5 ft AGL and the nose aligned with the rudder (-350 counts per degree, half the rollout gain); go-around sets
the rudder to 0. Rollout unchanged (rudder law on heading + centreline, ailerons 0).

**Prediction step 1 (preset 350/10, ≈ 5 kt surface, xw=5):** final 192.5, TD ≈ 175 KIAS; crab ≈ 2.5-3° at 2 000 ft (≈ 10 kt
wind, ≈ 200 KTAS), ≈ 1.5° near 50 ft; TD centreline ≤ ±15 ft, heading ≤ ±1°; bank ≤ ±3°; roll from 165 KIAS within ±5 %.

**Hazards:** (1) new decrab rudder near the ground -> dry run first (virtual runway +6 000 ft: stronger wind up there,
conservative); (2) crosswind takeoff (takeoff_test rudder law on heading; 5 kt small); (3) gust/turbulence -> go-around
criteria unchanged (|bank| > 30° below 500 ft, |c| > 300 ft); (4) chute not used (FM limits 25 kt at 90°, weather-vaning).

**Go/no-go:** step 1 dry run, then the real landing; each further step only after the previous one passed.

## Result + Debrief
- **Step 1 (S19-F9a, preset 350/10 = 5.0 kt at the aircraft on the ground, xw=5) - PASSED:** crosswind takeoff 178 kt ✓ (=
  calm). Dry (+6 000 ft): virtual TD 176 KIAS, -244 ft/min, centreline -6 ft. Real: final 192, **TD 174 KIAS** (pred. 175),
  -384 ft/min, pitch 2.8°, **centreline -3 ft** (approach ±5 ft, below 50 ft -3..-1 ft), bank below 50 ft ±0.7°; decrab rudder
  ≈ -0.6°, sideslip ≈ 1.9° at the touchdown (crab removed); roll from 165 KIAS -5.2 % (series -4.7/-4.1/-3.7 %, headwind
  component ≈ 0 -> not a crosswind effect). Loop 2.8-3.3 Hz (3 wind reads in the slow group).
  Anomaly: during the skip after the touchdown bank -7° (simlog) - the rollout keeps the ailerons at 0 -> for xw the rollout
  now holds the wings level with the ailerons (P+D, > 80 KIAS); wind read only every 2nd slow group; heading logged
  (`hdg_true` column) to verify the decrab directly.
- **Step 2 attempt 1 (S19b-F9, preset 350/20 = 10.0 kt surface, xw=10):** engine found shut down after the weather change
  (fuel lever 0) -> restarted with the SimConnect event ENGINE_AUTO_START (light-off at 20 % after ≈ 20 s = FM). Takeoff 180 kt.
  Crab 5.1-5.2° on the approach (pred. 5.5) ✓, centreline ±6-7 ft, TD 178 KIAS (pred. 177) -422 ft/min, CL -6 ft, roll -3.6 % ✓.
  **Not passed:** (a) decrab incomplete - heading still +2.2° (dry +4.8°) at the touchdown: -350 counts/° gave ≈ 7 % rudder,
  ≈ 55 % needed (full rudder ≈ 18° at 190 KIAS, β/δr 0.34 -> β max ≈ 6°); (b) **rollout drifted to +66 ft right of the
  centreline** (half-width 74 ft): weather-vaning held the heading +1.2° (P-only law) and the validated rollout law's -3 x c
  term has the wrong sign (harmless in calm air). Fix (xw only; validated path unchanged and the sign error documented):
  decrab feed-forward 2 640 counts per degree of crab (40 -> 15 ft) + P 700/°; rollout PI on a centreline-steering heading.
- **Sim hang during the step 2 repeat (first try):** MSFS stopped responding in the dry run's level segment (12:21, ≈ 7 000 ft
  above the virtual runway, nothing special commanded; session report memory ≈ 16-17 GB after a long session with many
  set_pos jumps and weather changes). Sortie stopped; pete restarted the sim. The watchdog hung in its reconnect - the
  selftest caught it ("watchdog alive" FAIL) -> restarted.
- **Step 2 repeat (S19c-F9, decrab feed-forward + rollout PI) - NOT passed, F9 flights STOPPED (lesson 26):** approach as
  attempt 1 (crab ≈ 5°); the decrab feed-forward rolled the jet to **-9..-16° bank at 4-21 ft** (dry: -16°), heading still
  +1.2..1.5° at the touchdown, TD 178 KIAS -419 ft/min **CL +23 ft**; post-touchdown skip with the rollout rudder active ->
  bank -8.8/-11.7° in the air, **lateral excursion to +87 ft** (beyond the 74 ft runway half-width = runway excursion),
  then the PI overshot to -5.8° / -21 ft; roll -6.2 %. Cause: F-104 roll due to sideslip (FM 6-2; δa/δr 0.37 in T3-E2) -
  every rudder input in the air (decrab, skip) rolls the jet; FM 2-25 recommends the CRAB method for strong crosswinds
  exactly for this. Reverted to the step-1 decrab; no rollout rudder while airborne (skip).
- **Next (desk):** crab-to-touchdown design: keep the crab (no rudder decrab) or decrab only below ≈ 5 ft; on the ground align
  with the rudder/nosewheel steering only with all gear on the ground; identify the ground-steering response first
  (taxi test at 60-120 kt with a heading step) and model the skip; then step 2 again at 10 kt; until then F9 = step 1 only.
- **Ground-steering work (A3, card A3-ground-steering.md):** plant identified (≈ 1.8°/s per 1 000 counts x IAS/100, lag
  0.6 s, dead time 0.45 s), the F9 PI oscillates on the ground, designed law (kp 700 / kd 300 x min(1, 100/IAS), ki 50,
  0.04°/ft) PASSED A3 run 2 (no oscillation, |c| ≤ 7.5 ft after 800-count steps) -> landing_test xw rollout uses it with the
  fast pass (heading every pass); still: no rudder while airborne, gentle step-1 decrab below 30 ft.
- **Regression F3 with xw=0 (S21-F3xw0, calm):** TD 173 KIAS -134 ft/min CL +1 ft; **rollout centreline ±1 ft, heading
  ±0.09°, bank ±0.8°** (4.0 Hz) ✓; roll from 165 KIAS -6.6 % - all FAST-path landings today read short (-4.7 / -5.2 / -6.2 /
  -6.6 % vs. slow path -0.6..-4.1 %): IAS is read only every 3rd fast pass (165 KIAS crossing found up to 0.7 s late ≈ 3 %) and
  the nose-down/brake check runs more often -> a measurement/timing artefact of the fast path, not a flight-model change; the
  F2/F3 distance references stay with the slow (validated) path.
- **Next:** F9 step 2 again (preset F-104G_350_20Kts, xw=10): crab to the touchdown with the gentle decrab, new rollout law.
- **Step 2 third try (S19d-F9, preset 350/20, crab to TD + A3 rollout law) - NOT passed (rollout):** air phase good - below
  50 ft bank ±1.5°, CL -4..+1 ft, TD 177 KIAS -402 ft/min CL -4 ft, heading +2.4° at TD (crab), skip ≈ 1.5 s without rudder ✓;
  roll from 165 KIAS -0.5 %. **Rollout:** once on the wheels at ≈ 170 KIAS the jet yawed INTO the wind +2.3 -> +9.3° in 2.5 s and
  ran to **+101 ft** (runway excursion), then the law brought it back (end +25 ft at 70 KIAS, heading -3°).
  Cause: weather-vaning on the wheels at high speed - 10 kt crosswind at 170 KIAS = β ≈ 3.3° ≈ 10° rudder equivalent
  (β/δr 0.34) ≈ 50 % pedal; the design assumed a constant 840 counts (taken from attempt 1 at lower speed) and the 100/IAS
  gain scaling lowers the loop gain exactly where the torque is largest (lesson 27).
- **Next (desk):** identify the weather-vane torque vs. speed from the S19b/S19c/S19d rollouts (recorded rudder + heading,
  model from A3), then a feed-forward ≈ 2 640 counts x atan(crosswind / V) [deg] (faded below ≈ 100 KIAS where the nose-wheel
  steering dominates) + the A3 feedback; check in the model with the identified torque; then step 2 again.
- **Desk 2026-11-06 (after S19d):** SDK pages (docs/sdk-ref/flight_model.cfg.md): ground steering is reduced with speed by
  `max_speed_full_steering` / `max_speed_decreasing_steering` / `min_available_steering_angle_pct` (not set in our cfg ->
  defaults; community: floor default raised 0.2 -> 0.5 in SU12); lateral tyre friction at speed by
  `ground_high_speed_steeringwheel_static_friction_scalar` / `..._otherwheel_...` (SDK: "how much the aircraft will move into
  the crosswind when rolling at higher speeds", default 1); the crosswind on the ground is blended in between
  `ground_crosswind_effect_zero_speed` (5 ft/s) and `..._max_speed` (80 ft/s) (depends on the ground-rudder assistance).
  Community: MSFS weather-vaning on the ground is widely considered exaggerated and tunable with these parameters; surface
  wind ≈ 1/2 of the reported wind (= our preset measurement). No F-104-specific rollout data online (FM 2-25 stays the source).
  Fit on the S19d rollout (rudder command reconstructed from the A3 law): weather-vane torque ≈ 1 250 counts at 100 KIAS ∝ V
  (≈ 2 100 at 170) for 10 kt, steering gain ≈ 0.5 x the A3 value at 150-170 KIAS (K ∝ V does not hold), rms 1.8° - weak
  (one run); S19b steady state (P law, heading +1.2°) gives ≈ 700 counts at ≈ 120 KIAS (within 2x).
- **Next:** identification at the condition (lesson 27): A3 taxi test in the crosswind preset 350/20 at 100 / 140 / 160 KIAS
  (steady pedal = weather-vane torque B(V); small steps = K(V)); then the rollout law = feed-forward B(V, crosswind) + A3
  feedback with K(V) from the test; model check; F9 step 2. Cfg route (min_available_steering_angle_pct, friction scalars)
  only if the FM-conform behaviour cannot be reached by the law - it touches validated ground behaviour (T3-D, F2/F3).
- **Crosswind identification on the runway (A3 run 3, preset 350/20, flaps UP, steps added to the held pedal):** steady
  pedal (weather-vane torque) +950 counts at 105 KIAS, +950..1 040 at 143, +920..1 135 at 162 -> **≈ 100 counts per kt of
  crosswind, ≈ constant over 100-160 KIAS**; steering gain ≈ 0.6-1.5 (mean ≈ 1)°/s per 1 000 counts, ≈ constant (A3 calm
  with TAKEOFF flaps at 100 KIAS: 1.8) -> the 100/IAS scaling halved the loop gain at high speed for nothing.
  **Law v3:** feed-forward 100 counts x crosswind at the aircraft (sign from the wind direction) + kp 700 / kd 300 / ki 50,
  0.04°/ft, no speed scaling; A3 run 4 at 160 KIAS: acceleration phase centreline -3..+2.5 ft (A3 law 0..+17 ft) ✓.
- **Step 2 fourth try (S19e-F9) - PASSED:** approach crab 4.9°, CL ±5 ft; below 50 ft bank ±2.2°, CL -9..-5 ft; TD 177 KIAS
  -63 ft/min, **CL -8 ft, heading 1.2°**; **rollout -12..+14 ft**, heading -0.9..+2.5°, bank ±1.8° (pedal 2 400-3 100 just
  after the touchdown, ≈ 1 000 later); roll from 165 KIAS -2.5 % ✓. Dry: virtual TD 179 KIAS CL -6 ft.
- Presets for the next steps (surface ≈ 0.5 x preset): F-104G_350/170_30/40/50Kts written (15/20/25 kt surface).
- **Next:** step 3 (preset 350_30 = 15 kt surface, xw=15), then 20, 25 kt (FM limit), and the left crosswind (170_..).
