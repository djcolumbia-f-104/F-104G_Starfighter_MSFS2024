# H2: APC stick shaker / kicker (MSFS native Stall Protection System)

Method: skill `f104-testcard` (incl. section 2b analysis gate). Script: `tools/config_test.py <csv> <alt> slow <ias_start>
clean|to|land <ias_stop> [alpha_stop]` (B7 procedure: level 1 kt/s deceleration, the elevator loop keeps pulling).
Test plan H2.

## Objective / acceptance
FM 1-69, 6-5..6-7: shaker first, then the kicker pushes the stick "slightly ahead of neutral" (abruptly) and keeps doing
so while beyond the boundary; shaker in all configurations, kicker inoperative with gear down / LAND flaps; thresholds
rise with flaps. References (1 g, low Mach):
| 19 100 lb (test weight) | shaker KIAS | kicker KIAS | source |
|---|---|---|---|
| clean | ≈ 222 | ≈ 196-198 | Fig. 6-4 (225 @ 19 500), FM 6-5 (175 kt @ 15 200), Fig. 6-3 |
| TAKEOFF | ≈ 188 | ≈ 179 | Fig. 6-4 (190), FM 6-5 (160 @ 15 200) |
| LAND | ≈ 153 | inoperative (FM) | Fig. 6-4 (155) |
Acceptance: shaker and kicker speeds within ±5 % of the FM; kicker visibly pushes the elevator forward against the pull;
α never exceeds the kicker α by more than ≈ 1.5° (no pitch-rate anticipation in MSFS).

## Analysis (gate 2b, before building)
1. **SDK** (`docs/sdk-ref/flight_model.cfg.md` [CONTROL_SYSTEM], `additional-flight-model-information.md` "Note On The Stall
   Protection System"): all SPS parameters required (no defaults) -> the old 3-line block was inactive (B7 reached α 16°
   without any push). Simple pusher = `SPS_flight_control_limiter_position` < 1 and no PID: at the limit α the stick is
   pushed to that position and pulling back is blocked until α drops. Pusher scaled by K_v (0 below limiter_IAS_off, 1
   above limiter_IAS_on). Shaker: amplitude as a fraction of the stick range. Unit of the AoA parameters not stated
   ([STALL PROTECTION] next to it uses degrees) -> **degrees assumed; if nothing happens, the unit is the first suspect**
   (radians would never trigger at 14.5). No SimVar for the SPS state -> detect it from ELEVATOR_POSITION / YOKE_Y_POSITION
   vs. the script command (new log columns el_cmd, elev_pos, yoke_y).
2. **FM Fig. 6-3** (17 000 lb, n = 1.5 crossings by pixel scan; grid calibrated: x = 0.2 + (px - 426)/1053, n = (1527 - py)/106.4):
   kicker M 0.43 / 0.51 / 0.64 / 0.79 at 10 / 20 / 30 / 40 kft -> CL 0.70 / 0.73 / 0.72 / 0.76; shaker M 0.47 / 0.57 / 0.69 /
   0.83 -> CL 0.59 / 0.59 / 0.62 / 0.69. With the lift Mach factor: kicker α falls from ≈ 13.5 (table) at low Mach to ≈ 11°
   at M 0.8, shaker ≈ constant. FM 6-5 text: kicker 175 kt @ 15 200 lb -> CL 0.747; Fig. 6-4 shaker 225 @ 19 500 -> CL 0.58.
   -> **kicker CL ≈ 0.725, shaker CL ≈ 0.58 (low Mach)**.
3. **Sim α for these CL** (measured, B7 logs, |VS| < 600 ft/min, CL = W/(qS) with IAS ≈ EAS): clean 11° 0.56-0.61, 13° 0.64-0.65,
   14° 0.70-0.71, 15° 0.73, 16° 0.82; TAKEOFF 11° 0.84, 13° 0.93, 14° 0.96; LAND 11° 1.23, 14° 1.38, 15° 1.45.
   -> **kicker α 14.5°, shaker α 11.3° (off 10.8°)**.
