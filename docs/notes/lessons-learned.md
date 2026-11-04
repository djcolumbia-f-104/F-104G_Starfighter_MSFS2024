# Lessons-learned register (test process step 8, docs/notes/test-process.md)

Rule: a lesson only counts as learned when it is **enforced** - by a script assert, a selftest/probe item, a postcondition,
the watchdog or a mandatory skill step. "Doc only" entries are open until an enforcement exists.
Older lessons (2026-10-25 .. 11-01) live in the skill `f104-testcard` ("Known sim pitfalls"); new ones go here first.

| # | Date | Event | Root cause | Fix | Enforced in | Status |
|---|---|---|---|---|---|---|
| 1 | 2026-11-03 | Build All with the jet paused at 16 400 ft -> reload in the air (AP off, flaps 15, trim 0) -> dived into the ground | Build All reloads the aircraft; nobody checked the sim after the build | Build All only with the jet on the runway; after every build: selftest + runway_start | skill pitfalls + CLAUDE.md (doc); selftest checks the module version after the build | **partly** (no automatic block of a Build All in the air - pete clicks; watchdog only refuels by decision 2026-11-04) |
| 2 | 2026-11-03 | module v7 blind (no SAS output, BLC/APC inactive) | invalid unit name "pounds per square foot" -> the whole state data definition failed silently | unit "psf"; probe every pair | `tools/probe_units.py`, called by `build_wasm.sh` (FAIL stops the build) and `selftest.py` | **enforced** (negative test with the old unit -> FAIL, exit 1) |
| 3 | 2026-11-03 | msfs_save_flight blocked the sim ≈ 23 min, fuel 3 509 -> 1 280 lb | target folder did not exist (most likely) + tool waits without a useful bound; MSFS 2024 cannot save/resume in the air anyway | never call it with the jet in the air | `tools/watchdog.py` (refuels < 1 500 lb in the air); skill pitfalls | **partly** (the call itself is not blocked) |
| 4 | 2026-11-03 | long desk analysis while the jet flew -> fuel burn, pete unsure whether Claude hangs | no rule | PAUSE_ON before desk work; sim_state between long steps | memory feedback + skill step 5 | doc (Claude discipline) |
| 5 | 2026-11-03 | sideslip_test aborted twice (bank 53°/57°) | probe and bank loop tuned before C4 (roll power ≈ 3x) | rework open; gains /3 not enough (0.6 s loop) | skill step 2 (THA after a cfg change: list scripts tuned to the old behaviour) | **open** (script rework) |
| 6 | 2026-11-03 | ROTATION_VELOCITY_BODY_X read ≈ 3.5x the true pitch rate -> false 18.6°/s abort | channel not cross-checked | use θ / α; body X banned | pitch_step_test.py reads α only; skill step 1 (cross-check every new channel against an independent one) | **enforced** in the tool, doc for new tools |
| 7 | 2026-11-03 | T3-G trim gradient accepted against a source range for other CGs -> 2x static stability unnoticed for days | acceptance band not reduced to the test CG | acceptance values always shifted to the test condition (CG, Mach, weight) | skill step 1 (prediction at the test condition) + T3-SP card | doc |
| 8 | 2026-11-04 | (prevention) scripts left the jet in unknown states | no defined end state | postcondition check at the end of every flight script | `tools/post.py` in takeoff/pitch_step/roll/doublet/sas_step tests (prints POST OK/FAIL) | **enforced** (landing_test, config_test, sideslip_test still to add) |
