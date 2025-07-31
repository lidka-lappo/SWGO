import numpy as np
from load_lookUpTable import load_general_config , load_rpc_parameters

import numpy as np

def calculate_Q_T(data, rpc):
    QFmax = data[f'QFmax_RPC{rpc}']
    QBmax = data[f'QBmax_RPC{rpc}']
    Xmax = data[f"Xmax_RPC{rpc}"] 
    
    rows = np.arange(Xmax.shape[0])

    TF_selected = data[f"TF_RPC{rpc}"][rows, Xmax]
    TB_selected = data[f"TB_RPC{rpc}"][rows, Xmax]

    T = (TF_selected + TB_selected) / 2
    Yraw = (TF_selected - TB_selected) / 2
    Xraw = Xmax + 1

    Q = np.full(T.shape[0], np.nan)
    valid_Q = (~np.isnan(QFmax)) & (~np.isnan(QBmax))
    Q[valid_Q] = (QFmax[valid_Q] + QBmax[valid_Q]) / 2



    results = {
        f"T_RPC{rpc}": T,
        f"Q_RPC{rpc}": Q,
        f"Yraw_RPC{rpc}": Yraw,
        f"Xraw_RPC{rpc}": Xraw
    }
    return results


def calculate_parameters(data, raw_events, rpc, verbose=False):
    """
    Analyze event data to calculate efficiency, charge statistics, and streamer fraction.

    Parameters:
    - data: dict-like object or namespace containing arrays QFmax, QBmax, and T (e.g. data.QFmax)
    - raw_events: int, total number of raw events (rawEvents)

    Returns:
      'efficiency', 'efficiency_error',
      'Qmean', 'Qmean_error', 'Qmedian', 'Qmedian_error',
      'Qmean_noST', 'Qmean_noST_error', 'Qmedian_noST', 'Qmedian_noST_error',
      'streamer_fraction', 'streamer_fraction_error'
    """

    general_config = load_general_config("lookUpTable_general.txt")
    strTh = general_config["general"]["streamer_threshold"]

    Q = data[f"Q_RPC{rpc}"]
    T = data[f"T_RPC{rpc}"]


    # Calculate efficiency
    Events = np.sum(~np.isnan(T))
    efficiency = Events / raw_events if raw_events > 0 else np.nan
    efficiency_error = np.sqrt(efficiency * (1 - efficiency) / raw_events) if raw_events > 0 else np.nan



    # Filter Q values
    Qvalid = Q[(Q < 10000) & (~np.isnan(Q))]
    Qvalid_noST = Q[(Q < strTh) & (~np.isnan(Q))]

    # With streamers
    Qmean = np.nanmean(Qvalid) if len(Qvalid) > 0 else np.nan
    Qstd = np.nanstd(Qvalid) if len(Qvalid) > 0 else np.nan
    err_Qmean = Qstd / np.sqrt(len(Qvalid)) if len(Qvalid) > 0 else np.nan

    Qmedian = np.nanmedian(Qvalid) if len(Qvalid) > 0 else np.nan
    err_Qmedian = np.nanmedian(np.abs(Qvalid - Qmedian)) if len(Qvalid) > 0 else np.nan

    # Without streamers
    Qmean_noST = np.nanmean(Qvalid_noST) if len(Qvalid_noST) > 0 else np.nan
    Qstd_noST = np.nanstd(Qvalid_noST) if len(Qvalid_noST) > 0 else np.nan
    err_Qmean_noST = Qstd_noST / np.sqrt(len(Qvalid_noST)) if len(Qvalid_noST) > 0 else np.nan

    Qmedian_noST = np.nanmedian(Qvalid_noST) if len(Qvalid_noST) > 0 else np.nan
    err_Qmedian_noST = np.nanmedian(np.abs(Qvalid_noST - Qmedian_noST)) if len(Qvalid_noST) > 0 else np.nan

    # Streamer fraction and error
    try:
        total_valid_events = np.sum(~np.isnan(Q))
        streamer_events = np.sum(Q > strTh)
        ST = 100 * streamer_events / total_valid_events
        err_ST = 100 * np.sqrt((ST/100) * (1 - ST/100) / total_valid_events)
    except ZeroDivisionError:
        ST = np.nan
        err_ST = np.nan

    results = {
        f'efficiency_RPC{rpc}': efficiency,
        f'efficiency_error_RPC{rpc}': efficiency_error,
        f'Qmean_RPC{rpc}': Qmean,
        f'Qmean_error_RPC{rpc}': err_Qmean,
        f'Qmedian_RPC{rpc}': Qmedian,
        f'Qmedian_error_RPC{rpc}': err_Qmedian,
        f'Qmean_noST_RPC{rpc}': Qmean_noST,
        f'Qmean_noST_error_RPC{rpc}': err_Qmean_noST,
        f'Qmedian_noST_RPC{rpc}': Qmedian_noST,
        f'Qmedian_noST_error_RPC{rpc}': err_Qmedian_noST,
        f'streamer_fraction_RPC{rpc}': ST,
        f'streamer_fraction_error_RPC{rpc}': err_ST
    }

    if verbose:
        print(f"RPC{rpc} results:")
        print(f"  Efficiency: {efficiency:.4f} ± {efficiency_error:.4f}")
        print(f"  Qmean: {Qmean:.2f} ± {err_Qmean:.2f}")
        print(f"  Qmean noST: {Qmean_noST:.2f} ± {err_Qmean_noST:.2f}")
        print(f"  Qmedian: {Qmedian:.2f} ± {err_Qmedian:.2f}")
        print(f"  Qmedian noST: {Qmedian_noST:.2f} ± {err_Qmedian_noST:.2f}")
        print(f"  Streamer fraction: {ST:.2f}% ± {err_ST:.2f}%")



    return results


