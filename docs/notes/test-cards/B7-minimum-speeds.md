# B7: minimum speeds / stall approach vs. FM Fig. 6-4

Method: skill `f104-testcard`. Script: `tools/config_test.py <csv> <alt> slow <ias_start> clean|to|land <ias_stop> [alpha_stop]`.
Test plan B7.

## Objective / acceptance
FM Fig. 6-4 (PDF 399; sea level-10 000 ft, no tip stores, 1 g), shaker speed (minimum control speed), and FM 6-5..6-8:
| 19 500 lb | shaker | min. control | CL at shaker / min. control |
|---|---|---|---|
| clean | 225 | 200 | 0.58 / 0.73 |
| TAKEOFF flaps | 190 | 180 | 0.81 / 0.91 |
| LAND flaps (power on, BLC) | 155 | 150 | 1.22 / 1.31 |
FM 6-5: clean 15 200 lb buffet 225 kt, shaker < 200, lateral instability 190, kicker (≈ pitch-up) 175 kt -> CL ≈ 0.75,
i.e. ≈ 198 KIAS at 19 500 lb. Pitch-up (T-tail) and the APC shaker/kicker are not modelled (test plan H2).
Questions: (1) α and CL the sim flies at the FM speeds (consistency with T3-A/T3-L lift), (2) how far below the FM
minimum control speeds the sim still flies level (sim stall), (3) whether it departs.

## Expected (desk check)
- Clean: lift table CLmax 0.95 at α 18° -> 1 g stall ≈ 176 KIAS at 19 500 lb, i.e. ≈ 24 kt below the FM minimum
  control speed and ≈ 22 kt below the pitch-up -> **expected finding: sim allows flight well below the FM limits, no
  pitch-up**. At 200 KIAS: CL 0.73 -> α ≈ 13.4° (table).
- TAKEOFF: ΔCL 0.30 -> CL 0.81 at α ≈ 9.5-10°, 0.91 at ≈ 11°. LAND: T3-L CL 1.145 at α 9.3° -> 1.22 at ≈ 10.5°, 1.31 at ≈ 12°.
- Elevator: trim preset 8/7/5.2°, the hand-flying loop adds elevator (tail ≈ 1.08 α -> ≈ 14-18° tail at high α;
  all-moving tail limit ±? - watch for elevator saturation).

## Preconditions
Clear skies, calm, ISA; trim-hold check; fuel ≈ 4 080 lb (refuel.py, tips empty); **airborne before the script runs
set_pos** (never position from the ground); 10 000 ft MSL start (≈ 8 500 ft AGL east of EDDM).

## Build-up
1. Each configuration first to the FM minimum control speed only (ias_stop = 200 / 180 / 150), alpha_stop 16°.
2. Only if 1 is clean (no departure, altitude held): continue to alpha_stop 18° (clean) at 15 000 ft.

## Abort / recovery
|bank| > 30°, pitch outside -10..25°, sink > 2 000 ft/min, AGL < 3 000 ft -> Maximum, unload (descend), recover to
ias_stop + 40, FM clean-up; if the script fails: reposition (MCP `position`, airborne), never improvise a loop.

## Runs
| Date | Config | Result | Notes |
|---|---|---|---|
| 2026-10-30 | clean bu1, 10 000 ft -> 200 | α 13.9° / CL 0.70 at 202 KIAS, altitude ±450 ft/min | lift table consistent |
| 2026-10-30 | clean bu2, 15 000 ft -> stall | invalid: α 16.2° limited by the script elevator clamp (12.45°) | clamp -> full 17° in slow mode |
| 2026-10-30 | **clean bu3** | elevator 17° stop, α max ≈ 16.2°, 0.91 g at 180 KIAS -> min. level speed ≈ 188-190 KIAS vs. FM min. control ≈ 197 (-4 %) ✓; mush, no pitch-up, no departure | behaviour -> H2 |
| 2026-10-30 | TAKEOFF bu1, 10 000 ft -> 180 | α 11.2° / CL 0.86 at 182 KIAS | after LE stage 10° + FULL restart |
| 2026-10-30 | **TAKEOFF bu2**, 15 000 ft -> limit | elevator stop ≈ 160 KIAS, α max 15.8°, 0.91-0.95 g -> min. level ≈ 165-168 vs. FM ≈ 178 (-6..-7 %) ◐ | mush, no departure |
| 2026-10-30 | LAND bu1, 10 000 ft -> 150 | α 11.1° / CL 1.23 at 152 KIAS | T3-L consistent |
| 2026-10-30 | **LAND bu2**, 12 000 ft -> limit | elevator stop ≈ 137 KIAS, α max 15.5°, 0.93 g -> min. level ≈ 141-144 vs. FM ≈ 148 (-3..-5 %) ✓ | |

## Result
Minimum level speeds 3-7 % below FM Fig. 6-4 minimum control speeds, limited by elevator authority (α ≈ 15.5-16.2°),
benign mush instead of pitch-up -> B7 ◐ (accepted; TAKEOFF marginally outside ±5 %). Pitch-up / APC = H2.