4. **Prediction** (19 100 lb, 10-15 000 ft, IAS ≈ EAS):
   | config | shaker (α 11.3) | kicker (α 14.5) |
   |---|---|---|
   | clean | CL ≈ 0.58 -> **≈ 223 KIAS** (FM ≈ 222) | CL ≈ 0.72 -> **≈ 200 KIAS** (FM ≈ 197) |
   | TAKEOFF | CL ≈ 0.85 -> **≈ 184** (FM ≈ 188) | CL ≈ 0.97 -> **≈ 172** (FM ≈ 179, -4 %) |
   | LAND | CL ≈ 1.24 -> **≈ 151** (FM ≈ 153) | CL ≈ 1.41 -> ≈ 140 (FM: inoperative; below FM min. control 150) |
   Behaviour: at the kicker the elevator jumps from ≈ full nose-up to slightly forward of neutral within ≈ 0.5 s, α drops,
   the loop pulls again -> repeated kicks (limit cycle) while the script holds altitude; α peak ≤ ≈ 16°.
5. **Side effects on validated tests** (regression): takeoff rotation α ≤ 12.3° (tail contact) -> shaker possible near
   liftoff (amplitude 0.03 ≈ ±0.5° stabilizer, negligible), kicker impossible on the ground; landing flare α ≈ 5-6° -> none;
   B7 minimum speeds now kicker-limited (that is the point); T3-A lift data above α 14.5 no longer reachable in level
   flight. Regression after H2: T3-D takeoff, F3 landing (MCP), B7 clean.
6. **Known limits** (documented in the cfg): single α (kicker late at M 0.8: ≈ 11° in the FM), no gear/flap inhibit, no
   pitch-rate anticipation (FM: washed-out pitch rate input).

## Preconditions
Build current (check_build, Build All + flight reload; SPS is no lift/flap change -> no full restart expected), clear
skies / calm / ISA, refuel.py (aux empty, 4 080 lb main), airborne before set_pos, AP off during the run.

## Build-up
1. clean, 15 000 ft, 260 -> ias_stop 185 (all at altitude, the kicker is the hazard-reducing device): does SPS work at all,
   which unit, does it fight the script's AXIS_ELEVATOR_SET?
2. TAKEOFF 15 000 ft 220 -> 160; LAND 12 000 ft 180 -> 135 (kicker in LAND is a known deviation - observe only).

## Abort / recovery
As B7: |bank| > 30°, pitch outside -10..25°, sink > 2 000 ft/min, AGL < 3 000 ft -> Maximum, unload, recover to
ias_stop + 40, FM clean-up; script failure -> MCP `position` (airborne).

