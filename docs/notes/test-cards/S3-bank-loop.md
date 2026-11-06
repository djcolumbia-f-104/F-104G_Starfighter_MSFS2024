# S3-BL: bank loop for the landing variants (F6 BLC failure / F5 no-flap) - identification + desk design

**Objective:** landing_test's bank PID (KP 250 / KD 150 / KI 60 counts per °, °/s, °·s; limit ±8 000) flew the validated
LAND landings (175-190 KIAS) but limit-cycled at 210 KIAS with TAKEOFF flaps (F6 dry 1-4, lesson 20: gain changes tried
in the air made it worse). Step 1 = measure the open-loop plant (axis counts -> roll rate) at 210 KIAS / TAKEOFF flaps /
gear down at altitude; step 2 = design the loop at the desk (crossover, phase margin with the measured landing_test loop
period ≈ 0.55 s); step 3 = virtual-runway dry runs; step 4 = F6 / F5.

## Analysis (2b) - plant from the cfg (desk, before flying)
- Generated flight_model.cfg (from the SDK template, never tuned by us):
  `aileron_scaling_table = -0.524:1, -0.349:1, -0.175:0.5, 0:0.3, 0.175:0.5, 0.349:1, 0.524:1` (SDK: scale on the input
  "angle", radians) -> the deflection per count is 0.3 at small inputs, 0.5 at 10°, 1.0 from 20° -> **progressive
  plant gain ≈ 3x between small and large commands**. A PID tuned for small errors sees ≈ 2-3x the gain in a larger
  correction (bank error 10° x KP 250 = 2 500 counts ≈ 15 %) -> classic cause of a limit cycle with a nonlinear plant.
  `aileron_elasticity_table = 0:1, 100:1, 250:0.5, 1000:0.5` (q̄ psf): 210 KIAS ≈ 150 psf -> 0.84; 175 KIAS ≈ 104 psf -> 0.99.
- Roll mode (CR-2144 F/C 4: p_ss/δa = 9.56 1/s per rad at TAS ≈ 570 kt) scales ≈ with TAS: 210 KIAS at 12 000 ft ≈ 255 KTAS
  -> ≈ 4.3 °/s per ° of δa (sum of both ailerons). τ = -1/L'p ≈ 0.4 s at F/C 4 -> ≈ 0.9 s at 255 KTAS.
- **Prediction** (if the full-axis aileron is ±9.75° each in this config): 3 % -> ≈ 0.5-1 °/s, 6 % ≈ 1-2, 12 % ≈ 3-4,
  25 % ≈ 8-12 °/s; per 1 000 counts rising with the step size (≈ 1.0 -> 2.0 °/s); τ 0.6-1.2 s; td ≈ one sim/read delay
  (0.05-0.15 s). If the gain per 1 000 counts does NOT rise with the step, the scaling table does not act as assumed.
- Tool: `tools/roll_id_test.py` (new; roll_test.py stays unchanged = validated C4 tool). Fast step phase reads only the
  bank (target ≥ 10 Hz).

## Hazards
- Low speed with gear/flaps down at altitude: 210 KIAS is 25-28 kt above the TAKEOFF shaker (182-185) -> throttle PI
  holds the IAS; abort IAS < 190 -> wings level 4 s at Military, then position routine (set_pos to 500 kt).
- Elevator frozen during a ≤ 2.5 s step: pitch excursion small (bank ≤ 40°); abort |pitch| > 25°.
- Gear limit 260 KIAS: abort > 255.
- The wings-level PID between steps is the one that limit-cycled at 210 KIAS (bank ±10-24° in dry 2 with SCALED gains;
  with the ORIGINAL gains dry 1 was level) -> abort |bank| > 60° and "not wings-level within 40 s" (ends the test, data
  of the finished steps kept). Altitude 12 000 ft (≈ 10 500 ft AGL).

## Preconditions
selftest ALL OK (session start 2026-11-06), watchdog running, jet airborne on the AP, fuel ≥ 2 000 lb (refuel step).

