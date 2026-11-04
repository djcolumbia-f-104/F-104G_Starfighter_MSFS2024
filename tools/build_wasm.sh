#!/bin/sh
# Builds the F-104G systems WASM module with the toolchain shipped in the MSFS 2024 SDK (no Visual Studio needed).
# Flags matched to the SDK StandaloneModule sample (2026-11-01: rebuilt sample has the identical export list:
# memory, malloc/free, mallinfo, mchunkit_*, get_pages_state, mark_decommit_pages, module_init/deinit, table).
# Usage (Git Bash): sh tools/build_wasm.sh  -> build/wasm/F104Systems.wasm (not copied into the package yet)
set -e
SDK="/c/MSFS 2024 SDK"
W="$SDK/WASM"
SRC="$(dirname "$0")/../source/wasm/f104_systems/F104Systems.cpp"
OUT="$(dirname "$0")/../build/wasm"
mkdir -p "$OUT"
# 2026-11-04 (lesson 2026-11-03, invalid unit "pounds per square foot" killed the module's state request): probe every
# SimVar/unit pair of the source in the running sim first; a FAIL stops the build, no sim = warning only.
PY="/c/Users/pete/AppData/Local/simconnect-mcp/.venv/Scripts/python.exe"
set +e
"$PY" -I "$(dirname "$0")/probe_units.py" "$SRC" > "$OUT/probe_units.txt"
RC=$?
set -e
tail -1 "$OUT/probe_units.txt"
if [ $RC -eq 1 ]; then grep FAIL "$OUT/probe_units.txt"; echo "BUILD STOPPED: invalid SimVar/unit pair"; exit 1; fi
if [ $RC -eq 2 ]; then echo "WARNING: sim not reachable - SimVar units NOT probed (run tools/probe_units.py before Build All)"; fi
"$W/llvm/bin/clang-cl.exe" --driver-mode=g++ --target=wasm32-unknown-wasi --sysroot="$W/wasi-sysroot" \
  -I"$W/include" -I"$SDK/SimConnect SDK/include" \
  -D_MSFS_WASM=1 -D__wasi__ -D_LIBCPP_HAS_NO_THREADS -D_LIBCPP_NO_EXCEPTIONS \
  -D_STRING_H_CPLUSPLUS_98_CONFORMANCE_ -D_WCHAR_H_CPLUSPLUS_98_CONFORMANCE_ \
  -fms-extensions -fno-exceptions -fvisibility=hidden -ffunction-sections -fdata-sections -fno-stack-protector -O2 \
  -c "$SRC" -o "$OUT/F104Systems.o"
"$W/llvm/bin/wasm-ld.exe" --no-entry --allow-undefined --export-dynamic \
  --export=malloc --export=free --export=mallinfo --export=mchunkit_begin --export=mchunkit_next \
  --export=get_pages_state --export=mark_decommit_pages --export=__wasm_call_ctors --export-table \
  --gc-sections -O3 --strip-debug -L"$W/wasi-sysroot/lib/wasm32-wasi" -lc -lc++ -lc++abi \
  "$OUT/F104Systems.o" -o "$OUT/F104Systems.wasm"
echo "built $OUT/F104Systems.wasm"
