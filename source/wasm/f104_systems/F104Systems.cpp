// F-104G systems module (MSFS 2024 WASM, standalone module in the aircraft package, docs/notes/systems-module.md).
//
// 1. H3 BLC (card docs/notes/test-cards/H3-blc-rpm.md): the rpm-dependent boundary-layer-control lift of the LAND flaps,
//    realised as an EFFECTIVE trailing-edge flap deflection - the law of tools/blc_driver.py, flown and validated
//    2026-10-31/11-01 (F3 -0.6/-0.9 %, F2 -0.4/-0.9 % from 165 KIAS, B6/B7/T3-L unchanged; module F3 -1.1 %):
//      BLC fraction f(N1) = 0.3 at 67 % (idle), 0.6 at 75 %, 0.9 at 80 %, 1.0 at >= 83 %   (FM 2-24, [S])
//      TE percent p = 1 - 0.52 (1 - f)                                                     (build-up 1, H3_bu1)
//    Written only with the flap lever in LAND (index 2) and once the LE flaps reached their stage (>= 29 deg; the coupled
//    flap travel stops them at 29.4 deg - an early TE write freezes the LE flaps). On leaving LAND the TE is restored to
//    100 % once so both flap systems leave LAND from the same travel fraction (desync found 2026-11-01).
// 2. H2 APC (card docs/notes/test-cards/H2-apc.md) - replaces the native SPS, which made the MSFS AP diverge after a full
//    restart (A/B 2026-10-31). FM 1-69, 6-5..6-7:
//      shaker: alpha > 11.3 deg (off 10.8) -> L:F104_APC_SHAKER (no stick-vibration output; for a later gauge/sound)
//      kicker: alpha + T_ANT x pitch rate > 14.5 deg (FM 6-6: pitch-rate input for anticipation), inhibited with the gear
//              down, the flap lever in LAND or below 120 KIAS (FM 6-6), and for 10 s after a position jump (set_pos);
//              FM 1-68: a hydraulic cylinder drives the STABILIZER nose-down and the stick to 1/2 inch ahead of neutral
//              (normal control forces cannot override it, only +40-50 lb). MSFS 2024 does not mask input events, and a
//              per-frame ELEVATOR POSITION write lost against continuous axis input (2026-11-01, alpha 24 deg) -> the
//              actuator is modelled as a stabilizer offset through the TRIM (not overwritten by stick inputs):
//              trim = trim0 + (stab(-0.1 stick) - stab(pilot stick)), stab = 17 deg x s (s > 0) / 5 deg x s (s < 0),
//              clamped to the trim range -5..+11 deg; nothing if the stick is already further forward ("not felt").
//              HOLDS while beyond the boundary (alpha > 12 deg) and for at least 0.8 s, then trim0 is restored over 1 s;
//              disengages the autopilot (FM 1-69); state in L:F104_APC_KICK.
//    Alpha thresholds from H2 (FM Fig. 6-3/6-4 CL -> sim alpha via the B7 logs). [S]: T_ANT, release alpha, hold time.
// 3. H1 SAS yaw damper (card docs/notes/test-cards/H1-sas.md) - FM 1-68: rate gyro -> rudder, does not move the pedals,
//    washout for pilot inputs. Actuator = the RUDDER TRIM channel (adds to the pedal rudder; bu0 2026-11-03: settable,
//    acts within one frame, +percent -> +body yaw rate, one trim degree acts like one rudder degree: beta/trim 0.33):
//      rudder trim = trim0 - K x HP(r) / 4 deg, HP = washout tau 1 s, K = K_REF x q_ref / q (q >= 200 psf), clamped +-4 deg
//    K_REF 0.7 deg per deg/s from CR-2144 F/C 4 (N'dr -4.49, Dutch roll zeta 0.09 -> 0.45). Switched and scaled by
//    L:F104_SAS_YAW (gain factor, 0 = off - build-up; on leaving: trim0 restored); off on the ground. Output in
//    L:F104_SAS_YAW_DEG (commanded SAS rudder, deg).
// Active only for the F-104G (TITLE contains "F-104G").
//
// Build: tools/build_wasm.sh (SDK clang-cl in g++ mode + wasm-ld, flags matched to the SDK StandaloneModule sample).

#include <MSFS/MSFS.h>
#include <MSFS/MSFS_WindowsTypes.h>
#include <SimConnect.h>
#include <string.h>
#include <stdio.h>