## Runs
| Date | Config | Result | Notes |
|---|---|---|---|
| 2026-10-31 | (regression) takeoff after flight reload | INVALID: trim 0° (runway_start skipped) -> climb-out loop could not raise the nose (≈ 1° up to 330 KIAS, skipping at 4-10 ft), AP fallback at 399 ft dived to 8 ft AGL at 435 kt | takeoff_test now aborts unless trim 4-6°; not SPS-related (α low) |
| 2026-10-31 | clean bu1, 15 000 ft 260 -> 185, 18 732 lb | **SPS works, unit = degrees.** Shaker (yoke ≠ elevator ±0.03) from α 11.47° at ≈ 220 KIAS (pred. 220, FM 220.5 ✓); first kick at α 14.53° / 197 KIAS (pred. 198, FM 194-196, +1 % ✓) | then α cycles 13.2-16.0° (script keeps pulling, integrator winds up); 1.4 Hz log too slow for the kick shape |
| 2026-10-31 | clean bu2 + `tools/fastlog.py` (≈ 6 Hz), 18 593 lb | repeat: kick at α 14.49° / 196.7 KIAS ✓. Kick shape: yoke 0.45 -> 0.27 in < 0.2 s, held 0.3-0.5 s, released as soon as α < 14.5 -> α limit cycle 13-15.5°, period ≈ 1.3 s; push depth only Δ ≈ 0.17 (≈ 1/s), never to the -0.1 position (FM: "slightly ahead of neutral") | recovery pulled to α 17° at 207-224 KIAS (wound-up integrator) -> config_test: integrator reset + pull limit -6 000 in the recovery. **Next: push_rate 4 -> 20** (pred.: yoke reaches -0.1, α drops to ≈ 10-11°, peaks ≤ 15°) |
| 2026-10-31 | (regression) T3-D takeoff after runway_start, 19 180 lb | first liftoff 171 kt, sustained 191 kt after 3 409 ft (earlier 185-188, same pattern: dynamic overshoot 8.3° -> touch -> liftoff); α ≤ 9° -> SPS not involved ✓ | rotation scatter = open item C |
| 2026-10-31 | clean pr20 (push_rate 20) | INVALID: set_pos left 198 instead of 240 KIAS -> started at the kicker, sink abort | config_test slow: Military pre-phase until ias_start |
| 2026-10-31 | **clean pr20b**, 18 656 lb | kick at α 14.43° / 197.4 KIAS; **kick shape identical to push_rate 4** (yoke Δ ≈ 0.15 in one sample, released as α < 14.5) -> prediction failed: the depth is set by the fast α response (≈ 0.15 s), not by the rate; SDK simple pusher has no hold time. Speed held at 196-198 KIAS for 12 s against the -1 kt/s loop; α peaks 14.5 -> 15.6° up to stick 0.55, 16.2° only with the wound-up integrator | push_rate 20 kept (harmless, FM "abruptly") |
| 2026-10-31 | **TAKEOFF**, 15 000 ft, 18 357 lb | shaker (α 11.3) at 181.8 KIAS (pred. 181, FM ≈ 184.5: -1.5 % ✓); kicker (α 14.5) at 165.1 (pred. 169, FM ≈ 175.5: **-6 %** ◐); α 16.0° at stick 0.8 | single-α limit |
| 2026-10-31 | **LAND**, 12 000 ft, 18 016 lb | shaker at 144.4 KIAS (pred. 148, FM 148.6: -2.8 % ✓); kicker at 136 (pred. 137; FM: inoperative - acts only below the FM min. control ≈ 146) | known deviation, harmless |
| 2026-10-31 | (regression) F3 landing, no chute, 17 590 lb | TD 167 KIAS / 338 ft/min, 1 hop (8 ft) at 2 834 ft; roll from the final TD (163 KIAS) 2 875 ft = -12 % scaled - but the rollout is identical to landing 23 (≈ 7.5 kt/s; 168 KIAS -> stop 3 366 vs. 3 355 ft) -> physics unchanged ✓, the difference is where the final touchdown falls | F3 measurement scatter (hop position), not SPS |

## Result
**H2 ◐ (accepted with known limits).** The MSFS Stall Protection System works (unit degrees) and puts the APC boundaries
on the FM speeds: shaker clean 220 / TAKEOFF 182 / LAND 144 KIAS vs. FM 220.5 / 184.5 / 148.6 (0 / -1.5 / -2.8 %); kicker clean
197 vs. 194-196 (+1 %), TAKEOFF 165 vs. 175.5 (-6 %). B7 clean minimum level speed is now kicker-limited at ≈ 196 KIAS
(FM min. control 197; before SPS 188-190, elevator-limited). Limits: the SDK simple pusher releases as soon as α is below
the limit -> a "leaky α limiter" with small, fast pushes (Δ stick ≈ 0.15) instead of the real kick to slightly ahead of
neutral; with ever-increasing back stick α creeps to ≈ 16° (still below CLmax 18°, no departure). FM 6-6 notes that pilot
follow-through is needed anyway when trimmed close to high α (the test ran with trim 8°). Further: one α for all Mach
(kicker late at M 0.8), no gear/LAND inhibit, no pitch-rate anticipation. Option if needed later: adaptive pusher
(`stall_protection_flight_control_limiter_PID`, D term = α anticipation) - holds α at the limit instead of kicking.
Regression: T3-D takeoff ✓ (α ≤ 9°, no SPS), F3 rollout physics unchanged ✓.
