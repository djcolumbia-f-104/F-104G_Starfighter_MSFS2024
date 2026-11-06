# F-104G flight test plan (sim)

Status 2026-10-27. Companion to `docs/flight-model-plan.md` (method, test levels T0-T3, work packages): this plan
lists the **test points**, in the order we iterate through them. Each test point gets a test card
(`docs/notes/test-cards/<id>.md`, skill `f104-testcard`) before it is flown; results go to
`docs/notes/measurements.md` and the status column here.

## 1. Method

Modelled on the 1950s USAF practice (Category I contractor tests -> Category II AFFTC evaluation) and the USAF/USN
Test Pilot School methods (performance and flying qualities textbooks, `docs/notes/research.md`):

- **Build-up**: ground before air, subsonic before supersonic, high altitude before low, simple configuration before
  complex. A test that depends on others runs after them (the landing needs lift, drag, thrust, trim, flare control).
- **One effect per test**: isolate what is validated (e.g. glide L/D = drag without thrust uncertainty).
- **Reference first**: every test point has a documented reference value (FM figure/page, NASA table) and a
  tolerance, written on the card before the flight.
- **Test card + desk check + go/no-go + build-up run + test + evaluation** (skill `f104-testcard`).
- **Change control**: validated values are frozen; a change needs data, documentation and the regression tests of
  the affected area (table in `f104-testcard`). Read `research.md` / `measurements.md` before any cfg change.
- **Iteration loop**: test -> compare -> root cause from the logs -> one change -> regression -> next test point.

## 2. Test configuration (baseline for all tests)

| Item | Setting / check |
|---|---|
| Aircraft | "F-104G Starfighter Pruefstand (TESTBED)", build current (`check_build` T1 green) |
| Sim settings | **assistance off** (auto-trim, assisted controls, AI piloting, stall protection), no analogue axis on elevator trim, no duplicate bindings (2026-10-27 trim run-down) |
| Weather | **no live weather**: preset clear skies, wind calm, ISA (FM charts are for no wind / standard day); crosswind tests (F9) separately. 2026-10-28 landing 9: live weather 14 kt crosswind + gusts rolled the jet 22° in the flare |
| Restart rules | lift/flap changes: FULL sim restart; lateral/systems: Build All + aircraft reload |
| Weight/fuel | note weight, fuel (≥ 1 500 lb), CG (`preflight`); FM speeds +5 kt per 1 000 lb |
| Flight control | scripts fly by hand (elevator/aileron controllers, signs probed); MSFS AP only for positioning, cruise, go-around (trim-based, trim locked while engaged) |
| Positioning | `set_pos` speed ≈ IAS, pitch at the expected attitude (negative = nose up); retracts the gear |
| Logging | script CSV + `simlog.py` (α, pitch, elevator, trim, N1, FF, ...) |

## 3. Test points

Status: ✓ passed · ◐ partly / accepted with deviation · ○ open · – later (needs systems/3D work).
"Ref." = reference and tolerance; FM = T.O. 1F-104G-1 (`docs/notes/fm-procedures.md`).

### Phase A - Ground

