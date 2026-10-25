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

## Not yet used
- Derivatives over Mach and altitude for flight conditions 1-10 (plots PDF 44-54, tables III-2 to III-12 on PDF
  55-65, printed sideways; read with `tools/pdf_clip.py --rot 90`). **Includes lateral-directional derivatives at
  cruise/high speed -> useful for AP-6 (rudder, roll due to sideslip).**
- Control system (gearing, feel, dampers): Fig. III-3, PDF 42.
