# Work package EPP: J79 part-power thrust curve (plan 2026-11-04, nothing changed yet)

Trigger: sortie S2b (2026-11-04) - at 83 % N1, TAKEOFF flaps, 260 KIAS, 6 500 ft the jet CLIMBED (+366 ft/min, accelerating to
291 KIAS); FM 3-41 says 1 800-2 000 ft/min DOWN. pete: fix the thrust curve first, "otherwise the rest may be wrong too",
plan everything properly first.

## 1. Method (research 2026-11-04)
Industry practice for validating a simulation model (flight-simulator qualification: Qualification Test Guide (QTG) under
14 CFR Part 60 / RAeS evaluation handbook; model-validation case studies DLR ISTAR, Bell V-280, NATO AVT-296):
- a fixed catalogue of **objective tests with tolerances**; after acceptance it becomes the **master test set (MQTG)**, re-run
  after every change (our equivalent: the regression sorties);
- **validate the sub-models (engine, aero, controls, ground) separately before the whole aircraft** - we validated the engine
  only at military/afterburner and at the approach rpm; the part-power range was never tested as a component;
- **data consistency check** before data are used (every channel cross-checked - lesson 6, body-X pitch rate);
- "essential match": the model is accepted when it matches within a fraction of the flight-test tolerance.
-> EPP is done component-first: (A) engine alone (thrust vs. N1 measured directly in the sim), (B) the aircraft tests that
depend on part power, (C) the full regression set.

## 2. What the sim does now (engines.f104.cfg)
- Thrust = static_thrust (10 000) x n1_and_mach_on_thrust_table(corrected N1, M) x δ - ram drag (corrected_airflow_table x
  inlet area 5 ft² x V); the table rows are LINEAR between idle (67 %: 0.035 at M 0) and 100 % (0.709 at M 0); airflow per ft²
  is proportional to N1 [S] (160 lb/s at 100 %).
- At 83 % N1, M 0.4: gross ≈ 0.486 x 10 000 ≈ 4 860 lbf, ram drag ≈ 133 lb/s x 440 ft/s / g ≈ 1 820 lbf -> **net ≈ 3 000 lbf**
  (S2b measured ≥ 3 100 lbf from the climb).
- Validated anchors that must NOT move: military/AB thrust (static and in flight, T3-F, D-7137 ✓), approach N1 87-90 % in LAND
  configuration (D5 ✓ 89.5-91 %), cruise fuel flow (D5, TSFC 0.72 on gross thrust ✓), idle N1 67 %, takeoff (T3-D).

