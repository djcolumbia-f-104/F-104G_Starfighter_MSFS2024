---
name: f104-testcard
description: Flight-test method for this project - write and validate a test card (objective, preconditions, setup, expected values, abort criteria, build-up) BEFORE any sim test, check every precondition with the tools, fly a safe build-up step first, then the real test, then evaluate against the card. Load before any sim flight test (takeoff, approach, landing, doublet, accel, sideslip) or when a test failed and is to be repeated.
---

# Flight-test method (test cards, build-up, go/no-go)

Real flight test never "just flies": every test point has a **test card**, reviewed before flight, and risky points
are approached by **build-up** (safe altitude / lower energy first). Do the same here - a crashed test costs pete a
flight reload and gives no data. Load the `f104-pilot` skill too (FM procedures and limits).

## 0. Think like test pilot + test engineer
- **Test engineer**: what exactly is validated (one parameter / cfg value per test where possible), against which
  documented reference (FM figure, NASA table - `docs/notes/fm-procedures.md` section 5 lists FM reference values,
  `docs/flight-model-plan.md` the test levels), which data proves it, what tolerance, what result triggers which cfg
  change. Prefer tests that isolate one effect (e.g. glide L/D = drag only, no thrust uncertainty).
- **Test pilot**: fly the FM procedure and configuration (checklists in `f104-pilot` / fm-procedures.md), respect the
  limits, know the abort criteria and the FM-conform recovery before the run, build up from safe to critical
  (altitude, speed, configuration), one test point at a time.
- Order of the test program: simple and safe first (engine on the ground, level flight, glide, approach config at
  altitude) before low-altitude or ground-contact tests (landing). A failed "complex" test is first decomposed into
  the simple tests it depends on.

## 1. Write / update the test card first
Cards live in `docs/notes/test-cards/<test-id>.md` (template below). Before the first run of a test, and after every
failed run, update the card - never re-run a failed test unchanged.

```
# <Test-ID>: <title>
Objective / acceptance: what is measured, against which source value (FM page/figure, NASA table), tolerance.
Preconditions (each with HOW it is checked):
  - build current (MCP check_build), sim restarted after flight_model changes?
  - aircraft state: fuel, engine N1, weight, CG, gear/flaps/trim, AP state, parking brake, position (MCP sim_state)
  - known sim pitfalls that apply (see list below)
Setup: exact position/altitude/speed/configuration and how the script establishes it (incl. what set_pos resets).
Procedure: phases with target values (FM numbers) and who controls what (AP mode, throttle loop, script axis).
Expected values per phase (e.g. α, trim, N1, sink rate) - computed BEFORE the test (CL = W / (q S) etc.).
Abort / go-around criteria and the safe recovery (must itself be FM-conform and tested).
Data: which logs (script CSV + simlog for α/pitch/elevator/trim/N1), file names.
Build-up: the safe step that validates the setup first (e.g. dry run at altitude).
Result: filled in after the run (with the measurement entry in docs/notes/measurements.md).
```

## 2. Validate the card before flying (desk check)
- Compute the expected values: required CL at the test speed/weight -> α from the lift data / earlier measurements
  (T3-L: CL 0.855 at α 4.1° with LAND flaps), trim from earlier rounds, thrust/N1 from FM.
- Check the script against the card line by line: units, signs (positive AXIS_RUDDER_SET = nose left, trim 16383 = 11°),
  event names (Python-SimConnect lacks some -> `Event(b"...", sm)`), order of events vs. set_pos.
- Check every recovery path (go-around, abort) is FM-conform: e.g. go-around with gear down and LAND flaps in AB,
  never retract flaps at low altitude.
- Syntax check: `python -I -m py_compile <script>`.

## 3. Check the preconditions in the sim (go/no-go)
MCP `check_build`, `preflight`, `sim_state`. No-go if anything deviates from the card (e.g. fuel < 1 500 lb after
idling on the runway, engine not at idle N1, wrong flaps/trim). Scripts must also abort themselves on these.

## 4. Build-up, then the test
1. Build-up run at a safe altitude (e.g. `landing_test.py ... <high_ft=8000>`: virtual runway 8 000 ft up). Compare
   the logs with the expected values. Only if it passes:
2. The real test point. Watch it (background run + screenshots/`sim_state`), stop the script on abnormal behaviour.

## 5. Evaluate
Against the card's acceptance values; enter the result in `docs/notes/measurements.md` and the card. A failed run ->
root cause from the logs (not a guess), card update, back to step 2.

## Change control and regression tests
Validated state = everything marked PASSED in `docs/notes/measurements.md` / CLAUDE.md. Rules:
0. **Before any cfg change, grep `docs/notes/research.md` and `measurements.md` for the parameter** (2026-10-27:
   research.md already said that `pitch_use_elevator_only = 1` forces the trim to 0 - not read, change broke the AP).