## Go/no-go
GO 2026-11-06: tool syntax-checked; all recoveries end in the unchanged position routine; at altitude, no ground hazard.

## Result + Debrief (S9-ID 2026-11-06, logs `flighttest_2026-11-06_S9-ID_rollid.csv` + `_steps.csv`)
Run 1 aborted correctly at 190 KIAS after the first step: the throttle law was a pure integrator (40/kt/s) that wound down
to 3 000 after the set_pos overshoot (223 KIAS) -> PI with base 8 500, floor 5 000, set_pos speed IAS - 10. Run 2 complete
(209-211 KIAS, 12 000 ft, 19 000 lb, trim 7.0°, yaw damper ON, main loop 6.3 Hz, step phase 29-30 Hz):

| step | counts | aileron L/R (SimVar) | rate 0.5-1.0 s | bank change |
|---|---|---|---|---|
| ±0.03 | ±491 | ±0.50° each | 2.0-2.2 °/s | 6.4-6.8° in 2.5 s |
| ±0.06 | ±983 | ±1.00° | 3.1-6.2 | 12.6-17.0° in 2.5 s |
| ±0.12 | ±1 966 | ±2.00° | 7.6-12.0 | 33° in 2.5 s |
| ±0.25 | ±4 096 | ±4.16° | 21-31 | 41° in 1.6 s |
- **AILERON_*_DEFLECTION is LINEAR in the counts (16.6° per full axis)** - the template scaling table is not visible in
  the SimVar; the RATE per count rises with the step (4.3 -> 6.3 °/s per 1 000 counts at 0.5-1.0 s, x 1.47 ≈ the table's
  0.3 -> 0.42) -> the table acts behind the SimVar. Rate per degree δa (sum) 4.2 at the smallest step = desk 4.3 ✓.
- The rate keeps growing after the roll mode (τ ≈ 0.5 s): slow bank-driven roll acceleration (sideslip/dihedral, rudder
  free). Desk fit (`tools/bank_loop_desk.py`, rms 0.67° over 8 steps): K0 5.25 °/s per 1 000 counts, + 15 % per
  1 000 counts, τ 0.50 s, td 0.10 s, λ 0.8 1/s² (bank -> roll acceleration, destabilising).
- **Closed loop in flight (the same PID 250/150/60, but at 6.3 Hz) between the steps: 8 recoveries from 7.6-48°**, back
  within ±2° in 1.4-2.6 s, overshoot 3.5-10°, residual ≈ 5 s ringing ±1.5-6° (grows with the upset: I term + λ).
- F6 dry runs (same PID, landing_test 0.55-0.56 s pass): dry 1 ±5° limit cycle 4.9 s; dry 2-4 ±25-31° 5.5 s.
- The simple model does NOT reproduce the slow-loop dry runs (it predicts the opposite gain trend) and is only roughly
  right for the fast loop (recovery 1.7-1.9 vs 2.55 s, overshoot 7 vs 10° - the model starts the recovery at p = 0) ->
  **not used for gain tuning** (lesson 21).
**Conclusion:** the plant is as the desk analysis said (rate per degree ✓), the bank PID is adequate at ≥ 5 Hz and NOT at
the landing_test pass of 0.55 s. Fix = landing_test lateral loop at ≥ 5 Hz (bank + aileron every pass, slow navigation
reads every n-th pass), not new gains. The dry 3/4 "inner fast loop" (extra P+D bank updates between slow passes, I term
in the slow pass) is not that design and failed. Next: implement the single fast loop, desk-check it line by line, F3
regression (cfg=land, unchanged gains -> expect the validated result), then F6 dry runs.

