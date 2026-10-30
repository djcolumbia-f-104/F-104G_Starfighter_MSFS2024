# H3: BLC flap lift depending on engine rpm (flap blowing)

Method: skill `f104-testcard` incl. section 2b (analysis gate). Test plan H3. Idea from pete (2026-10-27, training video);
trigger 2026-10-31: the landing "skip" is a 1 ft float after the idle cut (measurements 2026-10-31).

## Objective / acceptance
FM 2-24/2-25 (PDF 156/157): "the additional lift afforded by BLC is dependent on engine airflow ... varies with airspeed,
altitude and engine rpm. The greatest effect is realized at low airspeed, low altitude and engine speeds above 80 percent,
although some effectiveness is still retained at lower power settings." Flare: smooth reduction to 82-83 %, IDLE as the
main gear contacts the runway; "an abrupt thrust reduction results in abrupt rolloff tendency and a rapid increase in rate
of sink"; nose lowered immediately after touchdown. BLC = compressor (17th stage) bleed air over the TRAILING-EDGE flaps
in LAND only (FM 1-73/1-74); leading-edge flaps not blown.
Acceptance:
1. Every validated test at approach/Military power unchanged (N1 ≥ 83 %): T3-L approach (CL 0.855 at α 4.1°), B5/B6, B7
   LAND, F2/F3 approach and touchdown speeds.
2. No float after the idle cut at touchdown (mains stay down: compression > 0 continuously, fastlog).
3. F3 ground roll closer to FM A8-4 (now +9.6 / +9.8 %); prediction below. F2 (chute) then re-tuned (drag_coef_spoilers
   0.12 was fitted with full BLC lift on the roll).
4. Qualitative FM behaviour: throttle chop in the flare -> clear increase in sink rate.

## Analysis (gate 2b, 2026-10-31)
1. **No native MSFS parameter** for power-dependent flap lift: `flaps-position-inhibit-*` know only air/ground/
   increasing/decreasing; `flaps-position-speed-factor` only airspeed (docs/sdk-ref/flight_model.cfg.md [FLAPS.N]).
2. **Override works** (ground test 2026-10-31, lever LAND): SimVar `TRAILING_EDGE_FLAPS_LEFT/RIGHT_PERCENT` is settable;
   0.38 -> TE 17.1° held > 1.5 s, LE flaps stay 30°, the next lever move takes over normally. -> BLC loss = smaller
   EFFECTIVE TE deflection (physically sound: an unblown 45° plain flap separates and acts like a ≈ 15-20° flap).
   A driver must write the value continuously (tests: SimConnect script; final add-on: gauge/WASM, AP-9).
3. **Size of the BLC lift** (no F-104 BLC data found: NTRS/web search 2026-10-31; NASA TN D-6943 flew with BLC OFF and TE
   flaps only to ≈ 13°): our LAND ΔCL 0.62 (CR-2144 approach, i.e. WITH BLC at approach power) = LE 30° 0.328 (unblown) +
   TE 45° 0.292 (0.62 x 0.785 rad x 0.6). Unblown TE at 45° ≈ the 15-20° value (TE TAKEOFF 15° = 0.136, validated) ->
   **ΔCL_BLC ≈ 0.12-0.15, design value 0.135** (≈ 22 % of the LAND flap lift, ≈ 9 % of W at the touchdown speed).
4. **BLC fraction f(N1)** [S] (bleed mass flow ∝ compressor delivery pressure, choked nozzles; design point = approach
   power): f = 1.0 at N1 ≥ 83 %, 0.9 at 80 %, 0.6 at 75 %, 0.3 at idle 67 % ("some effectiveness retained"), linear in
   between. Airspeed/altitude dependence (Cμ ∝ ṁ / q) neglected (low speed, low altitude only matter for landing).
   Spool-down time of the engine (≈ 2-3 s 83 -> 67 %) gives the smooth decay by itself.
5. **TE percent for a given f**: ΔCL_TE(f) = 0.292 - 0.135 (1 - f). Unknown which lift scalar MSFS applies at an
   intermediate angle with the lever at LAND: (a) the LAND stage scalar 0.6 -> δ = ΔCL / (0.62 x 0.6) -> f = 0: 24.2° =
   **54 %**; (b) scalar interpolated between TAKEOFF (0.84 at 15°) and LAND (0.6 at 45°) -> ≈ 18.8° = **42 %**.
   -> measure first (build-up 1).
6. **Prediction ground roll** (`tools/blc_roll_estimate.py`: decel = [μ (W - L) + D - T_idle] / m, μ_eff 0.483 calibrated on
   the sim F3 3 430 ft = +9.6 %; flap lift on the roll with add incidence 1 = 0.62 W at touchdown!):
   | BLC at idle | F3 roll | vs. FM A8-4 3 130 ft |
   |---|---|---|
   | full (today) | 3 430 ft | +9.6 % (measured) |
   | 30 % retained (design) | 3 198 ft | **+2.2 %** |
   | 0 % | 3 110 ft | -0.6 % |
   Touchdown: lift -0.7 x 0.135 x q S ≈ -1 700 lb (≈ 9 % W) after the spool-down -> the float disappears.
7. **Side effects**: pitch moment of the TE flap (add aft feet 0) -> small trim change at idle; drag of the TE flap falls
   with the angle (drag scalar of the stage) -> slightly less drag at idle (roll +); flap overspeed/damage logic uses the
   lever stage. Approach/Military tests unaffected (N1 ≥ 87 % -> f = 1, TE 100 %).

## Plan (next session)
Preconditions: as usual (check_build, refuel, runway_start before takeoffs). No cfg change, no restart needed.
1. **Build-up 1 (in the air, 12 000 ft, LAND flaps + gear, ≈ 190 KIAS, Military, level, trim 5.2°)**: set TE 100 % ->
   54 % -> 42 % -> 100 % (each 15 s, elevator holds altitude) -> ΔCL at constant α (or Δα at constant CL) -> calibrate
   the TE-percent law (a or b) to ΔCL_BLC 0.135. Also log the pitch/trim change and drag (N1/speed).
2. **Driver** `tools/blc_driver.py` (background, SimConnect, ≈ 10 Hz): lever LAND -> TE percent = p(f(N1)); else no write.
   Dry run on a virtual runway (landing_test.py high_ft 4000) with the driver: flare + idle cut -> sink increase, no float.
3. **F3 real landing** with driver + fastlog (compression) -> no float, ground roll vs. prediction (+2 %).
4. Regression: T3-L approach (unchanged at approach power), B6 go-around climb (Military), F2 with chute -> re-tune
   drag_coef_spoilers (expected lower than 0.12).
5. Later (AP-9): the driver as an in-aircraft gauge (JS/WASM or model behaviour), so the effect exists without scripts.

## Runs
| Date | Step | Result | Notes |
|---|---|---|---|
| 2026-10-31 | ground override test | TE percent settable, 0.38 -> 17.1° held, LE unchanged, lever move restores | basis of the design |