static HANDLE g_sc = 0;
// build version, published as L:F104_SYS_VERSION (lets the tools check which module build the sim runs, e.g. after
// a Build All without restart - hot reload test 2026-11-01)
static const double SYS_VERSION = 7.1;
static bool g_active = false;      // BLC override engaged (latched until the lever leaves LAND)
static bool g_is_f104 = false;

// APC parameters
static const double SHAKER_ON = 11.3, SHAKER_OFF = 10.8;      // deg alpha (H2)
static const double KICK_ALPHA = 14.5, KICK_RELEASE = 12.0;   // deg alpha (H2 / [S])
static const double T_ANT = 0.3;                              // s, pitch-rate anticipation [S]
static const double KICK_HOLD = 0.8;                          // s, minimum kick duration [S]
static const double KICK_STICK = -0.1;                        // ELEVATOR POSITION, slightly ahead of neutral (FM 6-6)
static const double KICK_MIN_IAS = 120.0;                     // KIAS, no kicks on the ground roll [S]

static bool g_shaker = false, g_kick = false;
static double g_kick_t0 = 0.0, g_prev_t = -1.0, g_prev_theta = 0.0, g_q_f = 0.0;
static double g_trim0 = 0.0, g_prev_alt = -1e9, g_inhibit_until = 0.0;
static double g_trim_cmd = 0.0, g_release_t = -1.0, g_release_from = 0.0;
static const double KICK_RETRACT = 1.0;                       // s, actuator retract ramp back to trim0 [S]

// SAS yaw damper parameters (H1)
static const double K_R_REF = 0.7;                            // deg rudder per deg/s yaw rate at Q_REF [S] (CR-2144 F/C 4)
static const double Q_REF = 732.0, Q_MIN = 200.0;             // psf, gain schedule K ~ 1/q
static const double TAU_WO = 1.0;                             // s, yaw washout [S]
static const double RUD_TRIM_DEG = 4.0;                       // deg at 100 % rudder trim (rudder_trim_limit, FM 6-3)

static bool g_yaw_on = false;
static double g_rtrim0 = 0.0, g_r_prev = 0.0, g_r_hp = 0.0, g_yaw_prev_t = -1.0;

enum DataDefs { DEF_STATE = 1, DEF_TE = 2, DEF_TITLE = 3, DEF_TRIM = 4, DEF_LVARS = 5, DEF_VERSION = 6, DEF_RTRIM = 7,
                DEF_SAS_OUT = 8 };
enum Requests { REQ_STATE = 1, REQ_TITLE = 2 };
enum Events { EVT_AP_OFF = 1 };

struct State {
    double handle;      // FLAPS HANDLE INDEX
    double le_deg;      // LEADING EDGE FLAPS LEFT ANGLE, degrees
    double n1;          // TURB ENG N1:1, percent
    double alpha;       // INCIDENCE ALPHA, degrees
    double pitch;       // PLANE PITCH DEGREES, degrees (positive = nose DOWN)
    double gear;        // GEAR HANDLE POSITION, bool
    double ias;         // AIRSPEED INDICATED, knots
    double ap;          // AUTOPILOT MASTER, bool
    double t;           // SIMULATION TIME, seconds
    double stick;       // ELEVATOR POSITION, position (-1..1, + = pull) - the pilot's input
    double trim;        // ELEVATOR TRIM POSITION, degrees (+ = nose up)
    double alt;         // PLANE ALTITUDE, feet
    double r;           // ROTATION VELOCITY BODY Y, degrees per second (+ = the yaw a + rudder trim gives)
    double qbar;        // DYNAMIC PRESSURE, psf
    double ground;      // SIM ON GROUND, bool
    double rtrim;       // RUDDER TRIM PCT, percent over 100
    double sas_yaw;     // L:F104_SAS_YAW, gain factor (0 = off)
};
struct TeSet {
    double left;        // TRAILING EDGE FLAPS LEFT PERCENT, percent over 100
    double right;       // TRAILING EDGE FLAPS RIGHT PERCENT
};
struct LVars {
    double shaker;      // L:F104_APC_SHAKER
    double kick;        // L:F104_APC_KICK
};
struct Title {
    char title[256];
};