## Step 2: landing_test FAST loop (2026-11-06) - analysis, prediction, go/no-go
- Change (tools/landing_test.py): `FAST` (default for cfg=to|up, option `fast` for land): every airborne pass reads
  altitude, bank, pitch and updates elevator + ailerons; the slow values in three groups in turn (lat/lon, AGL/IAS/on-ground,
  heading/GS/gear); AGL and along-track dead-reckoned between their reads; VS filter coefficient 1 - 0.5^(dt/0.55) (same
  time constant as the 0.5/0.5 filter of the 0.55 s pass); gear-not-down counter only on real reads. Same gains.
  cfg=land without `fast`: the old reads moved verbatim into slow_read() -> behaviour unchanged (no F3 regression needed
  for the code move; F3 with `fast` later, before FAST becomes the LAND default).
- Loop estimate: 3 reads + 1 group (1-3 reads) + 2-3 events ≈ 0.2-0.25 s -> ≈ 4-5 Hz (roll_id: 4 reads + 3 events 0.16 s).
- Prediction F6 dry (cfg=to, virtual runway +6 000 ft): pass ≈ 0.22 s; level/approach bank within ±3° (no 5 s limit cycle;
  dry 1 ±5°, dry 2-4 ±25-31°); VS tracking as dry 1; flare/virtual TD at FM speeds (TD ≈ 181 KIAS at 19 000 lb).
- Hazard: new loop timing also for the pitch loop (flare gains were tuned at 0.55 s) -> dry run only (virtual runway
  +6 000 ft ≈ 6 000 ft AGL at the virtual TD); script aborts unchanged (|bank| > 35°, pitch, speed -> go-around); after
  the run the sortie repositions to 16 500 ft.
- GO 2026-11-06: syntax checked, diff reviewed line by line, at altitude only.
- **Result F6 dry 5** (`flighttest_2026-11-06_S10-F6dry_dry5.csv`, 19 008 lb, sortie S10-F6dry, POST OK): main loop
  **5.2 Hz** (pred. 4-5); bank level ±0.5-0.7°, approach ±0.8-0.9°, flare -0.6..+1.2°, go-around -1.6..+0.7° (dry 1 at
  0.55 s: ±1.8 / -6.3..+4.5 / -6.3..+8.1 / **-43..+49°**) ✓ far inside the ±3° prediction; VS tracking unchanged (median
  error approach 74 vs 80 ft/min); centreline +1 ft at the virtual TD. **Bank-loop problem solved by the loop rate.**
- Anomaly (open, desk next): virtual TD **197 KIAS** / -456 ft/min / pitch 7.4° vs. predicted ≈ 181 KIAS (FM: TD ≥ 165 +5
  per 1 000 lb = 179.5; final 210) - flare from 148 ft at 212 KIAS, the speed target ramps to 182.5 KIAS but the FM_FLARE
  82 % N1 floor (a BLC technique) holds the thrust; with TAKEOFF flaps (less drag than LAND) the jet cannot bleed the
  speed. F6 dry 1 with the idle cut: 213 -> 192 KIAS and -926 ft/min. To decide at the desk: thrust law in the flare for
  BLC-off landings (FM 3-32 text), then dry 6, then the real F6.
- **Re-assessment of the "anomaly" (desk, 2026-11-06):** FM 3-32 (PDF 202) BLC malfunction: final ≥ 195, "touch down at
  165 KIAS minimum" (16 100 lb); FM Fig. A8-2 (PDF 549, flight test; reading calibrated on the A8-2 sample problem: LAND
  final 170 / TD 150-155 at 15 100 lb ✓) TAKEOFF flaps at 19 000 lb: final ≈ 210, **minimum** TD ≈ 180 KIAS. My prediction
  used the minimum as the target. Physically 180 is not reachable in the flare from a 210 final (dry 1 idle cut: 213 -> 192;
  a PI without the floor would stay at ≈ 91 % N1). Dry 5 (197 KIAS, -456 ft/min, pitch 7.4° = 5° below the tail-strike
  attitude) is FM-conform -> **flare law unchanged** (a trial edit removing the 82 % floor for cfg=to|up was reverted before
  flying).

