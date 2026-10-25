# Plan: tuning the flight model with tests (state 2026-10-25)

Goal: every flight model change goes through a fixed loop, so that we measure instead of guess. Basis: the SDK
reference (`docs/sdk-ref/`, local copies) and the "Tuning the Flight Model" tutorials (links below).

## 1. Iteration loop

| Step | Who | What | Test |
|---|---|---|---|
| 1 | Claude | change in `source/cfg/*.f104.cfg`, value marked [Q]/[M]/[S] with source | |
| 2 | Claude | `tools\build_cfg.ps1` | **T0** `check_cfg.py` (no sim) |
| 3 | User | Dev Mode → Project Editor → Build All → **full sim restart** → flight on the EDDM runway | **T1** `check_cfg.py` (package = source, no new error log) |
| 4 | Claude | check the initial state | **T2** `preflight.py` |
| 5 | Claude | flight test per procedure below, logged with `simlog.py` | **T3** evaluation against acceptance criterion |
| 6 | Claude | result in `docs/notes/measurements.md`, status in this plan | |

Rules:
- **After every change to flight_model.cfg restart the sim COMPLETELY** (normalization only runs at sim start;
  restarting the flight or reloading the package is not enough, shown on 2026-10-25). Engine values already take
  effect after a flight restart.
- **Change only one work package per flight test where possible** (A/B comparison), otherwise effects cannot be
  attributed. Pure mandatory/format fixes may be built together. (Round C violated this: yaw damper + rudder change
  at once -> not separable.)
- Read the state before sending events (toggle events switch blindly).
- Query SimVars via MCP with `index=1`, not `NAME:1` (otherwise silently 0, false alarm on 2026-10-25).

Practical execution (command sequences, pitfalls): `docs/notes/test-procedures.md`.
Official test sequence (Microsoft "Testing the Aircraft") and best practices: `docs/notes/research.md`.
**Performance tests (takeoff, climb, top speed) always with the weather preset Clear Sky (ISA).**

## 2. Test levels

**T0 static** (`tools\.venv\Scripts\python.exe -I tools\check_cfg.py .`): rules from the SDK and sources, each
assigned to a work package. An ERROR (FEHLER) means "work package open". New findings are added as new rules.

**T1 build**: also `check_cfg.py`: package cfg = generated cfg (build really done), `BuilderLogError.txt` not newer
than the build.

**T2 preflight** (`...\simconnect-mcp\.venv\Scripts\python.exe -I tools\preflight.py`): test bed loaded, sim running,
engine burning, N1 ≥ 60 %, fuel selector ALL, battery; prints weight, CG, elevator/trim.

**T3 flight tests** (Claude positions the aircraft via MCP `msfs_set_aircraft_position`, no takeoff run needed):

| Test | Procedure | Measured | Acceptance |
|---|---|---|---|
| T3-A deceleration run | 16 500 ft, 480 kt TAS, gear/flaps up, AP altitude hold, idle down to ~215 kt | α, Mach, CL, elevator, trim | 1° band means \|CL_sim − CL_NASA\| ≤ 0.03 at M 0.4-0.95, only \|g−1\| < 0.15 (`analyse_lift.py`) |
| T3-B cruise trim | superseded: htail_incidence stays 0 (see section 4); trim at α = 0 must be ≈ 0 (T3-G intercept) | T3-G | intercept \|δ₀\| ≤ 0.5° |
| T3-C static run | parking brake, idle and military (short AB burst) | thrust, N1, FF, EGT | military 6 670 lbf ±2 %, idle 355-500 lbf, EGT ~595 °C |
| T3-D takeoff run | runway, full AB, user rotates per FM (rotation ~20 kt below takeoff speed) | IAS at liftoff, pitch | liftoff ≤ 200 kt [S], no tail strike (12.3°) |
| T3-E rudder | gear/flaps down, ~250 kt, full rudder | sideslip β, rudder δr (RUDDER_DEFLECTION = unscaled command) | β/δr = Cnδr/Cnβ = 0.32 (CR-2144) ±30 % — **passed round D** (0.34) |
| T3-E2 steady heading sideslip | as T3-E, opposite aileron holds wings level (closed-loop script) | aileron δa required at full rudder | ≈ Clβ·β/Clδa ≈ 17° (CR-2144 approach) ±30 % |
| T3-F drag | idle deceleration as in T3-A, dV/dt | CD_sim = (T − m·dV/dt − W sinγ)/(q S) | CD vs. D-7137 Table 2 ±10 % (`analyse_drag.py`) — **passed 2026-10-25** (1.00/1.04) |
| T3-G trim gradient | from T3-A data | elevator + trim vs. α | slope vs. CR-96008 −Cmα/Cmδe 0.67-1.05; intercept ≈ 0 (measured 1.06-1.08, −0.05°) |
| T3-H climb | ISA (Clear Sky), takeoff with max AB, climb per D-6398 profile | time/altitude/Mach | D-6398 flight test data ±10 % |
| T3-I top speed | 36 000-40 000 ft, max AB, sink in from above, then level | Mach | FM: M 2.0 (engine temperature limit) |
| T3-J dynamic stability | rudder doublet (Dutch roll), release 30° bank (spiral), pitch pulse | period, damping, doubling time | Dutch roll ~2.3 s at 260 kt (Cnβ 0.50); spiral > 20 s |
| T3-K roll rate | full aileron at cruise speed (gear up ±9.75°) | p max | FM/CR-2144 Clδa |
| T3-L stall/APC | idle, 1 kt/s from 1.4 Vs, clean and flaps LAND | Vs, α | FM values, pitch-up behaviour |