## 3. Sources for the part-power range (F-104G FM = primary)
| # | Source | Content | Thrust information |
|---|---|---|---|
| S1 | Stoelinga (J79-GE-11A data, local PDF) | idle 67 % 500 lbf, normal 100 % 9 700 lbf, military 100 % 10 000 lbf | end points; between normal and military the thrust is set by the NOZZLE at constant rpm |
| S2 | **FM Fig. 1-30** (PDF 56) | rpm linear in throttle angle (67 % at ≈ 15° to 100 % at ≈ 68°); **nozzle fully open (≈ 9) up to ≈ 25° (≈ 74 % rpm), closes mechanically between ≈ 74 and ≈ 87 % rpm to ≈ 2.5, then constant to military**; EGT 330 -> 590 °C; "cruise" band ≈ 40-60° throttle | shape: very little thrust below ≈ 74 %, steep rise 74-87 %, then rpm-driven to military |
| S3 | **FM 3-41** partial-power pattern | TAKEOFF flaps, 260 KIAS, ≈ 83 % -> 1 800-2 000 ft/min | net ≈ D - W sin γ ≈ 2 830 - 1 370 ≈ **1 460 lbf** (D from the validated drag: CL 0.42, CD ≈ 0.063, q̄ 229) |
| S4 | **FM 3-33** simulated flameout | 83 % + speed brakes out + gear up + TAKEOFF flaps ≈ dead-engine drag; flaps/gear up, RAT in: 275 KIAS at 84 % with speed brakes | net(83 %) ≈ ΔD speed brakes (ΔCD 0.046 x 229 x 196 ≈ 2 060 lbf) - windmill/RAT drag -> **≈ 1 500-2 000 lbf**; second independent point |
| S5 | FM 2-24/2-25, approach | ≥ 83 %, typ. 87-90 % at 175 KIAS LAND + gear; flare 82-83 %, idle at touchdown | D5 ✓ (anchor) |
| S6 | FM appendix cruise / endurance charts | check whether rpm is given (if yes: more anchor points) | to check (desk) |
| S8 | **FM Fig. A7-1** (PDF 540, flight test, 14 400-16 000 lb) | idle descent at 300 KIAS, flaps + gear up: average **5 600 ft/min** (speed brakes in), **11 150 ft/min** (out); 29 000 ft -> SL in 32 NM / 5.2 min / 54 lb | idle net thrust in flight (+ drag check); a further anchor for the low end |
| S9 | FM A7-1 remark 4 -> **Section IX "85 % rpm jet penetration descent"**; A7-3 ff. (PDF 541-543: probably the TAKEOFF-flap / speed-brake variants) | descent rates at 85 % rpm | **another part-power point** - read tomorrow |
| S10 | **T.O. 1F-4C-2-8 J79-15/17 power plant maintenance instructions** (USAF 1978, archive.org: https://archive.org/details/f-4-c-j-79-15-17-power-plant-maintenance-instructions; found by pete; read via the full text) | nozzle check (para. 2-66 d/e): **nozzle starts to close at 66-68 % rpm, stops closing at 86 %**, at idle 3/4-7/8 open; figures 2-11 EGT/RPM schedule, 2-13 throttle schedule, 2-14 military fuel flow; no test-cell thrust curve | confirms the Fig. 1-30 shape for the J79 family (-15/17 starts closing earlier than the -11A reading ≈ 74 %); throttle schedule for the A0 reading |
| S7 | J79 thesis (UMSL, `J79_Thesis_Rev._E.pdf`), DTIC AD0855992 (DTIC in maintenance 2026-11-04; title unknown - low priority) | possibly J79 maps / part-power data | **download blocked for the tools (HTTP 403) - pete: please download in the browser into docs/sources/** |

## 4. Plan (each step with gate)
**A0 (desk, now):** this document; FM appendix check (S6); reading of Fig. 1-30 with uncertainty (throttle-angle -> rpm map,
nozzle schedule points).
**A1 engine component baseline (sim, no cfg change):** new tool `tools/engine_sweep.py`: (a) on the ground, parking brake,
N1 steps 67/70/75/80/83/85/88/90/95/100 % (throttle loop on N1, 8 s each): net thrust (TURB ENG JET THRUST), fuel flow, EGT;
(b) in the air at ≈ 6 500 ft / 260 KIAS (AP holds altitude with gear/flaps as needed? no - throttle steps only for a few
seconds each, speed changes slowly): net thrust per N1 step. Output: the sim's thrust curve at M 0 and M 0.4. Gate: the
measured curve reproduces the table formula (data consistency check of the engine model itself).
**A2 target curve (desk):** net-thrust targets at M 0.4: 67 % ≈ 0 (in flight), 83 % 1 500-2 000 (S3 + S4), 87-90 % = current
sim value (D5 anchor), 100 % unchanged; shape between from Fig. 1-30 (nozzle). Convert to gross-table values (gross = net +
ram drag) for all Mach columns with the same relative reduction; rows ≥ 90 % unchanged. Decide whether the airflow table
(ram drag, [S] linear) also needs a part-power shape (J79 airflow at 83 % rpm is probably < 83 % of 160 lb/s) - prefer ONE
change (thrust table) first. Write predictions for every test in the regression matrix (section 5).
**A3 change + component check:** one change (engines.f104.cfg table rows 70-88), build_cfg, check_build, Build All + aircraft
reload (engine change; restart if the selftest says so); engine_sweep again -> curve = target ± 5 %.
**B system checks (sortie S5-EPP):** D6 descent at 6 500 ft (1 800-2 000 ft/min ± 10 %), simulated-flameout configuration at
83 % vs. the B4 glide (same descent angle as a windmilling glide ± 10 %), D5 approach N1 (87-91 %), D5 cruise fuel-flow points.
**C regression (master set):** S1a (takeoff, T3-J, SP step, F3 incl. fmflare 82-83 % flare), F2, T3-L, B6, H3 BLC check (TE
follows N1 in the flare), position/AP routine (throttle 8 000 = N1 ≈ 90 %: unaffected if rows ≥ 90 % unchanged).

## 5. Regression matrix (who depends on part-power thrust)
| Test / tool | Uses part power? | Expected effect of a lower 75-87 % thrust |
|---|---|---|
| T3-D takeoff, B6, B5, T3-F/T3-H, D3/D4 | no (military/AB) | none |
| D5 approach (87-91 %) | edge | small (rows ≥ 90 % kept; 88 % slightly lower -> approach N1 +0.5-1 %) |
| D5 cruise fuel flow | yes, if cruise N1 < 90 % corrected | N1 slightly higher for the same thrust; FF ≈ unchanged (TSFC on gross thrust) - verify |
| F2/F3 landing (fmflare 82-83 % flare) | **yes** | less thrust in the flare -> higher sink at touchdown -> check skips/TD sink; script may need flare N1 tweak |
| H3 BLC f(N1) | indirect | mapping unchanged (N1-based); approach N1 may rise a bit |
| landing_test approach throttle loop | yes | adapts by itself (closed loop) |
| `position` routine (throttle 8 000 ≈ N1 90 %) | edge | ≈ none |
| D6 descent | **target** | 1 800-2 000 ft/min |
| G1/G2/G3 (not yet flown) | yes | to be flown after EPP |

## 6. Process notes from this session (fold into the skill after EPP)
- Component first: before trusting a system-level test (D6), the component (engine thrust vs. N1) is measured directly.
- Every acceptance band is shifted to the test condition (lesson 7); the two FM points S3/S4 are a consistency check of each
  other (both ≈ 1 500-2 000 lbf at 83 %).
- One change per round; predictions for ALL configurations and the whole regression matrix before the build (lessons 15/16).

## 7. Agenda for the next session (2026-11-05) - written 2026-11-04 evening
Session start: watchdog (background), selftest; sim: EDDM 26L, runway_start. The validated state is in the sim (changes 1/1b
reverted, S1a passed).
1. **A0 finish (desk, sim paused):** read FM A7-3 ff. (PDF 541-543) and the Section IX 85 % penetration descent; read Fig. 1-30
   with a pixel scan (throttle angle -> rpm, nozzle position; calibrate the method on the axis ticks, write the uncertainty);
   if pete downloaded them: J79 thesis / DTIC report. Result: table of FM part-power points (rpm, config, speed, altitude,
   descent rate -> net thrust from the validated drag) in this document.
2. **A1 tool `tools/engine_sweep.py`** (desk, then sim): ground run with parking brake (N1 steps 67-100 %, throttle loop on N1,
   8 s each; parking brake holds military - no AB) and an in-flight sweep at ≈ 6 500 ft / 260 KIAS (gear up, TAKEOFF flaps;
   short N1 steps, AP ALT hold not used - elevator holds the altitude like config_test; stop after each step if IAS
   leaves 240-290). Output: net thrust, FF, EGT, nozzle?, corrected N1 per step + the table formula prediction. Gate:
   measured = formula (consistency check of the engine model). Hazards: ground - none (brake, no AB); air - low altitude
   ≥ 6 500 ft MSL, abort AGL < 3 500, speed/bank/pitch limits, end via `position`.
3. **A2 target curve (desk):** net-thrust targets at M 0.4 from S3/S4/S8/S9 + the Fig. 1-30 shape; gross-table rows 70-88 %
   (all Mach columns, same relative factor), rows ≥ 90 % unchanged; predictions for every line of the regression matrix
   (section 5) written into this document BEFORE the build.
4. **A3** one cfg change (engines.f104.cfg thrust table rows), build_cfg, check_build -> pete: Build All (+ restart if the
   engine normalisation needs it - check with the selftest/engine_sweep) -> engine_sweep again (target ± 5 %).
5. **B** sortie S5-EPP: D6 descent 6 500 ft (1 800-2 000 ft/min ± 10 %), simulated-flameout config at 83 % vs. B4 glide, idle
   descent 300 KIAS vs. A7-1, D5 approach N1 + cruise FF points.
6. **C** regression master set: S1a + F2 + T3-L + B6 (+ H3 BLC TE log in the flare); update test plan D6, measurements, data
   index, lessons; commit.
Open items parked: T3-SP longitudinal stiffness (deviation, see its card), H1 pitch/roll dampers, sideslip_test rework, S3/S4
sorties (landing variants, engine), H2 kicker Mach table.

