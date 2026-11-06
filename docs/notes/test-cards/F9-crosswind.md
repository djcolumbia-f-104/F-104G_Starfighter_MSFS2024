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
- **Step 2b (S19f-F9, preset 350/25 = 12.5 kt surface, xw=12.5) - NOT passed (rollout):** crosswind takeoff 177 kt ✓; air:
  crab 6.4°, below 50 ft bank ±1.2°, TD 179 KIAS -373 ft/min CL -20 ft, heading 3.2° (dry: 5.4°); roll from 165 KIAS +0.8 %.
  After the skip (≈ 1.5 s, rudder 0) the jet, back on the wheels at 175 KIAS with heading 3.8°, yawed right to 8° in 2 s
  although the law commanded 4 000-7 600 counts nose left - the simlog confirms the rudder followed (-8.8°, nose left) ->
  rollout +55 ft (runway edge 74 ft). The steady weather-vane torque of the taxi runs (≈ 1 250 counts) is 6-7x too small to
  explain it.
  **Hypothesis (desk next):** ground directional divergence after a crabbed touchdown ("wheelbarrowing"): the main gear is
  only ≈ 1.8 ft behind the CG (cfg point.1 x = -0.3 ft vs. CG ≈ +1.5 ft at 9 % MAC; old note: "check the main-gear x against
  the corrected CG") while the loaded nose wheel 12.6 ft ahead gets a large side force from the crab angle. Check the main
  gear station against CR-2144 Fig. III-2 / the FM three-view; test: taxi run at 150-170 KIAS with a commanded heading offset
  (step 4-5°) in calm air to see whether the heading diverges; possible cfg question (main-gear x, nose-wheel steering /
  ground friction parameters) under change control (T3-D, F2/F3 regression). Until then: F9 passed up to 10 kt.
- **Desk check of the hypothesis:** the main-gear station x = -0.3 ft was MEASURED on the CR-2144 three-view (F-104A, scale
  checked with two references, docs/flight-model-values.md) -> the short main-gear-to-CG distance (≈ 1.8 ft) is most likely
  real (the F-104 rotates very easily about the main gear). Geometry is probably not the error. More likely technique:
  after the skip the pedal is 0, so the nose wheel lands pointing along the body while the jet moves along the runway with
  3-4° crab -> nose-wheel side force on a 12.6 ft arm turns the jet further out (wheelbarrowing), the speed-reduced NWS cannot
  stop it. Options (desk, model first): (a) combined method per FM 2-25 - partial decrab with wing-down (bank into wind)
  so the remaining crab at the touchdown is ≤ 1-1.5° without the large rudder-induced roll (lesson 26); (b) align the nose
  wheel with the track before the nose touches (pedal ≈ crab x NWS gearing, only on the main wheels, rudder in the air rolls!);
  (c) check the MSFS nose-wheel steering/friction defaults (`min_available_steering_angle_pct`, high-speed friction
  scalars) - cfg change under change control. F9 remains passed up to 10 kt.
- **A3 run 5 (calm, heading offset 3° at 150 KIAS, LAND flaps): benign** (≈ 500 counts hold it) -> the divergence needs the
  touchdown mismatch (crab vs. track) + a loaded nose wheel. **Change (xw only, one variable):** rollout nose push +1 500
  instead of +4 000 above 120 KIAS. Test: 12.5 kt again (S19g). Prediction: heading after the touchdown ≤ 5°, rollout within
  ±30 ft; if it still diverges -> the decrab/wing-down route (reduce the crab at the touchdown).
- **S19g (12.5 kt, push +1 500 above 120 KIAS):** TD 178 KIAS CL -9 ft heading 3.0°; **rollout -12..+1 ft**, heading
  -0.7..+3.2°, pedal ≤ 2 400 (S19f: +55 ft, 7 600) -> hypothesis confirmed (loaded nose wheel after a crabbed touchdown).
  Side effect: roll from 165 KIAS -16.9 % (more weight on the braked main gear).
- **S19h (12.5 kt, +1 500 only for 4 s after the touchdown, then the validated +4 000) - lateral PASSED:** TD 178 KIAS CL -19 ft
  heading 3.6°, below 50 ft bank ±2.8°; **rollout -19..-4 ft**, heading -0.7..+3.6°, pedal ≤ 3 800; roll from 165 KIAS -11.6 %
  (the 165 KIAS point lies inside the light-push window; fast-path reading -2..-3 %).
  The ground roll in a crosswind is technique-dependent (nose-wheel load vs. braked main gear) and the FM charts have no
  crosswind correction -> informational for F9. **Open question for F2/F3 (change control):** FM 2-25 says only "Nosewheel -
  Lower"; the validated pair "+4 000 push + toe_brakes_scale 0.82" may be compensating - with a lighter, more realistic nose
  load the brake scale would have to be lower. To check with a dedicated F3 series (push 1 500 vs. 4 000) before any change.
- **Status F9:** right crosswind passed up to 12.5 kt surface (5 / 10 / 12.5). Next: 15 / 20 / 25 kt (presets 350_30/40/50),
  then the left side (170_..).
- **15 kt surface (S19i-F9, preset 350/30, xw=15) - PASSED:** crosswind takeoff 177 kt; approach crab 7.6° (dry 7.8°); below
  50 ft bank ±4.1° (limit ±5°), CL -12..+11 ft; TD 179 KIAS -389 ft/min **CL -12 ft, heading 3.8°**; **rollout -18..-7 ft**,
  heading ≤ 4.1°, bank ±3.6°, pedal ≤ 3 600; roll from 165 KIAS -8.0 % (informational).
- **20 kt surface (S19j-F9, preset 350/40, xw=20) - PASSED (marginal):** crosswind takeoff 176 kt; approach crab 9.9° (dry 10.0°);
  below 50 ft bank ±2.7° (dry -3.2..+7.0°), CL -24..-17 ft (drift to the downwind side as the crab is faded and the surface
  wind drops); TD 181 KIAS -412 ft/min **CL -24 ft** (limit ±25), heading 5.3°; **rollout -25..-7 ft**, heading ≤ 6.7°, pedal
  ≤ 5 800; roll from 165 KIAS -12.3 % (informational). Improvement candidate: integral on the cross-track in the localizer
  loop / less crab fade near the ground.
- **25 kt surface (S19k-F9 + S19k2-F9, preset 350/50, xw=25, FM limit) - plan:** prediction from the 15/20 kt trend: crab ≈ 12.5°,
  TD CL ≈ -30 ft (downwind drift), heading ≈ 6-7°, pedal ≈ 7 000. Hazards as 20 kt + takeoff in 25 kt (takeoff_test heading law,
  20 kt flown with 176 kt liftoff on the centreline). Split sortie: S19k = takeoff + dry run; the real landing (S19k2) only if the
  dry run is clean (virtual TD |CL| ≤ 30 ft, bank below 50 ft within ±5°). **GO** (selftest ALL OK, 25.0 kt from 350° at the
  aircraft, fuel 3 826 lb).
- **25 kt S19k - NOT passed (takeoff):** the PD heading law (700/400, no feed-forward, no integral) weather-vaned the jet to
  -10.2° at 176 kt (just after the first liftoff, touch-back) -> heading abort (idle + parking brake at 176 kt) -> the jet
  turned into the wind and stopped beside 26L on concrete, undamaged (screenshot ..._S19k-F9_takeoff_abort.png). Warning sign
  missed: the takeoff heading error at liftoff was already -4.6° (15 kt) and -6.5° (20 kt) - a passed step close to a script
  limit was not extrapolated (lesson 29). Torque fit on the S19h/i/j/k takeoff rolls (heading rate x 1 000 counts/(°/s) +
  pedal): ≈ 55-75 counts per kt up to 110 KIAS, 95 at 130, ≈ 135-140 at 150-170 (5° takeoff trim unloads the nose wheel;
  above 160 KIAS the rotation removes the nose-wheel steering). **Fix: takeoff_test option `xw`** - feed-forward
  min(150, 70 + 1.6 x (IAS-110)) counts/kt x measured crosswind + the PD law + integral 50 counts/°s (±40 °s), rudder
  limit 12 000, rudder faded to 0 in 1 s after the first liftoff, heading abort only below vr and then the gentle stop with
  the same law. Default path unchanged. Desk replay (crude model, not for tuning): PD 4.7° (flight 10°), xw 0.7°.
  **Build-up:** `takeoff_test.py ... taxi xw` (srot rotation from vr to pitch 2.5° / 165 KIAS, then idle stop) at 25 kt.
  Prediction: heading error ≤ 2° over the whole roll and the stop. GO after a clean runway_start (jet back on 26L).
- **xw takeoff law build-ups (25 kt, taxi to 165 KIAS / pitch 2.5°, then idle stop):** S19l (v1): heading -2.8° at vr,
  -4.3° at 169; S19l2 (v1 + new cross-track column `xt` from lat/lon, every 4th pass): **xt +17 ft at vr, +27 ft at 164 KIAS**
  (upwind side, the nose turns into the wind); S19l3 (v2: feed-forward min(200, 70 + 2.5 x (IAS-110)) counts/kt, PD x 1..2 from
  110 to 160 KIAS): -2.15° at vr, xt +14 / +22 ft, pedal 9 400 at 164 KIAS - doubling the pedal above 140 KIAS buys little.
  **Slow-taxi probe (2026-11-06):** GEAR STEER ANGLE PCT at pedal 8 000 (49 %) = 22 % at 17 kt, 9.8 % from ≈ 21 kt on
  -> the sim reduces the nose-wheel steering to ≈ 20 % of the commanded angle above ≈ 20 kt (max_speed_full_steering /
  max_speed_decreasing_steering / min_available_steering_angle_pct are NOT set in our cfg = engine defaults; real F-104:
  hydraulic steering, no speed schedule in the FM). Open item (needs a source for the F-104 steering + regression F2/F3/F9/A3).
  Prediction for the real takeoff with `xw`: xt ≈ +30..+50 ft at liftoff (rotation without steering), no heading abort.
- **S19m-F9 (25 kt, part 1) - takeoff with `xw` PASSED:** liftoff 178 kt after 2 792 ft (FM-normal), heading -2.15° at vr,
  **xt +21 ft at vr, +46 ft at liftoff** (prediction +30..+50 ✓), pedal up to 12 000 during the rotation, after the liftoff the
  jet weather-vaned to -19° (crab for the 50 kt wind aloft) - no abort, climb-out and AP handover normal. **Dry run** (virtual
  runway +6 000 ft, wind there 50 kt): crab 12.6-13.1°, CL -10..+4 ft above 50 ft, virtual TD 185 KIAS -493 ft/min **CL -15 ft**;
  bank while the crab is faded below 25 ft up to **+8.8° at 6 ft** (my dry-run criterion ±5° NOT met). Reason: aloft the wind
  does not drop, so the fade removes 13° crab instead of ≈ 7° near the real ground (20 kt: dry +7.0°, real landing ±2.7°).
  **GO for the real landing (S19k2)** with this documented exception; abort/go-around criteria in landing_test unchanged.
- **S19k2-F9 (25 kt surface = FM limit, real landing) - flown, landed on the runway, NOT passed (CL):** approach crab 10.3-14.1°
  above 300 ft, 5.8-11.8° in 50-300 ft (the wind drops 50 -> 25 kt through the boundary layer); **bank -14.4° at 182 ft /
  +13.1° at 120 ft** (15 kt: -6.9/+5.2, 20 kt: -3.3/+5.3) = the crab target follows the falling wind and the localizer loop
  chases it; below 50 ft bank -5.0..+3.9° (limit ±5, edge), CL -39..-12 ft; **TD 183 KIAS -306 ft/min, pitch 2.7°, CL -39 ft**
  (limit ±25 ✗), 1 skip; rollout -41..-3 ft (runway half-width ≈ 98 ft), heading ≤ 8.7°, pedal ≤ 6 350; roll from 165 KIAS
  -8.4 % (informational). Debrief: the dry run (constant 50 kt aloft) cannot show the wind-gradient part (crab target
  falling 14 -> 7° between 300 and 50 ft) - that was the cause of the bank swings, not the fade below 30 ft.
  **Next (desk, lesson 26 rule: no re-fly after a failed point without a design):** crab target from a low-pass filtered
  / rate-limited wind (≤ 1°/s), cross-track integral in the localizer loop for the downwind drift (15/20/25 kt: TD CL -12/-24/
  -39 ft, all to the downwind side); check with the S19i/j/k2 logs; then 25 kt again. Left crosswind (presets 170_..) after.
- **Status F9 (right crosswind):** 5 / 10 / 12.5 / 15 kt PASSED, 20 kt PASSED marginal, 25 kt flown safely but CL -39 ft ✗.
  Crosswind takeoff: `takeoff_test.py ... xw` needed from ≈ 20 kt (PD law alone: abort at 25 kt).
- **Desk analysis S19k2 + new landing_test option `trk` (2026-11-06):** true crab from the log (heading - track from Δcross/
  Δalong over 2 s) = 13.4° at 680 ft -> 10.5° at 250 ft -> 8.2° at 110 ft -> 6.9° at 20 ft; the track error stayed within ±1-2°,
  i.e. the wind-derived crab was good, but the localizer (heading target HDG + crab - 0.05 c) has no drift feedback: 1.5° track
  error for 4 s = 35 ft (+5 -> +35 ft between 177 and 109 ft); below 55 ft the crab fade + decrab turned the track to -0.4..-1.0°
  -> c -9 -> -39 ft at TD. **`trk`** (with xw=): crab measured = heading - ground track (VELOCITY_WORLD_X/Z, low-pass 1 s) ->
  heading target HDG + crab_m - 0.05 c = a track loop (track -> HDG - 0.05 c, drift feedback built in); no crab fade (crab method
  to the TD, gentle rudder decrab below 30 ft unchanged); bank target ±5° below 50 ft. Channel cross-check: CSV columns
  crab_m (measured) vs. crab_w (wind-derived) must agree within ≈ 1° in the dry run (constant wind). Prediction real landing:
  TD |CL| ≤ 15 ft, bank in 50-300 ft ≤ ±6°, TD heading ≈ 6-7° (crab kept), rollout as S19k2.
  Hazards: (1) bad track read -> wrong crab -> guarded (|v| > 100 ft/s, jump > 30° rejected, clamp ±30°); (2) no fade = larger
  crab at TD (≈ 7° vs 5-6°) -> the xw rollout law handled 8.7° in S19k2; (3) bank limit ±5° below 50 ft could leave drift
  uncorrected -> go-around criteria unchanged. Build-up: takeoff xw + dry run (S19n), real landing S19n2 only if crab_m ≈ crab_w,
  virtual TD |CL| ≤ 20 ft and bank below 50 ft ±5°.
- **S19n (takeoff xw 179 kt ✓) + trk dry run:** channel cross-check crab_m - crab_w = 0.0 ± 0.1° above 50 ft ✓ (-1.9° below
  30 ft = the decrab sideslip, as expected for a measured value); CL -8..+6 ft above 50 ft (S19m without trk -10..+4 / -22 at TD),
  bank ±1.3° in 50-300 ft, virtual TD -6 ft; but bank -8.9° at 10 ft: the decrab rudder (13° crab aloft -> 4 550 counts) rolls
  right (rudder rolling moment). -> pedal limit 2 500 with trk. **S19n3 dry repeat:** virtual TD 186 KIAS **CL -14 ft**, bank
  -1.4..-2.0° down to 28 ft, then -6.9° at 10 ft (bank target clamp -5° + overshoot while the track loop corrects 7 ft of drift in
  the flare). **GO for S19n2** (real landing): CL criterion met, bank exceeds ±5° by ≈ 2° only in the dry run's doubled wind.
- **S19n2-F9 (25 kt, real landing with `trk`) - TD ✓, rollout ✗:** crab_m tracks crab_w within ≈ 0.3° above 50 ft (real wind
  gradient: crab 13.2 -> 8.7 -> 6.6°); CL -11..+26 ft above 300 ft, -8..+14 ft in 50-300 ft, **-9..+2 ft below 50 ft**; bank
  -7.1..+9.2° above 300 ft, -9.3..+7.4° in 50-300 ft (prediction ±6 ✗; S19k2 ±14), -6.4..+2.4° below 50 ft (limit ±5, ≈ 1.4°
  over); **TD 184 KIAS -389 ft/min, pitch 1.9°, CL -4 ft** (S19k2 -39), heading 7.7°; then a skip (pitch 4.1°, bank -5.7°,
  ≈ 3 s with no rollout rudder while airborne) with 8-9° crab -> +18 ft, the rollout law aligned the jet but it ran on to
  **+55 ft** and overshot to -30 ft (rollout -30..+55, runway half-width ≈ 98 ft), heading ≤ 10.2°, pedal ≤ 8 600; roll from
  165 KIAS -10.4 %. Debrief: `trk` fixed the air part (TD CL -39 -> -4 ft); keeping the full crab moves the problem to the
  touchdown skip: every 25 kt landing skipped once (S19k2, S19n2), and a skip with 8° crab drives the jet sideways
  ≈ 40 ft/s. **F9 25 kt = flown safely twice, NOT passed (rollout +55 ft).** Two failed attempts at this point -> no third flight
  without a desk design (lesson 26 rule). Candidates: (a) a firmer touchdown / no skip (the general landing skip - flare sink
  target, gear rebound; open since 2026-10-30), (b) partial decrab (≈ 50 %) with trk, so a skip with less crab drifts less,
  (c) rollout law: track-based too (align the velocity, not the heading). Also the crosswind takeoff (`xw`) is done.