###############################################################




def strips2Dplots(X, Y, Q, binsX, binsY, STLevel, useBelowSTOnly=True):

    XY = np.zeros((len(binsX)-1, len(binsY)-1), dtype=int)
    XY_Qmean = np.zeros((len(binsX)-1, len(binsY)-1), dtype=float)
    XY_Qmedian = np.zeros((len(binsX)-1, len(binsY)-1), dtype=float)
    XY_ST = np.zeros((len(binsX)-1, len(binsY)-1), dtype=int)

    for i in range(len(binsX)-1):
        for j in range(len(binsY)-1):
            # Find indices within bin ranges (open on left, closed on right)
            mask = (X > binsX[i]) & (X <= binsX[i+1]) & (Y > binsY[j]) & (Y <= binsY[j+1])
            indices = np.where(mask)[0]

            XY[i, j] = len(indices)

            Qvalid = Q[indices]
            Qvalid = Qvalid[~np.isnan(Qvalid)]  # Remove NaNs

            if useBelowSTOnly:
                Qvalid = Qvalid[Qvalid < STLevel]  # Filter only below threshold

            if len(Qvalid) > 0:
                XY_Qmean[i, j] = np.mean(Qvalid)
                XY_Qmedian[i, j] = np.median(Qvalid)
            else:
                XY_Qmean[i, j] = 0
                XY_Qmedian[i, j] = 0

            XY_ST[i, j] = np.sum(Q[indices] > STLevel)

    return XY, XY_Qmean, XY_Qmedian, XY_ST



def calculate_XY(data, rpc):
    general_config = load_general_config("lookUpTable_general.txt")
    vprop = general_config["general"]["vprop"]
    pitch = general_config["general"]["pitch"]
    strips= general_config["general"]["strips"]
    strTh= general_config["general"]["streamer_threshold"]
    XRange = general_config["ranges"]["XRange"]
    YRange = general_config["ranges"]["YRange"]

    rpc_params = load_rpc_parameters(f"lookUpTable_RPC{rpc}.txt")
    YCenters = rpc_params["ycenters"]

    Yraw = data[f"Yraw_RPC{rpc}"]
    Xraw = data[f"Xraw_RPC{rpc}"]
    Q = data[f"Q_RPC{rpc}"]

    Ycal = Yraw.copy()

    for i in range(strips):
        indx = np.where(Xraw == i+1)[0]
        Ycal[indx] = Yraw[indx] - YCenters[i]

    Xmm = ((Xraw-0.5) * pitch) + ((np.random.rand(len(Xraw)) * pitch) - (pitch / 2))
    Ymm = Ycal * vprop


    STLevel = strTh
    XY, XY_Qmean, XY_Qmedian, XY_ST = strips2Dplots(Xmm, Ymm, Q, XRange, YRange, STLevel)
    

    data[f"Xmm_RPC{rpc}"] = Xmm
    data[f"Ymm_RPC{rpc}"] = Ymm
    data[f"XY_RPC{rpc}"] = XY
    data[f"XY_Qmean_RPC{rpc}"] = XY_Qmean
    data[f"XY_Qmedian_RPC{rpc}"] = XY_Qmedian
    data[f"XY_ST_RPC{rpc}"] = XY_ST


