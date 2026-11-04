# T3-SP: short period and static longitudinal stability (SAS off)

Method: skill `f104-testcard` incl. 2b. Tool `tools/pitch_step_test.py` (stabilizer step ±0.2° through the trim, AP off,
α at ≈ 20 Hz, fit of ωn/ζ, α/δ from the fit asymptote). Found during H1 (pitch damper, card H1-sas.md).

## Objective / acceptance
Short period SAS off vs. NASA (CR-2144 Table III-3/III-5 SAS off, CG 0.07 c̄, 16 300 lb; CR-96008 nondimensional, other CGs
-> shifted with Cmα(x_cg) = Cmα(x_ref) + CLα (x_cg - x_ref)). Acceptance: Cmα (back-calculated from ωn²) within ± 25 % of
the source band at subsonic Mach; damping (Mq + Mα̇ from 2ζωn) within ± 20 %; supersonic documented (no Mach knob).
Back-calculation: ωn² = -Mα + (Lα/V)(-Mq), Mα = q̄Sc̄ Cmα/Iy, Mq = q̄Sc̄ Cmq (c̄/2V)/Iy, Lα/V = q̄ S CLα/(m V);
Iy ≈ 63 000 slug ft² (58 611 empty + fuel + pilot), Cmq from CR-96008 (-8.03 subsonic, -6.83 at M 1.36).

## Baseline (2026-11-03, aero_center_lift 0, 18 700-19 300 lb, CG 7.6-9.3 % MAC)
| Point | h / M / q̄ | ωn rad/s | ζ | α/δ | Cmα sim | Cmα source (at the sim CG) | Mq+Mα̇ sim / src |
|---|---|---|---|---|---|---|---|
| C | 16 500 ft / 0.84 / 614 | 6.67 | 0.165 | 1.0 | **-2.39** | ≈ -1.0 (CR-96008 cond. 2 -1.09) | - |
| A | 16 500 ft / 0.94 / 767 | 7.53 | 0.162 | (1.0) | **-2.44** | -0.81 (CR-2144 F/C 4) .. -1.09 | -1.34 / -1.31 ✓ |
| B | 35 000 ft / 0.93 / 335 | 4.89 | 0.12 | 0.8 | **-2.37** | -1.15 (CR-2144 F/C 6) | -0.65 / -0.63 ✓ |
| D | 35 000 ft / 1.38 / 726 | 7.36 | 0.115 | 0.76 | **-2.49** | -2.1 (F/C 7 M 1.2), -2.2 (CR-96008 cond. 5), -1.9 (F/C 8 M 1.5) | - |
Cmδ from α/δ ≈ -1.9 (sources -1.44 .. -1.98) ✓. Neutral point: sim ≈ 60 % MAC at all Mach; real ≈ 30 % (M 0.84) ->
49 % (M 1.0) -> 61 % (M 1.36) (CR-96008). **Subsonic static stability 2.3x too high, supersonic ≈ 1.15x; damping ✓.**
Logs `flighttest_2026-11-03_SP_A/B/C/D_*.csv`, `_H1_pstep02_fast.csv`.

## Analysis (2b) - change 1: aero_center_lift 0 -> +3.6 ft (wing lift point forward)
- SDK (`docs/sdk-ref/flight_model.cfg.md`): aero_center_lift = longitudinal position of the aerodynamic centre (ft,
  relative to the model origin = our datum), used to place the wing surfaces once at start; all pitch-moment Mach tables
  are legacy (unused) -> no Mach-dependent knob. No downwash parameter. The tail sets Cmα AND Cmq (Cmq_tail ≈ -2 x 4.1 x
  0.246 x (19.0/9.55)² = -7.9 = CR-96008 -8.03) -> lowering elevator_lift_coef would also remove the (correct) damping.
- Missing physics = downwash at the tail (ΔCmα = a_t V_H dε/dα, ∝ CLα_wing). Equivalent: wing lift point forward,
  ΔCmα = CLα_wing(M) Δx/c̄ - scales with the lift Mach table like the downwash does.
- CLα_wing ≈ CLα_total - a_t S_t/S = 4.4 - 1.0 = 3.4 (M 0.94). Target ΔCmα +1.3 -> Δx = 1.3/3.4 x 9.55 = **3.6 ft**.
- Predictions: A Cmα -1.14, ωn ≈ 5.3, ζ ≈ 0.23 (same 2ζωn 2.44); B -1.07, ωn ≈ 3.5 (F/C 6 3.53), ζ ≈ 0.17; D ≈ -1.45,
  ωn ≈ 5.6; takeoff speeds ≈ -2.3 -> -1.4. Trim gradient δ/α (T3-G) 1.07 -> ≈ 0.55. Worst case (wing share 4.4): A -0.75,
  still stable.
- Side effects to check (regression): T3-A lift (normalization; FULL restart), T3-G trim gradient (new expectation ≈ 0.5),
  S12 supersonic trim, AP positioning/ALT hold (MCP `position`), T3-D takeoff (srot stick schedule S_HOLD -6 600 for
  α 10.5° will need less stick; takeoff trim 5° must not lift off by itself), T3-L/F3 landing (flare), H2 APC (kicker =
  trim offset; α thresholds unchanged), B7 minimum speeds. Reported CG % MAC may change if MSFS references the MAC to it.
- Abort criteria in flight: as the tool (|Δα| > 4°); first flight after the restart = takeoff_test (watch rotation;
  abort/stop on the runway if the nose rises before vr).
