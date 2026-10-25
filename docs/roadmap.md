# Roadmap

## State 2026-10-25
Phase 0 done (SDK, test bed instead of a Blender test cube). Phase 1/2 on the test bed: the F-104G flight model and
J79 fly; lift, drag, thrust and fuel flow match NASA data (see `docs/notes/measurements.md`). In progress:
lateral-directional stability (rudder/sideslip), then takeoff test and climb performance (see
`docs/flight-model-plan.md` and CLAUDE.md "CONTINUE HERE").

## Phase 0: learning and setup
- [x] Enable Developer Mode in MSFS 2024, install the SDK
- [x] Build an SDK sample aircraft and load it in the sim (understand the workflow) -> test bed
- [ ] Install Blender + MSFS glTF exporter, export a test cube and see it in the sim
- [x] Make the flight manual accessible (page index `docs/sources/manual-index.md`), document data in `aircraft-data.md`

## Phase 1: flying prototype
- [ ] Simple exterior model (fuselage, wing, tail, gear), rough, without cockpit
- [x] Contact points (gear, tail), CG, masses (on the test bed)
- [x] Take cfg files from the SDK template and fill them with F-104 data (`source/cfg`, `tools/build_cfg.ps1`)
- [ ] Goal: takeoff, climb, turns and landing possible (takeoff test T3-D open)

## Phase 2: tune the flight model
- [x] Thrust/drag/lift subsonic and transonic vs. NASA (T3-A, T3-C, T3-F), afterburner in flight
- [ ] Thrust/drag up to Mach 2 (T3-I), climb vs. D-6398 (T3-H)
- [ ] Lateral-directional stability (AP-6), dynamic stability (T3-J), roll rate (T3-K)
- [ ] Slow flight, BLC flaps, approach speeds per manual
- [ ] Pitch-up behaviour, APC (T3-L)

## Phase 3: animations and exterior model
- [ ] Control surfaces, flaps, gear, canopy, nozzle, drag chute
- [ ] Detailed model, LODs, PBR textures, livery

## Phase 4: cockpit
- [ ] 3D cockpit
- [ ] Basic instruments (airspeed, altitude, Mach, attitude, engine)
- [ ] Switches/levers with ModelBehaviors

## Phase 5: systems
- [ ] Electrical, hydraulics, fuel, cold start
- [ ] Navigation (TACAN, INS depending on scope)
- [ ] Sounds
