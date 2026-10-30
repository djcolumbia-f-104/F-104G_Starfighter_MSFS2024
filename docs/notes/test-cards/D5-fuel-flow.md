# D5: cruise fuel flow (part power) vs. FM miles-per-pound data

Method: skill `f104-testcard`. Script: `tools/cruise_test.py`. Test plan D5.

## Objective / acceptance
Stabilised level cruise at part power; fuel flow vs. FM Appendix Part 6, **Fig. A6-1 (PDF 521), configuration drag
index 0** (= clean aircraft, no tip tanks or stores, FM A1-2 PDF 434; data basis: flight test, J79-GE-11A, JP-4).
The chart gives nautical miles per 1 000 lb of fuel x δ vs. true Mach with W/δ as parameter, so
**FF_FM = TAS / (NMPP x δ / δ) x 1 000**. Tolerance ±10 %.
Why: the sim computes FF = TSFC 1.26 x GROSS thrust (calibrated statically at Military, AP-7). In flight the gross
thrust includes the ram drag, so part-power fuel flow is probably too high (evidence: approach 91 % N1 burned
8 270 lb/h at 5 170 lbf net, landing 7; pete noticed the tank emptying fast at 260 kt).

## Test points (chart read at 300 dpi; ±1.5 units)
W/δ chosen on a chart curve; the altitude follows from the weight (δ = W / (W/δ)).
| Point | W/δ | Mach | NMPP x δ | slope per 1 000 W/δ | at 19 000 lb: alt, TAS | FF_FM |
|---|---|---|---|---|---|---|
| A | 30 000 | 0.70 | 82.4 | -0.86 | δ 0.633, ≈ 12 300 ft, 444 kt | ≈ 3 410 lb/h |
| B | 40 000 | 0.80 | 73.5 | -0.78 | δ 0.475, ≈ 19 000 ft, 493 kt | ≈ 3 190 lb/h |
| C | 60 000 | 0.85 | 58.3 | -0.79 | δ 0.317, ≈ 28 800 ft, 503 kt | ≈ 2 730 lb/h |
The script scales the chart value to the flown W/δ with the slope and uses the real TAS and δ.

## Expected (desk check)
Point B: q ≈ 0.7 x 2 116 x 0.475 x 0.64 ≈ 450 psf, CL ≈ 0.215, CD ≈ 0.026-0.028 (D-7137 incl. compressibility, sim
≈ +6 %) -> drag ≈ 2 400 lbf net. Ram drag at cruise N1 (≈ 60-80 lb/s at ≈ 830 ft/s) ≈ 1 500-2 000 lbf -> gross
≈ 4 000-4 400 lbf -> sim FF ≈ 5 000-5 500 lb/h vs. FM ≈ 3 200 -> **expected result: sim +50..70 % ✗**. If it is
confirmed at all three points, the fix is engine-side (fuel flow only, no thrust change), options in this order:
1. `JET_density_on_FF_table` (FF multiplier vs. ambient density; acts on fuel only) - fits if the error grows with
   altitude; Military/AB static at sea level stays 1.0.
2. `fuel_flow_scalar_idle` (throttle-interpolated scalar between idle and full) - fits if the error depends on power.
3. Net-thrust based FF (`use_gross_thrust_on_fuelflow = 0`, `use_old_fuelflow_simvar = 1`) - would change the
   validated AB fuel flow (AP-7), last resort.
Regression after any change: static Military FF (8 400 lb/h), AB FF in flight (round A, D-7137 Table 4), D5 again.

## Preconditions
Clear skies, wind calm, ISA (wx check); trim-hold check done this session; fuel ≈ 4 080 lb (`tools/refuel.py`);
clean, gear up, speed brakes in; AP ALT + HDG hold engaged (trim-based AP is fine for steady cruise).