## Step 3: real F6 landing (sortie S11-F6) - hazards, go/no-go
- Prediction: TD 195-198 KIAS, sink 300-500 ft/min, pitch ≈ 7.5°, centreline ±5 ft, bank ≤ ±2°; ground roll without chute
  ≈ (197/170)² x 3 150 ≈ 4 200 ft (no FM reference for TAKEOFF-flap landings; recorded only); TD ≈ 2 300 ft past the
  threshold -> stop ≈ 6 500 ft of 13 100 ft (26L).
- Hazards: (1) first REAL touchdown with the FAST loop: on-ground read only every 3rd pass (≤ 0.6 s late, the validated
  slow pass was ≤ 0.55 s) -> the flare loop may keep pulling briefly on the ground -> hop; minimised by the tail-strike guard
  (pitch > 11° below 60 ft -> go-around) and the validated rollout (slow path); recovery = go-around (flown cleanly in dry 5).
  (2) TD ≈ 197 KIAS above the chute limit (180) -> `nochute`, hard braking as in F3. (3) Weather: selftest (calm, ISA).
- Build-up done: dry 5 covered level, approach, flare and go-around with the FAST loop (lesson 14).
- **GO 2026-11-06**: selftest in the sortie, refuel before the landing.
- **Result F6 (S11-F6, `flighttest_2026-11-06_S11-F6_f6.csv`) - PASSED:** 19 008 lb, final 210 KIAS, flare at 148 ft (213 KIAS,
  -939 ft/min), **TD 197 KIAS** (FM min. 180 ✓), **-302 ft/min**, pitch 6.8° (tail strike 12.3°), 2 359 ft past the threshold,
  centreline -1 ft; bank level ±1.1°, approach ±1.3°, flare ±1.7°; 1 skip of 1-2 ft (≈ 1 s, as in F3); ground roll 3 760 ft
  from the final touchdown at 196 KIAS (pred. ≈ 4 200, -10 %; no FM reference); loop 4.5 Hz. All predictions met.

## Step 4: F5 no-flap landing (FM 3-36) - analysis, prediction, build-up
- Reference: FM 3-36 (fuel low < 3 000 lb, final ≥ 230, sink ≤ 2 000 ft/min, TD ≥ 190 at 16 100 lb); **FM Fig. A8-2 NO FLAPS
  (flight test): final 225 / TD 190 at 15 100 lb, +5 kt per 1 000 lb** -> at 16 100 lb TD 195 (landing_test's (230, 190)
  takes the FM 3-36 text value; A8-2 is used via `vtd=`).
- Weight: refuel.py 2 500 lb (new optional argument, FM "fuel low") -> ≈ 17 430 lb at the start: final 230 + 6.6 ≈ 237 KIAS,
  A8-2 TD ≈ 202 -> `vtd=202`. CG ≈ 13-15 % MAC (low-fuel approach at 15.6 % was stable, 2026-10-30).
- Expected (CL slope ≈ 0.058/° from the 19 340 lb desk number): approach 237 KIAS CL ≈ 0.47 -> α ≈ 8°, pitch ≈ 5.5°; the
  flare bleeds ≈ 15-20 kt (F6: 213 -> 197 with the 82 % floor) -> **TD ≈ 215-222 KIAS**, α ≈ 9°, pitch ≈ 8.5° (tail strike
  12.3°, guard 11°); clean shaker ≈ 211 KIAS at 17 400 lb (Fig. 6-4; module shaker α 11.3°, kicker inhibited with the gear
  down) -> TD above the shaker. Ground roll (TD ≈ 218, no chute, limit 180): ≈ (218/170)² x 3 150 ≈ 5 200 ft; TD ≈ 2 400 ft
  past the threshold -> ≈ 7 600 of 13 100 ft.
