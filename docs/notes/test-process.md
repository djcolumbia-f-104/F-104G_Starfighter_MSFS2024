# Fixed test process: preconditions, postconditions, debrief, lessons learned (draft 2026-11-03, for 2026-11-04)

pete's question (2026-11-03): define a fixed test sequence - preconditions that must be met, postconditions, analyse the
findings afterwards and learn from them - plus the robustness measures (watchdog, routine checks). This draft combines
our skill `f104-testcard` with the practice of real flight-test organisations and today's incidents. **To be discussed
and then folded into the skill** (the skill stays the single place Claude follows).

## 1. What real flight-test organisations do (research 2026-11-03)
- **Approved test cards only**, with minimum contents incl. go/no-go criteria, risk level and data-acquisition settings,
  and a **unit process for updating cards from lessons learned** (Edwards AFB instruction 99-105).
- **Briefing**: the test conductor reviews the cards, the conduct of the flight, abort criteria and fuel management
  with the crew (SETP flight-briefing best practice). Condensed **"safety cards"** instead of the full hazard analysis
  for the briefing (Flight Test Safety Committee presentation).
- **Test Hazard Analysis (THA)**: one hazard per sheet, same format each: cause, effect, minimising procedures,
  **corrective action if the hazard occurs** ("breaks the link between hazard and mishap") (AFFTC safety review board).
- **Build-up**: from light to heavy, short to long predicted distances; re-check predictions against data before the
  next step; consider test-point complexity and the aircraft state at the END of each point (Textron, Navy safety fact).
- **Debrief right after the test**: unusual occurrences and anomalies first, then by subsystem; the test conductor writes
  a short summary from the test and debrief (not yet the full analysis) for immediate dissemination (SETP).
- **Flight readiness review**: measurable criteria satisfied before release, recorded decisions (FRR templates).
- Software side: Anthropic's "verification loop" idea - a skill that checks the work and fixes it, run automatically
  (e.g. on every change); published verify skills (oh-my-claudecode `verify`, everything-claude-code
  `verification-loop`) check build/tests after each change - no ready-made pre/postcondition skill exists; our
  `f104-testcard` is closer to the need than these.

## 2. Proposed fixed sequence (each step has an owner and an output)
| Step | What | Output / gate |
|---|---|---|
| 0 Session start | watchdog running, `selftest` (automated, see 4), build current, weather, fuel | selftest ALL OK, else stop |
| 1 Plan | objective, reference value with source, prediction (analysis gate 2b) | card sections Objective / Analysis |
| 2 THA (light) | for each new risk: cause, effect, minimising procedure, **recovery action** (scripted where possible) | card section "Hazards" (one line per hazard) |
| 3 Preconditions | written as checkable items, each with the tool that checks it; scripts refuse to start if one fails | card section "Preconditions" + script asserts |
| 4 Readiness ("go/no-go") | Claude runs the checks, posts a 3-line go/no-go to pete for risky points (new law, ground contact, first flight after a cfg change) | go/no-go line in the card |
| 5 Execute | build-up first; knock-it-off criteria in the script; watchdog; sim paused during desk work | logs in docs/data |
| 6 Postconditions | checked automatically at the end of every script: jet in a safe, defined state (AP on + verified, level, fuel ≥ x, trim/flaps/gear as specified, damper switches back to default, no leftover L-vars) | script prints POST OK / POST FAIL |
| 7 Debrief (immediately) | prediction vs. measurement, anomalies (also small ones), what surprised us | 5-line "TC summary" in the card |
| 8 Lessons learned | each lesson -> where it is enforced: script assert, selftest item, skill rule, card template | entry in `docs/notes/lessons-learned.md` (register: date, event, cause, fix, enforced in) |
| 9 Commit | card, data, measurements, index, register | git |

Rule for step 8: a lesson only counts as learned when it is **enforced by a check or a script**, not only written down
(today: "probe SimVar units" became a rule - better: build_wasm.sh probes them itself).

