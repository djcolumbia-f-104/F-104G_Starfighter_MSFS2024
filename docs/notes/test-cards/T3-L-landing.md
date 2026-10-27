# T3-L landing: scripted straight-in approach and landing, EDDM 26L

Method: `.claude/skills/f104-testcard`. Procedures/limits: `.claude/skills/f104-pilot`. Script: `tools/landing_test.py`.

## Objective / acceptance
- Touchdown IAS vs. FM Fig. 2-7 / A8-2: 155-160 KIAS @ 16 100 lb, +5 kt per 1 000 lb (19 180 lb: 170-175 KIAS), ±5 kt.
- Ground roll with chute vs. FM Fig. A8-3: 2 760 ft @ 17 900 lb, 1 500 ft, 12 °C, no wind (scale with weight / TD
  speed: roll ∝ V²), ±10 %. Without chute (A8-4): 3 130 ft.
- Approach itself (validates the configuration): 175 KIAS +5 kt/1 000 lb at 87-90 % N1, 700-800 ft/min.

## Preconditions (how checked)
| Item | Required | Check |
|---|---|---|
| Build | current, T1 green; full restart after lift/flap changes | MCP `check_build` |
| Aircraft | TESTBED, on EDDM 26L | MCP `preflight` |
| Engine | running, N1 ≥ 60 % (idle 67 %) | `sim_state`; script aborts below |
| Fuel | ≥ 1 500 lb (idling on the runway burns it: 2026-10-27 130 lb left) | `sim_state`; script aborts below |
| Weight | noted -> speeds (script computes them) | `sim_state` |
| Sim | Sim Curves open (optional) | pete |

## Setup (what the script does, and what set_pos resets)
1. AP HDG + ALT hold armed, `set_pos` 6 NM before the threshold on the centreline, level at ~1 110 ft above the
   (virtual) runway = ~2 NM before the 2.5° glide path (intercept ~4 NM before the threshold), speed 1.05 x v_app as TAS.
2. After set_pos (it retracts the gear, drops AP modes, sets trim ~2°, α 0): GEAR_DOWN, FLAPS_DOWN (LAND), trim
   preset 5° nose up, AP master/HDG/ALT re-armed and verified (watchdog every ~3 s).

## Expected values (computed 2026-10-27, 19 180 lb, v_app 190 KIAS)
| Phase | IAS | CL needed | α | pitch | trim | N1 | sink |
|---|---|---|---|---|---|---|---|
| Level (gear/LAND flaps) | 190 | 0.80 (q = 122 psf, S 196.1) | ~3.2° (T3-L: CL 0.855 at 4.1°, slope ~0.06/°) | ~3.2° | ~5-5.5° | ~88 % | 0 |
| Glide path 2.5° | 190 | 0.80 | ~3.2° | ~0.7° | ~5° | 87-90 % | ~840 ft/min (no wind) |
| Touchdown | 170 | 1.00 (q = 98 psf) | ~6.5° | ~6° (tail strike 12°) | | idle at TD | 150-300 ft/min |

## Dependencies (test-engineer decomposition, FM extract 2026-10-27)
The landing combines lift, drag, thrust, AP and ground model. Validate the simple parts first:
1. Approach configuration at altitude: T3-L done (CL 0.855 at α 4.1°, trim 5.6°).
2. **Landing-configuration drag + thrust**, low altitude: speed brakes + LAND flaps + gear at Military -> flat/level
   ≈ 190-200 KIAS (FM 3-41); final 175 KIAS @ 16 100 lb needs 87-90 % for 700-800 ft/min (Fig. 2-7).
3. **Go-around climb**, Military, landing configuration: ≈ 1 400 ft/min at 165-175 KIAS, 20 500 lb, sea level (Fig. 6-8).
4. Minimum speeds LAND flaps (Fig. 6-4): shaker 155 / min. control 150 KIAS at 19 500 lb. Note: the sim's stall
   debug shows 120 kt "at weight (flaps)" - check that the sim does not allow touchdowns far below the FM speeds.

## Deviations from the FM procedure (test aids)
- FM 2-24: autopilot OFF before landing. Here the MSFS AP (HDG + VS) flies to touchdown -> acceptable for the
  approach; the flare by AP VS is not the FM technique. Later: script-own elevator control for the flare.
