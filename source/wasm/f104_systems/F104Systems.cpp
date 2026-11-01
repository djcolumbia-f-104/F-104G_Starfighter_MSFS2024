// F-104G systems module (MSFS 2024 WASM, standalone module) - PROTOTYPE, not yet part of the package.
//
// H3 BLC (card docs/notes/test-cards/H3-blc-rpm.md): the rpm-dependent boundary-layer-control lift of the LAND flaps,
// realised as an EFFECTIVE trailing-edge flap deflection - the same law as tools/blc_driver.py, which was flown and
// validated on 2026-10-31/11-01 (F3 -0.6/-0.9 %, F2 -0.4/-0.9 % from 165 KIAS, B6/B7/T3-L unchanged):
//   BLC fraction f(N1) = 0.3 at 67 % (idle), 0.6 at 75 %, 0.9 at 80 %, 1.0 at >= 83 %   (FM 2-24, [S])
//   TE percent p = 1 - 0.52 (1 - f)                                                     (build-up 1, H3_bu1)
// Written only with the flap lever in LAND (index 2) and once the LE flaps reached their stage (>= 29 deg; the coupled
// flap travel stops them at 29.4 deg - an early TE write freezes the LE flaps). Active only for the F-104G (title).
//
// Build: tools/build_wasm.sh (SDK clang-cl in g++ mode + wasm-ld, flags matched to the SDK StandaloneModule sample).

#include <MSFS/MSFS.h>
#include <MSFS/MSFS_WindowsTypes.h>
#include <SimConnect.h>
#include <string.h>
#include <stdio.h>

static HANDLE g_sc = 0;
static bool g_active = false;      // BLC override engaged (latched until the lever leaves LAND)
static bool g_is_f104 = false;

enum DataDefs { DEF_STATE = 1, DEF_TE = 2, DEF_TITLE = 3 };
enum Requests { REQ_STATE = 1, REQ_TITLE = 2 };

struct State {
    double handle;      // FLAPS HANDLE INDEX
    double le_deg;      // LEADING EDGE FLAPS LEFT ANGLE, degrees
    double n1;          // TURB ENG N1:1, percent
};
struct TeSet {
    double left;        // TRAILING EDGE FLAPS LEFT PERCENT, percent over 100
    double right;       // TRAILING EDGE FLAPS RIGHT PERCENT
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

static void CALLBACK dispatch(SIMCONNECT_RECV* pData, DWORD cbData, void* pContext)
{
    if (pData->dwID != SIMCONNECT_RECV_ID_SIMOBJECT_DATA)
        return;
    SIMCONNECT_RECV_SIMOBJECT_DATA* d = (SIMCONNECT_RECV_SIMOBJECT_DATA*)pData;
    if (d->dwRequestID == REQ_TITLE) {
        const Title* t = (const Title*)&d->dwData;
        g_is_f104 = strstr(t->title, "F-104G") != nullptr;
        return;
    }
    if (d->dwRequestID != REQ_STATE || !g_is_f104)
        return;
    const State* s = (const State*)&d->dwData;
    if ((int)(s->handle + 0.5) != 2) {
        g_active = false;                        // outside LAND the flap system takes over
        return;
    }
    if (!g_active && s->le_deg < 29.0)
        return;                                  // wait until the LE flaps reached their LAND stage
    g_active = true;
    double p = 1.0 - 0.52 * (1.0 - blc_fraction(s->n1));
    TeSet te = {p, p};
    SimConnect_SetDataOnSimObject(g_sc, DEF_TE, SIMCONNECT_OBJECT_ID_USER, 0, 0, sizeof(te), &te);
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
    SimConnect_AddToDataDefinition(g_sc, DEF_TE, "TRAILING EDGE FLAPS LEFT PERCENT", "percent over 100");
    SimConnect_AddToDataDefinition(g_sc, DEF_TE, "TRAILING EDGE FLAPS RIGHT PERCENT", "percent over 100");
    SimConnect_AddToDataDefinition(g_sc, DEF_TITLE, "TITLE", nullptr, SIMCONNECT_DATATYPE_STRING256);
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
