# B5 / B6: landing-configuration drag and go-around climb (Military)

Method: skill `f104-testcard`. Script: `tools/config_test.py`. Test plan: `docs/test-plan.md` B5, B6.

## Objective / acceptance
- **B6 go-around climb** (isolates excess thrust = thrust - drag in landing configuration): gear down, LAND flaps,
  speed brakes in, Military, constant IAS 170 KIAS (sawtooth climb, hand-flown speed hold by elevator), 30-40 s steady.
  FM Fig. 6-8 (Military, landing configuration, 60 °F): 3 000 ft, 20 500 lb ≈ 800 ft/min max at ≈ 165-175 KIAS;
  sea level 20 500 lb ≈ 1 400 ft/min; 14 500 lb ≈ 3 000 ft/min (sea level). Chart read at 110 dpi -> ±200 ft/min.
  Acceptance: within ±300 ft/min of the chart value for the test weight/altitude (interpolate weight linearly).
- **B5 flat final with speed brakes** (FM 3-41 stuck throttle): speed brakes out + LAND flaps + gear down at Military
  -> flat approach ≈ 190-200 KIAS. Test: hold altitude, let the speed settle; acceptance: steady IAS 180-210 KIAS.
- Data also for D5: N1, net thrust, fuel flow at each point.

## Evidence so far
- Dry run 14 (6 500 ft, 19 180 lb, no speed brakes, Military): level 168 KIAS steady (zero excess thrust).
  FM Fig. 6-8 at 6 000 ft for 20 500 lb is not drawn; 3 000 ft ≈ +800 ft/min -> the sim looks short of excess thrust.
- Landing 7 approach (≈ 1 950 ft, 16 570 lb, 179 KIAS, 2.5°): N1 91 % vs. FM 87-90 %.

## Preconditions
| Item | Required | Check |
|---|---|---|
| Build | current | `check_build` |
| Sim settings | assistance off, trim holds | trim check passed 2026-10-28 |
| Fuel | ≥ 2 500 lb (refuel via SimVars) | `preflight` |
| Weight | noted (interpolate Fig. 6-8) | `preflight` |
| OAT | noted (Fig. 6-8 is for 60/90/120 °F) | `sim_state` |

## Setup and procedure (script)
1. `set_pos` at the test altitude east of EDDM, heading 263°, 185 KIAS, nose 3° up; gear down, LAND flaps, trim 5.2°
   with the AP off; speed brakes per mode.
2. Throttle Military (11141). Hand flying: ailerons hold wings level on heading 263°.
3. Mode `climb` (B6): elevator holds IAS 170 (vertical-speed target from the speed error); measure the mean vertical
   speed over the steady part (after 25 s), up to +3 000 ft above the start or 90 s.
   Mode `level` (B5): elevator holds the start altitude; measure the IAS it settles at (mean of the last 30 s).
4. End: FM go-around clean-up (gear up when climbing, TAKEOFF ≥ 180, UP ≥ 260 KIAS), AP ALT hold.

## Expected values (B6, 3 000 ft class)
Fig. 6-8, 60 °F, peak values: sea level 14 500 lb ≈ 3 000, 20 500 lb ≈ 1 400 ft/min; 3 000 ft 14 500 lb ≈ 2 700,
20 500 lb ≈ 800 ft/min. Linear in weight -> at 19 200 lb: ≈ 1 200 ft/min at 3 000 ft, ≈ 1 750 at sea level.
At 10 000 ft (build-up run) not in the chart - functional check only (stable speed hold, plausible ROC).

## Abort criteria
IAS < 150 KIAS, bank > 30°, pitch outside -10..+20°, height below 1 500 ft AGL -> Maximum, climb, clean up.

## Build-up
1. Both modes at 10 000 ft MSL (≈ 8 500 ft AGL): functional check of the speed hold and the clean-up.
2. Then 4 500 ft MSL (≈ 3 000 ft AGL) = the Fig. 6-8 3 000 ft curve.

## Runs
| Date | Run | Result | Notes |
|---|---|---|---|
| 2026-10-28 | B6 10 000 ft (build-up) | -690 ft/min at 167 KIAS, 18 780 lb; speed hold stable, clean-up ✓ | false abort on an AGL 0 read -> outlier guard |
| 2026-10-28 | **B6 4 500 ft** | **+389 ft/min** at 173 KIAS, 18 280 lb, OAT 3 °C ✗ (FM ≈ 1 200-1 400) | ≈ 850 lbf / ΔCD 0.043 too much drag |
| 2026-10-28 | **B5 4 500 ft, speed brakes** | **164 KIAS** level at Military ✗ (FM 190-200) | ≈ ΔCD 0.037 too much drag |

Verdict: landing-configuration drag ≈ 0.04 too high (CR-2144 flap + gear ΔCD 0.142 vs. FM). Thrust -5 % only.
Change 2026-10-28 (change control: reason = 3 FM points, documented here + measurements.md + cfg comment):
`flaps-position.2` drag scalar 1.273 -> 0.85 (LAND flap ΔCD 0.12 -> 0.08). Needs Build All + FULL sim restart.

Regression after the change (table "Change control", area flaps/drag):
1. B6 4 500 ft climb 170 KIAS - expect ≈ +1 100..+1 300 ft/min (ΔCD -0.04 ≈ +830 lbf).
2. B5 4 500 ft level with speed brakes - expect ≈ 185-195 KIAS.
3. F2 landing with chute and F3 without - ground roll will lengthen a few % (less aero drag at idle); approach N1
   expected ≈ 88-89 %. If the roll exceeds +10 %: chute ΔCD (now -7 % effect vs. FM -12 %) is the next candidate.
4. T3-L approach configuration lift/trim: unaffected (drag scalar only) - confirmed implicitly by the landing approach α.
5. T3-D takeoff: TAKEOFF flap position unchanged -> not affected (no re-run needed).
