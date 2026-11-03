# H1: own stability augmentation (SAS) - yaw, pitch, roll dampers in the systems module

Method: skill `f104-testcard` incl. 2b (new control law -> analysis + build-up). Module: `source/wasm/f104_systems/`.

## Objective / acceptance
The F-104G flies with a three-axis SAS "at all times" (FM 6-4); the sim is the bare airframe (CR-2144 derivatives are SAS
off, "their effect is not shown", PDF 39; our T3-J / C4 match them). H1 adds the dampers so that
- Dutch roll (T3-J doublet, 15 000 ft, M 0.9): SAS off 1.41 s / 0.43 per cycle (CR-2144 III-12, sim 1.48-1.60 s / 0.55-0.57)
  -> SAS on "motion damped completely" (FM Fig. 6-1): **amplitude ratio per cycle ≤ 0.1 (ζ ≥ 0.35)**, period ± 15 %.
- short period (pitch doublet, same point): SAS off ζ 0.289, ωn 4.54 rad/s (CR-2144 III-5 F/C 4) -> SAS on "damped
  immediately and completely" (FM Fig. 6-2): **ζ ≥ 0.5, no second overshoot**.
- steady manoeuvres unchanged: yaw/roll washout -> steady turn, steady sideslip (T3-E2) and steady roll rate (C4 linear,
  45/95°/s) within ± 5 % of SAS off. Pitch has NO washout (FM 1-68) -> steady pitch rate in a pull-up reduced (accepted,
  real behaviour).
- the full-deflection roll (C4, 248°/s + departure without SAS) is flown only after yaw + pitch dampers pass.

## Sources (read 2026-11-03)
- FM 1-68 (PDF 84): three-axis SAS; rate gyros -> electrically amplified signal -> hydraulic valves move rudder, stabilizer
  or ailerons "relative to the amount of correction necessary"; does NOT move the control linkage or the cockpit controls;
  washout circuit cancels the signals in favour of pilot-initiated ones; **no washout in pitch** (to limit pitch changes /
  high negative g). Guarded switches STABILITY CONT ROLL/PITCH/YAW; any one or two can be off without affecting the
  others; **if any channel is off the autopilot disengages**.
- FM 6-3 Fig. 6-1 (PDF 393): yaw and roll motion without SAS "decreases with time" subsonic, "remains essentially
  constant" supersonic; with SAS "damped completely" (below and above 400 KIAS). FM 6-4 Fig. 6-2: pitch without SAS "good
  damping but some oscillations" subsonic, lighter supersonic; with SAS "damped immediately and completely". Yaw failure:
  surface stays or drifts slowly, damping noticeably reduced; roll failure: more sensitive to roll disturbances in
  turbulence, the yaw augmenter alone damps the Dutch roll.
- CR-2144 Fig. III-3 (PDF 42): δs_SAS and δa_SAS are summed after the pilot gearing (no gains given). Tables III-3 (PDF 56),
  III-5 (PDF 58), III-9 (PDF 62), III-12 (PDF 65), all SAS off.
- No SAS gain/authority source found (FM, CR-2144); gains below are [S] from the derivatives and a damping target
  (MIL-F-8785C level 1: ζ_DR ≥ 0.4 cat. A, ζ_SP 0.35-1.3). To do: NTRS search "F-104 stability augmentation gain" (2b.5).

## Analysis
### Actuator channels (MSFS 2024 does not mask pilot axis inputs - H2 lesson)
The SAS must add to the pilot's input without moving the stick -> the trim channels ("deflection adds to the rudder/
elevator deflection", SDK flight_model.cfg `rudder_trim_limit`, `elevator_trim_limit`):
| axis | channel | range | conflicts |
|---|---|---|---|
| yaw | RUDDER TRIM (PCT) | ± 4° (`rudder_trim_limit` 4 [Q] FM 6-3) shared with the pilot's rudder trim | none known (AP yaw damper off) |
| pitch | ELEVATOR TRIM POSITION | -5..+11° shared with pilot trim + APC kicker | **MSFS AP flies by trim and locks it** -> pitch SAS inactive while the AP is engaged, and while the kicker acts / retracts |
| roll | AILERON TRIM (PCT) | `aileron_trim_limit` not set (template default unknown) | AP wing leveler (ailerons) - to check |
Unknowns -> build-up bu0 (below): settable at all, sign, degrees per percent, lag/rate limit, does the trim degree act
like a rudder degree of CR-2144 (β/δr 0.32-0.42 measured for the rudder in T3-E2)?

### Damper law (per axis)
δ_SAS = -K(q̄) x HP(ω_body), HP = washout s τ/(1 + s τ) for yaw/roll (τ_w 1.0 s [S]: phase lead at the Dutch roll
ω 4.5 rad/s only 13°, steady turn rates washed out in ≈ 3 s), none for pitch. Gain scheduled with dynamic pressure
K = K_ref x q̄_ref / q̄ (control power N'δ, M'δ ∝ q̄), q̄ clamped ≥ 200 psf (gain ≤ 3.7 K_ref), q̄_ref = 732 psf (F/C 4).
Rates from ROTATION VELOCITY BODY X/Y/Z (rad/s; signs from bu0) at the sim frame rate (module; a Python loop with
3 reads runs ≈ 5 Hz = 26° phase lag at 0.7 Hz -> too slow, prototype directly in the module).

