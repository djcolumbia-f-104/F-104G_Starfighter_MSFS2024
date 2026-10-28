# F-104G Starfighter for MSFS 2024: project notes

From-scratch aircraft add-on: Lockheed F-104G Starfighter for Microsoft Flight Simulator 2024.
**Communicate with the user (pete) in German.** The whole repository is in English (docs, code, cfg comments, script
output) since 2026-10-25; write new comments in English too.
Public repo: https://github.com/djcolumbia-f-104/F-104G_Starfighter_MSFS2024 (commit identity:
`pete <273588133+djcolumbia-f-104@users.noreply.github.com>`, set locally; push via Git Credential Manager).

## >>> CONTINUE HERE (state 2026-10-28 evening) <<<
**TOMORROW START HERE (note for 2026-10-29):**
0. pete builds/restarts tonight (pending: `drag_coef_spoilers` 0.21 -> 0.43 = drag chute, needs FULL restart).
   Test configuration every session: MSFS assistance off, **weather clear skies / wind calm / ISA** (check with
   AMBIENT_WIND_VELOCITY), flight on EDDM 26L. Engine cold? `sim_event ENGINE_AUTO_START`. Fuel: `tools/refuel.py`
   (4 080 lb fuselage, tip tanks EMPTY) instead of reloading. After every sim restart: trim-hold check (AP off ->
   SimVar trim 5° must stay).
1. **F2 regression** (landing with chute): `landing_test.py <csv> 6 2.5` -> FM A8-3 2 760 ft scaled by
   (166.5/TD IAS)²; target ±10 %. F3 (no chute) already passes (+9.4 %, brakes 0.82). If the chute is now too strong
   or weak, adjust drag_coef_spoilers (MSFS applies ≈ 1/3 of it on the ground).
0b. **Data index first** (pete, 2026-10-28): write `docs/data/README.md` - for every `flighttest_*.csv` (+ `_simlog`):
   test ID, date, conditions (weather live/ISA-calm, weight, cfg state / relevant commit), result and validity
   (valid / superseded / invalid, e.g. live-weather runs). Purpose: validation evidence and re-analysis without
   re-flying; MSFS itself needs no curves from our data (FM values go into REFERENCE SPEEDS/checklists later).
   Later: plot tool sim-vs-FM from the raw data (regenerable charts for the docs).
0c. Check pete's input (research.md, 2026-10-28 evening): verify CG limits 0.07-0.164 MAC in CR-2144; new test D1b
   takeoff ground run vs. FM Fig. A2-4.