- RAT not modelled; drag chute = ground spoiler drag.

## Abort / go-around
Below 500 ft: |cross-track| > 300 ft or |bank| > 30°; below 400 ft: 300 ft below the path; gear not down 2 NM out
-> FM 2-29: full AB (Maximum), speed brakes in, AP VS +3 000 ft/min; **gear UP only once climbing (> 500 ft/min,
> 200 ft), flaps TAKEOFF only at ≥ 180 KIAS** (landing 6: immediate FLAPS_1 -> crash).

## Data
Script CSV `docs/data/flighttest_<date>_T3L_<name>.csv` + `..._simlog.csv` (α, pitch, elevator, trim, N1, flaps, AP).

## Build-up
1. Dry run with a virtual runway 4 000 ft up: `landing_test.py <csv> 6 2.5 4000` (8 000 ft: ~30 % less thrust at
   ~10 000 ft -> not representative of the approach power; 4 000 ft keeps ~4 000 ft terrain margin). Pass if: level segment holds
   altitude ±200 ft, α/trim/N1 near the table, glide path within ±100 ft after intercept, virtual touchdown 165-180 KIAS
   with sink < 600 ft/min.
2. Only then the real landing (`landing_test.py <csv> 6 2.5`).

## Runs
| Date | Run | Result | Root cause / change |
|---|---|---|---|
| 2026-10-26/27 | 1, 3 | belly landings | set_pos retracts the gear -> gear after positioning + gear check |
| 2026-10-27 | 4 | go-around at 370 ft, -940 ft below path | started on the path at α 0; AP modes dropped by set_pos -> re-arm |
| 2026-10-27 | 5 | go-around, crash | AP armed but sank -4 000 ft/min -> level segment + simlog |
| 2026-10-27 | 6 | sank -3 300 ft/min in ALT hold, crash in go-around | simlog: trim 2.2° after set_pos, AP trims ~0.13°/s, α 2.5° (needed ~3.2); go-around retracted flaps -> trim preset 5°, go-around keeps LAND flaps, dry-run mode, this card |
| 2026-10-27 | dry 1 (8 000 ft) | sank ~4 000 ft/min in ALT hold, go-around at virtual 400 ft | trim preset did not stick (2.1° at t 0), AP trimmed 2.1 -> 4.4° in 16 s, α 2.7° |
| 2026-10-27 | dry 2 (8 000 ft) | same, α reached 4.7° only after 30 s | trim preset overwritten by the AP (read back 1.2°); AP pitches by trim only (~0.13°/s) + 1°/s² accel limit -> systems: `pitch_use_elevator_only = 1`, `max_pitch_acceleration = 3` (Build All + aircraft reload) |

| 2026-10-27 | dry 3 (4 000 ft, elevator-only AP) | dive to pitch -17°, α ≈ 0, go-around | trim preset 0.0°: isolated test -> trim LOCKED while the AP is engaged; AP elevator only ~1.4° |
| 2026-10-27 | dry 4 (4 000 ft, trim preset with AP off, elevator-only AP) | dive again, α ≈ 1° | preset 5.1° read back, but the elevator-only AP reset the trim to 0 on engagement, max ~3° elevator -> `pitch_use_elevator_only` reverted (Build All + reload) |

| 2026-10-27 | regression `position` (AP reverted) | AP holds, sank 1 150 ft (noted ~300 ft earlier, now 19 100 lb full fuel) | deviation noted, AP functional |
| 2026-10-27 | **dry 5** (4 000 ft, trim preset 5.0° with AP off) | **first complete approach**: glide path α 3.1-3.4° (exp. 3.2), pitch 0.5-0.9° (0.7), trim 4.8-5.1° (5), path +5..+92 ft, 190-192 KIAS ✓; virtual TD 166 KIAS ✓, sink 745 ft/min ✗ (< 600), level segment -450 ft ✗ (±200, start transient ~250 KIAS); N1 96-98 % vs. FM 87-90 % (⚠, 5 500 ft MSL -> ~15 % less thrust; check with the landing-config drag test) | flare start 100 -> 200 ft (AP trim rate) |

