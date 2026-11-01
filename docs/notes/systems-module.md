# In-aircraft systems logic (WASM module) - design and status

Purpose: aircraft behaviour that the cfg alone cannot express runs inside the sim instead of in test scripts:
rpm-dependent BLC flap lift (H3), the APC stick shaker/kicker (H2), later drag chute handle/jettison, yaw SAS etc.

## Toolchain (verified 2026-11-01, no Visual Studio needed)
- The MSFS 2024 SDK ships `WASM/llvm/bin/clang-cl.exe` (clang 15, Asobo build) + `wasm-ld.exe` + `wasi-sysroot`.
  `clang-cl --driver-mode=g++ --target=wasm32-unknown-wasi` compiles; the link flags in `tools/build_wasm.sh` give the
  **same export list as the SDK's own StandaloneModule.wasm** (memory, malloc/free, mallinfo, mchunkit_begin/next,
  get_pages_state, mark_decommit_pages, module_init/deinit, __indirect_function_table) - checked with a small wasm
  section parser by rebuilding the SDK sample.
- Inside the sim a module uses the normal SimConnect API (SDK sample `Misc/StandaloneModule`), i.e. the same calls as
  the Python test tools - the validated script logic can be ported 1:1.

## Options considered
| option | pro | con |
|---|---|---|
| **standalone WASM module** (`modules/*.wasm` in our package, AssetGroup type Copy, as the SDK sample) | runs every frame, no cockpit screen needed (the test bed has none of ours), C++, SimConnect API | full sim restart to load; must gate on the aircraft title |
| aircraft WASM gauge (panel.cfg + WasmInstrument, SDK `WasmAircraft`) | aircraft-bound | needs a VCockpit screen in the model (later, own 3D model) |
| JS/HTML instrument (`SimVar.SetSimVarValue`) | quick to write | same screen requirement; JS timing |
| model behaviour XML (RPN) | no code build | writing A: SimVars from RPN is limited; awkward for tables/state |
-> **standalone module now** (test bed), move to an aircraft gauge with the real cockpit (AP-9) if needed.

## Status
1. **BLC (H3)** - prototype `source/wasm/f104_systems/F104Systems.cpp`, builds (`sh tools/build_wasm.sh` ->
   `build/wasm/F104Systems.wasm`). Same law as `tools/blc_driver.py` (validated: F3 -0.6/-0.9 %, F2 -0.4/-0.9 %, B6/B7/
   T3-L unchanged). Reads lever/LE angle/N1 every sim frame, writes TE percent only in LAND after the LE flaps reached
   29°, gated on TITLE containing "F-104G". **VERIFIED 2026-11-01 (ground check + F3 -1.1 % from 165 KIAS, TE follows the N1 spool-down). Packaged 2026-11-01 (PackageSources/modules/F104Systems.wasm + AssetGroup
   F104G_Systems_Module) - active after Build All + full restart; from then on do NOT run blc_driver.py.**
   Integration (needs pete: Build All + full restart): copy the wasm to `PackageSources/modules/F104Systems.wasm`, add to
   `PackageDefinitions/pete-aircraft-f104g.xml`:
   ```xml
   <AssetGroup Name="F104G_Systems_Module">
       <Type>Copy</Type>
       <Flags><FSXCompatibility>false</FSXCompatibility></Flags>
       <AssetDir>PackageSources\modules\</AssetDir>
       <OutputDir>modules\</OutputDir>
   </AssetGroup>
   ```
   Verification: fastlog of TRAILING EDGE FLAPS LEFT ANGLE + N1 on an approach / idle cut **without** blc_driver.py
   (never both at once), then F3 from 165 KIAS (expect ≈ -0.6 %), B6 unchanged.
2. **APC (H2 rework)** - design, not coded. The native SPS is disabled because after a full restart it makes the MSFS
   AP diverge (trim to the stop + roll, A/B 2026-10-31). Own logic in the module instead, closer to the FM:
   - shaker: α > 11.3° (FM CL 0.58, B7 calibration) -> stall warning only (there is no stick-vibration output for a
     keyboard/mouse user; a controller rumble / sound later).
   - kicker: α_pred = α + T·q > 14.5° (FM 6-6: pitch-rate input washed out to 1/3 in 0.5 s -> T from the washout,
     start T ≈ 0.3 s), **inhibited with gear down or flap lever LAND** (FM 6-6, missing in the SPS), push the stick to
     slightly ahead of neutral and HOLD it while beyond the boundary (FM: "as long as ... beyond the safe range"), i.e. an
     elevator override for ≥ 0.5-1 s instead of the SPS leaky limiter; **disengages the AP** (FM 1-69).
   - how to command the stick from a module: AXIS_ELEVATOR_SET (transmit event) overrides the pilot axis for that
     frame - must be re-sent every frame while kicking; to be tested at altitude like H2 (build-up first).
   - the Mach dependence of Fig. 6-3 (kicker α ≈ 11° at M 0.8) can be a table α_kick(M) in the module.
3. Later candidates: drag chute as its own handle (deploy limit 180 KIAS MB-7G, jettison) instead of the speed-brake
   emulation; yaw damper / SAS logic.

## Rules
- Never run the Python driver and the module at the same time (both write the TE percent).
- Every module change: build, Build All + FULL restart (modules load at sim start), regression of the area (H3/H2 card).