0d. Targeted primary-source search directly in NASA NTRS (API: https://ntrs.nasa.gov/api/citations/search?q=...)
   and DTIC - not via Gemini (hallucinates): F-104 flight tests with landing-configuration / BLC data, J79
   part-power fuel consumption, F-104 CG limits. Download found PDFs to docs/sources/ and read the numbers there.
1b. **All tests before 2026-10-28 afternoon ran in LIVE weather** (pete). Re-verify in ISA/calm: B6/B5, T3-F drag,
   T3-H excess thrust, thrust/fuel flow; spot checks T3-E2/T3-J (measurements.md note, test plan step 2b).
2. Then test plan order (`docs/test-plan.md` section 4): B4 glide L/D, D5 fuel flow (strong evidence: approach 91 % N1
   burns 8 270 lb/h at 5 170 lbf -> part-power TSFC ≈ 1.25 vs. ≈ 0.85-0.9), B7 minimum speeds.
3. MCP `landing` tool output parsing predates the hand-flown script -> update or call the script directly.
Results 2026-10-28 (details `docs/notes/measurements.md`, cards in `docs/notes/test-cards/`):
- Hand-flown landing script complete (dry runs 13-17, outlier rejection, FM go-around flown by the script, 24-30 ft
  height loss); normal landing F2 ✓ (162 KIAS) and F3 ✓ in live weather, re-flown in calm weather after changes.
- **LAND flap drag 0.12 -> 0.08** (3 FM points: Fig. 6-8 go-around climb, FM 3-41 flat final, approach rpm) ->
  B6 +1 061 ft/min ✓, B5 194 KIAS ✓ (`tools/config_test.py`, card B5-B6-landing-config.md).
- **Flap damaging-speed 240 -> 370** (it applies to every position; TAKEOFF flaps stuck in the go-around).
- **toe_brakes_scale 0.68 (template) -> 0.82** (calm-weather ground roll +20 % -> F3 +9.4 % ✓).
- Live weather gave false good ground rolls (headwind) and a 22° gust roll in the flare -> calm weather mandatory.

## Older state (2026-10-27 evening)
**Since 2026-10-27: every sim flight test follows the test-card method (skill `f104-testcard`, cards in
`docs/notes/test-cards/`): card with preconditions + expected values, desk check, go/no-go, build-up run, then the test.**
**Test plan with all test points and the iteration order: `docs/test-plan.md`** (phases A-H, FM/NASA references).
FM extract with checklists/limits/test reference values: `docs/notes/fm-procedures.md`.

**TOMORROW START HERE (note for 2026-10-28):**
1. pete: reload the flight (full fuel, EDDM 26L); MSFS assistance off (checked 2026-10-27, trim holds).
2. Dry run 13 (`landing_test.py <csv> 6 2.5 4000`) to confirm the outlier rejection (change control), then the real
   landing F2 (`landing_test.py <csv> 6 2.5`): TD IAS vs. Fig. 2-7, ground roll vs. A8-3. Card:
   `docs/notes/test-cards/T3-L-landing.md` (dry runs 1-12 with root causes).
3. Then test-plan order: B5 landing-config drag (N1 96-98 % vs. FM 87-90 %), B6 go-around climb, B4 glide, D5 fuel.
Key findings 2026-10-27: MSFS AP flies pitch by trim only (~0.13°/s) and LOCKS the trim while engaged; set trim with
the AP off (SimVar). `pitch_use_elevator_only` unusable (reverted). set_pos speed ≈ IAS, pitch negative = nose up.
landing_test.py now flies by hand (elevator PI on VS + pitch damping, aileron PID on a localizer bank target).
Older notes (2026-10-26, still valid as background):
- Drag chute = ground spoiler drag `drag_coef_spoilers` 0.21 (FM: chute only -12 %); A8-3 with chute 2 760 ft,
  A8-4 without 3 130 ft @ 17 900 lb. Landings 1/3 were belly landings (set_pos retracts the gear).
- MCP `landing` tool wraps landing_test.py (its output parsing predates the hand-flown rewrite - check).
1b. Idea from pete (YouTube training video): flap blowing - the BLC blows engine bleed air over the LAND flaps (FM 1-74,
   2-24/25: lift depends on engine rpm, effective above ~80 %, approach at ~88 %). Our LAND ΔCL (CR-2144) includes BLC
   at approach power, but the rpm dependence is NOT modelled (lift should drop at idle, e.g. in the flare/go-around).
   Search the web for the video/BLC data; possible implementation later (e.g. flaps lift via a power-dependent scalar).
2. Then: 3D model planning (AP-9) or remaining items (yaw SAS logic, CR-2144 δa definition, .gitignore `.opencode`
   line added by another tool - user decides).
State: flight model validated against NASA/FM for lift, drag, thrust to M 1.8, takeoff, climb, lateral/Dutch roll,
speed brakes, trim, LAND/TAKEOFF flaps (TE + LE flaps, T3-L), first scripted landing. Details below and in
`docs/notes/measurements.md` (newest entries at the end).

**Achieved (all evidence in `docs/notes/measurements.md`, sim rounds A/B/B2/C):**
- Lift T3-A ✓ (1° band means within ±0.03 of NASA TN D-7137), drag T3-F ✓ (1.00-1.04 x NASA), static thrust ✓
  and afterburner thrust in flight ✓ (-2..-4 %), military fuel flow ✓, AB fuel flow in flight ✓ (static -33 %,
  known weakness), EGT at military ✓ (593 °C). All-moving tail (htail_area 0, elevator_lift_coef 4.1), trim range
  11°/5°, takeoff trim 5°, tail contact point 12.3°, CG verified. Autopilot holds altitude down to ~213 kt (≈ 1.27 Vs).
- Test tools: check_cfg.py (T0/T1), preflight.py (T2), analyse_lift/drag.py (T3), screenshot.ps1, simlog.py.
**Round D (2026-10-25):** rudder fixed with `rudder_maxangle_scalar = 0.32` (T3-E β/δr 0.34 ✓). Roll due to
sideslip is strong, as in the real F-104 (FM 6-2) - the AP wing leveler cannot hold it.
**Round D part 2 / round E:** `tools/sideslip_test.py` (closed-loop sideslip) works; yaw damper (gain 1.0) was
destabilizing -> disabled in systems.f104.cfg. **T3-E2 passed (round E):** δa/δr 0.39, β/δr 0.32, both within CR-2144
Table III-9 (0.27-0.47 / 0.32-0.42; the rudder's own rolling moment L'δr must be included). AP-6 done.
Positioning only at ≥ 16 500 ft (α = 0 after positioning, AP pitches at 2°/s; even then the jet sinks ~6 500 ft).
**T3-D takeoff PASSED (2026-10-25, `tools/takeoff_test.py`, run 6):** liftoff 185 kt vs. FM 179 kt (+3.4 %) after two
fixes: flap lift formula (AP-10, SDK radians + add incidence) and flaps/gear that never moved (hydraulic system_type
without a hydraulic system in the template -> now electric).
**T3-H climb potential (2026-10-25, `tools/analyse_climb.py`):** subsonic ✓ at 10 000/20 000 ft; supersonic
-20 %/+30 % of excess thrust (≤ 800 lbf, opposite signs) -> accepted, revisit with T3-I.
**Round F (2026-10-25 evening):** speed brakes ✓ (ΔCD 0.046), AP pitch rate 5°/s ✓, yaw damper 0.3 harmless (no effect).
**Finding: Dutch roll period 0.87 s vs. ~2.0 s (CR-2144) -> directional stiffness ~5x too high (AP-11).**
**Project MCP server `f104` (2026-10-26, `tools/mcp_f104/server.py`, registered in `.mcp.json`) - USE IT for the
test loop, it returns only key figures:** `check_build`, `build_cfg`, `preflight`, `sim_state`, `position` (AP verified
before/after, re-arms ALT hold -> sinks only ~300 ft), `runway_start`, `takeoff`, `doublet`, `sideslip`, `accel_run`,
`log`, `analyse(lift|drag|climb)`, `sim_event`, `restart_sim` (kill + Steam start, waits for SimConnect; the user
still starts the flight). Runs with the simconnect-mcp venv Python; each action is a subprocess with its own short
SimConnect connection. Lateral cfg changes: Build All + aircraft reload is enough (AP-11). **Lift/flap changes need a FULL
sim restart** (normalization; debug Sim Curves TgtClAOA0 vs. FinClAOA0 shows it, T3-L 2026-10-26).
**S12 done (2026-10-26):** trim 1.2° at M 1.27 / 16 500 ft, 2.0° at M 1.8 / 40 000 ft - far from the stops.
**T3-L approach configuration PASSED (2026-10-26):** TE + new LE flaps; CL 0.855 at α 4.1° (CR-2144 0.845), trim 5.6°.
**First scripted landing (2026-10-26, MCP `landing`):** touchdown 162 KIAS (FM 166-171), ground roll 3 158 ft (FM ≈ 2 850).
**Next step:** see TOMORROW START HERE above. Open: CR-2144 δa definition (one aileron or sum).
**How to test: `docs/notes/test-procedures.md` (cookbook).**
**Since 2026-10-25 `docs/flight-model-plan.md` is authoritative** (iteration loop, test levels T0-T3, work packages,
step-by-step schedule in section 3a, official Microsoft test sequence).

**Sim workflow (proven):** Dev Mode → Project Editor → `F104G.xml` → Build All → restart flight (enough only for
engines/aircraft; **after flight_model changes restart the sim COMPLETELY**, normalization only runs at sim start) →
aircraft "F-104G Starfighter Pruefstand (TESTBED)". Check `BuilderLogError.txt` after every build (check_cfg.py T1
does this). Flight tests: Claude positions the aircraft and flies via MCP (autopilot/throttle), logs with
`tools/simlog.py` in the background. `msfs_get_simvars_bulk` returns stale values at times -> use
`msfs_watch_simvar` or `simlog.py`. **Query indexed SimVars via MCP with `index=1`, never `NAME:1`** (silently
returns 0 -> false alarm on 2026-10-25).

## Basics
- Variant: **F-104G** (inertia taken from the F-104A).
- **Test bed**: the package uses model, textures, sounds, cameras and cockpit of the SDK sample `SimpleAircraft`
  (propeller aircraft), but the complete F-104G flight model and a J79 jet engine. Purpose: test the flight model in
  the sim before a dedicated 3D model exists. Visuals, gear stance and sounds therefore do not match the F-104.
  These SDK assets are excluded from the public repo (.gitignore); copy them from the SDK sample.
- MSFS 2024 SDK 1.8.1 installed: `C:\MSFS 2024 SDK` (samples under `Samples\DevmodeProjects\SimObjects\Aircraft`;
  no jet sample there). Blender is not installed.
- **MCP server `simconnect`** (simconnect-mcp 1.0.2 by robin24, code reviewed 2026-10-24) is registered for the user:
  venv `C:\Users\pete\AppData\Local\simconnect-mcp\.venv` (Python 3.13). Tools `msfs_*`: read/write/watch SimVars,
  position the aircraft, load/save flights. Call `msfs_connect` first; after a sim restart `msfs_disconnect` +
  `msfs_connect`. HubHop tools go to the internet and are not needed.

## Important rules
- **Change control (since 2026-10-27): validated values are frozen.** A cfg value or script behaviour that passed a
  test (see `docs/notes/measurements.md`, "PASSED") is only changed with (1) a documented reason from test data, (2) an
  entry in the test card / measurements, and (3) the regression tests of the affected area re-run afterwards
  (table in skill `f104-testcard`, section "Change control"). Prefer fixing a test script over changing a validated
  cfg value (2026-10-27: `pitch_use_elevator_only` broke the AP used by all earlier tests -> reverted).
- **No third-party assets**: nothing from the DCS mod (VSN F-104C, in `Downloads\F-104C Standalone`) and nothing
  from the SimSkunkWorks package. Model, textures and code must be self-made or cleanly licensed. The VSN manual in
  `docs/sources/` is reading material only. The SDK sample assets are test bed only.
- **Do not edit cfg files in `common/config` directly** (flight_model, engines, aircraft, cockpit, systems): they
  are generated by `tools/build_cfg.ps1` from `source/cfg/*.f104.cfg` + SDK template. Make changes in `source/cfg/`.
- Back numbers with sources; mark them in the cfg as [Q] source / [M] measured / [S] estimate, derivation in
  `docs/flight-model-values.md`, raw data in `docs/aircraft-data.md` and `docs/data/`.
- MSFS units: feet, pounds, knots, slug·ft². Datum = 25 % MAC (F.S. 472.5 in, W.L. 100).
- One change per sim round where possible (A/B), see the plan.

## Project layout
```
F104G.xml                       project file for Dev Mode (Project Editor → Build)
PackageDefinitions/             pete-aircraft-f104g.xml (ModularSimObject) + ContentInfo/Thumbnail.jpg (SDK, not in repo)
PackageSources/SimObjects/Airplanes/pete-f104g/
    common/config/              aircraft/flight_model/engines/cockpit/systems.cfg GENERATED; cameras/gameplay/ai.cfg from SDK
    common/flt                  flight states (cleaned with clean_flt.py, YawDamper=True)
    common/model, texture, texture.base, sound, soundAI, panel   test bed assets from SDK SimpleAircraft (not in repo)
    presets/pete/f104g/config/aircraft.cfg   preset (MODULAR_MERGE)
    liveries/pete/testbed/      livery "Pruefstand"
source/cfg/                     F-104 values (source files for build_cfg.ps1)
source/blender, textures, sounds  working files (not in the package)
tools/                          Python scripts (venv tools/.venv), build_cfg.ps1, screenshot.ps1
docs/
    flight-model-plan.md          plan, test levels, acceptance criteria, schedule (authoritative)
    aircraft-data.md, flight-model-values.md, roadmap.md
    data/                      cleaned NASA tables (CSV), CR-2144 extract, flight test logs flighttest_*.csv
    sources/                    PDFs (not in repo), Markdown conversions, manual-index.md
    sdk-ref/                    MSFS 2024 reference copies (local only, not in repo)
    notes/                    measurements.md (all test results), test-procedures.md (cookbook), research.md,
                                engine-start.md, msfs2024-sdk.md
Packages/, _PackageInt/, PackagesMetadata/   build output
```

## Tools (tools/, run with tools\.venv\Scripts\python.exe -I)
- `build_cfg.ps1`: generates the cfg files (calls `merge_cfg.py`). Run after every change in `source/cfg/`.
- `fm_calc.py <project>`: wing geometry, CL/CD tables, Oswald factor from `docs/data`.
- `engine_calc.py <project>`: thrust and airflow tables from NASA thrust, incl. sim-vs-NASA check.
- `sdkref_params.py <docs/sdk-ref/x.md> [section]`: compact parameter list of an SDK reference page.
- PDF: `pdf_check.py`, `pdf_pages.py`, `pdf_sheet.py` (contact sheet), `pdf_clip.py` (crop, `--rot 90`).
- `simlog.py <csv> <seconds> [hz]`: flight data logger (2 Hz). Run with the Python of the MCP venv:
  `C:\Users\pete\AppData\Local\simconnect-mcp\.venv\Scripts\python.exe -I tools\simlog.py ...` (in the background).
- `analyse_lift.py <project> <csv>`: T3-A (CL sim vs. NASA, 1° band means) and T3-G (trim gradient).
- `analyse_drag.py <project> <csv> [t_from t_to]`: T3-F, CD in the sim (flight path balance) vs. NASA.
- `check_cfg.py <project>`: T0 (rules per work package) + T1 (build current, no new error log).
- `preflight.py` (MCP venv): T2 in the running sim (test bed, engine, fuel selector, initial state).
- `screenshot.ps1 <out.png> -Sim`: Claude takes screenshots itself (brings the sim forward briefly, 3840x2160, then
  VS Code back). The user must open Dev Mode windows (e.g. "Debug Aircraft Sim Curves") once.
  Crop text with pymupdf (pixels x 0.75 = page coordinates).
- `clean_flt.py <flt folder>`: removes piston engine states from .flt files.
- `build_cfg.ps1 -Engine minimal`: diagnostic engine (required parameters only).
- `mcp_f104/server.py` + `mcp_f104/sim_actions.py`: project MCP server (see CONTINUE HERE).
- `doublet_test.py`, `sideslip_test.py`, `takeoff_test.py`, `analyse_climb.py`: T3-J, T3-E2, T3-D, T3-H/I.
- `landing_test.py <csv> [nm] [glide] [high_ft] [nochute]`: hand-flown approach/landing (F1-F3), dry run with a
  virtual runway; `config_test.py <csv> <alt> climb|level [ias] [sb]`: B5/B6 landing configuration at Military;
  `refuel.py`: standard fuel state via SimVars (MCP venv Python).
- `C:\MSFS 2024 SDK\Tools\bin\fspackagetool.exe` attaches to the running sim and waits -> do not use;
  build via Dev Mode in the sim.

## MSFS findings
- `wing_sweep` = leading-edge sweep; no tip chord (from S, b, root chord). Tables `x:y, x:y` (AoA in rad, max. 17
  or 47 entries).
- Jet thrust: gross = static_thrust × n1_and_mach_on_thrust_table(N1c, M) × AB factor × δ_total, minus ram drag
  (corrected_airflow_table × inlet_area). `uncorrected_commanded_Ne_table` controls mechanical N1 (like the J79) ->
  corrected N1 > 100 % at altitude. Formulas: `docs/sdk-ref/engines-additional-information.md`.
- **Distinguish table formats** (`docs/sdk-ref/cfg-files-general-information.md`): 1D curve `x:y, x:y`; old 2D
  table `0:m1:m2, n1:z:z`; **nD table** (new parameters, e.g. `uncorrected_commanded_Ne_table`):
  `x1, x2, x3 :: y1, y2, y3`. Wrong format -> build succeeds, but `BuilderLogError.txt`
  (in `%APPDATA%\Microsoft Flight Simulator 2024\`) reports "can't parse value".
- Build warning "absolute path in image or buffer uri" comes from the SDK sample gltf (test bed), harmless.
- Test bed start (2026-10-24): with `starter_type = 2` (air start) the starter only reached 21 % N1, no ignition
  -> set to 0 (electric). `auto_ignition` only applies to [PISTON_ENGINE].
- **Engine start troubleshooting: `docs/notes/engine-start.md`** (start chain, debug fields, findings).
  Main finding: the template .flt files set a piston engine initial state -> cleaned with `tools/clean_flt.py`.
  Engine runs since 2026-10-24 (missing: temperature/pressure model egt/itt/epr/oil/fuel_press in TURBINEENGINEDATA).
  Always check .flt files when taking new template assets.
- **MSFS turbines are N2 based**: ignition (`min_n2_for_combustion`), fuel (`min_n2_for_fuel_flow`), starter
  (`n2_raw_starter`, `starter_time` default only 1.5 s!), N1 via `n2_to_n1_table` (J79 single spool: N1 = N2).
  Working reference for structure/parameters: FlyByWire A32NX `engines.cfg` (open source, GitHub) - read only.
- Second reference (read only, freeware with Milviz permission): `Downloads\F-4J Phantom II_vjdRH\...\engines.cfg`,
  J79 in MSFS 2020; afterburner there via thrust table up to 125 % N1 (fallback). Performance values "about right"
  per readme -> do not use.
- Engine source: `docs/sources/J79_Engine_System_Stoelinga.pdf` (J79-GE-11A: 160 lb/s, idle 67 %/500 lbf,
  military 10 000 lbf, min AB 12 320 lbf, max AB 15 800 lbf, SFC AB 1.97). PDF has a "no extraction" flag ->
  the .md is a local reading aid only (not in repo).
- `cockpit.cfg` of the template had all instrument ranges = 0; markings now from FM 5-2/5-3 in
  `source/cfg/cockpit.f104.cfg`. External HUD bar still shows piston values (AP-9, later).
- Inlet: `inlet_area = 5` ft², `corrected_airflow_table` = airflow per ft² (160/5 = 32 at 100 %).
- CG: tank positions [S] so that 50 % fuel ≈ 7-10 % MAC; sim value matches hand calculation (AP-8 done).
- Parking brake does not hold full afterburner -> static runs up to military (plus a short AB burst).
- Open: whether lift_coef_mach_table acts twice together with internal compressibility.
- **Flight model findings 2026-10-25** (evidence in `docs/notes/measurements.md`):
  - Normalization (debug "Sim Curves") only at sim start; target = lift_coef_aoa_table at α = 0 with the tail at
    `htail_incidence`. For trimmed NASA data use htail_incidence = trim at α = 0 (here 0), NOT cruise trim.
  - Positive `htail_incidence` acts like nose-up trim; ELEVATOR_TRIM_POSITION positive = nose up.
  - `wing_camber = 0` becomes 1° internally -> extra lift; FSX legacy terms (lift_coef_delta_elevator etc.) set to 0.
  - `rudder_lift_coef` = whole fin (directional stability! sets the Dutch roll period; 2.0 with the G fin, AP-11). `rudder_effectiveness` scales that lift and does not
    change the β = δr equilibrium. Rudder authority via `rudder_maxangle_scalar` (SDK: < 1 for flap rudders).
    `elevator_maxangle_scalar` = 1 for the all-moving tail.
  - All lateral FSX coefficients of the template (roll_moment_slip_angle, yaw_moment_* ...) are legacy/unused;
    lateral stability comes from geometry (vtail, wing_dihedral, fuselage_lateral_cx).
  - Turbine: `egt_tuning_constant` has no effect -> `egt_peak_temperature`. Fuel flow via gross thrust
    (`use_gross_thrust_on_fuelflow`); AB TSFC only applies to the AB thrust increment.
  - Starting from the world map ignores .flt files (yaw damper off) -> send `YAW_DAMPER_ON`.
  - `htail_area = 0` becomes 0.1 ft² (warning in debug, harmless).
  - Flaps are modelled as an INCIDENCE increment of the flapped wing section (≈ 0.62 x angle x lift scalar): above
    ~30 (angle x scalar) the section stalls -> no flap lift (T3-L). Split large flap lift onto TE + LE flaps ([FLAPS.1]).
    Check with debug Sim Curves: TgtClAOA0 vs. FinClAOA0 with the flaps out.
  - Flaps: ΔCL = lift_coef_flaps x lift scalar x deflection in RADIANS; per-position `add incidence` (default 0.5)
    adds only half at α 0 -> set it to 1 and scale per position (8 values in `flaps-position.i`).
  - `AP_ALT_HOLD_ON` holds the current altitude; positive `AXIS_RUDDER_SET` = nose left. Python-SimConnect lacks some
    events (`AP_VS_ON`): map them with `SimConnect.EventList.Event(b"AP_PANEL_VS_ON", sm)`.
  - Flaps/gear with `system_type`/`gear_system_type` = 1 (hydraulic) do not move without a [HYDRAULIC_SYSTEM] with
    pressure -> always check the real angle (TRAILING_EDGE_FLAPS_LEFT_ANGLE, GEAR_TOTAL_PCT_EXTENDED), not the lever.

## Python
- Python 3.15.1 (default) is too new for many packages; project venv `tools\.venv` (3.13, markitdown, PyMuPDF).

## Sources (details in docs/aircraft-data.md, docs/notes/research.md)
- `docs/sources/FlightManual-F-RF-TF-104G.pdf`: T.O. 1F-104G-1, pure scan (694 pages); page index `manual-index.md`.
  Reading: render pages with `pdf_pages.py` (130 dpi text, 150-200 dpi tables), search with `pdf_sheet.py`.
- `NASA_TN-D-6398`: geometry table, climb performance. `NASA_TN-D-7137`: CL(α,M), CD(M,CL), thrust, fuel flow
  (cleaned in `docs/data/*.csv`; markitdown tables are misaligned, always check against the scan).
- `NASA_CR-2144`: F-104A inertia, derivatives, three-view (PDF 38-66, printed sideways).
- `NASA_CR-96008` (Teper 1969): F-104 longitudinal derivatives for 5 flight conditions (PDF 80-85), see research.md.
- NACA RM SL56H06 (1956, NTRS 20090026345, not stored): 0.04-scale F-104A model, Table I = full tail geometry
  (fin 36.0 ft², LE sweeps wing 27.1°/htail 19.5°/fin 52.3°, ventral fins) -> `docs/aircraft-data.md`.
- https://www.916-starfighter.de/documents.htm: articles, F-104D/S manuals; no geometry data.
- Screenshots from Steam (F12) are in `C:\Program Files (x86)\Steam\userdata\1490757\760\remote\2537590\screenshots`.
