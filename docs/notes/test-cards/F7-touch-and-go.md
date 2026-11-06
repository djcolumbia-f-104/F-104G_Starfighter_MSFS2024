# F7: touch-and-go (FM 2-28)

**Objective / acceptance:** fly the FM 2-28 touch-and-go from a normal F3-type approach (LAND flaps, FM flare): after the
touchdown 1. IDLE, 2. flaps TAKEOFF, 3. MILITARY, 4. speed brakes IN, 5. trim as required (takeoff trim 5°), 6. normal
takeoff technique (rotation ≈ 20 kt below the takeoff speed, attitude ≈ 5-10°, liftoff ≈ 178-182 KIAS at 19 000 lb as T3-D).
Acceptance: FM sequence, no tail strike (pitch on the ground < 12.3°), single liftoff, liftoff speed 178-185 KIAS, airborne
before 8 000 ft past the threshold (runway 26L 13 100 ft). No FM distance reference (recorded only).

**Tool:** `landing_test.py <csv> 6 2.5 0 nochute fmflare tg[=stop]` (new phase `tg`, FAST loop forced; card text in the
script header). Rotation = the takeoff_test srot law (stick schedule to S_HOLD -6 600 = α 10.5° in the air, attitude
integrator from θ > 3°, rate damping 150 counts per °/s, never push, tail guard θ > 11° below 20 ft) with a ramp over 25 kt
OR 4 s (Military accelerates slower than the T3-D Maximum takeoff); from 35 ft AGL the F8 go-around law (bumpless offset
over 5 s). Nose-wheel hold +2 000 (nose down) until the rotation.

**Analysis / prediction (desk):** TD ≈ 173 KIAS ≈ 2 300 ft past the threshold (F3 series). Idle 1-1.5 s, flaps LAND -> TAKEOFF
≈ 2 s, J79 idle -> Military ≈ 5-7 s (FM ≤ 10 s): the jet decelerates at ≈ 5-6 kt/s rolling with idle/flaps (no brakes) -> minimum
≈ 150-158 KIAS at ≈ 4 500-5 500 ft, then accelerates at Military (≈ 3-4 kt/s) -> rotation from 155-160, liftoff ≈ 178-182 at
≈ 6 500-7 500 ft. If the speed falls below 140 KIAS before the rotation -> abort (full stop); still on the ground at 8 000 ft
-> abort (stop from ≤ 185 KIAS without chute ≈ 3 500 ft -> ≈ 11 500 ft < 13 100).

**Hazards:** (1) new ground sequence at high speed (the srot law starts from a rolling jet at Military instead of from rest
at Maximum) -> build-up `tg=stop` first: the same ground run to 170 KIAS / 7 000 ft without rotation, full stop (checks the
reconfiguration, speed history, distances, nose-wheel hold, rudder law). (2) Runway length: aborts at 8 000 ft / < 140 KIAS.
(3) Rotation: srot validated on T3-D with the same flaps/trim; tail guard; never push. (4) Climb-out: F8 law (validated).
(5) Skip at the touchdown (1 per F3 landing): the idle phase waits for the nose wheel (θ < 1.5° on the ground).

**Go/no-go:** build-up (S16-F7a, tg=stop) GO 2026-11-06; real T&G only if the build-up matches the prediction (speeds,
distances) and the nose stayed down.

## Result + Debrief (2026-11-06) - PASSED (after a go-around law fix)
- **Build-up S16-F7a (tg=stop):** TD 172 KIAS (2 skips; the idle phase waited for the nose wheel), flaps TAKEOFF at 169 KIAS /
  3 771 ft, MILITARY at 162 / 4 714 ft, minimum 160 KIAS, N1 95 % at ≈ 166 KIAS (≈ 5 700 ft), 172 KIAS at 6 141 ft -> full stop
  ✓; nose wheel held down (pitch 0.1-0.8°). Prediction ✓ (minimum 150-158 predicted, 160 measured).
- **S16b-F7 (first real T&G):** rotation from 166 KIAS / 5 778 ft, **liftoff 180 KIAS** pitch 9.1° at 6 814 ft, single liftoff,
  max pitch on the ground 5.7°; climb-out law at 36 ft ✓. **Finding in the climb-out (not the T&G law):** after flaps UP at
  340 KIAS the go-around law (gains for ≈ 190 KIAS) oscillated in pitch (0 <-> 15°, ≈ 5 s) and roll (up to -42°) at 380-450
  KIAS / 1 200-1 500 ft AGL; a failed AGL read dead-reckoned AGL to 15 ft. The sortie's `position` step recovered the jet.
  Other go-arounds today already showed 14° pitch swings above 330 KIAS. Fix (lesson 25): go-around elevator gains x
  (v_app/IAS)², aileron gains x v_app/IAS (ks = 1 up to v_app -> the low-altitude part is unchanged); AGL failed-read guard.
  Check S17-GAscale (F8 dry, FAST): loss 12 ft (unchanged), above 250 KIAS pitch 4.2-7.6°, bank ±3° ✓.
- **S16c-F7 (repeat, PASSED):** TD 173 KIAS -344 ft/min at 2 242 ft (1 skip), flaps TAKEOFF at 167 KIAS / 3 039 ft, MILITARY
  162 / 3 962 ft, rotation from 165 / 5 091 ft, **liftoff 182 KIAS** at 6 521 ft (4 279 ft after the touchdown), single liftoff,
  **max pitch on the ground 8.1°** (tail 12.3°), 12.4° at ≈ 5 ft (T3-D 8.6-9.4° - a little more overshoot from the rolling
  start, noted), gear up 254 KIAS (< 260), flaps UP 341 KIAS; climb-out pitch 4-14°, bank ≤ ±3°. Acceptance ✓ (FM sequence,
  liftoff 178-185, airborne before 8 000 ft, no tail strike).
