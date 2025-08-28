import numpy as np
from load_lookUpTable import load_general_config , load_rpc_parameters

import numpy as np
import datetime
from datetime import datetime, timedelta
from readMetaData import read_hv, read_thp


import pandas as pd
import numpy as np

def calculate_Q_T(data, rpc):

    qfmax = data[f"QFmax_RPC{rpc}"]
    qbmax = data[f"QBmax_RPC{rpc}"]
    xmax = data[f"Xmax_RPC{rpc}"]
    ebtime = data["EBtime"]

    # Select TF and TB values at the strip given by Xmax
    TF_selected = data.apply(
        lambda row: row[f"TF_RPC{rpc}"][row[f"Xmax_RPC{rpc}"]] 
                    if row[f"Xmax_RPC{rpc}"] >= 0 else np.nan, 
        axis=1
    )
    TB_selected = data.apply(
        lambda row: row[f"TB_RPC{rpc}"][row[f"Xmax_RPC{rpc}"]] 
                    if row[f"Xmax_RPC{rpc}"] >= 0 else np.nan, 
        axis=1
    )

    # Calculate timing & positions
    T = (TF_selected + TB_selected) / 2
    Yraw = (TF_selected - TB_selected) / 2
    Xraw = xmax + 1  # shift to 1-based index

    # Charge: average of QFmax and QBmax if both valid
    Q = (qfmax + qbmax) / 2
    Q[ qfmax.isna() | qbmax.isna() ] = np.nan

    # Save results back to DataFrame
    df = pd.DataFrame({
        f"T_RPC{rpc}": T,
        f"Q_RPC{rpc}": Q,
        f"Yraw_RPC{rpc}": Yraw,
        f"Xraw_RPC{rpc}": Xraw,
        f"EBtime_RPC{rpc}": ebtime
    })

    return df
   

def matlab_datenum_to_datetime(matlab_datenum):
    # MATLAB datenum starts at year 0, Python datetime starts at 0001-01-01
    days = int(matlab_datenum)
    frac = matlab_datenum % 1
    python_datetime = datetime.fromordinal(days - 366) + timedelta(days=frac)
    return python_datetime



def calculate_parameters(df, raw_events, rpc, verbose=False):
    general_config = load_general_config("lookUpTable_general.txt")
    strTh = general_config["general"]["streamer_threshold"]

    # Get numpy arrays from DataFrame
    Q = df[f"Q_RPC{rpc}"].to_numpy()
    T = df[f"T_RPC{rpc}"].to_numpy()
    EBtime = df[f"EBtime_RPC{rpc}"].to_numpy()

    # Convert MATLAB datenum to datetime for start and end
    t_start = matlab_datenum_to_datetime(EBtime[0] + T[0] / (24 * 3600))
    t_end   = matlab_datenum_to_datetime(EBtime[-1] + T[-1] / (24 * 3600))

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

    # Streamer fraction
    try:
        total_valid_events = np.sum(~np.isnan(Q))
        streamer_events = np.sum(Q > strTh)
        ST = 100 * streamer_events / total_valid_events
        err_ST = 100 * np.sqrt((ST/100) * (1 - ST/100) / total_valid_events)
    except ZeroDivisionError:
        ST = np.nan
        err_ST = np.nan

    # ===== Get mean HV in time range =====
    mean_HV = np.nan
    df_hv = read_hv(
        "hv",
        start_date=t_start.strftime("%Y-%m-%d"),
        end_date=t_end.strftime("%Y-%m-%d")
    )

    df_hv = df_hv.loc[(df_hv.index >= t_start) & (df_hv.index <= t_end)]
    if not df_hv.empty:
        cols_to_sum = [f"RPC{rpc}_readHV_1", f"RPC{rpc}_readHV_2"]
        mean_HV = (df_hv[cols_to_sum].sum(axis=1)).mean()

    # ===== Get Temperature, Humidity and Pressure in time range =====
    mean_Temp = np.nan
    mean_Hum = np.nan
    mean_Press = np.nan

    df_thp = read_thp(
        "thp",
        start_date=t_start.strftime("%Y-%m-%d"),
        end_date=t_end.strftime("%Y-%m-%d")
    )

    df_thp = df_thp.loc[(df_thp.index >= t_start) & (df_thp.index <= t_end)]

    def no_outliers(row, min_val, max_val):
        values = row.values.astype(float)
        filtered = [v for v in values if min_val <= v <= max_val]
        return np.mean(filtered)

    if not df_thp.empty:
        cols_T = ["T1", "T2", "T3", "T4"]
        row_T_means = df_thp[cols_T].apply(no_outliers, axis=1, min_val=10, max_val=50)
        mean_Temp = row_T_means.mean(skipna=True)

        cols_H = ["h1", "h2"]
        mean_H_rows = df_thp[cols_H].apply(no_outliers, axis=1, min_val=0, max_val=100)
        mean_Hum = mean_H_rows.mean(skipna=True)

        cols_P = ["p1", "p2"]
        mean_P_rows = df_thp[cols_P].apply(no_outliers, axis=1, min_val=400, max_val=1200)
        mean_Press = mean_P_rows.mean(skipna=True)

    # Collect results
    results = {
        f"time_start": t_start,
        f"time_end": t_end,
        f'efficiency': efficiency,
        f'efficiency_error': efficiency_error,
        f'Qmean': Qmean,
        f'Qmean_error': err_Qmean,
        f'Qmedian': Qmedian,
        f'Qmedian_error': err_Qmedian,
        f'Qmean_noST': Qmean_noST,
        f'Qmean_noST_error': err_Qmean_noST,
        f'Qmedian_noST': Qmedian_noST,
        f'Qmedian_noST_error': err_Qmedian_noST,
        f'streamer_fraction': ST,
        f'streamer_fraction_error': err_ST,
        f'mean_HV': mean_HV,
        f'mean_Temp': mean_Temp,
        f'mean_Hum': mean_Hum,
        f'mean_Press': mean_Press
    }

    if verbose:
        print(f"RPC{rpc} results:")
        print(f"  Time range: {t_start} -> {t_end}")
        print(f"  Efficiency: {efficiency:.4f} ± {efficiency_error:.4f}")
        print(f"  Qmean: {Qmean:.2f} ± {err_Qmean:.2f}")
        print(f"  Qmean noST: {Qmean_noST:.2f} ± {err_Qmean_noST:.2f}")
        print(f"  Qmedian: {Qmedian:.2f} ± {err_Qmedian:.2f}")
        print(f"  Qmedian noST: {Qmedian_noST:.2f} ± {err_Qmedian_noST:.2f}")
        print(f"  Streamer fraction: {ST:.2f}% ± {err_ST:.2f}%")
        print(f"  Mean HV in range: {mean_HV:.2f}" if not np.isnan(mean_HV) else "  Mean HV: No data")

    # Return as DataFrame
    return pd.DataFrame([results])


