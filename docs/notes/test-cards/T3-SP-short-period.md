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
