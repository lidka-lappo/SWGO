import os
import pandas as pd
import numpy as np
from load_lookUpTable import load_general_config
import plots
from calculate_parameters import generate_XY_maps

import os
import pandas as pd

def load_run_parameters_csv(rpc, timestamp, dir):
    """
    Load run parameters CSV for one RPC.
    Returns a pandas DataFrame.
    """
    run_param_file = os.path.join(dir, f"run_parameters_RPC{rpc}_{timestamp}.csv")

    if not os.path.exists(run_param_file):
        print(f"Warning: {run_param_file} not found.")
        return pd.DataFrame()  # empty DF

    df = pd.read_csv(run_param_file)
    return df

def load_final_data(rpc, timestamp, dir):
    """
    Load the final data for one RPC.
    Returns:
        final_data: pandas DataFrame
    """
    final_data_file = os.path.join(dir, f"final_data_RPC{rpc}_{timestamp}.txt")
    final_data = None

    if os.path.exists(final_data_file):
        try:
            final_data = pd.read_csv(final_data_file, sep='\t')
        except Exception as e:
            print(f"Could not load final data as DataFrame: {e}")
    else:
        print(f"Warning: {final_data_file} not found.")

    return final_data



folder = "silver"
files = [
    "25296110150",
]
# folder = "6000V_results"
# files = [
#     "25296110150",
# ]




rpc = 4
runs_df = load_run_parameters_csv(rpc, files[0], folder)
final_data = load_final_data(rpc, files[0], folder)

print("Number of runs:", len(runs_df))

efficiency = runs_df['efficiency'].iloc[0]
efficiency_error = runs_df['efficiency_error'].iloc[0]

print("Efficiency:", efficiency)
print("Efficiency error:", efficiency_error)



general_config = load_general_config("lookUpTable_general.txt")
XRange = general_config["ranges"]["XRange"]
YRange = general_config["ranges"]["YRange"]

XY_data = generate_XY_maps(final_data, rpc)


plots. plot_heatmap(XY_data[f"XY_RPC{rpc}"], XRange, YRange, rpc, "XY Hits")
plots. plot_heatmap(XY_data[f"XY_Qmean_RPC{rpc}"], XRange, YRange, rpc, "XY Q Mean")
plots. plot_heatmap(XY_data[f"XY_Qmedian_RPC{rpc}"], XRange, YRange, rpc, "XY Q Median")
plots. plot_heatmap(XY_data[f"XY_ST_RPC{rpc}"], XRange, YRange, rpc, "XY Streamer Threshold")