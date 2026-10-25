# F-104A: masses, inertia, stability derivatives (NASA CR-2144)

Source: Heffley & Jewell, *Aircraft Handling Qualities Data*, NASA CR-2144, Dec. 1972, Section III F-104A
(PDF `sources/NASA_CR-2144_Heffley_Handling_Qualities_Data.pdf`, chapter PDF 38-66). Primary source there:
Lockheed LR 10794 (Stability and Control, F-104A, 1955), drag from LR 12873.
All values read from the scan (PDF 40, 41, 43).

**Caution: F-104A, not F-104G.** The G is heavier (empty weight 14 760 lb, FM 1-5) and has a larger fin.
Use the moments of inertia as a starting point and scale them with mass.

## Reference values (PDF 41, Fig. III-2)
| Quantity | Value |
|---|---|
| Wing area S | 196.1 ft² |
| Span b | 21.94 ft |
| Mean aerodynamic chord c̄ (MAC) | 9.55 ft |
| 25 % c̄ at fuselage station | F.S. 472.5 in |
| MAC at span station | B.L. 55.8 in |
| Cockpit (pilot's eye, approx.) | F.S. 236 in, W.L. 129 in |
| Thrust axis | W.L. 103.4 in, 2.5° to the fuselage reference line (W.L. 100) |

## Configurations (PDF 40, Fig. III-1)
| | Nominal (combat) | Power approach (PA) |
|---|---|---|
| Condition | clean, 750 rounds, 50 % fuel | clean, 20 % fuel, flaps 45° + BLC, gear down, 1.4 Vs |
| Weight W | 16 300 lb | 14 126 lb |
| CG | 0.070 c̄ | 0.164 c̄ |
| Ix | 3 549 slug·ft² | 3 450 slug·ft² |
| Iy | 58 611 slug·ft² | 55 800 slug·ft² |
| Iz | 59 669 slug·ft² | 56 800 slug·ft² |
| ε (principal axis to fuselage axis) | 2.76° | 2.86° |

Moments of inertia in principal axes.

## Stability derivatives, power approach (PDF 43, Table III-1)
Sea level, V = 287 ft/s = 170 kt, α₀ = 2.3°, stabilizer δs = −7.1°. All values per rad.

| Longitudinal | | Lateral-directional (stability axes) | |
|---|---|---|---|
| CL | 0.735 | Cyβ | −1.17 |
| CD | 0.263 | Cnβ | 0.50 |
| CLα | 3.44 | Clβ | −0.175 |
| CDα | 0.45 | Clp | −0.285 |
| Cmα | −0.64 | Cnp | −0.14 |
| Cmα̇ | −1.6 | Clr | 0.265 |
| Cmq | −5.8 | Cnr | −0.75 |
| CLδs | 0.68 | Cnδa | 0.0042 |
| Cmδs | −1.46 | Clδa | 0.039 |
| | | Cyδr | 0.208 |
| | | Clδr | 0.045 |
| | | Cnδr | −0.16 |
| | | Cyδd | 0.0325 |
| | | Cnδd | −0.025 |
| | | Clδd | −0.0044 |

(δd = differential/spoiler effect per CR-2144; δa = ailerons.)
Used so far: Cnδr/Cnβ = 0.32 as target for the rudder test T3-E; Cnβ for the Dutch roll estimate (T3-J).

## Lateral-directional dimensional derivatives (PDF 62, Table III-9, body axes, per rad, primed)
| F/C | H | M | L'β | N'β | L'δa | N'δa | L'δr | N'δr | L'p | N'r |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | SL | 0.257 | -20.9 | 2.68 | 4.76 | 0.266 | 5.35 | -0.923 | -1.38 | -0.157 |
| 2 | SL | 0.80 | -146 | 13.6 | 49.6 | 3.51 | 41.5 | -7.07 | -4.64 | -0.498 |
| 4 | 15 000 ft | 0.90 | -134 | 9.91 | 34.7 | 2.64 | 27.6 | -4.49 | -3.63 | -0.350 |
| 5 | 35 000 ft | 0.60 | -32.3 | 1.06 | 6.35 | 0.407 | 6.66 | -1.18 | -0.374 | -0.0809 |
| 6 | 35 000 ft | 0.90 | -58.1 | 4.98 | 14.8 | 1.01 | 11.2 | -1.91 | -1.77 | -0.169 |
| 7 | 35 000 ft | 1.20 | -115 | 11.9 | 19.4 | 1.49 | 13.1 | -2.09 | -2.27 | -0.292 |
Flight conditions (PDF 55, Table III-2): F/C 4 = 465 KCAS, α 4.8°; F/C 6 = 311 KCAS, α 2.5°; W 16 300 lb.
Steady sideslip (p = r = 0) per unit rudder: β/δr = 0.32-0.42, δa/δr = 0.27-0.47 (used for T3-E2, round E).
Open: whether δa is one aileron or the sum (Fig. III-3: 2.14°/in lateral stick).

## Not yet used
- Remaining tables III-3 to III-12 (PDF 56-65, sideways, `tools/pdf_clip.py --rot 90`): longitudinal dimensional
  derivatives, transfer functions, handling qualities parameters (Dutch roll period/damping -> T3-J).
- Control system (gearing, feel, dampers): Fig. III-3, PDF 42.
