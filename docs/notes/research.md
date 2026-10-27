# Research: F-104 data and jet development in MSFS (state 2026-10-25)

## New source: NASA CR-96008 (Teper, "Aircraft Stability and Control Data", 1969)
File: `docs/sources/NASA_CR-96008_Teper_Stability_Data.pdf` (NASA, public domain; found at jsbsim.sourceforge.net).
F-104 section PDF 80-85 (Section VII). Variant not stated, primary source "unpublished data". Longitudinal only
("Lateral data not available"). Body-fixed stability axes, S = 196.1 ft², c̄ = 9.55 ft, b = 21.9 ft.

| Condition | 1 Takeoff | 2 Start Cruise | 3 End Cruise | 4 Vmax | 5 Vmax sea level |
|---|---|---|---|---|---|
| h ft / M | 0 / 0.273 | 30 000 / 0.84 | 30 000 / 1.0 | 30 000 / 1.9 | 0 / 1.36 |
| W lb / x_cg/c̄ | 24 000 / 0.046 | 23 310 / 0.040 | 14 960 / 0.18 | 15 000 / 0.18 | 15 000 / 0.18 |
| tip/pylon tanks | on/on | on/on | clean | clean | clean |
| flaps leading/trailing edge | -15° / 15° | -3° / 15° | -3° / 0° | -3° / 0° | -3° / 0° |
| q̄ lb/ft² | 110.5 | 310 | 440 | 1590 | 2740 |
| Iy slug·ft² | 65 000 | 64 500 | 56 650 | 56 650 | 56 650 |
| α₀ ° | 19.6 | 4.0 | 2.0 | 1.4 | 1.1 |
| CL | 1.125 | 0.342 | 0.1375 | 0.0383 | 0.0278 |
| CD | 0.185 | 0.0365 | 0.04 | 0.041 | 0.045 |
| CLα /rad | 4.44 | 4.97 | 5.10 | 2.92 | 4.18 |
| CLδe /rad | 0.762 | 1.015 | 1.071 | 0.6925 | 0.8035 |
| Cmα /rad | -1.496 | -1.319 | -1.564 | -1.255 | -1.80 |
| Cmα̇ | -3.44 | -3.90 | -4.99 | -3.04 | -2.005 |
| Cmq | -5.615 | -8.03 | -8.60 | -4.59 | -6.825 |
| Mδe 1/s² (Tab. VII-C) | -4.67 | -17.8 | -30.8 | -57.2 | -140 |
| -> Cmδe = Mδe·Iy/(q̄ S c̄) | -1.43 | -1.98 | -2.12 | -1.08 | -1.55 |

(Condition 1 lists M 0.237 in Tab. VII-B vs. 0.273 in VII-A, as in the original.)

**Cross-check:** condition 3 (clean, M 1.0, α 2.0°) CL 0.1375 vs. TN D-7137 Table 1 (M 1.0, α 2°) 0.140 -> matches
(-2 %). Independently confirms the target table.

**Consequences for the flight model:**
- All-moving tail: CLδe 0.76-1.07/rad (subsonic), referenced to S. Converted to the tail area of 48.2 ft²:
  a_t = CLδe × 196.1/48.2 = 3.1 (takeoff) / 4.1 (M 0.84) / 4.4 (M 1.0). CR-2144 approach: 2.8.
  -> `elevator_lift_coef` ~3-4.4; tutorial range 3.3-4.25. Chosen 4.1 (cruise) [Q].
- Cmα ≈ -1.3 to -1.6/rad with CG 4-18 % MAC: target for longitudinal stability (T3-G: −Cmα/Cmδe 0.67-1.05).
- Condition 2 (M 0.84, 30 000 ft) has tip tanks and 15° flaps -> not clean.

## MSFS: autopilot and trim (DevSupport)
- Thread "Elevator trim held/reset to zero when pitch_use_elevator_only = 1" (DevSupport, 2026):
  `[AUTOPILOT] pitch_use_elevator_only = 1` -> the AP drives the elevator directly and forces trim to 0.
  Since SU7 beta additionally `autopilot_resets_trim_when_not_used` (Asobo answer, "fixed").
