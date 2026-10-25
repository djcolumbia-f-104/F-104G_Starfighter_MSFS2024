# Test procedures in the sim (cookbook, state 2026-10-25)

How the tests in `docs/flight-model-plan.md` are flown in practice. Everything via the MCP server `simconnect`
(tools `msfs_*`) and the scripts in `tools/`. Always record results in `docs/notes/measurements.md`.

## 0. Before every sim round
1. Changes only in `source/cfg/*.f104.cfg` (flight_model, engines, aircraft, cockpit, systems), then
   `powershell -ExecutionPolicy Bypass -File tools\build_cfg.ps1` and `tools\.venv\Scripts\python.exe -I tools\check_cfg.py .`
   (T0: 0 ERRORS; T1 warnings are fine as long as nothing is built).
2. User: Dev Mode -> Project Editor -> **Build All** -> **quit and restart the sim completely** (normalization runs
   ONLY at sim start) -> flight on the **EDDM runway** from the world map -> "ready".
   For performance tests (takeoff, climb, top speed) choose the weather preset **Clear Sky (ISA)** (Microsoft
   "Testing the Aircraft"); irrelevant for T3-A/F/E (evaluation uses measured air density), but wind is better off.
3. Claude: `check_cfg.py` (T1 green?) + sim process start time > package timestamp:
   `Get-Process | ? { $_.MainWindowTitle -match "Flight Simulator" } | select StartTime` and
   `Get-Item Packages\pete-aircraft-f104g\SimObjects\Airplanes\pete-f104g\common\config\flight_model.cfg`.
4. Reconnect MCP (`msfs_disconnect`, `msfs_connect`) - after a sim restart the old connection is dead
   (error 0xc00000b0).
5. `C:\Users\pete\AppData\Local\simconnect-mcp\.venv\Scripts\python.exe -I tools\preflight.py` (T2).
   Expected: takeoff trim 5.00°, N1 ~67 % (right after start possibly still < 60 % -> wait 10 s).
6. Optional: capture the debug window "Debug Aircraft Sim Curves" with `tools\screenshot.ps1 <png> -Sim`:
   TgtClAOA0 must be 0.0100 (= table at α 0).

## Pitfalls
- Indexed SimVars: `msfs_get_simvar(name="TURB_ENG_N1", index=1)`, NEVER `TURB_ENG_N1:1` (silently returns 0).
  In `simlog.py`/`preflight.py` (Python-SimConnect) `NAME:1` is correct.
- `msfs_watch_simvar` max. 30 s; parallel calls run at the same time (not one after another).
- Toggle events (`TOGGLE_*`, `PARKING_BRAKES`, `AP_MASTER`) switch blindly -> read the state first.
- Yaw damper: disabled in the cfg since round D (gain 1.0 was destabilizing); do not send `YAW_DAMPER_ON` until tuned.
- Positioning sets α = 0 (g ≈ 0.3) and the AP raises the nose only at 2°/s -> **position at 16 500 ft or higher**
  (at 9 000 ft the jet hit the ground twice), AP must already be on.
- `msfs_set_aircraft_position(airspeed=...)` is TRUE airspeed (480 -> ~370 kt IAS at 16 500 ft).
- After positioning watch the g load for 5-10 s (`G_FORCE`); abort if g < 0.5 and altitude is dropping.
- Throttle: `THROTTLE1_SET` 0 = idle, 11141 = military (68 %), 16383 = full afterburner.
- Round E: after the post-positioning dive, GEAR_DOWN/FLAPS_DOWN at ~217 kt moved the handles but gear/flaps stayed
  retracted (cause unknown) -> check GEAR_TOTAL_PCT_EXTENDED and TRAILING_EDGE_FLAPS_LEFT_ANGLE, not only the handles.
- Crash detection is off; after a crash the jet keeps sliding on the ground -> simply reposition.
- `PLANE_PITCH_DEGREES`: nose up = negative. `ELEVATOR_TRIM_POSITION`: nose up = positive.
- simlog column `VERTICAL_SPEED[ft/min]`: unit uncertain -> compute the flight path angle from the altitude change.
- Logger may abort after a crash/teleport with SimConnect error 0xc00000b0; data up to that point is kept.

## T3-C static run (on the ground, parking brake on)
Logger 55-60 s in the background: `...simconnect-mcp\.venv\Scripts\python.exe -I tools\simlog.py docs\data\flighttest_<date>_<round>_static.csv 60 2`
(Bash with run_in_background). Sequence: 15-20 s idle -> `THROTTLE1_SET 11141` for 25 s -> optionally 5 s 16383
(the parking brake does not hold AB for long) -> 0. Target: idle 355-500 lbf, military ~6 630 lbf / 8 400 lb/h / ~593 °C.

## T3-A / T3-F / T3-G deceleration run (lift, drag, trim gradient)
1. `msfs_set_aircraft_position(latitude=48.25, longitude=11, altitude=16500, heading=270, airspeed=480)`
2. Immediately: `GEAR_UP`, `FLAPS_UP`, `THROTTLE1_SET 16383`, `AP_ALT_VAR_SET_ENGLISH 16500`, `HEADING_BUG_SET 270`,
   `AP_MASTER` (only if off!), `AP_ALT_HOLD_ON`, `AP_HDG_HOLD_ON`.
