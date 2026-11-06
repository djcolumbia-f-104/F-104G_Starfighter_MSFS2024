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
