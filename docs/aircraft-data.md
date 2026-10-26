# F-104G: technical data

Source "FM" = flight manual T.O. 1F-104G-1 (`sources/FlightManual-F-RF-TF-104G.pdf`, Change 6, 31 Jan 1973).
Cited as "FM <manual page> / PDF <PDF page>". Page overview: `sources/manual-index.md`.
Status: **confirmed** = read from the FM. **provisional** = secondary source, still to be found in the FM.
Project variant: single-seat F-104G, engine J79-GE-11A.

## Dimensions
| Value | Imperial | Metric | Status / source |
|---|---|---|---|
| Span (without tip tanks) | 22 ft | 6.71 m | confirmed, FM 1-5 / PDF 17 |
| Length (with pitot boom) | 58¼ ft | 17.75 m | confirmed, FM 1-5 / PDF 17 |
| Height (to the fin) | 13½ ft | 4.11 m | confirmed, FM 1-5 / PDF 17 |
| Main gear track | 8¾ ft | 2.67 m | confirmed, FM 1-5 / PDF 17 |
| Wing area | 196.1 ft² | 18.2 m² | confirmed, D-6398 Tab. 1 |
| Span (exact) | 21.94 ft | 6.69 m | confirmed, D-6398 Tab. 1 |
| Wing aspect ratio | 2.45 | | confirmed, D-6398 Tab. 1 |
| Wing anhedral | −10° | | confirmed, FM 6-2 / PDF 392 ("the 10 degrees negative wing dihedral") |
| Leading-edge sweep | 27.1° (quarter chord 18.1°, 70.4 % chord 0°) | | confirmed, NACA RM SL56H06 Tab. I (F-104A); Wikipedia gave 26° |
| Wing taper ratio / root chord / tip chord | 0.377 / 12.98 ft / 4.89 ft | 3.96 / 1.49 m | taper confirmed (RM SL56H06, D-6398 consistent); chords calculated from S, b, taper (theoretical, to the centreline) |
| Airfoil | biconvex, 3.36 % thickness at root and tip | | provisional (Wikipedia) |
| Fuselage: frontal area / length / fineness | 25.0 ft² / 51.25 ft / 9.09 | | confirmed, D-6398 Tab. 1 |
| Horizontal tail: area / span / aspect ratio | 48.2 ft² / 11.91 ft / 2.95 | | confirmed, D-6398 Tab. 1 |
| Horizontal tail deflection | +5° to −17° | | confirmed, D-6398 Tab. 1 (consistent with FM 6-5) |
| Horizontal tail | all-moving T-tail | | confirmed, FM 1-1 / PDF 13 |

**D-6398** = NASA TN D-6398 (1971), **D-7137** = NASA TN D-7137 (1973), both in `sources/` (PDF + Markdown).
D-6398 test aircraft: basic mass 13 608 lb, pilot 230 lb, fuel 6228 lb, total 20 066 lb.
Wikipedia (specifications per NASA SP-468): empty weight 14 000 lb, MTOW 29 027 lb, ceiling 73 000 ft
(record/zoom value, not service ceiling), climb rate 48 000 ft/min, L/D max 9.2.

Minimum turning radius and ground clearance: FM Fig. 2-4 (not read yet).

## Weights (F/RF-104G)
| Configuration | lb | Status / source |
|---|---|---|
| Empty (no fuel, no pilot) | 14 760 | confirmed, FM 1-5 / PDF 17 |
| Full, no external stores (with gun + 725 rounds) | 20 800 | confirmed, FM 1-5 / PDF 17 |
| AIM-9B missiles | 21 200 | confirmed, FM 1-5 |
| Tip tanks | 23 450 | confirmed, FM 1-5 |
| Missiles + pylon tanks | 24 350 | confirmed, FM 1-5 |
| Tip tanks + pylon tanks | 26 600 | confirmed, FM 1-5 |
| Max. takeoff weight | 29 027 | provisional; further configurations in the FM appendix |