| ID | Test | Method | Ref. | Status |
|---|---|---|---|---|
| A1 | Engine idle | stabilised idle on the ground | 67 ± 1 %, EGT 320-420 °C, FF 700-1 600 lb/h (FM 2-13) | ◐ idle EGT 470 °C (AP-7) |
| A2 | Engine military / static thrust (T3-C) | parking brake, burst to military | 100 ± 1 %, EGT 590 ± 10 °C, idle->mil ≤ 10 s, FF Fig. 2-5 ±500 lb/h; thrust per NASA | ✓ thrust/EGT; ○ accel time, Fig. 2-5 |
| A3 | Taxi, steering, brakes | low/high speed taxi, brake stop | anti-skid < 10 kt inop; turning radius Fig. 2-4 | ◔ 2026-11-06 (S20-A3, `tools/taxi_steer_test.py`): steering ≈ 1.8°/s per 1 000 counts at 80-110 KIAS; the F9 PI rollout law oscillates on the ground (±4°, ±10 ft, abort at 7.1°); designed law (yaw-rate damping) ✓ run 2 (|c| ≤ 7.5 ft), F3 xw=0 rollout ±1 ft |
| A4 | Control limits | full deflections gear up/down | rudder ±20° gear down / ±6° gear up, ailerons ±20° / ±9.75° (FM 6-3) | ◑ 2026-11-06 desk (card A4-H4-control-limits.md): sim limits = 20° x elasticity(q̄) - FM gear-up values only above ≈ 280 KIAS; below 1.3-2x aileron / 1.6-3.3x rudder; gear-switched limiter -> cockpit phase (AP-9) |
| A5 | Drag chute deceleration | high-speed taxi, chute at ≤ 180 KIAS | ground roll Fig. A8-3 vs. A8-4 (chute -12 %) | ○ (with F5) |

### Phase B - Basic aerodynamics, subsonic

| ID | Test | Method | Ref. | Status |
|---|---|---|---|---|
| B1 | Lift (T3-A) | idle deceleration 16 500 ft | NASA TN D-7137, ±0.03 | ✓ |
| B2 | Drag (T3-F) | idle deceleration, dV/dt | D-7137 ±10 % | ✓ ISA steady-level (D5 logs) 1.03-1.07 at M 0.5-0.85; accel/decel 1.04-1.05 mean |
| B3 | Trim gradient (T3-G) | from B1 data | CR-96008 | ✓ |
| B4 | **Glide L/D** | idle (≈ windmilling), gear up, TAKEOFF flaps, 245 KIAS, 20 000 -> 10 000 ft; flaps up 275 KIAS | Fig. 3-8: 9 NM per 10 000 ft with RAT (no RAT: ≈ 11 NM), gear down 5.5 NM | ◐ clean -4 %, TAKEOFF -11 % (drag scalar 0.42) |
| B5 | **Landing-configuration drag + thrust** | gear + LAND flaps + speed brakes at Military, low altitude, stabilise | flat/level ≈ 190-200 KIAS (FM 3-41); final 175 KIAS needs 87-90 % for 700-800 ft/min | ✓ 2026-10-28 after LAND flap drag 0.12 -> 0.08: 194 KIAS (was 164) |
| B6 | Go-around climb | landing config, Military, sawtooth climbs 160-200 KIAS | Fig. 6-8: ≈ 1 400 ft/min at 165-175 KIAS (20 500 lb, SL) | ✓ 2026-10-28 after the flap drag change: +1 061 ft/min (FM ≈ 1 050-1 250; was +389) |
| B7 | Minimum speeds / stall approach (old T3-L "stall/APC") | 1 kt/s deceleration to the shaker speed, clean/TAKEOFF/LAND, 1 g and 40°/60° bank | Fig. 6-4 shaker (min. control), e.g. 19 500 lb: 225 (200) / 190 (180) / 155 (150) KIAS; no full stalls (pitch-up) | ◐ min. level speed clean -4 % / TAKEOFF -6..-7 % / LAND -3..-5 % vs. min. control (elevator-limited, mush, no pitch-up -> H2); since H2 clean kicker-limited ≈ 196 KIAS (0 %) |
| B8 | Approach configuration (T3-L) | LAND flaps at altitude | CR-2144 CL 0.845 at α 4.1° | ✓ |
| B9 | Maneuvering flaps | TAKEOFF flaps, gear up, wind-up turn | +≈ 1 g available load factor (FM 6-2) | ○ |

### Phase C - Lateral-directional