static double blc_fraction(double n1)
{
    static const double x[] = {67.0, 75.0, 80.0, 83.0};
    static const double y[] = {0.3, 0.6, 0.9, 1.0};
    if (n1 <= x[0]) return y[0];
    for (int i = 1; i < 4; ++i)
        if (n1 <= x[i]) return y[i - 1] + (y[i] - y[i - 1]) * (n1 - x[i - 1]) / (x[i] - x[i - 1]);
    return 1.0;
}

static void set_te(double p)
{
    TeSet te = {p, p};
    SimConnect_SetDataOnSimObject(g_sc, DEF_TE, SIMCONNECT_OBJECT_ID_USER, 0, 0, sizeof(te), &te);
}

static void blc(const State* s)
{
    if ((int)(s->handle + 0.5) != 2) {
        if (g_active)
            set_te(1.0);                         // restore the LAND stage once (flap travel sync)
        g_active = false;                        // outside LAND the flap system takes over
        return;
    }
    if (!g_active && s->le_deg < 29.0)
        return;                                  // wait until the LE flaps reached their LAND stage
    g_active = true;
    set_te(1.0 - 0.52 * (1.0 - blc_fraction(s->n1)));
}

static void apc(const State* s)
{
    double theta = -s->pitch;                    // nose up positive
    double dt = (g_prev_t < 0.0) ? 0.0 : s->t - g_prev_t;
    if (dt > 0.0 && dt < 0.5)
        g_q_f += (((theta - g_prev_theta) / dt) - g_q_f) * 0.3;   // filtered pitch rate, deg/s
    g_prev_t = s->t;
    g_prev_theta = theta;

    if (g_prev_alt > -1e8 && (s->alt - g_prev_alt > 300.0 || g_prev_alt - s->alt > 300.0))
        g_inhibit_until = s->t + 10.0;           // position jump (set_pos): the alpha 0 -> trim transient lasts ≈ 8-10 s (H2t4: kick at t 8 s)
    g_prev_alt = s->alt;
    bool shaker = g_shaker ? (s->alpha > SHAKER_OFF) : (s->alpha > SHAKER_ON);
    bool inhibit = s->gear > 0.5 || (int)(s->handle + 0.5) == 2 || s->ias < KICK_MIN_IAS || s->t < g_inhibit_until;
    // 2026-11-01 (H2t5_to): with the anticipation active at any alpha the kicks excited themselves - each kick pushed
    // alpha to 0-2°, the nose came back at ≈ 15°/s and the next kick fired at alpha ≈ 9° (8 kicks, up to 290 KIAS) ->
    // the pitch-rate anticipation only acts near the boundary (alpha above the shaker threshold) [S]
    double alpha_pred = s->alpha + ((s->alpha > SHAKER_ON && g_q_f > 0.0) ? T_ANT * g_q_f : 0.0);
    if (!g_kick && !inhibit && alpha_pred > KICK_ALPHA) {
        if (g_release_t < 0.0)
            g_trim0 = s->trim;                   // during a retract ramp keep the pilot's original trim
        g_kick = true;
        g_kick_t0 = s->t;
        g_release_t = -1.0;
        if (s->ap > 0.5)
            SimConnect_TransmitClientEvent(g_sc, SIMCONNECT_OBJECT_ID_USER, EVT_AP_OFF, 0,
                                           SIMCONNECT_GROUP_PRIORITY_HIGHEST, SIMCONNECT_EVENT_FLAG_GROUPID_IS_PRIORITY);
    }
    if (g_kick && (inhibit || (s->alpha < KICK_RELEASE && s->t - g_kick_t0 >= KICK_HOLD))) {
        g_kick = false;
        // 2026-11-01 (H2t_clean): the step back to trim0 (8° in the slow test) pitched the nose up so fast that the
        // pitch-rate anticipation kicked again at alpha 10-12° (4 kicks, alpha 3 <-> 12°) -> the actuator retracts over
        // KICK_RETRACT seconds (the real cylinder retracts with a finite rate and the pilot follows through)
        g_release_t = s->t;
        g_release_from = g_trim_cmd;
    }
    if (!g_kick && g_release_t >= 0.0) {
        double f = (s->t - g_release_t) / KICK_RETRACT;
        double trim = f >= 1.0 ? g_trim0 : g_release_from + (g_trim0 - g_release_from) * f;
        SimConnect_SetDataOnSimObject(g_sc, DEF_TRIM, SIMCONNECT_OBJECT_ID_USER, 0, 0, sizeof(trim), &trim);
        if (f >= 1.0)
            g_release_t = -1.0;
    }
    if (g_kick) {
        double pilot = s->stick > 0.0 ? 17.0 * s->stick : 5.0 * s->stick;
        double target = 5.0 * KICK_STICK;        // stick 1/2 inch ahead of neutral -> -0.5 deg
        double offset = target - pilot;
        if (offset > 0.0)
            offset = 0.0;                        // stick already further forward: kicker not felt
        double trim = g_trim0 + offset;
        if (trim < -5.0) trim = -5.0;
        if (trim > 11.0) trim = 11.0;
        g_trim_cmd = trim;
        SimConnect_SetDataOnSimObject(g_sc, DEF_TRIM, SIMCONNECT_OBJECT_ID_USER, 0, 0, sizeof(trim), &trim);
    }
    if (shaker != g_shaker || g_kick || s->t - g_kick_t0 < 2.0) {
        LVars lv = {shaker ? 1.0 : 0.0, g_kick ? 1.0 : 0.0};
        SimConnect_SetDataOnSimObject(g_sc, DEF_LVARS, SIMCONNECT_OBJECT_ID_USER, 0, 0, sizeof(lv), &lv);
    }
    g_shaker = shaker;
}