FM 5-15: "There are no weight limitations as long as standard external load items are used."

## Fuel (JP-4, 6.5 lb/US gal)
Source: FM Fig. 1-35 "Fuel Quantity Data", FM 1-49 / PDF 65. Status: confirmed.

| Tank | usable (flight attitude) lb / gal | full (ground attitude) lb / gal |
|---|---|---|
| Main cells (forward + aft) | 4901 / 754 | 4959 / 763 |
| Auxiliary tank | 923 / 142 | 929 / 143 |
| Extended-range tanks F-104G (instead of gun) | 793 / 122 | 799 / 123 |
| Tip tank (each) | 1105 / 170 | 1137 / 175 |
| Pylon tank (each) | 1267 / 195 | 1293 / 199 |

Total usable: internal 5824 lb (896 gal), with tip tanks 8034 lb (1236 gal), with pylon tanks 8359 lb
(1286 gal), with both 10 569 lb (1626 gal).
Layout: forward main cell (all pumps, feeds the engine), aft main cell (3 connected cells), auxiliary tank ahead of
the main cell; external tanks transfer by bleed air into the aft main cell (FM 1-42/43, PDF 58/59).

## Engine: GE J79-GE-11A
| Value | Status / source |
|---|---|
| Dry thrust (military, static sea level) approx. 10 000 lbf | confirmed, FM 1-5 / PDF 17 |
| Thrust with afterburner (maximum) approx. 15 800 lbf | confirmed, FM 1-5 / PDF 17 |
| 17-stage axial compressor, 3-stage turbine | confirmed, FM 1-5 |
| 100 % rpm = 7460 rpm | confirmed, FM 1-5 |
| RPM: min. 66 %, normal 87-104.5 %, max. 107 % overspeed | confirmed, FM 5-3 / PDF 377 |
| EGT: continuous 50-600 °C, max. 1000 °C (overtemperature) | confirmed, FM 5-3 / PDF 377 |
| Fuel flow: 400-12 000 lb/h normal range | confirmed, FM 5-3 / PDF 377 |
| Oil quantity 28-30 pints | confirmed, FM 1-40 / PDF 56 |
| Nozzle indication: idle 8.5-9.5; military 1.0-3.5; max. A/B 7.5-9.5 | confirmed, FM 5-3 / PDF 377 |

RPM/EGT/nozzle vs. throttle angle: FM Fig. 1-30, FM 1-40 / PDF 56 (useful for `engines.cfg`).
Throttle: cutoff, idle, cruise, military, A/B transition, sector burning, uniform burning (up to approx. 115°).

## Speeds and limits
| Value | Status / source |
|---|---|
| Max. 750 KIAS (EAS limit engine), limit Mach 2.0 | confirmed, FM Fig. 5-2 / PDF 378 |
| Mach limit from inlet air temperature (CIT 121 °C MAP / 100 °C consortium) | confirmed, FM 5-2, 5-4 |
| Gear extended | 295 KIAS, confirmed, FM 5-5 / PDF 379 |
| Gear extension/retraction | 260 KIAS, confirmed, FM 5-4 / PDF 378 |
| Flaps LAND | 240 KIAS, confirmed, FM 5-2, 5-5 |
| Flaps TAKEOFF | per FM Fig. 5-7 to 5-9 |
| Drag chute MB-7G / BS-4000 | 180 / 205 KIAS, confirmed, FM 5-5 |
| Load factors F/RF | +7.33 g / −3.0 g (no external stores, ≤ 5500 lb fuel), confirmed, FM 5-2 / PDF 376 |
| Hydraulics 2800-3200 psi normal, max. 3850 psi | confirmed, FM 5-2 / PDF 376 |

