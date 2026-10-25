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
| Leading-edge sweep | 26° | | provisional (Wikipedia) |
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

## Still open
- Root/tip chords, F-104G fin area: no source yet (CR-2144 drawing of the A gives ≈ 38 ft²).
- Scale moments of inertia to the F-104G mass.
- Flap effect (TAKEOFF/LAND, BLC) and slow flight below Mach 0.4.
- CG limits (read FM 5-15 "Center of Gravity Limitations").
- Takeoff and landing distances, approach speeds: FM appendix (Performance Data), Section II.