static void sas_yaw(const State* s)
{
    bool on = s->sas_yaw > 0.0 && s->ground < 0.5;
    if (on && !g_yaw_on) {
        g_rtrim0 = s->rtrim;                     // the pilot's rudder trim, restored when the damper goes off
        g_r_prev = s->r;
        g_r_hp = 0.0;
        g_yaw_prev_t = s->t;
    }
    if (!on && g_yaw_on) {
        double v = g_rtrim0, out = 0.0;
        SimConnect_SetDataOnSimObject(g_sc, DEF_RTRIM, SIMCONNECT_OBJECT_ID_USER, 0, 0, sizeof(v), &v);
        SimConnect_SetDataOnSimObject(g_sc, DEF_SAS_OUT, SIMCONNECT_OBJECT_ID_USER, 0, 0, sizeof(out), &out);
    }
    g_yaw_on = on;
    if (!on)
        return;
    double dt = s->t - g_yaw_prev_t;
    g_yaw_prev_t = s->t;
    if (dt > 0.0 && dt < 0.5)
        g_r_hp = TAU_WO / (TAU_WO + dt) * (g_r_hp + s->r - g_r_prev);   // washout (first-order high pass)
    g_r_prev = s->r;
    double q = s->qbar > Q_MIN ? s->qbar : Q_MIN;
    double pct = g_rtrim0 - s->sas_yaw * K_R_REF * Q_REF / q * g_r_hp / RUD_TRIM_DEG;
    if (pct > 1.0) pct = 1.0;
    if (pct < -1.0) pct = -1.0;
    SimConnect_SetDataOnSimObject(g_sc, DEF_RTRIM, SIMCONNECT_OBJECT_ID_USER, 0, 0, sizeof(pct), &pct);
    double out = (pct - g_rtrim0) * RUD_TRIM_DEG;
    SimConnect_SetDataOnSimObject(g_sc, DEF_SAS_OUT, SIMCONNECT_OBJECT_ID_USER, 0, 0, sizeof(out), &out);
}

static void CALLBACK dispatch(SIMCONNECT_RECV* pData, DWORD cbData, void* pContext)
{
    if (pData->dwID != SIMCONNECT_RECV_ID_SIMOBJECT_DATA)
        return;
    SIMCONNECT_RECV_SIMOBJECT_DATA* d = (SIMCONNECT_RECV_SIMOBJECT_DATA*)pData;
    if (d->dwRequestID == REQ_TITLE) {
        const Title* t = (const Title*)&d->dwData;
        g_is_f104 = strstr(t->title, "F-104G") != nullptr;
        double v = SYS_VERSION;                  // refreshed once a second
        SimConnect_SetDataOnSimObject(g_sc, DEF_VERSION, SIMCONNECT_OBJECT_ID_USER, 0, 0, sizeof(v), &v);
        return;
    }
    if (d->dwRequestID != REQ_STATE || !g_is_f104)
        return;
    const State* s = (const State*)&d->dwData;
    blc(s);
    apc(s);
    sas_yaw(s);
}

