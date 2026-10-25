# MSFS 2024 SDK: notes

## Links
- SDK documentation: https://docs.flightsimulator.com/msfs2024/html/ (newer: .../msfs2024/retail/...;
  appending `index.md` to a page URL returns the Markdown source, which is easier to read programmatically)
- Official forum, SDK / developer support: https://devsupport.flightsimulator.com/
- MSFS forum, developer thread on the SSW F-104 (experience with 2024):
  https://forums.flightsimulator.com/t/development-of-sim-skunk-works-lockheed-tf-frf-104-g/372909

## Workflow
1. Enable Developer Mode in the sim (Options → General → Developers).
2. Open the project `F104G.xml` in the Project Editor and run "Build" → output to `Packages/`.
3. To test outside Dev Mode, copy or link the built folder `Packages/pete-aircraft-f104g` into the Community folder.
4. After flight model changes restart the sim completely (normalization only at sim start).

## Structure
- MSFS 2024 has, besides the classic SimObject layout (from 2020, still loaded), a modular layout with
  presets/liveries. The project uses a ModularSimObject package with a preset (MODULAR_MERGE).

## Pitfalls
- Without a valid `.gltf` model the aircraft does not appear in the selection.
- 2020 aircraft in 2024: known problems with switches/systems (see SSW thread). Test own instruments against 2024.
- Dev Mode "Aircraft Selector" (Load) and package reload do NOT re-run the flight model normalization.

## Open questions
- (collect here)
