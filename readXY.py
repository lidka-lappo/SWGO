import os
import pandas as pd
import numpy as np
from load_lookUpTable import load_general_config
import plots
from calculate_parameters import generate_XY_maps

def load_rpc_results(rpc, timestamp, dir):
    """
    Load the run parameters and final data for one RPC.
    Handles multiple appended runs.
    Returns:
        run_parameters_list: list of dicts, one per run
        final_data: pandas DataFrame
    """
    run_param_file = os.path.join(dir, f"run_parameters_RPC{rpc}_{timestamp}.txt")
    final_data_file = os.path.join(dir, f"final_data_RPC{rpc}_{timestamp}.txt")

    run_parameters_list = []

    # --- Load run parameters ---
    if os.path.exists(run_param_file):
        with open(run_param_file, 'r') as f:
            content = f.read().strip()

        # Split different runs if multiple blocks exist
        blocks = [block.strip() for block in content.split("=== New Run ===") if block.strip()]
        for block in blocks:
            run_params = {}
            for line in block.splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    run_params[key.strip()] = val.strip()
            run_parameters_list.append(run_params)
    else:
        print(f"Warning: {run_param_file} not found.")
        run_parameters_list = []

    # --- Load final data ---
    if os.path.exists(final_data_file):
        try:
            final_data = pd.read_csv(final_data_file, sep='\t')
        except Exception as e:
            print(f"Could not load as DataFrame: {e}")
            final_data = None
    else:
        print(f"Warning: {final_data_file} not found.")
        final_data = None

    return run_parameters_list, final_data




folder = "6000V_results"
files = [
    "25296110150",
]



rpc=4
runs, final_data = load_rpc_results(rpc, files[0], folder)
# print("Number of runs:", len(runs))
# print("First run parameters:", runs[0])
# print("Final data (first 5 rows):")
# print(final_data.head())


efficiencies = []

for run in runs:
    eff_str = run.get('efficiency', None)
    if eff_str:
        # Extract numeric value
        # The format seems like: '0    0.274'
        try:
            eff_value = float(eff_str.split()[1])
            efficiencies.append(eff_value)
        except Exception as e:
            print(f"Could not parse efficiency: {eff_str}, {e}")

# Calculate mean
if efficiencies:
    mean_efficiency = np.mean(efficiencies)
    print("Mean efficiency:", mean_efficiency)
else:
    print("No efficiencies found")

general_config = load_general_config("lookUpTable_general.txt")
XRange = general_config["ranges"]["XRange"]
YRange = general_config["ranges"]["YRange"]

XY_data = generate_XY_maps(final_data, rpc)


plots. plot_heatmap(XY_data[f"XY_RPC{rpc}"], XRange, YRange, rpc, "XY Hits")
plots. plot_heatmap(XY_data[f"XY_Qmean_RPC{rpc}"], XRange, YRange, rpc, "XY Q Mean")
plots. plot_heatmap(XY_data[f"XY_Qmedian_RPC{rpc}"], XRange, YRange, rpc, "XY Q Median")
plots. plot_heatmap(XY_data[f"XY_ST_RPC{rpc}"], XRange, YRange, rpc, "XY Streamer Threshold")