- Hazards: (1) high-α touchdown -> tail strike: guard (pitch > 11° below 60 ft -> go-around); if the dry run shows pitch
  > 10° in the flare -> raise vtd before the real landing. (2) Low fuel 2 500 lb + go-around at Maximum: ≈ 1 000 lb in the
  go-around - the watchdog refuels below 1 500 lb; the dry run ends with `position`. (3) Sink ≤ 2 000 ft/min (FM): the
  approach flies ≈ 1 050 ft/min at 237 KIAS on 2.5°.
- Build-up: dry run at virtual runway +6 000 ft (sortie S12-F5dry). GO 2026-11-06.
- **F5 dry 1** (`S12-F5dry_dry1`, 17 428 lb, 5.1 Hz): approach 237 KIAS α 8.6° (pred. ≈ 8), bank ≤ ±1.3° to the virtual TD;
  **virtual TD 227 KIAS** (pred. 215-222), -572 ft/min, pitch 8.7° (pred. 8.5), flare max 10.1°. Glide-path intercept: raw VS
  -2 000..-2 497 ft/min for 1.5 s (FM ≤ 2 000 is about the steady approach, ≈ -1 200 here) - noted.
  **INCIDENT (at the virtual-runway height, no hazard): go-around pitch-up to 38° / 20 000 ft/min** - the go-around step
  FLAPS_1 EXTENDED the flaps from UP at 250 KIAS with the 8° no-flap trim; the stabilizer reached the -5° nose-down stop
  (net +3° nose up), 1.3 g pitch-up, no attitude guard in the go-around; the sortie's `position` step recovered it, POST OK.
  Fix: FLAPS_1 only for cfg=land; trim relief 1°/s nose down while the elevator command is within 10 % of the nose-down
  clamp; pitch > 25° warning (lesson 23).
- **F5 dry 2** (fix 1): go-around pitch ≤ 16.8°, flaps stayed UP, trim relief acted once (8.0 -> 5.6°); TD 227 KIAS
  -551 ft/min. New finding: gear raised at ≈ 271 KIAS (limit 260; Maximum accelerates the clean jet before the climb
  criterion) -> cfg=up go-around at Military, gear up also at > 245 KIAS once above 50 ft.
- **F5 dry 3** (fix 2): gear up at 242 KIAS ✓, go-around pitch ≤ 16.6°, trim relief not needed, bank ±5.4° (at 220-375
  KIAS); TD 227 KIAS -554 ft/min pitch 8.6°, centreline -1 ft. Build-up complete for all phases.
- Real F5 prediction: TD ≈ 225-228 KIAS (Fig. A8-2 "touchdown speed" 202 -> +12 %: the script's flare cannot bleed 35 kt from
  the 237 final; a flight-model check of the no-flap TD speed would need a different flare technique - open), sink
  ≈ -350..-450 ft/min (ground effect: F6 real -302 vs dry -456), pitch ≈ 8°, roll ≈ (227/170)² x 3 150 ≈ 5 600 ft, stop ≈ 8 600
  of 13 100 ft. Hazards as above + brake energy from 227 KIAS (not modelled as a failure in the sim as far as known).
  **GO 2026-11-06.**
- **Result F5 (S13-F5, `flighttest_2026-11-06_S13-F5_f5.csv`) - flown safely, TD speed above Fig. A8-2:** 17 429 lb, intercept
  247 KIAS (set_pos speed) -> final 237, flare at 147 ft (241 KIAS), **TD 226 KIAS** (A8-2 202, +12 %), sink +29 ft/min
  (float, TD 3 575 ft past the threshold), pitch 5.2°, centreline +4 ft, no skip, ground roll **4 594 ft** (pred. 5 600,
  -18 %; no FM reference), loop 4.4 Hz. Procedure ✓ (final ≥ 230, sink ≤ 2 000 ft/min, TD ≥ 190+); TD speed vs. the A8-2
  chart = script flare technique (82 % floor + 147 ft flare cannot bleed 35 kt) - open item if the no-flap TD speed is to
  be checked as a flight-model value.
