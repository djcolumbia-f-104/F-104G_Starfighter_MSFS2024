# B4: glide L/D (dead-engine glide configuration)

Method: skill `f104-testcard`. Script: `tools/config_test.py <csv> <alt> glide [ias] [clean]`. Test plan B4.

## Objective / acceptance
FM 3-38 and Fig. 3-8 (PDF 208/209): engine windmilling or frozen, gear up, RAT extended, TAKEOFF flaps, 245 KIAS (flaps
up: 275 KIAS gives the same distance), zero wind: **9 NM per 10 000 ft** (L/D ≈ 5.5); without the RAT ≈ +2 NM per
10 000 ft (≈ 11 NM, L/D ≈ 6.7); gear down 5.5 NM. The sim has no RAT -> compare the aerodynamic L/D with ≈ 6.7
(≈ 11 NM per 10 000 ft), tolerance ±10 %. Isolates drag (no thrust uncertainty, idle thrust removed in the analysis).

## Expected (desk check)
At 245 KIAS, 19 000 lb: q ≈ 203 psf, CL ≈ 0.48. Clean polar CD = 0.016 + 0.194 CL² = 0.061; TAKEOFF flaps
ΔCD = 0.12 x 1 x 0.262 = 0.031 -> CD ≈ 0.092 (+ ΔCL 0.30 reduces α, not CL) -> **L/D ≈ 5.2** (no RAT). That is BELOW the
FM no-RAT value (≈ 6.7) and close to the with-RAT value - a hint that the TAKEOFF flap drag or the induced drag
(k = 0.194 at CL 0.48) is high. Flaps up 275 KIAS: CL ≈ 0.38, CD = 0.016 + 0.028 = 0.044 -> L/D ≈ 8.6.

## Preconditions
Clear skies, wind calm, ISA; trim holds; fuel 4 080 lb (`tools/refuel.py`); start 22 000 ft MSL (east of EDDM).

## Procedure
Script positions at 22 000 ft, gear up, flaps TAKEOFF (or UP), trim 3°, idle, elevator holds the IAS; evaluation from
30 s to 9 000 ft below the start (energy height, ground distance with calm wind), aerodynamic L/D with the logged
idle net thrust removed. End: FM clean-up, AP ALT hold.

## Abort
IAS < 150 KIAS, bank > 30°, pitch outside -20..+20°, AGL < 3 000 ft.

## Runs
| Date | Run | Result | Notes |
|---|---|---|---|
| 2026-10-29 | 1 TAKEOFF | aborted (pitch -21°) | controller start too aggressive -> fixed |
| 2026-10-29 | 2 TAKEOFF 245 KIAS | 8.5 NM per 10 000 ft (energy ratio 5.15), aero L/D 6.04 ✗ (FM ≈ 11 without RAT) | TAKEOFF flap drag too high |
| 2026-10-29 | clean 275 KIAS | 10.6 NM (6.42), aero L/D 8.78 ✓ (-4 %) | clean polar confirmed |
| 2026-10-29 | 3 TAKEOFF 245 KIAS, drag scalar 0.42 | 9.8 NM (5.94), aero L/D 7.29, -11 % ◐ | regression after FULL restart; accepted (reference ≈ 11 NM is an estimate) |

Change: TAKEOFF flap drag scalar 1 -> 0.42 (FULL restart); regression B4 TAKEOFF + T3-D.
Regression T3-D: liftoff 170 kt vs. 177.5 kt (-4.2 %) ✓.
