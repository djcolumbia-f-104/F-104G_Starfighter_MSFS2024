# F-104G flight model: derivation of the cfg values

Variant: **F-104G** (J79-GE-11A). Moments of inertia from the F-104A (only source).
Values entered in `source/cfg/flight_model.f104.cfg` and `engines.f104.cfg` (generated into `PackageSources/...`);
tables with `tools/fm_calc.py`. Marking in the cfg: [Q] source, [M] measured from a drawing (±1 ft) or in the sim,
[S] estimate. Changes and their test results since 2026-10-25: `docs/flight-model-plan.md` and `docs/notes/measurements.md`.

## Reference system
- Datum = 25 % MAC: fuselage station F.S. 472.5 in, height W.L. 100 (fuselage reference line), centreline
  (CR-2144 Fig. III-2).
- MSFS axes: z forward +, x right +, y up +, in ft.
- `reference_datum_position` (datum relative to the model centre) will be set once the 3D model exists.

## Wing (calculated)
Trapezoidal wing from S = 196.1 ft², b = 21.94 ft, MAC = 9.55 ft:
taper ratio λ = 0.376, root chord 12.99 ft, tip chord 4.89 ft, AR = 2.455.
**Check:** spanwise MAC position = b/6·(1+2λ)/(1+λ) = 4.656 ft = 55.9 in; drawing: B.L. 55.8 ✔.
Leading-edge apex at the fuselage centreline (`wing_pos_apex_lon`): MAC leading edge 0.25·9.55 = 2.39 ft ahead of the
datum, plus 4.65 ft · tan 26° = 2.27 ft → 4.66 ft.

## Measurements in the three-view (CR-2144 PDF 41, F-104A)
Scale 11.0-11.25 px/ft at 110 dpi, 17.3 px/ft at 200 dpi (20 ft bar and distance F.S. 236 ↔ 472.5 = 19.7 ft agree).

| Point | z (ft) | y (ft) |
|---|---|---|
| Nose (without pitot boom) | +31.3 | |
| Fuselage end / nozzle bottom | −19.1 | −0.4 (contact point; thrust axis W.L. 103.4 = +0.3) |
| Ventral fin trailing edge bottom | −11.3 | −1.9 |
| Cockpit (F.S. 236) | +19.7 | |
| Horizontal tail leading edge root | −17.4 | +8.6 |
| Vertical tail leading edge root (apex) | −8.4 | +3.6 |
| Nose wheel | +14.1 | approx. −4.5 (ground) |
| Main gear | −0.3 | approx. −4.5, track ±4.375 (FM 1-5) |

Ground height from total height 13.5 ft (FM) minus fin tip approx. 9 ft above W.L. 100. Tail strike angle about the
main wheels: 12.3° at the nozzle, 13.3° at the ventral fin (was 7.6° with the old tail point at y −2.0).
Vertical tail area from the drawing ≈ 38 ft² (root ~10.7 ft, tip ~4.0 ft, height ~5.2 ft); F-104G fin is larger.

## Aerodynamics (NASA TN D-7137)
- `drag_coef_zero_lift` 0.0160; `drag_coef_zero_lift_mach_tab` = CD0(M) − 0.016 (17 points = SDK maximum).
- `oswald_efficiency_factor` 0.668 from a least-squares fit CD − CD0 = k·CL², k = 0.194 (M ≤ 0.8).
- `lift_coef_aoa_table`: M 0.4, 0-14° measured (CLα ≈ 3.0/rad; CR-2144 approach 3.44/rad).
  Above 14°: estimate CLmax ≈ 0.95 at 18°, then decreasing (pitch-up). Negative: mirrored.
- `lift_coef_mach_table`: CL(6°, M)/CL(6°, 0.4). Verified in flight up to M 0.95 (T3-A) and spot-checked at
  M 1.14; whether MSFS also applies compressibility internally is still open for higher Mach.
- Control surface lift slopes and tail setting: see `docs/flight-model-plan.md` (AP-2, AP-3, AP-6).

## Engine
- `static_thrust` 10 000 lbf (dry), afterburner factor 1.58 → 15 800 lbf (FM 1-5).
- Check values max. afterburner installed (D-7137): static 11 200 lbf. The difference to 15 800 lbf is installation
  loss; tuned via n1_and_mach_on_thrust_table (`tools/engine_calc.py`), verified static (±1 %) and in flight (−2..−4 %).
- TSFC afterburner installed ≈ 25 700 / 11 200 ≈ 2.3 lb/(lbf·h) (sea level, M 0). In the sim the AB TSFC is applied
  to the AB increment only; 2.54 matches NASA in flight (see AP-7).

## Masses and inertia
- Empty weight 14 760 lb, max. 26 600 lb (FM 1-5; Wikipedia gives MTOW 29 027 lb, not in the FM).
- Inertia F-104A (16 300 lb, 50 % fuel): 3 549 / 58 611 / 59 669 slug·ft². Used as empty-weight MOI of the G:
  the G is ~1 500 lb heavier empty, but the A values include fuel and ammunition.
- CG: CR-2144 0.07 MAC (combat) or 0.164 MAC (approach) → limits provisionally 0.00-0.20. Sim with 50 % fuel and no
  ammunition: 10.0 % MAC (matches hand calculation, AP-8).

## Flight tests
The original test list (climb vs. D-6398, Mach 2, approach, takeoff) is now part of the test plan in
`docs/flight-model-plan.md` (T3-D, T3-H, T3-I, T3-L) together with Microsoft's official test sequence.
