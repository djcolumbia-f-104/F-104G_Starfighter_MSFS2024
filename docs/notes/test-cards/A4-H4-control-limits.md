# A4 / H4: control travel limits with the gear (FM 1-67, 6-3) - desk evaluation 2026-11-06

**Reference:** FM 1-67 (PDF 83) aileron travel limiting system: gear DOWN ±20°, gear UP ±9.75° (+5° more with aileron trim),
electrically switched by the gear (RUD/AIL LIMIT CONT breaker removes it); rudder likewise ±20° gear down / ±6° gear up
(FM 6-3). The flight controls are irreversible hydraulic ("cannot be moved by external aerodynamic forces", FM 1-67) ->
the real limits do NOT depend on dynamic pressure.

**Sim (cfg):** aileron_up/down_limit 20, rudder_limit 20 (gear-down values) x elasticity tables (template shapes)
aileron 0:1, 100:1, 250:0.5; rudder 0:1, 100:1, 250:0.3 (q̄ psf). SDK: deflection = limit x elasticity(q̄). Checked against
two measurements: roll_id 210 KIAS (q̄ 149) aileron 16.6° (formula 16.7°); T3-E2 460 KIAS rudder 6.0° (formula 6.0°) ✓.

| KIAS | q̄ psf | aileron sim | / FM gear up 9.75° | rudder sim | / FM gear up 6° |
|---|---|---|---|---|---|
| 150-170 | 76-98 | 20.0° | 2.05x | 20.0° | 3.33x |
| 190 | 122 | 18.5° | 1.90x | 17.9° | 2.99x |
| 210 | 149 | 16.7° | 1.71x | 15.4° | 2.57x |
| 230 | 179 | 14.7° | 1.51x | 12.6° | 2.10x |
| 250 | 212 | 12.6° | 1.29x | 9.6° | 1.60x |
| 260 | 229 | 11.4° | 1.17x | 8.0° | 1.33x |
| ≥ 280 | ≥ 265 | 10.0° | 1.03x | 6.0° | 1.00x |
Gear down (approach 165-210 KIAS): sim 15-20° instead of 20° (0.77-1.0 x).

**Result: documented deviation (◑).** Gear-up flight above ≈ 280 KIAS matches the FM (all validated lateral tests: C4 at
465 KCAS, T3-E2/T3-J at 460 KIAS); gear-up flight below ≈ 280 KIAS has 1.3-2x aileron and 1.6-3.3x rudder authority (low-speed
clean handling, B7, pitch-up recovery); gear-down approach slightly less (≤ -23 %). No cfg change now: a re-shaped
elasticity table is only a compromise between the two gear states and would shift the just-validated landing loops (F6 at
210 KIAS: aileron gain +19 %). **Proper fix: a gear-switched limiter** - not possible in the systems module (it cannot
override pilot axis inputs, H2 lesson) -> in the cockpit phase (AP-9) via the aircraft's input events / model behaviors
(clamp AXIS_AILERONS_SET / AXIS_RUDDER_SET with the gear handle), with the elasticity tables set to 1 (irreversible
controls). Regression then: C4, T3-E2, T3-J, H1 damper, F3/F6 landings, sideslip/doublet tools.