## Controls (FM 6-3 / PDF 393, status: confirmed)
- **Ailerons**: gear up ±9.75°, gear down ±20°.
- **Rudder**: gear down ±20°, gear up automatically ±6° about the trim position. Trim range ±4°.
- **Horizontal tail** (all-moving): max. 17° leading edge down (nose up); full 17° only when trimmed between 1° and
  11° leading edge down; takeoff trim 5° leading edge down (FM 6-5 / PDF 395).

## Flight characteristics (FM Section VI, from PDF 391)
- Takeoff: initiate rotation approx. 20 kt below the computed takeoff speed, nose wheel lifts 10-20 kt below (FM 6-5).
- **Pitch-up** in the stalled condition (T-tail, small wing); APC system: stick shaker, then stick kicker (FM 6-5).
- Stability augmenters in yaw and roll ("motion damped completely" below 400 kt), damper in pitch
  (FM Fig. 6-1, 6-2 / PDF 393, 394).
- High T-tail acts as an end plate on the fin: effective dihedral of the fin equivalent to 15-20°, reduced to 5-10°
  net by the −10° wing anhedral (FM 6-2).
- BLC: bleed air over the landing flaps, reduces landing speed (FM 1-74).

## Aerodynamics and thrust: NASA TN D-7137 (basis for the flight model)
Clean tables in `docs/data/` (checked against the scan):
- `nasa_d7137_cl_alpha_mach.csv`: CL over α (0-14°) and Mach 0.4-2.0. Subsonic: dCL/dα ≈ 0.055/° (M 0.4).
- `nasa_d7137_cd_mach_cl.csv`: drag polar CD(M, CL). **CD0 = 0.0160** (subsonic), rise from M 0.9, maximum 0.050 at
  M 1.1-1.15, 0.042 at M 2.0.
- `nasa_d7137_thrust_maxab_lbf.csv`: net thrust max. afterburner (installed) over altitude 0-60 000 ft and Mach 0-2.
- `nasa_d7137_fuelflow_maxab_lbs.csv`: fuel flow max. afterburner.
Valid without external stores, flaps retracted. Thrust values are predictions (Lockheed); the flight tests confirm
them within ±5 %. CR-96008 (see `notes/research.md`) independently confirms CL at M 1.0.

## Inertia and stability: NASA CR-2144 (F-104A)
Details in `docs/data/nasa_cr2144_f104a.md`. In short: MAC c̄ = 9.55 ft (25 % at F.S. 472.5 in);
Ix/Iy/Iz = 3549 / 58 611 / 59 669 slug·ft² at 16 300 lb (CG 0.070 c̄);
approach: 170 kt, α 2.3°, flaps 45° + BLC, CL 0.735, CD 0.263, CLα 3.44/rad, Cmα −0.64/rad, Cnβ 0.50/rad.
Status: confirmed for the F-104A, guide value for the G (heavier, larger fin).

## Tail geometry: NACA RM SL56H06 (F-104A wind-tunnel model, scale 0.04)
Spearman et al., *Longitudinal and lateral stability characteristics of a 0.04-scale model of the Lockheed F-104A
airplane at Mach numbers of 1.82 and 2.01*, NACA RM SL56H06, 1956 (declassified; NTRS 20090026345, downloaded
2026-10-25, not in the repo). Table I (PDF 15), converted to full scale (lengths / 0.04, areas / 0.0016):