**Yaw** (CR-2144 F/C 4: N'δr -4.49, Dutch roll ωd 2π/1.41 = 4.46 rad/s; sim ζ ≈ 0.09 from 0.55-0.57/cycle):
added damping ΔN'r = K_r N'δr; 2ζω target 0.45 -> Δ = 2 (0.45 - 0.09) 4.46 = 3.2 1/s -> **K_r ≈ 0.7 °/(°/s)** at F/C 4.
Check F/C 6 (35 000 ft M 0.9, 311 KCAS, q̄ 328): N'δr -1.91, ω 2.84, ζ0 ≈ 0.01 -> needs K 1.34; scheduled K 0.7 x 2.23 =
1.6 -> ζ ≈ 0.54 ✓ (1/q̄ scheduling fits). Authority: 4° at K 0.7 saturates above r ≈ 5.7°/s; doublet r peaks ≈ 9°/s
(β 2° x 4.46) -> saturates in the first half-cycle, linear afterwards.
**Pitch** (F/C 4: M'q -0.956, M'δs -33.6, SP ζ 0.289, ω 4.54): target ζ 0.6 -> ΔM'q = 2 (0.6 - 0.289) 4.54 = 2.8 1/s ->
**K_q ≈ 0.084 °/(°/s)**. F/C 6: M'q -0.434, M'δs -16.3, ζ 0.185, ω 3.53 -> needs 0.18; scheduled 0.084 x 2.23 = 0.19 ✓.
Authority ± 2° stab around the pilot trim [S] (10°/s pitch rate -> 0.8°). Prerequisite: the SAS-off short period of the
sim measured first (not validated yet - if it is far from CR-2144 that is a flight-model item, not a SAS tuning item).
**Roll** last: sim roll damping is already ≥ CR-2144 (τ 0.2 vs 0.28 s, C4), FM: the yaw augmenter alone damps the Dutch
roll -> roll damper with a small gain (K_p ≈ 0.05) after yaw/pitch, if the aileron trim channel works.

### Predictions
- bu0 rudder trim step 50 % (2°) at F/C 4: steady β ≈ 0.35 x 2 = 0.7° if one trim degree = one rudder degree (T3-E2
  β/δr 0.35); a different β gives the scale factor for K_r.
- yaw damper on (K_r 0.7 scaled): doublet ratio ≤ 0.1/cycle, period 1.5 ± 0.2 s; T3-E2 β/δr unchanged (washout).

### Failure modes / safety
Wrong sign = negative damping (divergent Dutch roll / PIO) -> every channel is first enabled at half gain with a
hard authority limit, at 15 000 ft, AP ALT + wing leveler, switch L:F104_SAS_YAW/PITCH/ROLL (0 = off) so a script can
cut it at once; abort criteria |β| > 5°, |bank| > 45°, |r| > 20°/s -> switch off, unload, PAUSE if not recovering.
On SAS off the module restores the pilot's trim (latched at engage).

## Preconditions
check_build, preflight, refuel.py, runway_start, takeoff (`takeoff_test.py <csv> 157 10.5`), MCP `position` 15 000 ft
TAS ≈ 545 kt (M 0.9 ≈ 460 KIAS = F/C 4), AP ALT + wing leveler verified, yaw damper OFF, calm ISA weather.

## Build-up
- **bu0 channel check (Python, no module change)**: `tools/sas_channel_test.py`: rudder trim 0 -> +50 % -> -50 % -> 0
  (4 s each), log β, yaw rate (body Y), RUDDER TRIM, RUDDER DEFLECTION; same for aileron trim ± 10 % (roll rate,
  body Z). Gives sign, scale, lag. Pitch channel known from H2 (trim write acts at once, AP off only).
- bu1 module v7 yaw damper at half gain, doublet; bu2 full gain, doublet + T3-E2; then pitch (SAS-off pitch doublet first).

## Runs
| Date | Run | Result | Notes |
|---|---|---|---|
| 2026-11-03 | bu0 (`..._H1_bu0.csv`, 16 200 ft M 0.89, AP ALT + WL) | **rudder trim**: settable, 50 % = 2.0° (RUDDER TRIM), acts within one sample; steady β -0.65° / +0.72° for ± 2° -> **β/trim° 0.33** (prediction 0.35 ✓, one trim degree = one rudder degree); RUDDER_DEFLECTION does NOT include the trim. **Aileron trim**: settable, but **10 % -> -171°/s roll, bank -47°** (abort, AP wing leveler recovered); + = roll left (bank negative) | aileron trim range = template default (not in our cfg), far too large for a SAS channel -> scale/limit before any roll damper |
| 2026-11-03 | rstep (fast, ≈ 10 Hz, +50 % rudder trim for 1.2 s) | **+trim -> +ROTATION VELOCITY BODY Y** (+3.8°/s after 0.09 s, peak +7.9°/s at 0.3 s), β negative; free oscillation afterwards ≈ 1.4 s, ratio ≈ 0.54/cycle (= T3-J) | damper sign: trim = trim0 - K HP(r). Yaw rate peaks 8°/s for a 2° step -> K 0.7 saturates the 4° channel for rates > 5.7°/s |
Module v7 (2026-11-03): yaw damper as in the analysis, switched/scaled by L:F104_SAS_YAW (default 0 = off), output
L:F104_SAS_YAW_DEG. Build All (hot reload, v7 confirmed) was done with the jet paused at 16 400 ft -> **the build reloaded
the aircraft in the air (AP off, flaps 15°, trim 0) and the jet dived into the ground** - lost, no data. Rule: Build All
only with the jet on the runway. Next: bu1 = L:F104_SAS_YAW 0.5 + doublet (prediction ratio ≈ 0.2/cycle), bu2 = 1.0 (≤ 0.1).
