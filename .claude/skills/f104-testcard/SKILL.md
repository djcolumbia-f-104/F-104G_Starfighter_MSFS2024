---
name: f104-testcard
description: Flight-test method for this project - the fixed test sequence (session-start selftest, plan with prediction, hazard list, checkable preconditions, go/no-go, build-up, postconditions, debrief, lessons-learned register) and the test card BEFORE any sim test. Load before any sim flight test (takeoff, approach, landing, doublet, step, accel, sideslip), before any cfg or module change that will be flown, or when a test failed and is to be repeated.
---

# Flight-test method (test cards, build-up, go/no-go)

Real flight test never "just flies": every test point has a **test card**, reviewed before flight, and risky points
are approached by **build-up** (safe altitude / lower energy first). Do the same here - a crashed test costs pete a
flight reload and gives no data. Load the `f104-pilot` skill too (FM procedures and limits).

## Fixed test sequence (since 2026-11-04, pete; background `docs/notes/test-process.md`)
Every test follows these steps; each has an output. Claude decides go/no-go itself (pete 2026-11-04: no confirmation
question), but writes the go/no-go line into the card before risky points.
| Step | What | Output / gate |
|---|---|---|
| 0 Session start | `tools/watchdog.py` in the background (refuels only), `tools/selftest.py` (module version, all SimVar/unit pairs, watchdog alive, ISA calm weather, build current) | SELFTEST ALL OK, else stop; repeat after every Build All / restart |
| 1 Plan | objective, reference value **shifted to the test condition** (CG, Mach, weight), prediction (2b); every new measurement channel cross-checked against an independent one | card: Objective, Analysis |
| 2 Hazards (light THA) | one line per new risk: cause -> effect -> minimising procedure -> **recovery action** (scripted where possible); after a cfg change: list the scripts tuned to the old behaviour | card: Hazards |
| 3 Preconditions | checkable items, each with the tool that checks it; scripts assert them | card: Preconditions |
| 4 Go/no-go | Claude runs the checks; one line "GO: ..." / "NO-GO: ..." | card |
| 5 Execute | build-up first; abort criteria in the script; **PAUSE_ON before any desk work longer than ≈ 1 min**, `sim_state` between long steps; no unbounded tool calls while airborne | logs in docs/data |
| 6 Postconditions | `tools/post.py` (air: AP on, level, fuel ≥ 1 500, gear/flaps up, damper default; ground: stopped, idle) - flight scripts print POST OK/FAIL at the end | POST OK, else fix before the next test |
| 7 Debrief (at once) | prediction vs. measurement, every anomaly (also small ones), surprises - 5 lines | card: Debrief |
| 8 Lessons learned | each lesson -> where it is **enforced** (assert, selftest/probe item, postcondition, skill step) | `docs/notes/lessons-learned.md` |
| 9 Commit | card, data, measurements.md, data index, register | git |
A lesson only counts as learned when a check or a script enforces it.

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
Hazards: one line each - cause -> effect -> minimising procedure -> recovery action.
Abort / go-around criteria and the safe recovery (must itself be FM-conform and tested).
Postconditions: the state the script leaves (post.py air/ground + test-specific items, e.g. damper switch back ON).
Data: which logs (script CSV + simlog for α/pitch/elevator/trim/N1), file names.
Build-up: the safe step that validates the setup first (e.g. dry run at altitude).
Go/no-go: one line before the run.
Result + Debrief: filled in right after the run - prediction vs. measurement, anomalies, surprises (5 lines);
  measurement entry in docs/notes/measurements.md; lessons -> docs/notes/lessons-learned.md.
