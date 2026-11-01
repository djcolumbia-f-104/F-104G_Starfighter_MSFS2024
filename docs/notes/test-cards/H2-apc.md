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

## 2026-11-01: rework as own APC logic in the WASM systems module (SPS disabled)
Reason: the native SPS made the MSFS AP diverge after a full sim restart (A/B 2026-10-31) and is only a leaky limiter.
Module logic (source/wasm/f104_systems/F104Systems.cpp): shaker α > 11.3° (off 10.8°) -> L:F104_APC_SHAKER; kicker when
α + 0.3 s x pitch rate > 14.5°, inhibited with gear down / flap lever LAND / < 120 KIAS (FM 6-6), ELEVATOR POSITION -0.1 written
every frame and HELD until α < 12° and ≥ 0.8 s, AUTOPILOT_OFF on the kick (FM 1-69); L:F104_APC_KICK.
**Prediction (build-up, config_test slow clean 15 000 ft 260 -> 185 KIAS, fastlog α / ELEVATOR_POSITION / L:F104_APC_KICK):**
first kick at α ≈ 14.5° (the 1 kt/s deceleration gives almost no pitch rate) ≈ 197 KIAS; elevator -0.1 for ≥ 0.8 s until
α < 12°; α peaks ≤ 15° (the SPS leaked to 16°); kick cycles slower and deeper than the SPS (13-15.5° / 1.3 s).
Then TAKEOFF (15 000 ft) and LAND (12 000 ft, expect NO kick: inhibited) runs, and a takeoff (gear down -> no kick).
| 2026-11-01 | module takeoff (H2m_takeoff) | 178 kt, α max 10.8°: no shaker, no kick ✓ | gear down inhibit |
| 2026-11-01 | **module clean build-up** (H2m_clean + fastlog) | **first real kick at α 14.32° / 199.4 KIAS** (pred. 14.5 / 197) ✓, elevator -0.1, α 14.3 -> 10.2° in 0.5 s ✓. BUT: (1) while the kick flag was 1 the elevator read +0.36/+0.67 several times - **the per-frame ELEVATOR POSITION write does not dominate a script/joystick that keeps sending AXIS_ELEVATOR_SET**; (2) after each release the test pilot (wound-up integrator) pulled +0.67 -> α 18-24° (beyond CLmax 18°); (3) a kick at α 9.5° right after set_pos (positioning transient, pitch-rate anticipation). The config_test end then engaged the AP at 225 KIAS / trim 8° / Military -> 3 465 ft at 610 KIAS, recovered with MCP position. | kick override method must change; config_test end -> position routine |
Decision needed: (A) intercept the elevator inputs in the module (maskable AXIS_ELEVATOR_SET at the highest maskable
priority, forward min(pilot, kick)) - the proper way, but a module bug would cost pitch control; (B) kick via a trim offset
(ELEVATOR_TRIM_POSITION is not overwritten by stick inputs; trim range -5..+11° limits the kick); (C) warning only.
Also the test pilot must "follow through" after a kick (FM 6-6): reset the integrator / relax the pull when L:F104_APC_KICK = 1.
**Decision 2026-11-01 (FM 1-68 + research):** the real kicker is a hydraulic cylinder that drives the STABILIZER nose-down
and the stick to ½ inch ahead of neutral; only +40-50 lb override it; "more than ½ inch forward: kicker not felt".
MSFS 2024 does not mask input events (SimConnect API reference) -> input interception is not possible from a module.
-> kick = stabilizer offset through the TRIM (trim0 + stab(-0.1) - stab(pilot stick), clamp -5..+11°, nothing if the
stick is further forward), held as before, trim0 restored on release; 3 s kick inhibit after a position jump; the test
pilot (config_test) follows through on L:F104_APC_KICK (integrator reset, pull ≤ -2 000 for 2 s).
**Prediction (rerun clean 15 000 ft):** kick at α ≈ 14.5° / ≈ 199 KIAS, trim drops by ≈ (stick x 17° + 0.5°) (down to -5°),
α < 12° within ≈ 1 s, α peaks ≤ 15°, no excursion after the release, no kick after set_pos. Sources: FM 1-68 (PDF 84);
https://docs.flightsimulator.com/msfs2024/retail/programming-apis/simconnect/simconnect-api-reference/ ;
https://916-starfighter.de/Large/dc119.htm (CF-104 handling: ease off near the kicker).
| 2026-11-01 | **trim kicker clean** (H2t_clean + fastlog) | **first kick α 14.24° / 200.4 KIAS** (pred. 14.5 / 199) ✓; trim 8 -> 1.9° (stick 0.43), α 14.2 -> 3.0° in 0.75 s ✓; **α max 14.24°** ✓ (SPS 16°, elevator-write module 24°); BUT the step back to trim0 = 8° pitched the nose up so fast that the anticipation kicked again at α 10-12° (4 kicks, α 3 <-> 12°, ≈ 2 s) | -> trim retract ramp 1 s (module v4); config_test end via position ✓ |
| 2026-11-01 | v5 clean (H2t5_clean) | no false kick after set_pos ✓; kick α 14.27° / 204 KIAS (FM ≈ 197, +3 %); α max 14.27° ✓; trim retract ramp 5.4 -> 8° in 1 s ✓; 3 kicks (2nd/3rd at α 12.3/11.6 via the anticipation after the test pilot re-pulled to +0.70) | FM: kicker repeats while beyond the boundary |
| 2026-11-01 | v5 TAKEOFF (H2t5_to) | shaker 184.8 KIAS (FM ≈ 188, -1.7 %) ✓; first kick α 14.24° / 169.6 KIAS (pred. 165-172 ✓, FM ≈ 179 -5 %); α max 15.5° (stick full aft, trim at the -5° stop = known limit); **8 kicks: self-excited (kick -> α 0-2° -> nose back at ≈ 15°/s -> anticipation kick at α ≈ 9°, up to 290 KIAS in the clean-up)** | -> v6: anticipation only above the shaker α |
| 2026-11-01 | v5 LAND (H2t5_land) | **0 kicks** (inhibit) ✓; shaker 154.1 KIAS (FM ≈ 149-155) ✓; α max 17.7° (no kicker in LAND per FM) | |
