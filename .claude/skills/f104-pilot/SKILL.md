---
name: f104-pilot
description: F-104G pilot procedures, checklists and limits from the flight manual T.O. 1F-104G-1 (engine start/check values, takeoff, pattern, approach, flare, touchdown, drag chute, braking, go-around, emergencies such as flameout/no-flap/BLC failure/spin, stall and minimum speeds, speeds per weight, gear/flap/chute limits). Load before scripting or flying any takeoff, approach, landing or other sim test, or when choosing speeds/configurations for a test.
---

# F-104G pilot procedures (T.O. 1F-104G-1, Change 6)

Full extract with page numbers: **`docs/notes/fm-procedures.md`** (checklists, emergencies, limits, flight
characteristics, test reference values). This skill is the compact version. Speeds are for 16 100 lb unless stated:
**approach/landing speeds +5 kt per 1 000 lb** (FM 2-23). PDF pages: `docs/sources/manual-index.md`.

## Limits
- Gear: transient (extend/retract) 260 KIAS, down and locked 295 KIAS. Flaps LAND 240 KIAS (lowered at 240-210).
- Drag chute ≤ 180 KIAS (MB-7G) / 205 (BS-4000), only with all three gear on the ground (nose-down moment), at idle.
- Crosswind 25 kt (dry); chute 25 kt at 90° / 35 kt at 45°. Gusts: +5 KIAS per 10 kt above steady wind.
- EGT continuous 600 °C (-11A), 750 °C max. 3 s. 750 KEAS, M 2.0. Load factor 7.33 g (no stores).
- Rolls: full-deflection rolls ≤ 360°, entry ≥ 0.5 g (flaps up); maneuvering (TAKEOFF) flaps: entry ≥ 1 g.
- Takeoff trim 5° LED (nose up); full 17° stabilizer only with trim 1-11°. Tail strike ≈ 12° pitch (CR-2144).

## Engine (FM 2-12..2-19)
- Start: fuel flow 400-800 lb/h at 10-12 %, light-off by 20 % / 20 s, starter ≤ 1 min, start ≤ 1 min.
- **Idle: 67 ± 1 %, EGT 320-420 °C, nozzle 8.5-9.5, fuel flow 700-1 600 lb/h, oil ≥ 12 psi.**
- **Military: 100 ± 1 %, EGT 590 ± 10 °C, nozzle 1.0-3.5, idle -> Military ≤ 10 s.** AB: EGT 580-600, nozzle
  3.5-5 (min AB) / 7.5-9.5 (max AB); blowout = EGT < 500, nozzle < 7. No AB light in 3 s (SL) / 5 s: recycle.
- Do not chop the throttle to OFF in flight (flameout). Shutdown after 3 min at idle.

## Takeoff (FM 2-20..2-22, 6-5, Fig. 2-6)
- Flaps TAKEOFF, takeoff trim, speed brakes IN, Military -> brakes off -> min AB -> max AB.
- Back stick 20-25 kt below takeoff speed; nose wheel lifts 10-20 kt below; **attitude ≈ 5°**. Takeoff speed
  **190 KIAS @ 20 800 lb** (normal liftoff ≈ 155 + 4.43 kt per 1 000 lb above 14 000 lb, Fig. A2-3).
- Gear UP when definitely airborne, up before 260 KIAS; flaps UP at ≥ 260 KIAS (mild nose-up).

## Pattern and approach (FM 2-23..2-27, Fig. 2-7)
- **Autopilot OFF before landing** (reduced stick rate with AP engaged).
- Initial: flaps TAKEOFF, 325 KIAS, 1 500 ft AGL. Downwind: gear < 260; LAND flaps 240-210 KIAS; level until BLC
  works (mild roll transient). Base ≥ 200 KIAS, lose ≤ 500 ft.
- Final: rollout ≥ 6 000 ft out, ≥ 190 KIAS until on final, then **175 KIAS, 87-90 % rpm (never < 83 %)**, flat
  powered approach like ILS/PAR, **700-800 ft/min**. Speed brakes not needed on the approach.
- BLC lift depends on engine airflow (best > 80 % rpm) -> **never chop the throttle in the air**.

## Flare, touchdown, rollout (FM 2-25, 2-28)
- Flare just short of the runway, thrust smoothly to **82-83 %**, idle as the main gear touches.
- **Touchdown 155-160 KIAS**; slower = wing drop, high pitch, tail dragging.
- IDLE, nose wheel down, steering (pedals aligned), **chute as soon as the nose wheel is down**, anti-skid brakes
  with smoothly increasing pressure. No speed brakes on the roll when steering/anti-skid are needed.
- Minimum-run: TD 140 kt near the runway end. Touch-and-go: idle, flaps TAKEOFF, Military, speed brakes in, trim.

## Go-around (FM 2-29, Fig. 2-8)
1. **Military** (Maximum if needed). 2. **Speed brakes IN.** 3. **Gear UP** once airborne with a climb established.
4. **Flaps TAKEOFF at ≥ 180 KIAS** after a definite climb (nose-up trim change), lever in TAKEOFF 30-60 s.
5. Flaps UP ≥ 260 KIAS. Decide early, preferably ≥ 165 KIAS (slow to accelerate with LAND flaps). Military climb in
   landing configuration only ≈ 1 400 ft/min at 20 500 lb, sea level (Fig. 6-8) - AB if marginal.

## Stall / minimum speeds (FM 6-5..6-9, Fig. 6-4)
- APC: stick shaker, then kicker; **kicker inoperative with LAND flaps or gear down** -> stop at the shaker.
- Fig. 6-4 shaker speed (min. control speed), 1 g, 19 500 lb: clean 225 (200), TAKEOFF 190 (180), LAND 155 (150);
  15 000 lb: 195 (175), 170 (160), 135 (130). Clean 15 200 lb: shaker < 200, kicker 175.
- Pitch-up/spin: idle - rudder opposite - stabilizer full forward + nose-down trim - aileron INTO the spin; eject if
  rotating at 15 000 ft AGL. Intentional pitch-ups/spins prohibited.

## Emergencies (memory items; details in fm-procedures.md)
- Abort: idle - jettison - chute - hook. Air start / stall clearing: START - throttle OFF - IDLE.
- BLC malfunction: flaps TAKEOFF, final ≥ 195, TD ≥ 165. No-flap: final ≥ 230, sink ≤ 2 000 ft/min, TD ≥ 190.
- Flameout: glide 245-260 KIAS TAKEOFF flaps (9 NM per 10 000 ft), gear only after the flare is assured.

## Sim notes (this project)
- `set_pos` in the air retracts the gear, drops AP modes, resets the trim (~2°) and starts at α 0 -> configure,
  trim and re-arm the AP after positioning, level segment before the test phase (see `f104-testcard`).
- MSFS AP flies pitch by trim only (~0.13°/s) and LOCKS the trim while engaged -> preset the trim with the AP OFF
  (SimVar ELEVATOR_TRIM_POSITION), then engage. `pitch_use_elevator_only = 1` was tried and is unusable (trim reset
  to 0, only ~1.4-3° elevator).
- Drag chute = ground spoiler drag (speed brake handle on the ground). RAT is not modelled.
- Scripts: `tools/takeoff_test.py`, `tools/landing_test.py`; MCP server `f104` (`takeoff`, `landing`).