```

## 2. Validate the card before flying (desk check)
- Compute the expected values: required CL at the test speed/weight -> α from the lift data / earlier measurements
  (T3-L: CL 0.855 at α 4.1° with LAND flaps), trim from earlier rounds, thrust/N1 from FM.
- Check the script against the card line by line: units, signs (positive AXIS_RUDDER_SET = nose left, trim 16383 = 11°),
  event names (Python-SimConnect lacks some -> `Event(b"...", sm)`), order of events vs. set_pos.
- Check every recovery path (go-around, abort) is FM-conform: e.g. go-around with gear down and LAND flaps in AB,
  never retract flaps at low altitude.
- Syntax check: `python -I -m py_compile <script>`.

## 2b. Engineering analysis gate (mandatory before the cases below; since 2026-10-31)
Lessons 2026-10-29..31: the desk-checked changes worked first time (D5 TSFC predicted +6.5 %, measured +7 %; CG fit), the
un-analysed ones cost incidents or rebuild loops (rotation law tried live -> jet off the runway twice; spoiler_limit
guessed twice although the local SDK page states the formula; two chart misreadings; a "+14 %" that was a skip).
Before flying, write into the card (section "Analysis") and check:
1. **cfg change**: read the SDK parameter page FIRST (`docs/sdk-ref/`, `python -I tools/sdkref_params.py`; fetch missing
   pages from docs.flightsimulator.com into docs/sdk-ref/). Write the formula and a numeric prediction with its source
   ("drag = coef x deflection [rad] -> 0.12 x 1.134 = ΔCD 0.136 -> ground roll ≈ -12 %"). Only then build. After the test:
   prediction vs. measurement; if the gap is > 2x the tolerance, stop and find out why before the next change.
   **A new knob is first measured in isolation at altitude in every configuration it touches** (clean / TAKEOFF / LAND,
   ground and air) before it is combined or flown near the ground (2026-11-04: aero_center_lift and flap `add aft feet`
   each did something different from the assumption -> taxi liftoff, then a dive with TAKEOFF flaps; both reverted).
2. **New or changed control law** (takeoff, flare, any closed loop near the ground): estimate the loop rate
   (≈ 70 ms per SimConnect read: n reads -> 1/(n x 0.07) Hz), the fastest dynamics it must handle (e.g. nose-wheel
   break-out ≈ 3-6°/s) and the worst output (never push during a rotation, never hand over to the AP near the ground).
   Then a build-up WITHOUT the hazard (in the air at the same speed/configuration, or a taxi run without liftoff), then the
   real test. Never tune a law live on a takeoff or landing. **The build-up must cover EVERY phase of the law** (2026-11-04:
   the brot taxi build-up passed, but the airborne part to 35 ft had none -> pitch limit cycle at 0-24 ft, near-loss).
   Before replacing a law, read the card/measurements of the old law for its known failure modes (here: "ground-run gains
   oscillate in the air", known since 2026-10-30).
3. **Reading an FM / NASA chart**: calibrate the reading method on the chart's own sample problem first (FM appendix
   texts give them), identify the lines by their labels on a zoom (pixel scan), write the reading with its uncertainty.
4. **Measurement**: check that the logger rate and the definition fit the question (touchdown/skip needs ≥ 2 Hz on few
   SimVars - tools/rollout_log.py; failed reads return 0 -> never treat a single 0 as an event).
5. **Research**: if no source exists for a value, search (NTRS API, DTIC, FM, local sources) before guessing; record the
   result (also "nothing found") in docs/notes/research.md.
Not needed for pure regression re-runs of an unchanged test.

## 3. Check the preconditions in the sim (go/no-go)
`tools/selftest.py` (step 0), MCP `check_build`, `preflight`, `sim_state`. No-go if anything deviates from the card (e.g. fuel < 1 500 lb after
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
- **New control laws for takeoff/landing need a build-up** (2026-10-30: an untested pitch-rate rotation pushed the nose
  down after liftoff, the fallback handed over to the AP at 4 ft and the jet bounced along/off the runway): first in the air
  at the same speed and configuration, or a high-speed taxi run up to nose-wheel lift-off with idle; fallbacks never
  near the ground.
- **Never leave the jet at idle after a test** (2026-10-30: idle + AP ALT hold -> unattended belly landing); end every
  script at part power / Military with AP ALT hold.
- Respawn on the runway only with the gear DOWN first (runway_start does it and waits until the jet sits still).
- **After every flight reload run `runway_start` before a takeoff**, even if the jet already sits on 26L: the loaded flight
  has trim 0° (2026-10-31: takeoff with trim 0 -> no climb-out, AP fallback dived to 8 ft AGL at 435 kt; takeoff_test now
  refuses trim outside 4-6°).
- **The native SPS (APC shaker/kicker) is DISABLED since 2026-10-31**: after a FULL sim restart it made the MSFS AP diverge
  on engagement (trim ≈ 9°/s to the -5° stop + roll to 180°; three crashes). A cfg block that was only activated by Build
  All + aircraft reload may not be initialised at all -> **re-test anything new after a full restart** before relying on it.
- **Engage the MSFS AP only in stabilised level flight** (trim transferred, elevator ≈ 0), never in a steep climb or near
  the ground; takeoff_test now flies the climb to 10 000 ft itself. Diagnose AP behaviour with `takeoff_test.py ... apdiag`
  (1.5 s AP, recovery, sim PAUSED). When no working AP is available, PAUSE the sim instead of leaving the jet alone.
- Check the fuel before EVERY landing/dry run (a dry-run go-around left the jet at 558 KIAS at 7 600 ft; 617 lb left).
- BLC driver (H3): write flap percents only after all flap systems reached their stage (one travel fraction for all
  systems: an early TE write froze the LE flaps at 3°); the LE flaps stop at 29.4° in LAND.
- A fresh flight load can carry fuel in the tip tanks: always run `tools/refuel.py` (tips empty) before a test.
- Python-SimConnect returns VERTICAL_SPEED in ft/min (not ft/s); AMBIENT_DENSITY in slug/ft³ (use Rankine for p = ρRT).
- **set_pos / MCP `position` does not stop body rotation**: applied during a departure (2026-11-01 full roll, α -34°,
  β 28°) the dive went on to 5 400 ft / 590 KIAS. First unload/level (or PAUSE the sim), then reposition.
- Full-deflection rolls (FM 5-14 inertial coupling) only with pitch/yaw dampers (H1) - the sim departed without them.
- **Build All reloads the aircraft** (2026-11-03: module hot reload with the jet paused at 16 400 ft -> AP off, flaps 15°,
  trim 0 -> dived into the ground). Build All only with the jet standing on the runway; afterwards runway_start again.
- **Rotation laws keep the srot structure** (stick schedule + slow integrator + rate damping, never push before liftoff); a
  high-gain attitude PID between break-out and 35 ft AGL (brot, 2026-11-04) fought the natural rotation, dropped the nose at
  liftoff and limit-cycled at 0-24 ft (θ -8..+15°, heading 24° off, tail contact).