| Item | Model | Full scale | Remark |
|---|---|---|---|
| Wing area / span / MAC | 0.3137 ft² / 10.48 in / 4.584 in | 196.1 ft² / 21.83 ft / 9.55 ft | matches D-6398, CR-2144 |
| Wing LE sweep / taper / dihedral | 27.1° / 0.377 / −10° | same | 3.36 % modified circular arc |
| Horizontal tail area / span / MAC | 0.0771 ft² / 5.72 in / 2.116 in | 48.2 ft² / 11.92 ft / 4.41 ft | matches D-6398 |
| Horizontal tail LE sweep / taper | 19.5° / 0.311 | same | quarter chord 10.1°, midchord 0° |
| **Vertical tail V2 (basic F-104A)**: area to theoretical root / span | 8.30 in² / 2.66 in | **36.0 ft² / 5.54 ft** | theoretical root 1.52 in (3.17 ft) above the fuselage reference line |
| V2 root chord / tip chord / MAC / taper | 4.50 / 1.70 / 3.44 in, 0.378 | 9.38 / 3.54 / 7.17 ft | aspect ratio (panel) 0.85 |
| V2 LE sweep / quarter-chord sweep | 52.3° / 34.9° | same | 4.25 % modified circular arc |
| Vertical tail V3 ("enlarged", tested) | 11.7 in², span 3.61 in, LE 44.0° | 50.8 ft², 7.52 ft | wind-tunnel variant, not necessarily the G fin |
| Ventral fins U1 / U2 / U3 / U4 | 5.8 / 3.5 / 2.2 / 1.6 in² | 25.2 / 15.2 / 9.5 / 6.9 ft² | report: U2 preferred (no ground-clearance restriction) |

## Surface areas F-104G: historicalfighters.com (secondary source)
https://historicalfighters.com/f-104g-general-technical-data/ (read 2026-10-25; no original source cited, page does
not state the "25 % larger" claim). Plausibility: its horizontal tail 48.21 ft² matches D-6398 (48.2 ft²) exactly,
wing 196.1 ft² as well.

| Surface | ft² | m² | cfg today |
|---|---|---|---|
| **Vertical stabilizer (fin)** | **47.77** | 4.44 | `vtail_area` 38 [S] |
| Rudder | 5.48 | 0.51 | `rudder_area` 9 [S] |
| Ventral fin | 5.81 | 0.54 | not modelled separately |
| Horizontal stabilizer | 48.21 | 4.48 | 48.2 ✓ |
| Ailerons (total) | 9.47 | 0.88 | `aileron_area` 12 [S] |
| Trailing edge flaps (total) | 23.13 | 2.15 | – |
| Leading edge flaps (total) | 17 | 1.58 | – |

Status: provisional (secondary). Consistent with the G having a larger fin than the A (36.0 ft², NACA RM SL56H06):
47.77/36.0 = 1.33, and between the A fin and the tested V3 (50.8 ft²). Unclear whether 47.77 ft² is the exposed area
or measured to a theoretical root.

## Fin measured on the NASA TN D-6398 three-view (Fig. 2, PDF 24, F-104G test airplane)
Digitized at 600 dpi (scratchpad script, method: polygon area). Scale from the drawing's own dimensions: height
13.49 ft = 753 px (55.8 px/ft vertical), length 54.77 ft = 2937 px (53.6 px/ft longitudinal; scan distortion 4 %).
- Area above the fuselage top line (incl. dorsal blend and tip fairing): **≈ 57 ft²**; without the dorsal fillet
  (straight leading edge) ≈ 56.5 ft². Very sensitive to the root definition: 1 ft of height ≈ 12 ft² -> consistent
  with 47.77 ft² measured to a higher reference line.
- **Leading-edge sweep ≈ 45°** (A fin V2: 52.3°, enlarged wind-tunnel fin V3: 44.0°), height above the fuselage
  at the nozzle ≈ 7.2 ft (V3: 7.5 ft), root chord ≈ 12.5 ft, tip chord ≈ 4.8 ft.
- **Conclusion: the F-104G has the enlarged fin (V3 type, ~50.8 ft² to the theoretical root), not the A fin.**
  Use for the cfg (AP-11): `vtail_area` ≈ 48-51 ft² [Q/M], `vtail_sweep` 45° [M], span ≈ 7.2-7.5 ft.