## 3. Work packages

| WP | Content | Evidence | Test | Status |
|---|---|---|---|---|
| AP-0 | test tools: `check_cfg.py`, `preflight.py`, simlog with elevator/trim; T3-A baseline (`flighttest_2026-10-25_baseline.csv`, dev. +0.129) | | T0-T3 | done 2026-10-25 |
| AP-1 | mandatory values: `modern_fm_only = 1`; `lift_coef_at_drag_zero = 0` (D-7137 polar without CL0); `wing_camber` > 0 (0 is replaced by 1!), smallest value [S] | SDK reference, tutorial Fine Tuning | T0, T3-A | **done**: with AP-1b after sim restart normalizer target = table, **T3-A passed** |
| AP-1b | A/B: FSX legacy lift terms to 0 (`lift_coef_delta_elevator`, `lift_coef_horizontal_incidence`, `lift_coef_pitch_rate`, `lift_coef_daoa`; template −0.37/−0.57/−3.9/1.7) | contradiction in SDK docs | T3-A | **done** (tested together with AP-1) |
| AP-1c | normalizer target hypothesis H1 (from empty_weight and cruise_speed): cruise_speed 490 -> 700 | debug window | debug window | **refuted** (target unchanged) |
| AP-2 | all-moving tail: `htail_area = 0` (becomes 0.1 internally), `elevator_area = 48.2`, `elevator_lift_coef` 4.1 (CR-96008 M 0.84: CLδe 1.015/rad × S/S_h) | tutorial Tail Geometry, CR-96008 | T0, T3-A | **done** (round A: T3-A unchanged ✓) |
| AP-2b | trim range: nose-up 11° [Q FM 6-5], nose-down 5° [S]; AP holds altitude to ~213 kt ≈ 1.27 Vs (accepted) | FM 6-5 | T3-A | **done** |
| AP-3 | `htail_incidence`: tutorial rule "cruise trim 0" does NOT fit trimmed NASA data -> stays 0 (−4.3 = crash, +4.3 = +0.05 lift); takeoff trim `elevator_trim_neutral = 5` [Q FM 6-5] | rounds B/B2/C | T3-A, T3-G | **done** |
| AP-4 | recalibrate lift table | | | **not needed** (T3-A passed) |
| AP-5 | tail contact points from CR-2144 three-view: nozzle −19.1/−0.4 ft, ventral fin −11.3/−1.9 ft -> tail strike 12.3° (was 7.6°) | CR-2144 PDF 41 | T0, later T3-D | **done** (T3-D open) |
| AP-6 | lateral-directional: rudder ~3x too effective (β = δr). `rudder_lift_coef` must stay 5 (whole fin); `rudder_effectiveness` has no effect on the equilibrium; fixed via `rudder_maxangle_scalar` 0.32. Roll due to sideslip: strong, as in the real aircraft; verify aileron required (T3-E2) | CR-2144, SDK, FM 6-2 | T3-E ✓, T3-E2, T3-J | **rudder done** (round D); T3-E2 first run: roll due to sideslip weaker than estimate; yaw damper off (destabilizing) |
| AP-7 | engine: FF via gross thrust ✓ (military 8 400 lb/h), AB TSFC 2.54 (in flight +1..+4 %, static −33 %), EGT via egt_peak_temperature 2187 R (military 593 °C ✓, idle 470 °C slightly high) | Stoelinga, D-7137 | T3-C | **done** (static AB fuel = known weakness) |
| AP-8 | CG: sim 9.96 % MAC = hand calculation 10.1 % (without ammunition) -> no bug | CR-2144 | T2 | **done** |
| AP-9 | displays: external HUD bar and test bed cockpit show piston values. Later with own cockpit (roadmap phase 4) | cockpit.cfg | visual | later |