extern "C" MSFS_CALLBACK void module_init(void)
{
    if (SimConnect_Open(&g_sc, "F104G Systems", nullptr, 0, 0, 0) != S_OK) {
        fprintf(stderr, "F104G Systems: SimConnect_Open failed\n");
        return;
    }
    SimConnect_AddToDataDefinition(g_sc, DEF_STATE, "FLAPS HANDLE INDEX", "number");
    SimConnect_AddToDataDefinition(g_sc, DEF_STATE, "LEADING EDGE FLAPS LEFT ANGLE", "degrees");
    SimConnect_AddToDataDefinition(g_sc, DEF_STATE, "TURB ENG N1:1", "percent");
    SimConnect_AddToDataDefinition(g_sc, DEF_STATE, "INCIDENCE ALPHA", "degrees");
    SimConnect_AddToDataDefinition(g_sc, DEF_STATE, "PLANE PITCH DEGREES", "degrees");
    SimConnect_AddToDataDefinition(g_sc, DEF_STATE, "GEAR HANDLE POSITION", "bool");
    SimConnect_AddToDataDefinition(g_sc, DEF_STATE, "AIRSPEED INDICATED", "knots");
    SimConnect_AddToDataDefinition(g_sc, DEF_STATE, "AUTOPILOT MASTER", "bool");
    SimConnect_AddToDataDefinition(g_sc, DEF_STATE, "SIMULATION TIME", "seconds");
    SimConnect_AddToDataDefinition(g_sc, DEF_STATE, "ELEVATOR POSITION", "position");
    SimConnect_AddToDataDefinition(g_sc, DEF_STATE, "ELEVATOR TRIM POSITION", "degrees");
    SimConnect_AddToDataDefinition(g_sc, DEF_STATE, "PLANE ALTITUDE", "feet");
    SimConnect_AddToDataDefinition(g_sc, DEF_STATE, "ROTATION VELOCITY BODY Y", "degrees per second");
    SimConnect_AddToDataDefinition(g_sc, DEF_STATE, "DYNAMIC PRESSURE", "psf");   // "pounds per square foot" is NOT a unit name (v7: whole definition dead)
    SimConnect_AddToDataDefinition(g_sc, DEF_STATE, "SIM ON GROUND", "bool");
    SimConnect_AddToDataDefinition(g_sc, DEF_STATE, "RUDDER TRIM PCT", "percent over 100");
    SimConnect_AddToDataDefinition(g_sc, DEF_STATE, "L:F104_SAS_YAW", "number");
    SimConnect_AddToDataDefinition(g_sc, DEF_TE, "TRAILING EDGE FLAPS LEFT PERCENT", "percent over 100");
    SimConnect_AddToDataDefinition(g_sc, DEF_TE, "TRAILING EDGE FLAPS RIGHT PERCENT", "percent over 100");
    SimConnect_AddToDataDefinition(g_sc, DEF_TITLE, "TITLE", nullptr, SIMCONNECT_DATATYPE_STRING256);
    SimConnect_AddToDataDefinition(g_sc, DEF_TRIM, "ELEVATOR TRIM POSITION", "degrees");
    SimConnect_AddToDataDefinition(g_sc, DEF_LVARS, "L:F104_APC_SHAKER", "number");
    SimConnect_AddToDataDefinition(g_sc, DEF_LVARS, "L:F104_APC_KICK", "number");
    SimConnect_AddToDataDefinition(g_sc, DEF_VERSION, "L:F104_SYS_VERSION", "number");
    SimConnect_AddToDataDefinition(g_sc, DEF_RTRIM, "RUDDER TRIM PCT", "percent over 100");
    SimConnect_AddToDataDefinition(g_sc, DEF_SAS_OUT, "L:F104_SAS_YAW_DEG", "number");
    SimConnect_MapClientEventToSimEvent(g_sc, EVT_AP_OFF, "AUTOPILOT_OFF");
    SimConnect_RequestDataOnSimObject(g_sc, REQ_TITLE, DEF_TITLE, SIMCONNECT_OBJECT_ID_USER, SIMCONNECT_PERIOD_SECOND);
    SimConnect_RequestDataOnSimObject(g_sc, REQ_STATE, DEF_STATE, SIMCONNECT_OBJECT_ID_USER, SIMCONNECT_PERIOD_SIM_FRAME);
    SimConnect_CallDispatch(g_sc, dispatch, nullptr);
}

extern "C" MSFS_CALLBACK void module_deinit(void)
{
    if (g_sc)
        SimConnect_Close(g_sc);
    g_sc = 0;
}
