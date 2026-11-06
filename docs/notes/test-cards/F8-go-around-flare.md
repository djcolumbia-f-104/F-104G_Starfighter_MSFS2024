# F8: go-around from the flare (FM 2-29, Fig. 2-8)

**Objective / acceptance:** fly the FM 2-29 go-around started in the flare (LAND flaps, gear down, FM flare at 82 % N1):
height loss ≤ 100 ft (test plan) and no ground contact; positive climb established; FM sequence (Military/Maximum, speed
brakes in, gear up when definitely airborne and climbing, TAKEOFF flaps ≥ 180 KIAS, UP ≥ 260 KIAS after 30 s). Climb
performance itself = B6 (Fig. 6-8, validated +905..+982 ft/min at Military).

**Tool:** `landing_test.py <csv> 6 2.5 <high> nochute fmflare ga=50` (new option ga=<ft>: go-around commanded in the flare
below <ft> AGL; prints height loss, lowest AGL, time to a positive climb). Default LAND path (1.8 Hz loop, validated).

**Analysis / prediction:** go-arounds after the virtual touchdown today (sink ≈ -480..-540 ft/min): LAND (S14 dry) loss 17 ft
in 2.5 s, positive climb after 3.2 s; earlier LAND dry runs 24-30 ft. At 50 ft in the flare the sink is ≈ -400..-600 ft/min
and the throttle at the 82 % floor (spool-up to Maximum ≈ 2-4 s, BLC f(N1) rises with it). **Prediction: loss 15-30 ft,
lowest 20-35 ft AGL, positive climb after 2.5-4 s, IAS ≈ 170-175 KIAS at the bottom.** Ground effect (real run) lowers the
sink -> real loss ≤ dry loss.

**Hazards:** (1) loss larger than predicted (> 50 ft = ground contact): build-up dry run with the same trigger at +6 000 ft
first; GO for the real run only if the dry loss ≤ 30 ft. Gear contact at low sink would be a touch-and-go-like event (gear
down, LAND flaps) - survivable, script continues the go-around. (2) Tail strike: pitch in the go-around 5-15°; tail
geometry 12.3° only with the wheels on the ground - guard (pitch > 11° below 60 ft) is in the approach/flare branch only;
the go-around starts above 20 ft. (3) Low fuel in the go-around (Maximum) - refuel before.

**Postconditions:** script ends clean ≥ 1 500 ft AGL with AP ALT hold; sortie repositions to 16 500 ft + post.py air.

**Go/no-go:** dry run first (S15-F8 step dry); real run GO only if dry loss ≤ 30 ft.

## Result + Debrief (2026-11-06) - PASSED
| Run | trigger | height loss | lowest | positive climb | sequence |
|---|---|---|---|---|---|
| dry (S15-F8, +6 000 ft) | 46 ft, 186 KIAS, -536 ft/min | 13 ft | 33 ft | 1.9 s | gear + TAKEOFF flaps at 195 KIAS (VS +1 800), UP at 327 KIAS after 30 s; pitch ≤ 17.5°, bank ±1.6° |
| **real (S15b-F8, EDDM 26L)** | 49 ft, 187 KIAS, -525 ft/min | **13 ft** | **36 ft AGL** | **2.1 s** | gear + TAKEOFF flaps at 202 KIAS (VS +1 900), UP at 341 KIAS; pitch ≤ 16.6°, bank ±2.1°, no ground contact |
19 009 lb, LAND flaps, gear down, FM flare (82 % floor), Maximum. Prediction 15-30 ft / 2.5-4 s -> measured slightly better
(13 ft / 2 s: the 82 % floor keeps the J79 spooled, BLC lift stays). Acceptance (≤ 100 ft, no contact) ✓; FM 2-29 sequence ✓.
Anomaly: none in the flight; the first S15b start stopped at the selftest (watchdog fuel line older than the last refuel -
second time, 2026-11-05 too) -> selftest now waits for the next watchdog line before failing (lesson 24).
