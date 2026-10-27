---
name: f104-pilot
description: F-104G pilot procedures and limits from the flight manual T.O. 1F-104G-1 (takeoff, pattern, approach, flare, touchdown, drag chute, braking, go-around, speeds per weight, gear/flap/chute limits). Load before scripting or flying any takeoff, approach or landing test in the sim, or when choosing speeds/configurations for a test.
---

# F-104G pilot procedures (T.O. 1F-104G-1, Change 6)

Speeds are for a gross weight of 16 100 lb unless stated: **adjust approach and landing speeds 5 kt per 1 000 lb**
(FM 2-23). Sources: FM pages in brackets, PDF page = see `docs/sources/manual-index.md`.

## Limits
- Gear: extend below 260 KIAS (FM 2-24); flaps LAND only below 240 KIAS (FM 5-5), lowered at 240-210 KIAS.
- Drag chute: deploy ≤ 180 KIAS (MB-7G) / 205 KIAS (BS-4000) (FM 5-5); only with all three gear on the ground
  (nose-down moment); max. crosswind 25 kt at 90°, 35 kt at 45° on dry runways.
- Max. crosswind for landing 25 kt; +5 kt touchdown speed per 10 kt crosswind with LAND flaps.
- Takeoff trim 5° leading edge down (nose up); full 17° stabilizer only with trim 1-11° (FM 6-5).
- Tail strike at ~12° pitch on the ground (CR-2144 three-view, AP-5).

## Takeoff (FM 6-5, appendix Fig. A2-3)
- Flaps TAKEOFF, trim 5°, max. AB or military. Rotate ~20 kt below the computed takeoff speed; nose wheel lifts
  10-20 kt below (5-10 kt for forward CG). Liftoff IAS (normal) ≈ 155 + 4.43 kt per 1 000 lb above 14 000 lb.
- A quick, large stick input gives a "dynamic" nose-up; then the nose may settle back ("light stick").

## Pattern and approach (FM 2-24..2-27, Fig. 2-7)
- Initial: flaps TAKEOFF, 325 KIAS, 1 500 ft AGL, ~88 % rpm.
- Downwind: gear down < 260 KIAS; LAND flaps at 240-210 KIAS, ~88 % rpm; keep level until flaps and BLC are known
  to work (mild roll transient possible: asymmetric BLC).
- Base: ≥ 200 KIAS, lose ≤ 500 ft (300-400 desired) before the final turn.
- Final: roll out ≥ 6 000 ft from the runway at ~300 ft; **175 KIAS, 87-90 % rpm (never below 83 %)**; flat powered
  approach like ILS/PAR, **700-800 ft/min** sink, intercepted ≥ 1 NM before touchdown. Speed brakes not needed.
- BLC lift depends on engine airflow (best above 80 % rpm, low speed, low altitude) -> **never chop the throttle in
  the air** (abrupt loss of lift); steep approaches are hazardous (excessive sink not recognised in time).
- Heavy weight: speeds per weight, wider pattern or straight-in; military may not hold the descent rate in the final
  turn; go-around needs AB with gear down and LAND flaps.

## Flare, touchdown, rollout (FM 2-25, 2-27, 2-28)
- Flare just short of the runway; **after the flare smoothly reduce rpm** (82-83 %), idle as the main gear touches;
  speed brakes may be used in the roundout to control the touchdown point.
- **Normal touchdown 155-160 KIAS** (16 100 lb); holding off slower -> wing drop, high pitch, tail dragging.
- After touchdown: throttle IDLE, lower the nose wheel, nose wheel steering (pedals aligned!), drag chute timed to
  blossom as the nose wheel touches; anti-skid brakes with smoothly increasing pedal pressure.
- Do not use speed brakes during the ground roll when steering/anti-skid braking is needed (except minimum-run).
- Minimum-run landing: touch down near the runway end at **140 kt**, speed brakes for touchdown control and drag.
- Touch-and-go: idle, flaps TAKEOFF, military, speed brakes in, trim, normal takeoff.

## Reference numbers (appendix Part 8)
- Landing speed schedule (Fig. A8-2): LAND flaps final 170 KIAS up to 15 000 lb (+5 kt/1 000 lb), normal touchdown
  152-157 -> 192 at 23 000 lb; TAKEOFF flaps final 190 -> 255, touchdown ≥ 160 -> 224; no flaps final 225, td 190.
- Ground roll, dry, anti-skid, hard braking, 17 900 lb, 1 500 ft, 12 °C, no wind: **3 130 ft without chute
  (Fig. A8-4), 2 760 ft with the 18-ft chute (Fig. A8-3)**.

## Sim notes (this project)
- `msfs_set_aircraft_position`/`set_pos` in the air RETRACTS the gear -> extend gear/flaps after positioning and
  check GEAR_TOTAL_PCT_EXTENDED before touchdown (landings 1/3 on 2026-10-26/27 were belly landings).
- Drag chute = ground spoiler drag (speed brake handle on the ground). MSFS AP trims only (no elevator).
- Scripts: `tools/takeoff_test.py`, `tools/landing_test.py`; MCP server `f104` (`takeoff`, `landing`).