3. Check the g load, then start the logger for 220-240 s (`..._flug.csv`).
4. Accelerate with AB to ~600 kt IAS (M ~1.15, about 30 s), then `THROTTLE1_SET 0`.
5. Watch the airspeed every 10 s; at trim 11° (stop, ~213 kt) or when sinking: `THROTTLE1_SET 11141`.
6. Evaluation: `tools\.venv\Scripts\python.exe -I tools\analyse_lift.py . <csv>` (T3-A band means, T3-G) and
   `analyse_drag.py . <csv> <t_idle+3> <t_recovery>` (T3-F). AB fuel flow/thrust against
   `docs/data/nasa_d7137_*_maxab_*.csv` (calculation see measurements.md, round A).

## T3-D takeoff (scripted)
1. Jet on the runway: after a sim start from the world map (EDDM runway 26L), or reposition:
   `msfs_set_aircraft_position(latitude=48.34472097713059, longitude=11.803858844132039, heading=263.4, on_ground=true)`,
   then `THROTTLE1_SET 0`, `GEAR_DOWN`, `FLAPS_1` (TAKEOFF), `AUTOPILOT_OFF`, `ELEVATOR_TRIM_SET 7447` (= 5° nose up,
   16383 = 11°); check with preflight.py (trim 5.00°, N1 ~67 %).
2. `...simconnect-mcp\.venv\Scripts\python.exe -I tools\takeoff_test.py docs\data\flighttest_<date>_T3D_takeoff_runN.csv`
   (defaults Vr 157 kt, θ 10.5°). Prints liftoff IAS, θ, ground roll; AP takes over in VS mode at 30 ft.
3. Compare with FM Fig. A2-3: liftoff ≈ 155 + 4.43 kt per 1 000 lb above 14 000 lb (weight from preflight).
Pitfalls: positive AXIS_RUDDER_SET = nose left; loop runs at only ~3 Hz (reads wait for sim frames) -> low gains;
`AP_ALT_HOLD_ON` holds the CURRENT altitude (never use it right after liftoff).

## T3-E rudder (sideslip)
1. **AP must be ON before positioning** (after a sim restart it is off: check `AUTOPILOT_MASTER`, send `AP_MASTER`,
   `AP_ALT_VAR_SET_ENGLISH 16000`, `AP_ALT_HOLD_ON`, `AP_WING_LEVELER_ON`).
2. Position **clean** at 16 500 ft, heading 270, airspeed 330 (TAS ≈ 250 kt IAS). Positioning sets α = 0
   (g ≈ 0.3 at first) -> the AP needs ~30 s and may lose several thousand ft; wait until stable, idle to < 240 kt.
3. Below 240 kt IAS: `GEAR_DOWN`, `FLAPS_DOWN` (never above the 240 kt flap limit - strong nose-down moment),
   `THROTTLE1_SET` ~9 500-11 141 to hold ~250 kt.
4. Logger 40-50 s; after 6 s `AXIS_RUDDER_SET 16383` (full), hold 15 s, then `AXIS_RUDDER_SET 0`,
   `GEAR_UP`, `FLAPS_UP`, `AP_HDG_HOLD_ON`.
5. Evaluation (awk on the CSV): column 23 = INCIDENCE_BETA, 24 = RUDDER_DEFLECTION (unscaled command, before
   rudder_maxangle_scalar), 25 = PLANE_BANK_DEGREES. Target β/δr ≈ 0.32 (CR-2144 approach).
   The jet rolls away (real F-104 behaviour, FM 6-2); the AP wing leveler does NOT hold it. Recover after ~15 s.
   For the aileron required (T3-E2) a closed-loop aileron script is needed (planned `tools/sideslip_test.py`).

## Cruise (trim in equilibrium)
30 000 ft, airspeed 501 (TAS, ≈ M 0.85). Military is too much there (accelerates to M 0.98); equilibrium at about
`THROTTLE1_SET` 9 000-9 300, the AP oscillates at first (g 0.7-0.95). Wait at least 60 s for stable flight before logging.

## T3-E2 steady heading sideslip (closed loop)
Configure as T3-E (gear/flaps down, ~250 kt, AP on, yaw damper off), then run
`...simconnect-mcp\.venv\Scripts\python.exe -I tools\sideslip_test.py docs\data\flighttest_<date>_<round>_sideslip.csv 15 1.0`
(foreground, ~35 s). The script switches the AP off, probes the axis signs, holds bank 0 (PI on aileron) and
altitude (elevator), applies full rudder for 15 s, then releases the axes and re-engages the AP. Abort at |bank| > 45°
or > 1 500 ft altitude loss. Keep the speed constant with the throttle beforehand (round D drifted 263 -> 338 kt).
Evaluate per phase (second half): β, rudder, aileron (AILERON_LEFT_DEFLECTION); targets β/δr and δa/δr from
CR-2144 Table III-9 (see measurements.md round E), solved with the rudder's own rolling moment L'δr.
Round E variant (works well): clean, ~310 kt at 15 800 ft with `THROTTLE1_SET` ~6 200.