| ID | Test | Method | Ref. | Status |
|---|---|---|---|---|
| C1 | Rudder effectiveness (T3-E) | full rudder, gear down | β/δr 0.32 (CR-2144) | ✓ |
| C2 | Steady heading sideslip (T3-E2) | closed loop | δa/δr 0.27-0.47 | ✓ (regression after C4 ✓ 2026-11-05, sideslip_test v2: β/δr 0.34, δa/δr 0.37 = prediction) |
| C3 | Dutch roll (T3-J) | rudder doublet | period 1.41 s, damping (CR-2144) | ✓ 1.48 s |
| C4 | Roll rate (T3-K) | full aileron, gear up (±9.75°) | CR-2144 Clδa; roll limits FM 5-14 | ○; ◐ 2026-11-01 roll_stability 0.1 + aileron_effectiveness 1.17: δa 5/10° -> 45/95°/s vs CR-2144 48/96 ✓; full δa 20° 248°/s (+30 %) + inertial-coupling departure (no SAS) -> H1 first (card C4-roll-rate.md) |
| C5 | Transonic lateral oscillation | M 0.94-0.98 above 25 000 ft | ≈ 0.5 Hz, lightly damped without SAS (FM 6-17) | ✓ 2026-11-04 S2: 0.53 Hz, 0.36/cycle SAS off; SAS on deadbeat |
| C6 | Spiral stability | release 30° bank | > 20 s doubling time | ✓ 2026-11-04 S2: doubles in 65 s (R), converges (L) |

### Phase D - Performance

| ID | Test | Method | Ref. | Status |
|---|---|---|---|---|
| D1 | Takeoff (T3-D) | scripted, max AB | Fig. A2-3 / Fig. 2-6 (190 KIAS @ 20 800 lb), ±5 % | ✓ -4.2 % (ISA, LE flaps, 2026-10-29); 2026-10-31 stick-schedule rotation (srot): 178 kt single liftoff = FM 177.9 (0 %), no touch-back |
| D1b | Takeoff ground run | `takeoff_test.py`, calm/ISA, distance brake release -> liftoff | FM Fig. A2-5 (ground run, max thrust, PDF 458), ±10 % | ◐ +10 % (2 900 vs. 2 630 ft at 19 000 lb, 1 500 ft, 15 °C); low-speed AB thrust to check; with srot rotation +9 % (2 865 ft normalised) |
| D2 | Excess thrust / climb (T3-H) | level max-AB accelerations | D-6398 Fig. 6 | ◐ explained: sim follows D-7137; D-7137 model itself vs. D-6398 = 0.86-0.90 at 10 000 ft, 1.03-1.12 at 20 000 ft (ISA 20 000 ft sim 0.97-1.08) |
| D3 | Level acceleration | M 0.9 -> 1.8 at 35 000 ft (740 KIAS limit at M ≈ 1.8) | Fig. A9-1 time/fuel/distance | ◐ time +8 %, distance +3 % ✓; fuel +20 % (AB FF rises with Mach, known) |
| D4 | Top speed (T3-I) | 36 000-40 000 ft, max AB | M 2.0 / engine inlet temperature limit, 750 KEAS | ✓ M 2.056 at 40 000 ft, still accelerating 0.18 M/min at M 1.96 (sim IAS reads high supersonic -> limits on EAS) |
| D5 | **Fuel flow / range** | stabilised cruise points (e.g. 260 KIAS, M 0.8, M 0.9) | Appendix Part 6 (miles per pound), Part 9 | ✓ after TSFC 1.26 -> 0.72: 0.96-1.07 (M 0.5-0.85, 5-30 kft); was 1.66-1.86. after EPP (cruise N1 now 88-91 %) TSFC 0.72 -> 0.69: ✓ 2026-11-05 C 1.02, A 1.04, E2 1.00, E1 0.99 (B ≈ 1.06) |
| D6 | Descent rates | partial-power pattern (TAKEOFF flaps, 260 KIAS, 83 %) and simulated flameout (83 %, speed brakes, TAKEOFF flaps) | 1 800-2 000 ft/min (FM 3-41); flameout glide 245-260 KIAS | ✓ 2026-11-05 after EPP (part-power thrust rows 70-90 from FM A7 flight-test descents): 83 % 2 205 ft/min (+10..22 %), FM A7-3 85 % clean 1.12, A7-2 85 % TO+brakes 1.04, A7-1 idle 0.95 (was: jet climbed at 83 %) |
| D7 | Climb schedule | max thrust / military climb | Fig. 6-7 climb angles, appendix climb charts | ✓ max thrust M 0.90 (Fig. A3-7, DI 0): 10 000 -> 35 000 ft 1.09 vs. 1.13 min, pitch ≤ 50°; military M 0.85 (Fig. A3-10): 3.50 vs. 3.36 min (+4 %) |

