# docs/data: reference data and flight-test raw data

Purpose: validation evidence and re-analysis without re-flying. Every result in `docs/notes/measurements.md` points to a
log here; this index says under which conditions each log was flown and whether it still counts.

## Reference data (NASA, cleaned)
| File | Content | Source |
|---|---|---|
| `nasa_d7137_cl_alpha_mach.csv` | CL(α, M), trimmed | NASA TN D-7137 |
| `nasa_d7137_cd_mach_cl.csv` | CD(M, CL) | TN D-7137 Table 2 |
| `nasa_d7137_thrust_maxab_lbf.csv` | net thrust max AB (M, altitude) | TN D-7137 Table 3 |
| `nasa_d7137_fuelflow_maxab_lbs.csv` | fuel flow max AB | TN D-7137 Table 4 |
| `nasa_d6398_excess_thrust_lbf.csv` | excess thrust 10 000-40 000 ft, read from Fig. 6(a)-(d), ±300 lbf | NASA TN D-6398 |
| `nasa_cr2144_f104a.md` | inertia, derivatives, flight conditions | NASA CR-2144 |

## Flight-test logs `flighttest_<date>_<test>.csv`
- `<name>.csv` from the test script itself (its own channels); `<name>_simlog.csv` from `tools/simlog.py` running in
  parallel (α, pitch, elevator, trim, N1, thrust, fuel flow, flaps, AP ...). Older runs have only one file.
- Re-analysis: `tools/analyse_lift.py`, `analyse_drag.py`, `analyse_climb.py` (see `docs/notes/test-procedures.md`).

### Validity
- **Weather**: every log **before landing 10 on 2026-10-28** was flown in **live weather** (wind, non-ISA, turbulence;
  pete, measurements.md 2026-10-28 NOTE). Still usable: T3-A lift, T3-G trim, liftoff and touchdown IAS. Not usable as
  evidence: drag, excess thrust, climb rates, ground rolls, thrust/fuel-flow comparisons. From dry run 16 on:
  clear skies, wind ≈ 1 kt, 1013.25 hPa (≈ ISA, a few °C warm).
- **cfg state**: a log is evidence only for the cfg state it was flown with (commit = the one that documents the run
  in measurements.md). After a cfg change the affected logs become *superseded*, not wrong.
- Status: **valid** = current evidence; **superseded** = correct then, cfg/weather changed since; **invalid** = flawed
  run (wrong state, script error), do not analyse; **dev** = script development, no result.

### 2026-10-24 / 2026-10-25 (live weather; rounds A-F, T3-D, T3-H)
| Log | Test | Conditions / cfg | Result | Status |
|---|---|---|---|---|
| `2026-10-24_test` | simlog test | | | dev |
| `2026-10-24_deceleration` | T3-A first lift run | old normalization | CL +0.08 high | invalid (normalization) |
| `2026-10-25_baseline` | T3-A/F | old normalization | CL +0.13, CD x1.9 ✗ | invalid (normalization) |
| `2026-10-25_ap1` | T3-A after AP-1 | flight restart only | ✗ | invalid (no sim restart) |
| `2026-10-25_ap1b_restart` | T3-A/F after AP-1/1b | full restart | lift ✓ -0.001, drag 1.00 | superseded (live weather; ISA: `2026-10-29_T3AF_decel_isa`) |
| `2026-10-25_roundA_static` | T3-C static | round A | military 6 628 lbf, 8 400 lb/h ✓ | superseded (EGT fixed in B2) |
| `2026-10-25_roundA_flight` | AB in flight, T3-A/G | round A | AB thrust -2..-4 % ✓ | superseded (live weather) |
| `2026-10-25_roundA_cruise` | cruise M 0.87 | round A | AP oscillation | dev |
| `2026-10-25_roundA_rudder` | T3-E | round A | β/δr 1.0 ✗ | superseded (rudder fixed) |
| `2026-10-25_roundB_static` / `_flight` | static, htail -4.3 | round B | crash, sign wrong | invalid |
| `2026-10-25_roundB2_flight` / `_rudder` | htail +4.3, rudder 1.6 | round B2 | T3-A ✗, departure | superseded |
| `2026-10-25_roundC_flight` / `_rudder` | T3-A/F, T3-E | round C | T3-A ✓, T3-F 1.04, T3-E ✗ | superseded |
| `2026-10-25_roundD_rudder` | T3-E | rudder_maxangle_scalar 0.32 | β/δr 0.34 ✓ | superseded (AP-11) |
| `2026-10-25_roundD_sideslip` | T3-E2 first | | δa -2.4° | dev |
| `2026-10-25_roundE_sideslip` | T3-E2 | | β/δr 0.32, δa/δr 0.39 ✓ | superseded (AP-11, ISA re-run) |
| `2026-10-25_T3D_takeoff_run3`/`4`/`5` | T3-D | flaps never extended | 194-242 kt ✗ | invalid (flaps) |
| `2026-10-25_T3D_takeoff_run6` | T3-D | electric flaps, no LE flaps, ~20 kt headwind | 185 kt (+3.4 %) | superseded (`2026-10-29_T3D_takeoff_reg_flap042`) |
| `2026-10-25_T3H_accel10k` / `_accel20k` | T3-H | round C/F state | subsonic ✓, supersonic -20/+30 % | superseded (live weather; ISA 10k: `2026-10-29_T3H_accel10k_isa`; 20k not re-flown) |
| `2026-10-25_roundF_speedbrake` | S11e speed brakes | round F | ΔCD 0.046 ✓ | valid (speed-brake ΔCD; drag ratio method, steady wind no effect) - re-check in ISA optional |
| `2026-10-25_roundF_doublet_ydoff` / `_ydon` | T3-J | fin 38 ft² | 0.87 s ✗ | superseded (AP-11) |