## Procedure
1. MCP `position` at the point altitude, TAS ≈ point TAS, lateral hdg, throttle ≈ 7 000.
2. `cruise_test.py <csv> <alt> <mach> <fm_nmpp_delta> <wd_ref> <slope>`: throttle PI holds the Mach (no AB,
   ≤ Military), waits for steady state (|ΔM| < 0.005, |VS| < 150 ft/min for 20 s), then averages 60 s.
3. Evaluation printed: FF, gross/net thrust, N1, W/δ, FF_FM, ratio.

## Abort
Mach error not settled after 240 s; altitude ±500 ft; IAS < 250 KIAS; AP off.

## Runs
| Date | Point | Result | Notes |
|---|---|---|---|
| 2026-10-29 | A 11 900 ft M 0.70 | sim 6 148 vs. FM 3 427 lb/h: **1.79 ✗** | evaluated from simlog (script VS unit bug, fixed) |
| 2026-10-29 | B 19 600 ft M 0.80 | 5 825 vs. 3 124: **1.86 ✗** | |
| 2026-10-29 | C 29 500 ft M 0.85 | 4 816 vs. 2 616: **1.84 ✗** | |
| 2026-10-29 | E1 5 000 ft M 0.50 (FM A5-1 endurance) | 5 210 vs. 3 132: **1.66 ✗** | |
| 2026-10-29 | E2 10 000 ft M 0.556 (A5-1) | 5 085 vs. 3 000: **1.70 ✗** | |

## Finding and fix plan (2026-10-29)
Error independent of altitude, so it is the ram drag inside the gross thrust (Mach effect), not density. Needed:
FF/gross ≈ 0.69 at M 0.7-0.85 vs. 1.26 at M 0 (static Military). Next steps, in order:
1. **More reference points before any change**: FM Part 5 maximum endurance (PDF ≈ 514-515, fuel flow directly in
   lb/h vs. weight and altitude, incl. low altitude and low Mach ≈ 0.4-0.5) and the approach (FM Fig. 2-7: 87-90 % N1),
   so the Mach dependence between 0 and 0.7 is known.
2. Evaluate the options against ALL points (static Military 8 400 lb/h, AB in flight D-7137 Table 4, endurance, D5):
   a. modern fuel model (`use_gross_thrust_on_fuelflow = 0`: FF from the fuel controller, ≈ δ√θ f(N1) like a real
      turbojet) - physically right for dry power, but AP-7 found that it ignores the afterburner;
   b. lower dry TSFC (≈ 0.69) + higher AB TSFC to keep the AB fuel flow - static Military would drop to ≈ 4 600 lb/h
      (ground only; takeoff uses AB);
   c. net-thrust based FF (`use_old_fuelflow_simvar = 1`): needs net TSFC 1.37-1.59 cruise vs. 1.26 static,
      idle net thrust is negative in flight (FF 0?);
   d. `fuel_flow_scalar_idle` (throttle-interpolated) - also scales the AB, and per SDK acts on tank drain only (gauge
      would disagree).
3. One A/B sim round with the chosen option; regression: D5 A-C, static Military/idle FF, AB FF in flight (round A
   method), approach N1/FF (landing script), engine start/idle (flameout check).

## Change 2026-10-29 (change control)
Option (b): `ThrustSpecificFuelConsumption` 1.26 -> 0.72 (predicted -5..+7 % at all 5 points). Then: AB TSFC re-calibration
(accel run 10 000 ft vs. ..._T3H_accel10k_isa.csv), regression D5 A/B/C/E1/E2, approach N1/FF, idle in flight
(no flameout), engine start.

## Regression 2026-10-29 (TSFC 0.72): PASSED
B 1.07, C 1.04, E1 0.96 (±10 %) ✓; AB fuel flow unchanged (full AB uses only the AB TSFC); engine start, idle in flight,
T3-D ✓. Approach (2026-10-30, landing 15): N1 89.5 % (FM 87-90 %) ✓, FF 4 311 lb/h (was 8 270). Pitfall: MCP `position` from the ground crashed MSFS; position
only when airborne, throttle ≥ 7 000.

