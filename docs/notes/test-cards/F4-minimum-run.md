# F4: minimum-run landing (FM 2-28)

**Objective / acceptance:** FM 2-28: fly the approach for close control of TD point and speed, touch down at 140 KIAS for
normal landing gross weight (+5 kt per 1 000 lb above 15 100 lb, Fig. A8-2 note -> **≈ 159.5 KIAS at 19 000 lb**, normal TD
169.5-174.5), speed brakes to aid, chute planned to blossom as the nose wheel touches, maximum anti-skid braking.
Acceptance: TD ≤ 167 KIAS (clearly below the normal band; the script flare cannot fully reach 160, see prediction), no tail
strike (pitch < 11° guard), roll from 150 KIAS with chute within ± 5 % of FM A8-3 scaled ((150/166.5)² x 2 760 = 2 240 ft;
F2 series -0.9/-0.4 %).

**Tool:** `landing_test.py <csv> 6 2.5 <high> fmflare minrun` (new option: TD target, SPOILERS_ON at the flare start = air
speed brakes, which become the chute emulation on the ground; chute logic unchanged). Default LAND path (1.8 Hz).

**Analysis (desk):** CL at 160 KIAS = 19 000 / (86.7 psf x 196.1) = 1.12; LAND points (approach 191 KIAS α 3.4° CL 0.78; T3-L CL
0.855 α 4.1°) -> ≈ 0.09/° -> α ≈ 7.0° out of ground effect, ≈ 6° in it (F3 at 172 KIAS: CL 0.97, pitch 3.9° at TD consistent)
-> **pitch at TD ≈ 5-7°**, tail strike 12.3° (margin ≈ 5°). Sim LAND shaker 144 KIAS (H2) -> 16 kt margin. Speed bleed in
the flare: F3 190 -> 172 (18 kt, 82 % floor); speed brakes ΔCD 0.046 (S11e) ≈ 900 lbf at 100 psf ≈ 0.9 kt/s over ≈ 8 s ->
**TD ≈ 163-167 KIAS**. Roll from 150 KIAS with chute ≈ 2 240 ft ± 5 %.

**Hazards:** (1) slower TD -> higher α -> tail strike: guard (θ > 11° below 60 ft -> go-around); build-up dry run at +6 000 ft
first (pitch in the flare must stay ≤ 9°). (2) Speed brakes in the flare change the flare dynamics (drag, pitch) -> dry run.
(3) Go-around from the flare with speed brakes out: go_around() retracts them (SPOILERS_OFF), F8 law validated.
(4) Chute emulation acts at the main-gear touch (spoiler handle already ON) - earlier than the FM "as the nose wheel touches";
recorded.

**Go/no-go:** dry run (S18-F4 step dry) first; real run only if the dry TD pitch ≤ 9° and no guard trip.

## Result + Debrief (2026-11-06) - procedure ✓, TD speed and roll metric partly open (◑)
- **Dry (S18-F4, +6 000 ft):** speed brakes out at the flare, virtual TD **168 KIAS**, -607 ft/min (F3 dry -483), pitch 4.8°,
  1 795 ft past the threshold, flare pitch 1.0-4.9°, bank ±0.5°. GO criteria met (pitch ≤ 9°, no guard).
- **Real (S18b-F4, 19 008 lb):** flare at 118 ft / 189 KIAS, **TD 168 KIAS, -533 ft/min, pitch 4.0°, 1 557 ft past the
  threshold** (earliest of all landings), CL -1 ft, 1 skip, chute 162 KIAS, stop **4 778 ft past the threshold**.
  Comparison F2 with chute (H3_F2b/F2c 2026-11-01): TD 2 837-3 548 ft, stop 6 709-7 527 ft -> **F4 total distance -29..-37 %**
  = the FM minimum-run effect (no FM chart for it).
- vs. acceptance: TD 168 vs ≤ 167 (target 159.5): the script flare (82 % floor, speed ramp 100 -> 20 ft) bleeds only 21 kt
  even with the speed brakes (prediction 163-167) - same limitation as F5; a min-run flare technique (earlier speed bleed on
  short final) would be needed to reach 160. Roll metrics ambiguous: from 165 KIAS +5.3 % (TD only 3 kt above 165 -> the
  touchdown transient is inside the window), from 150 KIAS -7.0 % (V² scaling of A8-3 to a low reference speed with the chute
  (drag ∝ V²) shortens the reference) -> neither is a clean FM comparison; sink -533 ft/min (firmer than F3 -349: speed-brake
  drag in the flare).