####################################3



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

    # Load configs
    general_config = load_general_config("lookUpTable_general.txt")
    vprop   = general_config["general"]["vprop"]
    pitch   = general_config["general"]["pitch"]
    strips  = general_config["general"]["strips"]
    strTh   = general_config["general"]["streamer_threshold"]
    XRange  = general_config["ranges"]["XRange"]
    YRange  = general_config["ranges"]["YRange"]

    rpc_params = load_rpc_parameters(f"lookUpTable_RPC{rpc}.txt")
    YCenters = rpc_params["ycenters"]

    # Extract columns

    Yraw = data[f"Yraw_RPC{rpc}"].to_numpy()
    Xraw = data[f"Xraw_RPC{rpc}"].to_numpy()
    Q    = data[f"Q_RPC{rpc}"].to_numpy()
    T    = data[f"T_RPC{rpc}"].to_numpy()
    ebtime = data[f"EBtime_RPC{rpc}"].to_numpy()


    # Calibrate Y: subtract Y-centers depending on which strip fired
    Ycal = Yraw.copy()
    for i in range(strips):
        mask = (Xraw == i+1)
        Ycal[mask] = Yraw[mask] - YCenters[i]

    # Calculate X, Y in mm
    Xmm = ((Xraw - 0.5) * pitch) + ((np.random.rand(len(Xraw)) * pitch) - (pitch / 2))
    Ymm = Ycal * vprop

    # Threshold level for streamer plots
    STLevel = strTh

    # 2D histogram-like plots
    XY, XY_Qmean, XY_Qmedian, XY_ST = strips2Dplots(Xmm, Ymm, Q, XRange, YRange, STLevel)

    df = pd.DataFrame({ 
        f"Xmm_RPC{rpc}" : Xmm, 
        f"Ymm_RPC{rpc}" : Ymm, 
        f"Q_RPC{rpc}" : Q, 
        f"T_RPC{rpc}" : T, 
        f"EBtime_RPC{rpc}" : ebtime

    })


    XY_data = {
        f"XY_RPC{rpc}": XY,
        f"XY_Qmean_RPC{rpc}": XY_Qmean,
        f"XY_Qmedian_RPC{rpc}": XY_Qmedian,
        f"XY_ST_RPC{rpc}": XY_ST
    }

    return df, XY_data