### Phase E - Transonic / supersonic

| ID | Test | Method | Ref. | Status |
|---|---|---|---|---|
| E1 | Trim vs. Mach | stabilised level points M 0.6-2.0 | Fig. 6-9: ≈ 4° at M 0.6 -> ≈ 1.5° near M 1.2 -> ≈ 1° at M 2.0; nose-down M 0.88-0.90 | ◐ S12: 1.2° M 1.27, 2.0° M 1.8 |
| E2 | Maneuvering stick force / load factor | wind-up turns | Fig. 6-12, 6-14 (≈ 2 g constant speed at 35 000 ft) | ○ |
| E3 | Zoom climb | from M 2.0 / 40 000 ft, 1.5-2 g pull-up to 20° | ≈ 4 000 ft per 0.1 M (FM 6-14), AB blowout > 65 000 ft | – |

### Phase F - Approach and landing

| ID | Test | Method | Ref. | Status |
|---|---|---|---|---|
| F1 | Approach + flare (dry run) | `landing_test.py ... 4000` (virtual runway) | card T3-L-landing: TD 165-180 KIAS, < 600 ft/min | ✓ dry runs 15-17 (go-around 24-30 ft, flaps retract) |
| F2 | **Normal landing** | `landing_test.py <csv> 6 2.5` | TD 155-160 KIAS +5/1 000 lb (Fig. 2-7), ground roll Fig. A8-3 2 760 ft @ 17 900 lb (with chute) | ✓ 2026-10-31 (chute emulation): +0.1 % from the final touchdown; 2026-10-31 with BLC driver -7 % (chute coefficient to re-tune); **✓ 2026-11-01 chute 0.07 + BLC driver: -0.9 / -0.4 % (roll from 165 KIAS)** |
| F3 | Landing without chute | `landing_test.py <csv> 6 2.5 0 nochute` | Fig. A8-4: 3 130 ft | ✓ 2026-10-30 after the CG rework, roll from the FINAL touchdown (skips excluded): -0.3 / -4.8 / -2.6 %; open: touchdown skip (flare/gear dynamics); 2026-10-31 with BLC driver + fmflare -0.1 % (before +9.6 %); 2026-11-01 repeat -0.6 % (from 165 KIAS) |
| F4 | Minimum-run landing | TD 140 kt near the threshold | FM 2-28 | ◑ 2026-11-06 (S18b-F4, `minrun`): TD 168 KIAS (target 159.5) at 1 557 ft, -533 ft/min, pitch 4.0°, chute; stop 4 778 ft past the threshold = -29..-37 % vs. F2; TD speed and roll metric open |
| F5 | No-flap landing | flat final ≥ 230 KIAS, TD ≥ 190 KIAS | FM 3-36 | ◑ 2026-11-06 (S13-F5, 17 429 lb, vtd=202): procedure ✓ - final 237, TD 226 KIAS (Fig. A8-2 202: +12 %, script flare cannot bleed the speed), +29 ft/min, pitch 5.2°, CL +4 ft, roll 4 594 ft; TD speed vs. A8-2 open |
| F6 | BLC failure landing | TAKEOFF flaps, final ≥ 195, TD ≥ 165 KIAS | FM 3-32 | ✓ 2026-11-06 (S11-F6): final 210, TD 197 KIAS (Fig. A8-2 min. 180) -302 ft/min, pitch 6.8°, centreline -1 ft, bank ≤ ±1.7°, roll 3 760 ft (no FM reference); landing_test FAST loop 4.5-5.2 Hz |
| F7 | Touch-and-go | idle, flaps TAKEOFF, military | FM 2-28 | ✓ 2026-11-06 (S16c-F7, `tg`): TD 173, MILITARY at 162 KIAS, srot from 165, liftoff 182 KIAS at 6 521 ft (4 279 ft after TD), max ground pitch 8.1°; build-up `tg=stop` S16-F7a |
| F8 | Go-around from the flare | FM 2-29 procedure | Fig. 6-8 climb, height loss ≤ 100 ft | ✓ 2026-11-06 (S15b-F8, `ga=50`): commanded at 49 ft / 187 KIAS / -525 ft/min, loss 13 ft (lowest 36 ft AGL), climb after 2.1 s, FM sequence ✓ |
| F9 | Crosswind landing | 15-25 kt crosswind | FM 2-25 (max 25 kt) | ◑ 2026-11-06: 5 kt ✓ (CL -3 ft); 10 kt ✓ on the 4th try (crab to TD, CL -8 ft, rollout ±14 ft; rollout law v3 from a crosswind taxi identification - card F9-crosswind.md); 12.5 kt ✓ (after S19f ✗: light rollout push for 4 s after a crabbed touchdown - loaded nose wheel was the cause; rollout -19..-4 ft); 15-25 kt and left crosswind open; presets tools/make_wpr.py (surface ≈ 0.5 x preset) |