## 3a. Schedule from 2026-10-25 afternoon (Claude works autonomously)

Principle: everything without the sim first (research, calculation, cfg, T0); bundle sim rounds because each one
costs a build + **full sim restart**. Within a round only changes whose effects can be separated.
Physical order: tail geometry (AP-2) determines the trim gradient -> trim values afterwards (AP-2b, AP-3); ground
contact points (AP-5) only act on the ground.

| Step | Content | Sim? | Result |
|---|---|---|---|
| S1 | AP-8 CG hand calculation | no | done: no bug |
| S2 | AP-5 tail point from CR-2144, add ventral fin | no | done: 12.3° |
| S3 | AP-2 all-moving tail | no | done |
| S4 | AP-2b trim range 11°/5° | no | done |
| S5 | **sim round A** (S2-S4 + AP-7 fuel): T3-A, T3-G, AB in flight, T3-C, T3-E baseline | yes | done: T3-A ✓, AP to 214 kt, T3-G 1.07, AB thrust ✓, AB FF −11 %, T3-E β/δr 1.0 |
| S6-S8 | htail_incidence −4.3 + trim 0.7; rudder_lift_coef 1.6 + yaw damper; EGT factor 1.39, AB TSFC 2.54 | no | built |
| S9 | **sim round B**: aborted (crash: htail_incidence sign wrong); static run and AB-in-flight data evaluated | yes | measurements.md |
| S9b | htail_incidence +4.3, egt_peak_temperature 2187 R | no | T0 ✓ |
| S9c/d | **sim round B2**: EGT ✓; +4.3 -> extra lift (T3-A ✗) -> back to 0; rudder_lift_coef 1.6 -> departure | yes | measurements.md |
| S9e/f | **sim round C**: htail 0, takeoff trim 5°, rudder_lift_coef 5, rudder_effectiveness 0.32: T3-A ✓, T3-F ✓, T3-E ✗ (no effect, roll-off) | yes | measurements.md |
| S11a | analysis without sim: β = δr exactly -> MSFS rotates the whole fin; fix rudder_maxangle_scalar 0.32 | no | done, T0 ✓ |
| S11b | **sim round D**: ONLY rudder_maxangle_scalar changed | yes | **done**: β/δr 0.34 ✓; roll-off remains but is real F-104 behaviour (FM 6-2, CR-2144 estimate) |
| S11c | `tools/sideslip_test.py` written and flown (round D part 2): β/δr 0.32 ✓, aileron required ~2.4° vs. ~8.5° estimated -> roll due to sideslip weaker than CR-2144 estimate. Yaw damper (gain 1.0) found destabilizing -> off | yes | **partly done** |
| S11d | repeat T3-E2 with PI roll loop (script updated), constant speed, AILERON_LEFT_DEFLECTION; read CR-2144 lateral derivatives for cruise (PDF 55-65); then decide on roll due to sideslip (geometry: vtail_pos_vert/span, wing_dihedral) and tune the yaw damper separately (T3-J Dutch roll) | yes | δa vs. CR-2144 ±30 % |
| S10 | T3-D takeoff with the user (rotation, tail strike), then T3-H climb vs. D-6398 (ISA) | yes (user flies) | liftoff ≤ 200 kt, no tail strike |
| S12 | supersonic trim: at M 1.15 trim −4° (near the −5° stop); real F-104 needs more nose-up at supersonic speed (aft shift of the neutral point) -> check with T3-I | yes | trim within range up to M 2 |