- Our test bed (systems.cfg from SimpleAircraft): `max_pitch = 10`, no `pitch_use_elevator_only` -> the AP only
  trims. Solved via the trim range from FM 6-5 (AP-2b).
- PID primer: `pitchPID` sets the elevator angle; AP controller parameters in ai.cfg/engines.cfg.

- 2026-10-27 confirmed in our own dry runs (should have been read before changing the AP!): elevator-only AP reset
  the trim to 0 and gave only ~1.4-3° elevator -> reverted. With the AP engaged the trim is locked.
- 2026-10-27 trim runs down by itself (≈ 0.8°/s) after AP disconnect. Community explanations (unverified for us):
  an ANALOGUE controller axis bound to elevator trim resets the trim to the axis position after AP disconnect;
  piloting assistance auto-trim; duplicate bindings
  ([flyawaysimulation](https://flyawaysimulation.com/ask/answers/trim-keeps-returning-to-neutral-microsoft-flight-simulator/),
  [MSFS forum: elevator trim is broken](https://forums.flightsimulator.com/t/elevator-trim-is-broken/272761/65),
  [MSFS forum: abrupt control input reset when disconnecting AP](https://forums.flightsimulator.com/t/abrupt-control-input-reset-when-disconnecting-autopilot/727385)).
  No SimConnect event/SimVar found to switch assistance options -> pete sets them in the menu.

## Flight-test methodology sources (research 2026-10-27)
- **USAF/USN Test Pilot School course books are approved for public release** (AvioConsult link list,
  https://avioconsult.com/links.htm): USAFTPS Performance Phase Textbook Vol. I (1986, DTIC ADA170957), Flying
  Qualities Textbook Vol. II Parts 1/2 (ADA170959/ADA170960), Flying Qualities Phase Planning Guide (1996), Pitot-
  Statics and the Standard Atmosphere (AD1115005); USNTPS FTM-103 Fixed Wing Stability and Control, FTM-108 Fixed
  Wing Performance, FTM-109 Systems Testing. -> methods: level accelerations, sawtooth climbs, takeoff/landing,
  turns, stall approaches, doublets, steady heading sideslips, trim shots (to fetch for the test program).
- AFFTC era documents (1959, same time as the F-104 Category II tests): Flight Test Handbook Performance Part II
  (AFFTC TN 59-22, AD0215865), AFFTC Stability and Control Techniques (TN 59-21, AD0226523) - catalogued on
  Contrails (IIT), not scanned; DTIC copy possible.
- F-104 specific: "Lockheed F-104 Test Pilot's Notebook" (Scribd 788676444, 52 pages, uploader only, no author/date
  visible - not verified, Scribd login needed). AFFTC report on the F-104 high-density fuel range test
  (FTC-TDR-61-62). No F-104 Category II report found online yet. Cornell wind-tunnel F-104 dynamic tests AFFDL
  TR 66-153 (AD0651437).
- Phase model (Category I contractor / II AFFTC / III operational) is the USAF practice of the 1950s; for us the
  equivalent is our T0-T3 levels + build-up per test card.

## MSFS: horizontal tail (forum)
- User reports: `htail_area = 0` + full area in `elevator_area` works (not counted twice); some recommend 0.1
  instead of 0. Confirmed in the sim: 0 becomes 0.1 ft² (debug warning).

## MSFS: jets in general
- Early MSFS 2020 jets were stuck at Mach 1 (2020); afterburners "not properly supported" back then
  (IndiaFoxtEcho). In MSFS 2024: `afterburner_available`, `afterburner_on_thrust_table`,
  `afterburner_throttle_threshold`, `AfterBurnThrustSpecificFuelConsumption` (used with gross-thrust fuel flow).
- Microsoft "Turbojet Static Performance Tool" (Excel, steady-state only) for engines.cfg (AP-7).
- No open-source MSFS military jet found; JSBSim/FlightGear: no F-104 model found.

## Not found / open
- F-104G autopilot data (FM). Vertical tail area of the F-104G (larger than the A; CR-2144 drawing of the A gives
  ≈ 38 ft²).
- NACA RM on the F-104A at M 1.82/2.01 (wind tunnel, longitudinal/lateral stability) and XF-104 transonic: possibly
  useful for lateral work (AP-6); not downloaded.

Links:
[CR-96008](https://jsbsim.sourceforge.net/NASA_CR-96008.pdf),
[DevSupport pitch_use_elevator_only](https://devsupport.flightsimulator.com/t/elevator-trim-held-reset-to-zero-when-pitch-use-elevator-only-1/18041),
[Flight Model Physics Primer](https://docs.flightsimulator.com/msfs2024/retail/samples-tutorials/primers/flight-model-physics-primer/),
[PID Primer](https://docs.flightsimulator.com/msfs2024/retail/samples-tutorials/primers/pid-primer/),
[Forum Fast Jet Flight Model](https://forums.flightsimulator.com/t/fast-jet-flight-model/551996).

## Best practices for MSFS 2024 aircraft development (research 2026-10-25 afternoon)
**Official checklist "Aircraft Creation Workflow"** (approximate order): 1 preparation (audio, modular project) -
2 exterior model (file setup, materials, turbines, canopy, wheels, lights, collision, AO, animations, LODs) -
3 cockpit (optimization, LODs, gauges, lights, animations, EFB, VR) - 4 liveries - 5 export/package -
**6 flight model** (aerodynamics, geometry, wheels/contact points, weight and balance, engines, electrical, fuel,
fine tuning, testing) - 7 model behaviors - 8 instruments (HTML/JS, WASM) - 9 career - 10 cameras/lights -
11 checklists - 12 audio (Wwise) - 13 liveries (cfg) - 14 passive aircraft.
-> For us: flight model first on the test bed (running), then model/cockpit (roadmap phases 3/4).

**"Testing the Aircraft" (official test sequence, window "Debug Aircraft Tracking", weather preset Clear Sky = ISA,
sea level):** 1 takeoff distance (ground roll + 50 ft) - 2 takeoff trim: the aircraft must not lift off by itself
before/at rotation speed (guideline ~30 % above) - 3 climb (Vx/Vy, stabilized without control input) - 4 top speed
(sink in from above, then level at full power) - 5 fuel consumption/cruise - 6 stability: static (pitch pulse),
dynamic (short period, phugoid 20-60 s, Dutch roll, spiral: doubling of a 30° bank > 20 s), lateral: **steady
heading sideslip** at cruise and approach speed - 7 roll rate (full aileron) - 8 flaps - 9 stall (max weight, idle,
1.4 Vs, 1 kt/s) - 10 elasticity (full pull at Vne/Va, n_y max) - 11 approach (1.3 Vs0, 500 ft/min) - 12 damage last
(crash detection on: flaps, overspeed > 6 s above Vne, g limits, landing gear).

**Weight and Balance (tutorial):** Weight overlay + window "Sim Tuning"; empty CG "outside of 10 % to 35 % MAC may
result in an uncontrollable aircraft" (ours: 7 % [S], real F-104 4-18 % per CR-96008; so far unremarkable);
variable loads (pilot, passengers) should have mass 0, mass then comes from navigation_graph.cfg (ours: pilot
230 lb fixed -> check, roadmap career/modular); engine point at the nozzle exit (satisfied, Engine.0 at -19 ft).

**Further points:** ideally normalization makes "zero changes" (geometry consistent with performance; our nCl
0.98-1.01 ✓). SDK 2024 docs on wing/aero largely as in 2020 (DevSupport). Do not switch SDK versions mid-project
without a backup. FlyByWire: one git repo, aircraft in a subfolder, build scripts. No official .gitignore guidance found.
Sources: [Aircraft Creation Workflow](https://docs.flightsimulator.com/msfs2024/retail/samples-tutorials/tutorials/aircraft-checklist/aircraft-creation-workflow/),
[Testing the Aircraft](https://docs.flightsimulator.com/msfs2024/retail/samples-tutorials/tutorials/tuning-the-flight-model/testing-the-aircraft/),
[Weight and Balance](https://docs.flightsimulator.com/msfs2024/retail/samples-tutorials/tutorials/tuning-the-flight-model/weight-and-balance/),
[DevSupport: 2024 SDK flight model](https://devsupport.flightsimulator.com/t/msfs-2024-sdk-does-not-show-any-major-flight-model-updates/10562),
[FlyByWire setup](https://docs.flybywiresim.com/dev-corner/dev-guide/setup-environment/).
