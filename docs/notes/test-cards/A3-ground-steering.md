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

## Run 2: designed law (desk, 2026-11-06)
- Model fit on run 1 (recorded command -> heading, `fit_ground` in the session scratch, method in this card): first order,
  **yaw rate = 1.8°/s per 1 000 counts x IAS/100, lag τ 0.60 s, dead time 0.45 s**, rms 0.89° over 20 s (heading ±4°).
  Closed-loop validation: the run-1 PI law in the model oscillates with ±3.1° / ±8.1 ft (flight ±1-4° / ±5-10 ft ✓), period
  5.6 s (flight ≈ 4 s - model slightly slow; design with margin).
- Design: **kp 700 / kd 300 (yaw-rate damping) x min(1, 100/IAS), ki 50 (unscaled, weather-vaning), centreline 0.04°/ft**;
  model 80-175 KIAS: no oscillation, also with K x1.5 or dead time 0.6 s; weather-vane torque (840 counts) -> max 14-32 ft,
  end 1-4 ft; 2° crab at the touchdown -> ≤ 4 ft. (The validated P-only law drifts 148 ft with that torque; the F9 PI oscillates.)
- Prediction run 2 (law=new, steps 400/800): 400 at 80 KIAS -> |heading| ≤ 0.6°, |c| ≤ 3 ft; at 120 ≤ 1° / ≈ 5 ft; 800 ≈ 2x;
  no residual oscillation. Pass -> law into landing_test (xw rollout) -> F9 step 2.
- **Run 2 result (S20b-A3, law=new):** no oscillation; 400-count steps -> heading ±1.1-1.3°, |c| ≤ 4.4 ft; 800 -> ±2.4°,
  |c| ≤ 7.5 ft, settled at ≈ 3 ft (run 1: 7.9° / -31 ft, abort); calm segments 78-132 KIAS within 0.3°. Step amplitudes ≈ 2x the
  prediction (the jet keeps yawing ≈ 1 s after the step - dead time underestimated); core criteria met -> **A3 law PASSED**.
  Aborted at 130 KIAS (speed overshoot in the 120 KIAS acceleration: J79 spool-down) -> 120 KIAS steps incomplete (one 400
  step at 111 KIAS: 0.18°); stop at 9 554 ft. Model at the 0.55 s slow pass: oscillation ±0.6-0.9° above 140 KIAS -> in
  landing_test (xw) the rollout uses the fast pass with the heading read every pass.

## Run 3 (crosswind identification, preset 350/20 = 10 kt surface from the right) - plan
One speed per run (runway length): 100, then 140, then 160 KIAS; Maximum to 20 kt below the target, anticipating throttle
(run 2 overshoot), flaps UP (less lift at 160 KIAS), settle 8 s (mean pedal = weather-vane torque B(V)), steps ±400 added to
the held pedal, hold 4 s, then stop. Prediction (S19d fit, ± 2x): B ≈ 1 250 / 1 750 / 2 000 counts (≈ 8 / 11 / 12 % pedal).
Hazards as runs 1/2 (abort 40 ft / 6° / IAS > target + 25 / nose lift / 9 000 ft); 160 KIAS with flaps UP and trim 2° is
≈ 20 kt below the liftoff speed (T3-D 178-182 with rotation; the nose stays down: elevator push above 1° pitch).
GO 2026-11-06 (selftest wind=350:20 OK).

## Run 5 (F9 12.5 kt divergence diagnosis, calm air) - plan
LAND flaps, 150 KIAS, law v3, mode=offset: the heading reference is offset by +3° / -3° for 3 s (= a crabbed jet on the
wheels, as after the F9 touchdown), then back to the centreline law. If the heading diverges beyond the offset (abort at 6°)
or the pedal saturates -> ground physics with a crab angle; if it follows calmly -> the cause is in the touchdown transient
(skip, nose-wheel contact). GO (calm, on the runway, abort criteria unchanged).
- **Run 5 result (S24-A3off, calm, LAND flaps, 150 KIAS):** +3° offset reached and held with only ≈ ±500 counts pedal, no
  divergence (the abort at -41 ft is the test design: 3° for 3 s at 250 ft/s ≈ 40 ft lateral) -> the ground physics with the
  jet yawed is benign as long as the velocity follows the heading. The F9 divergence comes from the touchdown with a
  velocity/heading mismatch (crab): tyre slip angles; the nose wheel (12.6 ft arm) outweighs the main gear (1.8 ft), more so
  with the rollout push (+4 000) loading the nose wheel. 10 kt (TD heading 1.2°) passed, 12.5 kt (3.2°) diverged.