## 4. Findings from SDK, tutorials and tests (2026-10-25)

- The lift table is the target for the aircraft **without control deflection**; MSFS "normalizes" the surfaces in a
  virtual wind tunnel at sim start, matching **at α = 0 with the tail at `htail_incidence`** (debug window
  "Debug Aircraft Sim Curves": TgtClAOA0 = table at α 0). Normalization runs **only at sim start**.
- **`htail_incidence`**: for trimmed flight test data (NASA) it must equal the trim at α = 0 of the trimmed aircraft
  (here 0, T3-G intercept −0.05°). The tutorial rule "set it so the aircraft trims at cruise with trim 0" shifts the
  normalization reference and produced +0.05 extra lift (round B2). Positive values act like nose-up trim.
- `lift_coef_delta_elevator`, `lift_coef_horizontal_incidence`, `lift_coef_pitch_rate`, `lift_coef_daoa`: legacy per
  cfg reference; the "Flight Model Physics Primer" lists elevator/tail terms in the lift equation. Set to 0 (AP-1b);
  together with `wing_camber` 0.1 instead of 0 (internally 1°) the extra lift vanished.
- Primer: 640 surface elements (wing 2 × 80 × 5, tails 20 × 3 each, fuselage 40 × 3 as a box); α = angle between
  longitudinal axis and airflow (body axes).
- MSFS simulates tail + elevator and fin + rudder each as **one surface whose whole incidence follows the control
  deflection**. All-moving tail: correct as is (`elevator_maxangle_scalar` 1, `htail_area` 0). Flap-type rudder:
  equilibrium β = δr -> scale the effective deflection with `rudder_maxangle_scalar` (< 1 per SDK).
- `elevator_lift_coef`/`rudder_lift_coef`: lift slope of the whole tail/fin (default 5.0). Lowering
  `rudder_lift_coef` destroys directional stability (round B2: departure). Tutorial start values by aspect ratio
  (elevator 3.3-4.25 at AR 3-5; rudder 1.5-3 at AR 1-2). F-104 tail AR = 11.91²/48.2 ≈ 2.9.
- `wing_camber` (degrees) must not be 0, otherwise MSFS uses 1.
- All lateral FSX coefficients (`roll_moment_slip_angle`, `yaw_moment_slip_angle`, `yaw_moment_delta_rudder`,
  `side_force_slip_angle`, damping terms) are unused in the modern FM; lateral stability comes from geometry and
  `fuselage_lateral_cx`.
- Engine: `egt_tuning_constant` has no effect for turbines (EGT = ITT remapped to `egt_peak_temperature`);
  `use_gross_thrust_on_fuelflow = 1` with TSFC/AB-TSFC gives plausible fuel flow; AB TSFC applies to the AB increment.
- PlanePerformance.xlsx (tutorial "Preparation") derives CLmax/CD0 from stall speeds -> not needed (NASA data).
- Dev Mode checks: debug "Sim Curves" (normalizer), "Debug Aircraft CFD" (airflow), Weight (inertia), Speed
  (dynamic pressure for elasticity tables), Engines, "Debug Aircraft Tracking" (official test readouts).

Sources: [Basic Aerodynamics](https://docs.flightsimulator.com/msfs2024/retail/samples-tutorials/tutorials/tuning-the-flight-model/basic-aerodynamics/),
[Tail Geometry](https://docs.flightsimulator.com/msfs2024/retail/samples-tutorials/tutorials/tuning-the-flight-model/geometry/tail-geometry/),
[Fine Tuning](https://docs.flightsimulator.com/msfs2024/retail/samples-tutorials/tutorials/tuning-the-flight-model/fine-tuning/),
[Testing the Aircraft](https://docs.flightsimulator.com/msfs2024/retail/samples-tutorials/tutorials/tuning-the-flight-model/testing-the-aircraft/),
[Debug Aircraft CFD](https://docs.flightsimulator.com/msfs2024/retail/devmode/editors/simobject-editor/debug/debug-aircraft-cfd/),
[Turbojet Static Performance Tool](https://docs.flightsimulator.com/msfs2024/retail/sdk-tools/msfs-turbojet-static-performance-tool/).