| 2026-10-27 | dry 6 (flare 200 ft by AP VS) | TD 161 KIAS, sink 966 ft/min ✗ | trim-based AP cannot flare (FM 2-24: AP off anyway) -> own flare controller (elevator PI on VS + aileron wing leveler, gains/structure from sideslip_test.py; signs probed: +elevator axis = nose down, +aileron axis = raw bank +) |
| 2026-10-27 | dry 7 | level segment lost 850 ft, go-around | start at pitch 0 = α 0 -> set_pos with pitch -3° (nose up) |
| 2026-10-27 | dry 8 | level segment ✓ (pitch init works), glide path ✓; flare ✗: TD 181 KIAS, -1 665 ft/min | **after AP off the trim runs down by itself (5.0 -> 1.1° in 5 s, ≈ 0.8°/s)**, elevator +2.5° could not hold -> suspected MSFS assistance (auto-trim?) - seen also in the recovery and trim test |

| 2026-10-27 | dry 9 (sim settings fixed) | level segment: trim 5.2 -> 0.1° by the AP, sink 2 900 ft/min, go-around | start at 250 KIAS: set_pos speed behaves like IAS (my TAS correction was wrong); trim-based AP too slow -> **script flies pitch and roll itself** (FM 2-24 AP off), AP only for go-around/cleanup |
| 2026-10-27 | dry 10 (hand-flown) | level 1 067-1 117 ft ✓, path -10..+21 ft ✓, 186-192 KIAS ✓, bank ±0.3° ✓; TD 166 KIAS ✓, sink 864 ✗ | flare throttle cut to near idle in 3 s (FM: smoothly to 82-83 %), flare elevator too soft -> N1 gain 40 to 83 %, flare KP x1.6 |
| 2026-10-27 | dry 11 | TD 169 KIAS ✓, sink 254 ✓, pitch 4.7° ✓, -29 ft ✓; **but roll limit cycle ±20-31°, ~4.5 s** | aileron gains 600/400/200 too high for the F-104 roll power at ~2 Hz -> 250/150/60, limit ±4 000 |
| 2026-10-27 | **dry 12** | **PASS**: level 1 072-1 117 ft, bank ±3° level / ±0.8° flare, 182-186 KIAS; **TD 168 KIAS** (FM 163-168), **385 ft/min**, pitch 4.8°, -13 ft, 2 758 ft past the threshold | one failed lat/lon read (returns 0) -> false early intercept 510 ft below the path -> outlier rejection for position, altitude, IAS (needs one more dry run: change control) |

## Next
1. pete: reload the flight (fuel), MSFS assists as checked.
2. Dry run 13 (4 000 ft) to confirm the outlier rejection - script change = regression dry run.
3. Real landing `landing_test.py <csv> 6 2.5`; compare TD IAS and ground roll with chute (A8-3: 2 760 ft @ 17 900 lb).

## Preconditions added after dry 8
- **MSFS assistance settings** (pete): auto-trim / assisted controls / AI piloting OFF, no analogue axis on elevator
  trim, no duplicate bindings - part of the test configuration from now on.
- **Check 2026-10-27 after pete changed the settings** (`trim_hold_check`, ground and 16 500 ft): trim stays put after
  AP off (2.01° for 8 s), after SimVar set (5.00° for 10 s) and after an AP on/off cycle; elevator 0.00° without
  input. `position` regression: sank 100 ft / 0 ft (earlier today 1 150 ft) - the earlier trim run-down and
  probably the large positioning sink were caused by the sim settings, not by the flight model.

## Preconditions added after dry 4
- systems.cfg back to template AP pitch settings (trim-based AP), Build All + aircraft reload done.
- Script: AP off -> trim SimVar 5.2° -> read back ≥ 4.9° -> AP on. Expected: α ≈ 3.2° within ~5 s, level ±200 ft.

## Preconditions added after dry 2 (superseded by dry 3/4)
- systems.cfg with `pitch_use_elevator_only = 1` loaded (Build All + aircraft reload; `check_build` T1 green).
- Expected in the next dry run: α ≈ 3.2° within ~5 s after positioning, altitude held ±200 ft in the level segment.
