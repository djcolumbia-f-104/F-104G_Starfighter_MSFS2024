# Engine start in MSFS 2024: start chain and troubleshooting

State 2026-10-24. Sources: SDK reference (`docs/sdk-ref/engines.cfg.md`, `engines-additional-information.md`),
engine debug in Dev Mode (Debug → Aircraft → Engines), reference configurations FlyByWire A32NX and Milviz F-4J
(read only).

## Start chain (turbine, N2 based)
| # | Stage | Input(s) | F-104 value |
|---|---|---|---|
| 1 | Cranking | starter (`starter_type`), target `n2_raw_starter` (electric) or `n2_from_bleed_air_psi_table` (air) | electric, 25 % |
| 2 | Ignition | ignition switch, `ignition_auto_type` (empty = always on) | default |
| 3 | Fuel available | tank selector, pump, pressure > `min_fuel_press_for_combustion` | ALL, pump |
| 4 | Release | mixture/cutoff open, condition lever ≥ `min_condition_lever_for_combustion` (0.01) | check |
| 5 | Enough rpm | N2 ≥ `min_n2_for_fuel_flow` / `min_n2_for_combustion` | 12 / 15 % |
| 6 | Fuel demand | commanded Ne → PID → fuel flow demand | debug: ComN1, FF PID, Demand |
| 7 | Spool-up | flow ↔ N2 up to `low_idle_n2` | 67 % |

## Debug fields (engine debug)
`ComN1/TComN1` = commanded N1, `FF PID` = controller output, `Fuel Flow Demand` = actually requested flow,
`Fuel Avail` = fuel available, `MinN1/MinN2` = thresholds from the cfg.

## Findings
1. **.flt files of the piston template** set `Pct Engine RPM = 46 %` (runway/taxi) or 150 % (airborne states),
   magnetos and propeller data on load -> impossible initial state: N1 46.199 % at RPM 0, combustion = 1, IAS 231 kt
   at standstill, identical on every load. **All start tests before this fix were corrupted by it.** Fixed with
   `tools/clean_flt.py` (removes [Engine Parameters.*]/[Propeller.*]).
2. `starter_time`, `auto_ignition` only apply to [PISTON_ENGINE].
3. `uncorrected_commanded_Ne_table` is an nD table (`x1, x2 :: y1, y2`); temporarily disabled.
4. The F-4J `engines.cfg` has a format error (corrected_airflow_table on a separate line) that MSFS 2024 does not
   accept -> its airflow table was never loaded; not usable as evidence for the unit.
5. **SOLUTION (2026-10-24):** the temperature/pressure model was missing (`egt_peak_temperature`,
   `itt_peak_temperature`, `*_tc`, `*_tuning_constant`, `epr_*`, `oil_*`, `fuel_press_*`). Without them EGT/ITT stayed
   at ambient, fuel flowed, but MSFS never reported combustion. Found by cross-checking with the (complete) F-4J cfg
   from a clean initial state; entered with our own J79 values. Note: the SDK docs list some of these parameters only
   under [PISTON_ENGINE] - they are needed in [TURBINEENGINEDATA] as well.
6. When spawning on the runway MSFS starts the engine automatically -> quick start test: restart the flight.
7. First idle run (sea level ~1460 ft, 3 °C): 67.0 % / 4 997 rpm, EGT 241 °C, ITT 463 °C, oil 46 psi, 1 206 lb/h
   -> matches Stoelinga (67 %, EGT 120-420 °C). Thrust 1 482 lbf instead of ~355 lbf installed -> idle point added
   in `tools/engine_calc.py`.
8. **2026-10-25, FALSE ALARM "engine off":** querying via MCP with the index in the name (`TURB_ENG_N1:1`) always
   returns 0 with `msfs_get_simvar`. Correct: name without index + parameter `index=1`. The engine was running (engine
   debug: 5000/7460, N1 67 %, selector ALL). Caution: `TOGGLE_*` events were tried meanwhile -> toggle events change
   the state blindly; read the correctly indexed state first.

## Open
- Create flight states with a running jet (runway/airborne); air start with a hidden APU
  (`[PNEUMATIC_SYSTEM] apu_max_pressure`, `n2_from_bleed_air_psi_table`). Note: starting from the world map ignores
  the .flt files anyway (see measurements.md, round B).
- Re-enable and test `uncorrected_commanded_Ne_table`.
