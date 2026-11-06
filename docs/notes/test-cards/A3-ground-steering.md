# A3: ground steering (nose-wheel + rudder) identification - input for F9

**Objective:** measure the heading response to rudder-pedal inputs on the runway at 80 and 120 KIAS (open-loop steps of
400/800 counts = 2.4/4.9 % pedal, 1.5 s) and check the closed-loop centreline law that F9 needs (rudder PI on a heading that
steers back to the centreline, 0.1°/ft, + axis = nose left; the F9 rollout law with the correct sign). FM: nose-wheel
steering by the rudder pedals with the steering button (FM 1-67), turning radius Fig. 2-4 (low speed, not tested here).
Acceptance: data quality (step responses resolved at ≥ 10 Hz); closed loop back within ±0.5° without leaving ±40 ft.

**Analysis / prediction:** cfg nose gear steering angle 25° (contact point). If MSFS applied it fully at speed, the
kinematic yaw rate would be V/wheelbase x tan δ = 202 ft/s / 14.4 ft x tan(0.049 x 25°) ≈ 0.3 rad/s ≈ 17°/s per 800 counts at
120 kt - very sensitive; MSFS probably reduces the steering with speed (unknown -> this test). Aerodynamic rudder alone
(β/δr 0.34, small at 80-120 kt): ≈ 1-2°/s. Prediction: between these, step responses settle within ≈ 1 s.

**Hazards:** swerve at 120 kt -> small steps first (400 counts), abort at 40 ft / 6° / 130 KIAS (idle, brakes, centreline
law); nose lift (trim set to 2°, pitch > 2.5° -> abort); runway length (stop by ≈ 8 000 ft of 13 100; abort at 9 000 ft).
**Go/no-go:** GO 2026-11-06 (calm weather, selftest).

## Result + Debrief (S20-A3, 2026-11-06, `flighttest_2026-11-06_S20-A3_steer.csv`, 19 180 lb, calm)
- Aborted correctly at heading error 7.1° / 97 KIAS (limit 6°), stopped at 5 370 ft past the threshold. Loop 4.2 Hz. The
  speed PI was too slow (steps at 78 / 110 / 103 / 70 KIAS instead of 80) - acceptable for this run.
- **Open-loop plant:** +400 counts -> yaw rate ≈ 0.6-0.8°/s settling in ≈ 0.7-1 s (78-85 KIAS); 800 counts -> ≈ 1.4-1.7°/s
  (≈ 100 KIAS) -> **≈ 1.8°/s per 1 000 counts**, ≈ 10x less than full kinematic nose-wheel steering (prediction range
  1-17°/s) -> MSFS reduces the nose-wheel steering strongly with speed (aero rudder + reduced NWS).
- **Closed loop (the F9 rollout PI 700/100, 0.1°/ft):** oscillates on the ground at 100-110 KIAS - heading ±1-4°, centreline
  ±5-10 ft, period ≈ 3 s after the +400 step; after the 800 step 7.9° / -31 ft (abort). = the overshoot seen in F9 step 2
  (-5.8° / -21 ft after the skip) -> **this law must not be used**; the validated P-only rollout law (no I, tiny c term) was
  calm in all landings.
- Desk model (yaw rate = K x counts, lag 0.3 s, one-pass delay, c' = V sin ψ) does NOT reproduce the oscillation (predicts a
  stable loop) -> per lesson 21 not used for tuning. Next: fit the lag/delay (and tyre side-force dynamics) to this run's
  closed-loop data until the model oscillates like the flight, then design (yaw-rate damping, weaker centreline loop, slow I
  for weather-vaning), then A3 run 2 (closed loop only, 80 KIAS first), then F9 step 2.
