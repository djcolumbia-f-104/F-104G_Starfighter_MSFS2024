# C4: roll rate (T3-K) and the aileron limiter (H4)

Method: skill `f104-testcard` incl. 2b. Script: `tools/roll_test.py <csv> [steps] [alt] [ias]` (+ `tools/fastlog.py
<csv> 60 PLANE_BANK_DEGREES` for the time constant; the bank comes out in RADIANS, deduplicate repeated values).

## References
- FM 6-3 / 1-68: ailerons ±9.75° gear up, ±20° gear down (limiter on the gear handle); FM 5-14: full-deflection rolls
  ≤ 360°, inertial coupling. No roll rate figure in the FM.
- CR-2144 (F-104A): δa = SUM of both ailerons (PDF 53); F/C 4 (15 000 ft, M 0.90, 465 KCAS) L'δa 34.7, L'p -3.63 ->
  p_ss/δa 9.56 1/s, τ = 0.28 s; full gear-up aileron (δa 19.5°): ≈ 186°/s (SL M 0.8 ≈ 208, 35 000 ft M 0.9 ≈ 162).
- Limiter: already approximated by `aileron_elasticity_table = 0:1, 100:1, 250:0.5, 1000:0.5` (q > 250 psf -> ±10°);
  measured: 50 % stick at 465 KIAS -> 5.0° per side ✓. Known error: gear up below ≈ 275 KIAS gives more than ±9.75°.

## Runs
| Date | Run | Result | Notes |
|---|---|---|---|
| 2026-11-01 | bu1 (25 % / 50 %) | δa 5 / 10° (sum), p 14 / 30°/s vs. CR-2144 48 / 96°/s (**≈ 0.31x**) | linear in δa |
| 2026-11-01 | bu2 (50 %) + fast bank log (≈ 52 ms) | steady 30.9°/s; 63 % after ≈ 0.10-0.16 s (incl. aileron travel) -> **L'p ≈ 2.3x CR-2144, L'δa ≈ 0.74x** | damping is the main error |

## Analysis / next step
SDK `roll_stability` = target rotation resistance, the modern FM only ADDS resistance (default 1 here). Step 1:
roll_stability 1 -> 0.1 (native geometry damping only). Prediction: τ longer, p_ss/δa ≥ 2x higher (native value unknown -
this step measures it). Step 2: roll_stability to τ = 0.28 s, aileron_effectiveness to p_ss 96°/s at δa 10°.
Regression: T3-J Dutch roll, T3-E2 steady sideslip (lateral modes), T3-D takeoff (aileron use near the ground).
Needs Build All + FULL restart (flight_model).