1. **Do not touch a validated cfg value or a working tool behaviour to make a new test pass.** First ask: can the
   test script/setup be fixed instead? (2026-10-27: the landing problem was set_pos + trim locked by the AP - a
   script issue; changing the AP cfg broke positioning for every other test.)
2. If a change is unavoidable: reason from test data, entry in the card + measurements.md, one change per round,
   mark it [S]/[M] in the cfg - and **re-run the regression tests of every affected area** before building on it:

| Changed area | Regression tests to re-run (tool) |
|---|---|
| Lift, flaps, normalization (full sim restart!) | T3-A lift (`analyse lift`), T3-L approach config, T3-D takeoff |
| Drag, speed brakes, gear | T3-F drag (`accel_run` + `analyse drag`), S11e speed brakes, T3-H climb |
| Engine / thrust / fuel | static run, T3-F AB thrust, fuel flow checks, T3-H climb |
| Pitch: tail, trim, CG, elevator | T3-G trim gradient, S12 supersonic trim, T3-D takeoff |
| Lateral: fin, rudder, dihedral, ailerons | T3-E2 sideslip, T3-J doublet (Dutch roll) |
| Autopilot / systems.cfg | MCP `position` (ALT hold after repositioning), takeoff AP handover (T3-D), approach (T3-L) |
| Test scripts / MCP tools | the tests that use them, at least one dry/build-up run |

3. A tool that worked (e.g. `position`, `takeoff`) is changed only together with a re-run of the tests using it.

## Recovery in the sim
If the jet departs from a safe state (dive, low altitude, unknown AP state): **reposition it at once** (MCP
`position` to ≥ 15 000 ft or `runway_start`) or ask pete to reload - never improvise a control loop on the live jet
(2026-10-27: an ad-hoc trim pitch loop oscillated ±17° and flew the jet into the ground).

**The end of a script is part of the test**: what the script leaves behind (configuration changes, throttle, AP
mode) must follow the FM limits too (flaps UP only ≥ 260 KIAS, gear ≤ 260 KIAS, minimum speeds Fig. 6-4) and is
checked in the dry run (`sim_state` after the run). 2026-10-28: an untested cleanup retracted the flaps at 170 KIAS
and the jet sank into the ground after an otherwise perfect dry run.

## Known sim pitfalls (preconditions to check)
- `set_pos` in the air: retracts the gear, drops AP modes, resets the trim to ~2°, α starts at 0. Re-extend
  gear/flaps, preset trim, re-arm and verify the AP, give the jet time (level segment) before the test phase.
- The MSFS AP flies by trim only, ~0.13°/s -> it cannot catch fast pitch demands (nor a flare); preset the trim -
  but **with the AP engaged the trim is locked** (event, SimVar and trim switch ignored): AP off -> set SimVar
  ELEVATOR_TRIM_POSITION (rad) -> read back -> AP on. `AXIS_ELEV_TRIM_SET` has the opposite sign; ELEV_TRIM_UP
  moved the trim nose down.
- Idling on the runway burns the tanks empty; check fuel before every test.
- **Weather is part of the test configuration**: no live weather, clear skies, wind calm, ISA (FM charts: no wind,
  standard day). Check AMBIENT_WIND_VELOCITY before low-altitude tests (2026-10-28: 14 kt + gusts -> 22° bank in
  the flare, go-around at 25 ft).
- MSFS assistance settings are part of the test configuration (auto-trim, assisted controls, AI piloting): with the
  AP off the trim ran down by itself at ≈ 0.8°/s on 2026-10-27 (suspected auto-trim) -> confirm with pete.
- `set_pos` pitch argument: negative = nose up; start at the expected attitude (e.g. -3° for the approach) instead
  of 0, otherwise α starts at 0 and the jet sinks before the AP recovers.
- Lift/flap cfg changes need a FULL sim restart (normalization); lateral changes: Build All + aircraft reload.
- Flaps/gear: check the real angle/percentage, not the handle.
- Indexed SimVars via MCP with `index=1`; `msfs_get_simvars_bulk` can be stale.
- PowerShell has no `<` redirection: use `$null | & python ...` for stdin.
- **Never position (MCP `position` / set_pos) from the ground** - it crashed MSFS on 2026-10-29. Take off first, then
  position in the air with throttle ≥ 7 000 (throttle 5 000 gave a -22° dive to 9 500 ft; recover by repositioning).
- **Never leave the jet at idle after a test** (2026-10-30: idle + AP ALT hold -> unattended belly landing); end every
  script at part power / Military with AP ALT hold.
- Respawn on the runway only with the gear DOWN first (runway_start does it and waits until the jet sits still).
- A fresh flight load can carry fuel in the tip tanks: always run `tools/refuel.py` (tips empty) before a test.
- Python-SimConnect returns VERTICAL_SPEED in ft/min (not ft/s); AMBIENT_DENSITY in slug/ft³ (use Rankine for p = ρRT).
