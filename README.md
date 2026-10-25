# F-104G Starfighter for Microsoft Flight Simulator 2024

A from-scratch aircraft add-on: Lockheed F-104G Starfighter with the J79-GE-11A engine.
Current state: flight model development on a **test bed** (a stand-in model from the MSFS SDK sample
*SimpleAircraft*, carrying the F-104G flight model and engine). A dedicated 3D model will follow.

## Approach
- Every number is backed by evidence: `[Q]` source, `[M]` measured, `[S]` estimate (in the cfg comments).
- Main sources: NASA TN D-7137 and TN D-6398 (F-104G flight test data), NASA CR-2144 and CR-96008
  (stability derivatives), flight manual T.O. 1F-104G-1.
- Flight tests in the sim via SimConnect, evaluated against the NASA data (lift, drag, thrust, fuel flow).
  Results: `docs/notes/measurements.md`; plan and acceptance criteria: `docs/flight-model-plan.md`.

## Layout
- `source/cfg/*.f104.cfg`: F-104 values (source files). `tools/build_cfg.ps1` merges them over the SDK template
  and generates `PackageSources/.../common/config/*.cfg`.
- `tools/`: checking and analysis tools (Python), see `CLAUDE.md`.
- `docs/`: data, derivations, notes, test procedures. Code and cfg comments are in German.

## Not in the repository
- Test bed assets (model, textures, sounds, thumbnails) from the SDK sample *SimpleAircraft*: copy them from your
  own MSFS 2024 SDK (`Samples\DevmodeProjects\SimObjects\Aircraft\SimpleAircraft`) into the matching folders under
  `PackageSources/SimObjects/Airplanes/pete-f104g/`.
- Source PDFs (`docs/sources/*.pdf`) and copies of the SDK documentation.

## Building
MSFS 2024 Developer Mode -> Project Editor -> `F104G.xml` -> Build All. After changing the flight model, restart
the sim completely (normalization only runs at sim start).
