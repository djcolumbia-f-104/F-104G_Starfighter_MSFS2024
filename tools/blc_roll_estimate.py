# Ground-roll sensitivity to the BLC flap lift (desk estimate for the BLC design, 2026-10-31)
# decel = [mu (W - L) + D - T_idle] / m, L = q S CL_gnd, D = q S CD; integrate V from V_td to 0
S, W, g = 196.1, 17900.0, 32.174
CD = 0.02 + 0.08 + 0.022            # clean CD0 + LAND flap ΔCD 0.08 (B5) + gear 0.022
T_IDLE = 500.0                      # [S] residual idle thrust lbf
RHO = 0.0023769 * 0.957             # 1 500 ft
def roll(dcl_flap, mu, v_td_kt=166.5, cl_wing=0.01):
    v, x, dt = v_td_kt * 1.68781, 0.0, 0.01
    while v > 1:
        q = 0.5 * RHO * v * v
        L = q * S * (cl_wing + dcl_flap)
        a = (mu * max(W - L, 0) + q * S * CD - T_IDLE) / (W / g)
        v -= a * dt
        x += v * dt
    return x
# calibrate mu so that BLC-on (ΔCL 0.62) reproduces the sim F3 (+9.6 % vs FM A8-4 3 130 ft -> 3 430 ft)
lo, hi = 0.1, 1.5
for _ in range(60):
    mu = 0.5 * (lo + hi)
    lo, hi = (mu, hi) if roll(0.62, mu) > 3430 else (lo, mu)
print(f"calibrated mu_eff {mu:.3f}: BLC on (dCL 0.62) roll {roll(0.62, mu):.0f} ft")
print(f"lift share at touchdown (dCL 0.62): {0.5*RHO*(166.5*1.68781)**2*S*0.63/W:.2f} W")
for name, dcl in (("BLC at idle 30 % left (dCL 0.62-0.7*0.135)", 0.62 - 0.7 * 0.135),
                  ("BLC fully lost (dCL 0.62-0.135)", 0.62 - 0.135),
                  ("BLC low estimate 0.12, 30 % left", 0.62 - 0.7 * 0.12),
                  ("BLC high estimate 0.15, 0 % left", 0.62 - 0.15)):
    r = roll(dcl, mu)
    print(f"{name:45s} roll {r:.0f} ft = {100*(r/3130-1):+.1f} % vs FM A8-4")
