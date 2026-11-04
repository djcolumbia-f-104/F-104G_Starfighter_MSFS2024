# Watchdog concept: no lost jets, no lost time (draft 2026-11-03)

**DECIDED 2026-11-04 (pete):** the watchdog only refuels (dive/bank events are logged as ALERT, no pause, no popup).
Process decisions: `docs/notes/test-process.md`.

## What went wrong on 2026-11-03
| # | Event | Cost | Root cause |
|---|---|---|---|
| 1 | Build All with the jet paused at 16 400 ft | jet lost, reload + new takeoff (≈ 10 min) | Build All reloads the aircraft (AP off, flaps 15, trim 0); nobody watched the sim after the build |
| 2 | Module v7 with an invalid unit ("pounds per square foot") | one test flight without data, one more Build All | unit not probed before the build |
| 3 | `msfs_save_flight` with the jet in the air | ≈ 20 min blocked, fuel 3 509 -> 1 280 lb, pete had to interrupt | MSFS stops answering SimConnect while saving; the MCP tool waited without a useful bound |
| 4 | Long desk analysis (Fig. 6-9, SDK, Cmα back-calculation) while the jet flew on the AP | fuel burn, pete unsure whether Claude works or hangs | no rule "pause the sim before desk work"; no visible progress signal |
| 5 | Sideslip script (tuned before C4) aborted twice at 53°/57° bank | two recoveries | regression of a script after a cfg change not checked |

Two different problems: (A) **the jet** needs protection while nobody flies it, (B) **pete's time**: he must see whether
Claude is working, waiting for a tool or stuck, and a hanging tool call must be cut off automatically.

## A. Sim watchdog (exists since 2026-11-03: `tools/watchdog.py`)
Background process, every 2 s, independent of Claude: airborne fuel < 1 500 lb -> refuel to the standard state;
airborne and (AGL < 2 000 ft with sink > 6 000 ft/min or |bank| > 90°) -> PAUSE; one status line per minute in
`build/watchdog.log`; reconnects after a sim restart. Possible extensions:
1. **Idle pause**: test scripts set `L:F104_TEST_ACTIVE` = 1 while they run (one line at start/end); if the jet is airborne,
   no test is active and nothing changed for N minutes (e.g. 3) -> PAUSE. Saves fuel and stops "flying around" while
   Claude does desk work.
2. **Build-All detector**: L:F104_SYS_VERSION or the AP state changes while airborne and AP turns off without a test
   -> PAUSE at once (case 1 above would have been caught: the reload left AP off in a dive).
3. **Notification** on every REFUEL/PAUSE: Windows toast (PowerShell `New-BurntToastNotification` or a plain
   `msg`-style popup) so pete notices.
Open question: should a REFUEL during a running test abort that test (weight step)? With extension 1 the watchdog knows.

## B. Time watchdog (Claude side)
1. **Rule: pause before desk work.** Whenever Claude starts analysis that takes more than about a minute (reading
   sources, calculations, writing code), send PAUSE_ON first and PAUSE_OFF only right before the next flight action.
   Costs nothing, solves case 4. (Caveat: some tools need the sim running - unpause first, as today.)
2. **Hard timeouts on every sim tool call**: run Python tools through Bash with a `timeout` (already the case for most),
   and never use tools without a bound (msfs_save_flight; load_flight only with the jet on the ground/paused).
3. **Tool-duration watchdog via Claude Code hooks** (`.claude/settings.json`, PreToolUse/PostToolUse): the hooks write
   "tool X started hh:mm:ss" / "finished" into `build/claude_activity.log`; the sim watchdog reads it and, if a tool call
   runs longer than e.g. 3 minutes (a takeoff or landing script takes up to ≈ 8 min - per-tool limits), pauses the sim
   and shows a notification "Claude tool X hangs for 4 min". This would have caught case 3 after 3 minutes instead of 20.
4. **Visible progress for pete**: the same activity log, or a Claude Code status line showing the last tool and its
   age plus the watchdog status (fuel/alt/AP). In the VS Code extension the status line may not be shown - the log file
   (open in an editor tab, auto-refresh) works everywhere.

## C. Process rules (from the cases above)
- Build All only with the jet standing on the runway (in CLAUDE.md / skill since today).
- Probe every new SimVar/unit pair from Python before a module build (in the H1 card).
- After a cfg change that alters handling (C4, T3-SP), list the scripts tuned to the old behaviour (sideslip, srot,
  landing flare, kicker) and re-check them in a build-up BEFORE using them as tools.

## Proposal (to decide)
Start with the cheap, robust parts: B1 (rule), A1 + A2 + A3 (watchdog extensions, ≈ 30 lines + one line per test
script), B3 (hooks) as a second step once A works. B4 = the watchdog log in an editor tab.
