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
| S11 | **NAVWEPS 02B-151AGA-502, J79-GE-2 maintenance manual (1960)**, local `docs/sources/NAVWEPS02B-...pdf` (504 pages, text layer; via the ww2aircraft.net thread, pete) | p. 400: engine speed / nozzle position / EGT vs. throttle angle chart (third source for the nozzle schedule); p. 483: test-run sheet (idle 5 000 rpm, military 7 720 rpm 604 °C, maximum); pp. 385/389 run-up procedures | **read systematically on 2026-11-05** for part-power check points (rpm/EGT/fuel flow/thrust) |
| S7 | J79 thesis = Brimer 2017 (UMSL), local "Designing Simplicity ... The Ge.pdf": history of the J79, **no performance data**; DTIC AD0855992 (DTIC in maintenance, title unknown) - dropped | possibly J79 maps / part-power data | **download blocked for the tools (HTTP 403) - pete: please download in the browser into docs/sources/** |

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

## 8. Results A0/A1/A2 (2026-11-05, desk; tool `tools/epp_desk.py`, data `docs/data/fm_a7_descent.csv`)
**A0 sources read:**
- S11 J79-GE-2 MM: Fig. 6-35 performance test schedule - "75 % of Normal thrust" at nominal 6 950 rpm = **90.0 %**;
  Fig. 6-39/40/41 minimum thrust at 59 °F / 29.92 inHg: Military 10 340, Normal 9 970, 75 % Normal 7 480 lbf -> static
  thrust at 90 % rpm = **72.3 % of Military** (sim table M 0: 71.2 % ✓). Fig. 5-198 throttle schedule (-2): nozzle closes
  68 -> 81 % rpm, then constant to Normal.
- FM Fig. 1-30 re-read at 300 dpi (-11A): nozzle open up to 16° throttle (≈ 68.5 % rpm), closes linearly to the plateau
  (indicated 2.4) at 36.4° = **≈ 83 % rpm**, constant to ≈ 62°, then closes to ≈ 0.5 at Military. **Correction of section
  3 (S2): the nozzle is already on its closed plateau at 83-85 %** - the nozzle does NOT explain low thrust at 85 %.
- **FM 3-41 says "speed brakes - as necessary"** (and "using speed brakes as required to maintain 260 KIAS"): the S2b D6
  run (brakes in) was no clean contradiction; FM 3-41 only bounds net(83 %) to 1 460 (brakes in) .. ≈ 3 400 (brakes out).
- **FM Appendix Part 7 (flight test, J79-GE-11A) - the decisive data:** A7-1 idle 300 KIAS clean (5 600 / 11 150 ft/min),
  **A7-2 85 % 275 KIAS TAKEOFF flaps + speed brakes** (30 000 ft -> SL 29 NM, 5.1 min, 140 lb), **A7-3 85 % 300 KIAS
  clean, brakes in** (37 000 ft -> SL 120 NM, ≈ 17.5 min, ≈ 500 lb, avg 2 000 ft/min), A7-4 (estimated) 85 % 300 KIAS
  TAKEOFF flaps 3 500 / 8 500 ft/min. Curves digitized (grid detection + per-row trace, ±1 NM vs. the charts' example lines).
**A1 (desk gate instead of a new sweep):** the engine formula reproduces every measured sim net thrust (D5 cruise A/B/C,
endurance 5k/10k, approach, idle, Military) within +2..+6 % -> the formula is a valid model of the sim engine.
**Finding (fit mode):** required net thrust from the validated drag (NASA polar + the sim's own flap/brake ΔCD) and the
energy equation vs. the sim formula:
| chart | sim / required net thrust | fuel lb/min sim / FM |
|---|---|---|
| A7-1 idle | 0.75-1.05 (idle OK) | - |
| A7-2 85 % TO + brakes | 2.1-2.5 | 52 / 27.5 |
| A7-3 85 % clean | 2.3-6.0 | 50 / 28.6 (with the required gross thrust: 30 ✓) |
The deficit divided by q̄ (A_s = (T_sim - T_req)/q̄) **collapses onto ONE curve for A7-2 and A7-3** (different drag x3.5,
weight, q̄): ≈ 8.2 ft² at N1c 84-85 -> ≈ 4 ft² at 90.6 -> 0 at ≈ 95; idle ≈ 0. Interpretation: part-power installation
loss (inlet spillage / afterbody) ∝ q̄, not contained in the NASA polar (derived at max power, D-6398). Fuel flow (TSFC on
gross) agrees with the reduced gross thrust (independent channel). Cross-checks: FM 2-7 approach at 16 100 lb / 175 KIAS
needs only 85.8 % with the current table (FM 87-90 %) -> the current table is too strong there too; FM 3-33 SFO excess
+1 700..+2 160 lbf (A_s 6.5-9.4 at 84 %). Only FM 3-41 ("approximately 83 %") prefers a smaller A_s (≤ 5.3).
**A2 candidate (one change: n1_and_mach_on_thrust_table rows 70-90):** Δmult = 0.148 M² A_s(N1c)/(1+0.2M²)^3.5
(= q̄ x A_s, altitude independent), A_s knots 67:0, 70:0.5, 75:3, 80:5.5, 85:8, 90:4.4, 95:0 (70-80 [S] interpolation,
85/90 [M] A7-2/A7-3), Δ held above M 0.85 (data limit), columns made monotonic in N1, M 0 column and rows ≥ 95 unchanged.
**Predictions (epp_desk.py cand, before the build):**
| test | now (formula) | predicted | acceptance |
|---|---|---|---|
| A7-3 85 % clean descent | sim/req 2.3-6.0 | 1.03-1.27 (≈ 1 700-2 000 ft/min) | 2 000 ft/min ± 20 % |
| A7-2 85 % TO + brakes | 2.1-2.5 | 0.89-1.62 (mean 1.09) | 6 500 ft/min ± 20 % |
| A7-1 idle descent | 0.88 | 1.07 (unchanged at low altitude) | 5 600 ft/min ± 15 % |
| FM 2-7 approach N1 (16 100 lb, 175 KIAS) | 85.8 % | 89.0 % | 87-90 % |
| approach N1 in landing_test (18 900 lb, 190 KIAS) | 89.5 % (measured) | 91.3 % | plausibility |
| D5 cruise N1 A/B/C, E1 5k/10k | 83-85 / 81 % | 90.8 / 90.5 / 88.7 / 88.0 / 88.3 % | J79 cruise ≈ 88-92 % (plausibility) |
| D5 FF ratio A/B/C/E1/E1 | 1.06/1.08/1.04/0.99/1.00 | 1.08/1.09/1.03/1.00/1.01 | ± 10 % |
| SFO 84 % clean + brakes vs. idle glide (FM 3-33) | +1 690 lbf | -270 lbf | ± 500 lbf (≈ glide angle ± 1.5°) |
| SFO 83 % TO + brakes vs. idle + RAT | +2 160 | +505 | ± 600 (RAT drag estimated) |
| FM 3-41 83 % TO 260 KIAS brakes in | net 2 730 | 1 090 (≈ 2 300 ft/min) | 1 800-2 000 ft/min ± 25 % (FM "approximately") |
| `position` 16 500 ft equilibrium at 90.5 % (throttle 8 000) | 475 KIAS (measured 445-480) | 360 KIAS | -> throttle 8 800 (≈ 93 %): 450 KIAS |
| T3-D, B6, B5, D7, T3-F/H, AB (rows ≥ 95) | - | unchanged | regression S1a |
| B4 idle glide | - | ≈ -1 % | unchanged |
| F3 fmflare (82-83 % in the flare, M 0.25) | - | flare net ≈ -900 lbf -> more sink before the idle cut | TD sink < 400 ft/min, F3 ± 5 % |
| H3 BLC f(N1) | - | approach N1 higher -> f = 1 unchanged | unchanged |
Script adaptation in the same change set: `position` callers throttle 8 000 -> 8 800 (49 % -> 53.7 % lever = ≈ 93 % N1,
mapping from the sortie logs: 49 % -> 90.5 %, 68 % -> 100 %).

## 7. Agenda for the next session (2026-11-05) - written 2026-11-04 evening
Session start: watchdog (background), selftest; sim: EDDM 26L, runway_start. The validated state is in the sim (changes 1/1b
reverted, S1a passed).
1. **A0 finish (desk, sim paused):** read the J79-GE-2 maintenance manual (S11: p. 400 chart, test-run/trim tables, any
   part-power thrust or fuel-flow points); read FM A7-3 ff. (PDF 541-543) and the Section IX 85 % penetration descent; read Fig. 1-30
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