- **First flight after the change (2026-11-03 decision): no air start possible** (MSFS 2024 cannot save/resume a flight in
  the air) -> `srot taxi` high-speed taxi build-up at idle up to nose-wheel lift-off: break-out stick vs. prediction (≈ half
  the old value), check that the 5° takeoff trim alone does not lift the nose; derive S_HOLD; takeoff; fine-tune S_HOLD
  in the air with stick_hold_test.py; then the SP points A-D.

## Change 1 - hazards, preconditions, go/no-go (fixed test sequence, 2026-11-04)
**Hazards** (cause -> effect -> minimising -> recovery):
1. Takeoff stick schedule tuned to the old stiffness -> over-rotation / tail strike / kicker after liftoff -> first run
   = `srot taxi` with `shold=-2000` (taxi ends at θ 2.5° or 165 kt) -> script: idle, active nose-down push, brakes.
   Prediction: wing lift 3.6 ft further forward ≈ +21 000 ft lb nose-up at 160 kt (≈ +3.7° stab) -> break-out ≈ 163 kt with
   stick ≈ -1 600 (was -5 159 at 166 kt); the 5° trim alone would need ≈ 190 kt; no liftoff possible in the taxi run
   (CL 1.11 needed at 160 kt / θ 5°).
2. 5° takeoff trim lifts the nose before vr -> uncommanded rotation -> watch θ in the taxi log before vr ->
   recovery: the taxi stop routine (push, idle, brakes); next step would be a lower takeoff trim (FM 5°: flag, not change).
3. MSFS AP flies by trim; a less stiff airframe changes its loop -> oscillation after `position` -> post.py checks AP/level
   at the end of every script -> recovery: AP off, wings level, re-position from level flight; sim PAUSE if divergent.
4. Prediction wrong in the other direction (wing share 4.4 instead of 3.4) -> Cmα ≈ -0.75, still stable; short period
   slower -> no hazard; if any test shows |α| growing without input -> abort (tool |Δα| > 4°).
5. APC kicker = trim offset based on the stick-to-stab mapping; α thresholds unchanged -> first kicker check later (H2
   regression), not part of the first flights.
**Preconditions**: selftest ALL OK after the restart (module 7.2, units, watchdog, weather); check_build after build_cfg;
FULL sim restart done (normalization; lift check T3-A follows); runway_start (trim 5°, flaps 15); refuel; wind < 3 kt.
**Order**: (a) taxi `takeoff_test.py <csv> 157 10.5 taxi shold=-2000`; (b) takeoff with S_HOLD from (a) (proportional to the
break-out stick); (c) stick_hold_test.py in the air (gear down, TAKEOFF flaps) -> S_HOLD for α 10.5°; (d) SP points A, B, D
with pitch_step_test.py; (e) regression list above.
**Postconditions**: taxi: post.py ground (stopped, idle); flights: post.py air.
**Go/no-go 2026-11-04: GO** for the cfg change (prediction + hazards written, worst case still stable); flights after the FULL restart in the order above, each step gated by its postcondition.

## Change 1 - run (a) taxi SP1 (2026-11-04) and DEBRIEF
`takeoff_test.py ... taxi shold=-2000` (`flighttest_2026-11-04_SP1_taxi.csv`), 19 340 lb, trim 5°, TAKEOFF flaps:
- **The nose rose by itself from ≈ 137 kt with the 5° trim and no stick** (θ 0.5 -> 7.3° at 158 kt); the taxi end was only
  checked after vr (157 kt) -> **airborne 160-167 kt (θ up to 8.6°)**, the stop routine pushed it down at 169 kt; clean stop.
- Prediction "5° trim alone needs ≈ 190 kt" was WRONG (hand-waved scaling). Moment balance about the main gear with the
  data: old break-out 166 kt (q̄ 93) with stab 10.35°, new ≈ 138 kt (q̄ 64.5) with stab 5° -> the change added ≈ 490 ft³
  (moment per psf) nose-up on the ground, ≈ 2x the 240 ft³ from the wing lift alone (CL ≈ 0.34 x 196 x 3.6).
- **Root cause (concept):** moving the lift point moves the moment of the WHOLE lift, including the flap lift (TE + LE
  TAKEOFF/LAND); real downwash only changes the tail's α-derivative. With flaps at low speed this gives a large false
  nose-up Cm0. Before the change the takeoff matched the FM (5° trim, rotation with back stick at vr) = FM data point; the
  real flaps are strongly nose-down (CR-2144 PA: stab 7.1° nose-up at α 2.3°).
- Script gaps: taxi end only after vr; postconditions checked "air" after a taxi run -> fixed (uncommanded-rotation
  guard before vr in every mode -> stop routine; post.py ground after taxi/abort).
- Rule 2b.1 (gap > 2x tolerance -> stop and analyse) applied: no further flight with change 1 alone.

## Change 1b (2026-11-04): flap lift centre back to the validated place
SDK `flaps-position.i` value 7 `add aft feet`: centre of lift of the flap stage, positive = forward (pitch up). Set -3.6 for
TAKEOFF and LAND of [FLAPS.0] (TE) and [FLAPS.1] (LE) -> the flap lift acts where it did before change 1; the clean-wing
stiffness correction stays. Prediction: taxi break-out back near the validated values (nose stays down with the 5° trim
up to vr; break-out with back stick ≈ 160-166 kt); remaining difference = the basic-wing lift at ground attitude moved
3.6 ft (CL ≈ 0.05-0.1 -> ≈ 35-70 ft³, i.e. break-out a few knots earlier). Unknown: whether "add aft feet" moves only the
flap increment or the whole flapped-section lift - the taxi run shows it. Hazard 1/2 now guarded by the script.
**Go/no-go 1b: GO** (flap-lift shift reverted per stage; taxi run guarded by the uncommanded-rotation stop).
