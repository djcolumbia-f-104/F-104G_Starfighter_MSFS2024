# R-SU72: regression after MSFS Sim Update 7.2 (1.9.24.0)

**Objective / acceptance:** SU 7.2 release notes: "Reverted a change to drag simulation calculations to the pre-SU7
version to ensure backwards compatibility with certain third-party add-on aircraft." Our flight model was tuned
2026-10-25..11-05 on the previous sim build. The cfg/module state is unchanged (module 7.2, build current), so this is a
pure A/B on the sim version. Pass = every point within its tolerance AND within the scatter of the last runs. A shift
larger than the scatter (especially in drag) means the sim changed -> stop, analyse, no cfg change before a desk analysis.

| Point | Tool (sortie S8-SU72) | Reference (last runs, same cfg) | Tolerance / scatter |
|---|---|---|---|
| T3-D takeoff | takeoff_test srot | 180-182 kt (2026-11-05) | FM 178 ± 5 %; scatter ± 2 kt |
| T3-F drag, decel 16 500 ft | decel_test + analyse_drag | 0.97 / 1.05-1.06 / 1.08-1.09 / 1.02-1.03 (M 0.4-0.6 / 0.6-0.8 / 0.8-0.95 / 0.95-1.2), mean 1.03-1.04 | ± 10 % vs NASA; shift > 0.03 in a band = sim change |
| T3-A lift (same run) | analyse_lift | largest band -0.028..-0.031 | ± 0.03 |
| T3-G trim gradient (same run) | analyse_lift | tail = -0.01..-0.02° + 1.08 α | slope ± 0.03 |
| D5 C cruise M 0.85 / 29 500 ft | cruise_test | N1 ≈ 89.7 %, FF/FM 1.02 (TSFC 0.69) | N1 ± 0.7 %, FF ± 0.03 |
| T3-J doublet (SAS off) | doublet_test | 1.41 s / 0.48 per cycle (1.44 / 0.52) | ± 0.05 s / ± 0.05 |
| SP step | pitch_step_test 0.2 4 | ωn 6.82, ζ 0.17, α/δ 1.01 at ≈ 430 KIAS | ωn ± 0.3 |
| F3 landing (no chute, fmflare) | landing_test + roll_from_speed | roll from 165 KIAS -4.1 % / +0.9 %; TD 173-174 KIAS | FM ± 5 % |

**Analysis (prediction):** the release note gives no detail on WHICH drag term was reverted. Our drag tuning was done
against measured sim behaviour, so if the reverted code path is one the F-104 uses, the decel-run CD/NASA ratios and the
cruise N1 move together (≈ 1 % N1 per ≈ 4-5 % drag at cruise from the EPP fit). Prediction: unchanged (most
third-party aircraft that complained use legacy/FSX-style coefficients; we use the modern tables). If T3-F changes but
T3-A does not, the change is in drag only.

**Hazards:**
- decel_test ends at ≈ 215 KIAS with AP trim near 10.5° -> it sets Military; the sortie repositions at once (pos16,
  throttle 8 800); the jet is level and not rotating (position rule) -> recovery: position routine / PAUSE.
- A real drag change shifts the trim/speed of every scripted law (takeoff srot, landing flare): takeoff first with the
  normal srot abort criteria; if T3-D or T3-F is out of tolerance, the sortie is stopped before the landing (manual
  decision after the decel step, landing only if drag is unchanged).
- Scripts unchanged; all end via `position` / POST.

**Preconditions:** selftest ALL OK (done 2026-11-06: module 7.2, 24 SimVar/unit pairs, ISA calm, build current),
watchdog running, runway_start + refuel (sortie steps), flight EDDM 26L.

**Go/no-go:** GO 2026-11-06 - selftest ALL OK, unchanged scripts and cfg, all points flown before in the same form.

## Result + Debrief (2026-11-06) - PASSED, no effect of SU 7.2 on this flight model
| Point | Measured (S8-SU72a/b/c) | Reference | Verdict |
|---|---|---|---|
| T3-D | 178 / 179 kt (two takeoffs) | 180-182 | ✓ |
| T3-F (decel 16 500 ft, ended at 256 KIAS on the 400 ft altitude criterion) | 0.99 / 1.05 / 1.08 / 1.05, mean 1.05 | 0.97 / 1.05-1.06 / 1.08-1.09 / 1.02-1.03 | ✓ within scatter (M 0.95-1.2 n = 8) |
| T3-A | largest band -0.030 (tool prints FAILED at the edge), mean -0.016 | -0.028 .. -0.031 | ✓ unchanged scatter |
| T3-G | -0.02° + 1.08 α | -0.01..-0.02 + 1.08 α | ✓ identical |
| D5 C | N1 89.6 %, FF/FM 1.03 | 89.7 %, 1.02 | ✓ |
| T3-J | 1.34 s / 0.51 at ≈ 460-480 KIAS | 1.41 s / 0.48 at ≈ 430 KIAS | ✓ (period x √(q ratio) ≈ 1.32 expected) |
| SP step at the reference condition (S8-SU72c, 430 KIAS M 0.860) | ωn 6.72 / 6.85, ζ 0.17, α/δ 1.00 / 1.01 | 6.82, 0.17, 1.01 | ✓ identical |
| F3 | TD 172 KIAS, -230 ft/min, 1 skip, roll from 165 KIAS -3.7 % | -4.1 / +0.9 % | ✓ |
Debrief:
1. Prediction "unchanged" confirmed for drag, lift, trim, thrust/fuel, lateral, short period, ground roll.
2. Anomaly: SP step in part b at M 0.882 gave α/δ 0.75. Diagnosis S8-SU72c: the trim step is delivered exactly (simlog
   3.08 -> 3.28°, elevator 0); M 0.860 -> 1.00, M 0.884 -> 0.77, M 0.931 -> 0.76 (ωn always ∝ √q̄). The SAME raw
   evaluation of the pre-update logs gives 0.74 at point A 2026-11-03 (M 0.94; card said "(1.0)" from the old fit) but
   1.01 on 2026-11-04 (S1a, ≈ M 0.93, ωn 7.34) -> **α/δ is bimodal (≈ 1.0 / ≈ 0.75) at the same condition already before
   SU 7.2** -> not an update effect; new open item in T3-SP (cause unknown; ωn and ζ are the same in both modes, so
   Mα/Mq agree and the tail effectiveness per trim degree (Mδ) differs by ≈ 25 %).
3. Surprise: the decel run ended at 256 KIAS (altitude fell 400 ft below the idle reference), earlier runs reached
   ≈ 229 KIAS -> M 0.4-0.6 band has n = 12 only; sufficient for the A/B.
Logs `flighttest_2026-11-06_S8-SU72a_*`, `_S8-SU72b_*`, `_S8-SU72c_*`.