Use: The cfg uses `vtail_area` 38 ft², span 5.5 ft (close to the A fin V2) but
`vtail_sweep` 40° (V2: LE 52.3°) and `htail_sweep` 10° (LE 19.5°; 10° is the quarter-chord value) and `wing_sweep`
26° (27.1°). **Candidates for AP-11** (Dutch roll too fast): the fin in the cfg is even smaller than the G fin
(38 vs. 47.77 ft²), so the excess directional stiffness must come from `rudder_lift_coef` 5.0 or the fuselage terms.
In the AP-11 round: fin area 47.77, rudder 5.48, aileron 9.47 ft², sweeps per RM SL56H06, then reduce the fin lift
slope until the Dutch roll period matches CR-2144 (and re-check β/δr = 0.32, T3-E, and aileron power).
Also from the report: "a considerable portion of the vertical-tail contribution to directional stability was
required to overcome the large unstable yawing moment caused by the long fuselage" (conclusion 2).

## Still open
- F-104G fin area: 47.77 ft² from a secondary source (historicalfighters.com, see above); a primary source
  (Lockheed report, FM) would still be good.
- Scale moments of inertia to the F-104G mass: CR-2144 values are for 16 300 lb; the G at 18-20 000 lb is heavier
  mainly through fuel near the CG, so Iy/Iz grow less than the mass ratio - keep CR-2144 values until a source is found.
- Slow flight below Mach 0.4 (lift/drag tables start at M 0.4). Flap effect: done (AP-10, T3-D run 6).
- CG limits: **FM 5-15 gives no numbers** ("With any combination of standard external load items the center of
  gravity remains within limits"; no weight limitations with standard items) -> `CG_forward_limit`/`CG_aft_limit`
  stay [S] (CR-2144 range 0.07-0.164 c̄).
- Takeoff: liftoff speed FM Fig. A2-3 (PDF 457, used for T3-D); ground run Fig. A2-4 (PDF 458) not read yet.
  Landing: see below.

## Landing (FM Section II and appendix Part 8)
- **Landing speed schedule** (Fig. A8-2, PDF 549, flight test): LAND flaps final approach 170 KIAS up to 15 000 lb,
  +5 kt per 1 000 lb (210 kt at 23 000 lb); normal touchdown 152 -> 192 kt. TAKEOFF flaps: final 190 -> 255 kt, minimum
  touchdown 160 -> 224 kt (15 000-27 500 lb). No flaps: final 225 -> 290 kt, touchdown 190 -> 254 kt.
- **Typical landing pattern** (Fig. 2-7, PDF 158, 16 100 lb): LAND flaps at 240-210 KIAS (~88 % rpm), base >= 200 KIAS,
  final >= 190 KIAS, roll-out on final >= 6 000 ft from the runway at ~300 ft; flat powered approach at ~88 % rpm,
  engine >= 83 % (BLC lift depends on engine airflow); at heavy weight even military may not hold the descent rate in
  the final turn (high drag with LAND flaps).
- Pilot report (Rolf Stünkel, migflug.com): basic approach 175 kt with full flaps + 5 kt per 1 000 lb fuel above 1 000 lb;
  BLC worth about 40 kt (forum recollection); loss of BLC drops the nose.
- **Landing technique** (FM 2-25, PDF 157): carry power on the approach; in the flare reduce thrust smoothly to
  82-83 % rpm, idle when the main gear touches (abrupt reduction -> roll-off and sink). Normal landing speed range
  155-160 KIAS (Fig. 2-7 weight 16 100 lb, +5 kt per 1 000 lb). After touchdown: idle, lower the nose wheel, nose wheel
  steering, **drag chute as soon as the nose wheel is down** (nose-down moment, so only with all three gear on the
  ground; 18-ft chute, Fig. A8-3; deploy ≤ 180 KIAS MB-7G / 205 KIAS BS-4000, FM 5-5). Speed brakes: not needed in the
  pattern, allowed in the roundout, not during the ground roll. Max. crosswind 25 kt (chute: 25 kt at 90°, 35 kt at 45°).
  Holding off to lower speeds -> wing drop and tail dragging.