### 2026-10-26 (live weather; AP-11, T3-I, S12, T3-L approach)
| Log | Test | Conditions / cfg | Result | Status |
|---|---|---|---|---|
| `AP11_it1_reload`, `AP11_it1_sideslip` | AP-11 iteration 1 | rudder_lift_coef 1.7 | 1.6 s, β/δr 0.26 | superseded |
| `AP11_it2_doublet`, `AP11_it2_sideslip` | AP-11 iteration 2 | 2.0 / 0.32, fin 50 | 1.48 s, 0.35 / 0.41 ✓ | superseded (ISA: `2026-10-29_T3J_doublet_isa`, `_T3E2_sideslip_isa`) |
| `T3J_yd03`, `T3J_yd10`, `T3J_yd10b` | yaw damper 0.3 / 1.0 | | no effect / departure | valid (decision yaw damper off) |
| `T3I_accel40k` | T3-I 40 000 ft | -57 °C = ISA at altitude | thrust 0.98-1.01, drag 0.94-1.07 ✓ | valid with caveat (live weather, but ISA temperature; re-fly when T3-H is investigated) |
| `S12_trim16k` | S12 supersonic trim | ISA+8 | trim 1.2° at M 1.27 ✓ | valid (trim) |
| `mcp_test_doublet` | MCP server test | | | dev |
| `T3L_approach` ... `T3L_approach5`, `T3L_debug` | T3-L runs 1-5 | flap section stalled | ✗ | invalid (flap model wrong; runs 2-4 also no restart) |
| `T3L_approach6` | T3-L run 6 | TE + LE flaps, LAND drag 1.273 | CL 0.855 @ 4.1° ✓ | valid for lift; drag superseded (LAND drag 0.85) |
| `T3D_takeoff_run7` | T3-D re-check | after LE flaps | 187 kt | superseded (live weather; `2026-10-29_T3D_takeoff_reg_flap042`) |
| `T3L_landing1` | first landing | | belly landing | invalid |

### 2026-10-27 (live weather; landing script development)
| Log | Test | Result | Status |
|---|---|---|---|
| `T3L_landing3`, `T3L_landing4`, `T3L_landing6_simlog` | landings 3, 4, 6 | belly landing / go-around / crash | invalid (script; root causes in `docs/notes/test-cards/T3-L-landing.md`) |
| `T3L_dry1` ... `T3L_dry12` (+ `_simlog`) | dry runs 1-12 | dry 12 PASS | dev (card T3-L) |

### 2026-10-28 (live weather until landing 9, then clear skies / calm)
| Log | Test | Conditions / cfg | Result | Status |
|---|---|---|---|---|
| `T3L_dry13` ... `T3L_dry15` | dry runs | live | dry 15 PASS | dev |
| `T3L_landing7` | F2 (chute) | live, ~8 kt headwind | +7 % | invalid as evidence (headwind) |
| `T3L_landing8_nochute` | F3 | live | +4 % | invalid as evidence (headwind) |
| `B6_climb10k`, `B6_climb4500`, `B5_level4500_sb` | B6/B5 | LAND drag 1.273, live | ✗ drag too high | superseded (reason for LAND drag 0.85) |
| `B6_climb4500_r2`, `B5_level4500_sb_r2` | B6/B5 regression | LAND drag 0.85, live, 1 028 hPa | ✓ | superseded (ISA re-run 2026-10-29) |
| `T3L_landing9` | F2 | live, gusts | go-around | invalid |
| `T3L_dry16`, `T3L_dry17` | dry runs | calm/ISA, flap damaging-speed fix | PASS | dev (script regression) |
| `T3L_landing10` / `T3L_landing11_nochute` | F2/F3 | calm, brakes 0.68 | +24 % / +20 % ✗ | superseded (brakes 0.82) |
| `T3L_landing12_nochute` | **F3** | calm, brakes 0.82 | **+9.4 % ✓** | **valid** |
| `T3L_landing13` | F2 | calm, chute 0.21, tip fuel left | +20 % ✗ | superseded (`landing14`) |