### Phase G - Engine and emergencies

| ID | Test | Method | Ref. | Status |
|---|---|---|---|---|
| G1 | AB light / blowout | throttle into AB at altitude | light within 3 s (SL) / 5 s; blowout EGT < 500 °C, nozzle < 7 | ○ |
| G2 | Air start | throttle OFF -> START -> IDLE at several altitudes | FM 3-11 (sim capability?) | ○ |
| G3 | Flameout pattern | glide 245-260 KIAS, low key 6 000-8 000 ft, flare 300-500 ft | Fig. 3-7 | – |

### Phase H - Systems (later work packages)

| ID | Test | Ref. | Status |
|---|---|---|---|
| H1 | Own SAS logic (roll/pitch/yaw dampers) | FM 1-68, 6-3/6-4 Fig. 6-1/6-2; CR-2144 (SAS-off data) | ◐ 2026-11-03 yaw damper ✓ (module v7.1, rudder trim channel; doublet deadbeat, washout steady β +1 %); pitch: SAS-off short period measured 2026-11-03 ωn 7.6 / ζ 0.16 / α/δ 1.0 vs. ≈ 5 / 0.25-0.29 / 1.7-2.1 (static stability ≈ 2x too high, decision open) and roll (aileron trim range) open; card H1-sas.md |
| H2 | APC stick shaker / kicker (AoA + pitch rate) | FM 6-5/6-6, Fig. 6-3, kicker inop with LAND flaps / gear down | ◐ 2026-10-31 native SPS: shaker 0 / -1.5 / -2.8 %, kicker clean +1 %, TAKEOFF -6 %; leaky limiter (no hold), single α, no gear/LAND inhibit (card H2-apc.md); **2026-10-31 SPS DISABLED: makes the MSFS AP diverge after a full sim restart (A/B) - reopened**; **◐ 2026-11-01 own APC in the WASM module (v6): shaker 185/154 KIAS, kicker 200-204 clean / 170 TAKEOFF, LAND inhibited, AP unaffected (card H2-apc.md)** |
| H3 | BLC lift vs. engine rpm | FM 1-74, 2-24 (effective > 80 %) | ◔ 2026-10-31 analysis: ΔCL_BLC ≈ 0.135, f(N1) 0.3 at idle .. 1 at ≥ 83 %, via settable TE flap percent (ground test ✓); predicted F3 +9.6 -> +2 %, float after the idle cut gone (card H3-blc-rpm.md); **◐ 2026-10-31 driver tools/blc_driver.py built and flown: F3 -0.1 %, FM sink after power cut reproduced, fmflare technique**; 2026-11-01 regression B6/B7/T3-L ✓, WASM module prototype built (systems-module.md) |
| H5 | Drag chute with own system logic (MSFS ground spoiler drag has no measurable effect, 2026-10-29) | FM A8-3 vs. A8-4 (-12 %) | ✓ 2026-10-31: spoiler_limit 65° + drag_coef_spoilers 0.12 -> F2 +0.1 % vs. A8-3, coast 5.23 ft/s² as predicted, B5 unchanged |
| H4 | Rudder/aileron limiters with gear | FM 6-3 | ◑ see A4 (no gear switching in the sim; fix in AP-9 via input events) |