## 3. Today's incidents through this sequence (examples for the register)
| Event | Would have been caught by |
|---|---|
| Build All with the jet in the air -> reload, AP off, crash | step 0/4 precondition "jet on the runway before Build All" + watchdog reload detection (fuel jump + AP off + flaps 15 in the air -> PAUSE) |
| module v7 invalid unit "pounds per square foot" -> module blind | selftest / build_wasm.sh probes all datum/unit pairs from the C++ source before the build |
| msfs_save_flight 23 min blocked, fuel 3 509 -> 1 280 lb | THA "unbounded tool call in flight" -> rule: only on the ground, existing folder, tested once; watchdog refuels |
| desk analysis while the jet flies | step 5: PAUSE during desk work (pete prefers no automatic pausing by the watchdog - Claude pauses, the watchdog only refuels) |
| sideslip script aborted twice (tuned before C4) | step 2 THA after a cfg change: list of scripts tuned to the old behaviour -> build-up before use |
| body-X pitch rate 3.5x too large | step 1: cross-check every new measurement channel against an independent one (θ) before using it |

## 4. Robustness measures (as discussed 2026-11-03)
1. **Watchdog = separate program** (`tools/watchdog.py`, exists): runs independently of Claude (Claude cannot act while a
   tool call hangs - the screenshot idea needs a free Claude, so it cannot replace this). pete: it should NOT pause in
   normal operation. Planned: refuel (exists), reload detection -> pause (the one case where pausing saves the jet),
   emergency pause only for a dive near the ground, Windows notification on every intervention, start script.
2. **`tools/selftest.py`** (ground, ≈ 10 s): SimConnect, aircraft title, module version, all SimVar/unit pairs used by
   the module and the tools (parsed from the sources), watchdog alive (log age < 2 min), weather, fuel/trim/flaps;
   merge with `preflight`. **build_wasm.sh** runs the unit probe and refuses to build on an invalid pair.
3. **Bounded tool calls**: every sim script with a hard timeout and a safe end state on timeout; unbounded calls
   (msfs_save_flight, load_flight in flight) banned while airborne.
4. **Postcondition block** in every flight script (shared helper `tools/post.py`): AP on and verified, level ± 500 ft/min,
   fuel ≥ 1 500 lb, damper switches default, prints POST OK/FAIL.
5. Claude checks `sim_state` (numbers, cheap) between longer steps; screenshots only when the numbers look odd.

## 5. Plan for 2026-11-04 (proposal)
1. Discuss this draft + `session-watchdog.md` with pete (≈ 15 min), decide the sequence.
2. Implement: lessons-learned register (seed with today's 6 entries), selftest.py + unit probe in build_wasm.sh,
   watchdog extensions (reload detection, notification, start script), post.py helper; fold steps 2/6/7/8 into the skill
   `f104-testcard` and the card template.
3. Then T3-SP change 1 (aero_center_lift +3.6 ft) with the new process: air start prepared by pete (flight saved in the
   air via the sim menu), predictions in the card.

Sources: [Edwards AFB instruction 99-105](https://static.e-publishing.af.mil/production/1/edwardsafb/publication/edwardsafbi99-105/edwardsafbi99-105.pdf),
[SETP flight briefings](https://flighttestsafety.setp.org/images/stories/best-practices/fltbrfs1.docx),
[Flight Test Safety presentation](https://www.flighttestsafety.org/images/Safety_Presentation_Rev_C_Shorty.pdf),
[AFFTC safety review board / THA](https://flighttestsafety.setp.org/images/stories/best-practices/afftcsrb1.docx),
[Textron flight test safety risk management](https://flighttestsafety.org/images/Textron_Aviation_Flight_Test_Safety_Risk_Management_EFTSW_Oct_2022_Mark_Purvis.pdf),
[Flight Test Safety Fact 21-01](https://flighttestsafety.org/images/Flight_Test_Safety_Fact_21-01edit.pdf),
[FRR template](https://www.docsie.io/solutions/templates/aerospace-defense/flight-readiness-review/),
[Anthropic: verification loops with skills](https://claude.com/blog/building-verification-loops-in-claude-code-with-skills),
[oh-my-claudecode verify skill](https://skillselion.com/skills/yeachan-heo/oh-my-claudecode/verify),
[verification-loop skill](https://agentskillsfinder.com/skills/verification-loop).