### 2026-10-29 (clear skies, wind 1 kt, 1013.25 hPa)
| Log | Test | Conditions / cfg | Result | Status |
|---|---|---|---|---|
| `T3L_landing14` | **F2** (chute) | chute 0.43 | +17.6 % ✗ | **valid** (known deviation, H5) |
| `B6_climb4500_isa` | **B6** | LAND drag 0.85 | +905 ft/min ✓ | **valid** |
| `B5_level4500_sb_isa` | **B5** | | 182.8 KIAS ✓ | **valid** |
| `T3AF_decel_isa` | **T3-A/F/G** | | lift ✓, drag 1.04 (M 0.6-0.95 1.06-1.09), 1.08 α ✓ | **valid** |
| `T3H_accel10k_isa` | **T3-H 10 000 ft** | | subsonic -13..-24 % ✗ | **valid** (open investigation) |
| `T3J_doublet_isa` | **T3-J** | | 1.60 s ✓ | **valid** |
| `T3E2_sideslip_isa` | **T3-E2** | | 0.34 / 0.43 ✓ | **valid** |
| `B4_glide_to` | B4 TAKEOFF | | aborted (pitch -21°) | dev |
| `B4_glide_to2` | B4 TAKEOFF | TAKEOFF drag 1.0 | 8.5 NM ✗ | superseded (TAKEOFF drag 0.42) |
| `B4_glide_clean` | **B4 clean** | | 10.6 NM ✓ | **valid** |
| `B4_glide_to_reg` | **B4 TAKEOFF** | TAKEOFF drag 0.42 | 9.8 NM (-11 %) ◐ | **valid** |
| `D5_cruise_A` / `_B` / `_C` | **D5 cruise FF** | 11 900 / 19 600 / 29 500 ft, M 0.70 / 0.80 / 0.85 | sim/FM 1.79 / 1.86 / 1.84 ✗ | superseded (TSFC 0.72) - reason for the change |
| `T3D_takeoff_reg_flap042` | **T3-D** | TAKEOFF drag 0.42, LE flaps | 170 kt (-4.2 %) ✓, roll 2 627 ft | **valid** (D1b data point) |
| `D5_endur_5k` / `D5_endur_10k` | D5 endurance (FM A5-1) | TSFC 1.26 | 1.66 / 1.70 ✗ | superseded (TSFC 0.72) |
| `T3D_takeoff_tsfc072` | **T3-D** | TSFC 0.72, 19 340 lb | first 171 / sustained 185 kt ✓ | **valid** |
| `AB_accel10k_tsfc072` | **AB FF regression** | TSFC 0.72, full AB 10 000 ft | FF unchanged (M 1.0-1.2: 0.996-1.007) | **valid** |
| `D5_cruise_B_reg` / `D5_cruise_C_reg` / `D5_endur_5k_reg` | **D5 regression** | TSFC 0.72 | 1.07 / 1.04 / 0.96 ✓ | **valid** |

### 2026-10-30 (clear skies, wind 1 kt, 1013.25 hPa)
| Log | Test | Conditions / cfg | Result | Status |
|---|---|---|---|---|
| `T3D_takeoff_day4` | T3-D | 19 009 lb | first 171 / sustained 185 kt ✓ | **valid** |
| `T3L_landing15_nochute` (+ `_simlog`) | **F3** + approach N1/FF | TSFC 0.72 | +9.1 % ✓; N1 89.5 %, FF 4 311 lb/h | **valid** |
| `B7_clean_bu1` / `bu2` / `bu3` | **B7 clean** | 10 000 / 15 000 ft | α-IAS ✓ / bu2 invalid (script elevator clamp) / min. level 188-190 KIAS | bu1, bu3 **valid**; bu2 invalid |
| `T3D_takeoff_day4b` | T3-D | before the LE stage change; climb-out fault (gear up 330 KIAS) | liftoff 170 / 184 kt | valid for liftoff only |
| `T3D_takeoff_climbout1` | **T3-D + hand-flown climb-out** | LE TAKEOFF 10°, FULL restart | 169 / 188 kt, gear up 222 KIAS ✓ | **valid** |
| `B7_to_bu1` / `bu2` | **B7 TAKEOFF** | 10 000 / 15 000 ft | α-IAS ✓ / min. level 165-168 KIAS | **valid** |
| `B7_land_bu1` / `bu2` | **B7 LAND** | 10 000 / 12 000 ft | α-IAS ✓ / min. level 141-144 KIAS | **valid** |
| `T3H_accel20k_isa` | **T3-H / T3-F 20 000 ft ISA** | M 0.63 -> 1.30 | Fn,ex 0.97-1.08 (M ≥ 0.70), drag 1.05 | **valid** |
| `D1b_takeoff_fm1` | **D1b ground run** (FM technique) | 19 008 lb, wind 1 kt | 2 690 ft to 171 kt / 3 253 ft to 188 kt -> ≈ 2 900 ft at 177.6 kt vs. FM 2 630 (+10 %) | **valid** |
| `D1b_takeoff_fm2` + `D1b_takeoff_thrust` (simlog) | D1b repeat with thrust log | same | 2 678 ft / 3 224 ft; roll thrust 0.97-0.98 x D-7137 | **valid** |

## Keeping this index
Add a row for every new log in the same commit as its measurements.md entry. When a cfg change supersedes a test,
mark the old row superseded and name the replacement log.