## 4. Iteration order (next sessions)

**Note 2026-10-28:** every test before 2026-10-28 afternoon ran in LIVE weather (wind, non-ISA, turbulence) - see
measurements.md. Re-verification in ISA/calm is part of the order below (marked *ISA*).


1. ✓ F1, B5, B6, F3 (2026-10-28). **F2 regression** with chute 0.43 (calm weather).
2. ✓ (done above)
2b. *ISA* re-verification: B6/B5 (quick), T3-F drag + T3-H excess thrust (accel runs), thrust/fuel flow
   checks; spot checks T3-E2 and T3-J.
3. **B4 glide L/D** (cheap, drag-only check in two configurations).
4. **D5 fuel flow** at 260 KIAS and cruise (pete's observation) against appendix Part 6.
5. **B7 minimum speeds** (sim stall speed with flaps vs. Fig. 6-4).
6. A1/A2 engine checks (accel time, idle EGT), A4 control limits (cfg review).
7. E1 trim vs. Mach, C4 roll rate, D3 level acceleration, D4 top speed.
8. F4-F9 special landings, G1/G2, then Phase H with the systems work.

## 5. Open references to fetch

- USAFTPS Performance Phase Textbook Vol. I (DTIC ADA170957), Flying Qualities Textbook Vol. II (ADA170959/60),
  USNTPS FTM-103/108 - test techniques (sawtooth climbs, level accelerations, stall approaches).
- FM appendix Part 6 (range, PDF 520-537) and Part 9 charts for D3/D5.

## 6. Sorties: many test points per flight (pete 2026-11-04)
A sortie = one flight with several test cards in a fixed order; each card's postcondition (tools/post.py) is the next card's
precondition. Planned tool `tools/sortie.py <plan>`: runs the steps, checks POST between them, stops the sortie on POST FAIL
or any abort and leaves the jet in a safe state (AP, level, 16 500 ft) - the whole sortie in one go, one debrief at the end.
**Only on a stable configuration** (no open cfg change): sorties are for regression and for tests that do not change the
cfg; a cfg change is still flown alone with its own build-up (lesson 16).
| Sortie | Content (order) | Duration | Covers |
|---|---|---|---|
| S1 regression | takeoff (T3-D) -> climb (D7) -> AP/position check -> T3-J doublet -> SP step A -> accel run (T3-F/T3-H) -> supersonic SP D + trim (S12) -> descent (D6, new) -> approach (T3-L) -> landing F3 | ≈ 25 min | the full regression list after any change |
| S2 open performance | D6 descent rates, D2/D3 rest, E1 trim vs. Mach, C6 spiral stability, C5 transonic lateral oscillation (M 0.94-0.98 > 25 000 ft) | ≈ 20 min | 6 open/partial points |
| S3 landing variants | takeoff -> pattern -> F4 minimum run ... F7 touch-and-go back into the pattern -> F8 go-around from the flare -> F5 no-flap -> F6 BLC failure; F9 crosswind with weather set | ≈ 30 min | F4-F9 |
| S4 engine | G1 AB light/blowout at altitude, G2 air start, G3 flameout pattern (at altitude first) | ≈ 20 min | G1-G3 |
Prerequisites: sortie.py; post.py in landing_test/config_test; the sideslip script rework; descent/spiral tools.
