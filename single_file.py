import os
from filters import trigger_filter_scint

from read_data import read_data
import plots
from load_lookUpTable import load_rpc_parameters, load_general_config
from apply_filters import apply_rpc_offsets
import numpy as np
from filters import filter_rpc, find_Qmax_strips
from calculate_parameters import calculate_parameters, calculate_Q_T, calculate_XY
from calculate_parameters import generate_XY_maps, calculate_XY_positions
import pandas as pd
import os

import numpy as np
import pandas as pd

def rpc_fired(TF, TB):
    if TF is None or TB is None:
        return False
    return (TF != 0).any() and (TB != 0).any()



def at_least_two_rpcs_fired(rpc_data):
    def rpc_fired(TF, TB):
        if TF is None or TB is None:
            return False
        return (TF != 0).any() and (TB != 0).any()

    fired_counts = []
    for i in range(1, 5):  # RPC1 to RPC4
        fired = rpc_data.apply(
            lambda row: rpc_fired(row[f'TF_RPC{i}'], row[f'TB_RPC{i}']), axis=1
        )
        fired_counts.append(fired)

    # Combine all RPC fired results into one DataFrame
    fired_df = pd.concat(fired_counts, axis=1)
    fired_df.columns = [f'RPC{i}_fired' for i in range(1, 5)]

    # Count how many RPCs fired per row
    rpc_data['num_rpc_fired'] = fired_df.sum(axis=1)

    # Keep only rows with at least 2 RPCs fired
    filtered = rpc_data[rpc_data['num_rpc_fired'] >= 2].copy()
        

    return filtered


import os
import numpy as np
import pandas as pd

def save_rpc_results(rpc, run_parameters, final_data, output_dir="results"):
    """
    Save the run parameters and final data for one RPC to .txt files.
    If the final_data file already exists, new results are appended.
    """
    os.makedirs(output_dir, exist_ok=True)

    # --- Save run parameters ---
    run_param_file = os.path.join(output_dir, f"run_parameters_RPC{rpc}.txt")
    with open(run_param_file, 'a') as f:  # append mode
        f.write("=== New Run ===\n")
        for key, val in run_parameters.items():
            f.write(f"{key}: {val}\n")
        f.write("\n")
    print(f"Appended run parameters to {run_param_file}")

    # --- Save or append final data ---
    final_data_file = os.path.join(output_dir, f"final_data_RPC{rpc}.txt")

    if isinstance(final_data, pd.DataFrame):
        # Append without headers if file exists
        header = not os.path.exists(final_data_file)
        final_data.to_csv(final_data_file, sep='\t', index=False, mode='a', header=header)
    else:
        # Convert to numpy array and append
        with open(final_data_file, 'a') as f:
            np.savetxt(f, np.array(final_data), fmt='%s', delimiter='\t')
    print(f"Appended final data to {final_data_file}")




def single_file(file_path):
    data = read_data(file_path, verbose=0)
    if data is None:
        print("Failed to read data.")
    rawcounts=len(data)
   # plots. plot_hist_Q(data, detector=4, verbose=False)
    # print(data.head())
    # print(data.columns)
    #print(data.dtypes)


    filtered_data = at_least_two_rpcs_fired(data)
    print(f"Events after 2 or more RPCs fired filter: {len(filtered_data)}/{rawcounts}")
    #plots. plot_hist_Q(filtered_data, detector=1, verbose=False)
    raw_events = len(filtered_data)
  
    df = filtered_data

    # Define the common columns to keep
    base_cols = ['EBtime', 'triggerType']

    # Create one DataFrame per RPC detector
    df_rpc1 = df[base_cols + [col for col in df.columns if '_RPC1' in col]]
    df_rpc2 = df[base_cols + [col for col in df.columns if '_RPC2' in col]]
    df_rpc3 = df[base_cols + [col for col in df.columns if '_RPC3' in col]]
    df_rpc4 = df[base_cols + [col for col in df.columns if '_RPC4' in col]]

    n_of_rpcs = 4
    rpc_dfs = [df_rpc1, df_rpc2, df_rpc3, df_rpc4]


    
    
    #plot_hist_Q(data, detector=1, verbose=False)

    general_config = load_general_config("lookUpTable_general.txt")
    XRange = general_config["ranges"]["XRange"]
    YRange = general_config["ranges"]["YRange"]


    for rpc in range(1, n_of_rpcs + 1):
        
        print(f"\n=== Processing RPC{rpc} ===")

        # Select only the corresponding DataFrame
        de_rpc = rpc_dfs[rpc - 1].copy()

        rpc_params = load_rpc_parameters(f"lookUpTable_RPC{rpc}.txt")
        apply_rpc_offsets(de_rpc, rpc_params, rpc)

        # --- Apply your filter on de_rpc (not the whole data) ---
        mask1 = filter_rpc(de_rpc, rpc)

        print(f"\n=== FILTER 1 (both ends) ===")
        print(f"Events passing RPC{rpc} filter: {np.sum(mask1)} / {len(mask1)}")

        # Apply the mask only to de_rpc
        de_rpc = de_rpc[mask1]
        #plots. plot_hist_Q(de_rpc, detector=rpc, verbose=False)

            # filt 2 - find Qmax strips
        de_rpc_max, mask2 = find_Qmax_strips(de_rpc, rpc)     
        print(f"\n=== FILTER 2 (found Qmax) ===")
        print(f"After finding Qmax strips: {np.sum(mask2)} / {len(mask2)}")

        de_rpc = pd.concat([de_rpc, de_rpc_max], axis=1)
        de_rpc = de_rpc[mask2]

        #print(de_rpc.head())

        # results
        
        de_rpc = calculate_Q_T(de_rpc, rpc)
        #print(de_rpc.head())
        run_parameters = calculate_parameters(de_rpc, raw_events, rpc, verbose=0)

        final_data = calculate_XY_positions(de_rpc, rpc)
        XY_data = generate_XY_maps(final_data, rpc)

        #final_data, XY_data = calculate_XY(de_rpc, rpc)

        # plots. plot_heatmap(XY_data[f"XY_RPC{rpc}"], XRange, YRange, rpc, "XY Hits")
        # plots. plot_heatmap(XY_data[f"XY_Qmean_RPC{rpc}"], XRange, YRange, rpc, "XY Q Mean")
        # plots. plot_heatmap(XY_data[f"XY_Qmedian_RPC{rpc}"], XRange, YRange, rpc, "XY Q Median")
        # plots. plot_heatmap(XY_data[f"XY_ST_RPC{rpc}"], XRange, YRange, rpc, "XY Streamer Threshold")   
        
        save_rpc_results(rpc, run_parameters, final_data, output_dir="results")
        # Optional: store or process de_rpc further
        rpc_dfs[rpc - 1] = de_rpc  # update with filtered version



    return 0

import os
import pandas as pd

def load_rpc_results(rpc, output_dir="results"):
    """
    Load the run parameters and final data for one RPC.
    Handles multiple appended runs.
    Returns:
        run_parameters_list: list of dicts, one per run
        final_data: pandas DataFrame
    """
    run_param_file = os.path.join(output_dir, f"run_parameters_RPC{rpc}.txt")
    final_data_file = os.path.join(output_dir, f"final_data_RPC{rpc}.txt")

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


rpc=4
runs, final_data = load_rpc_results(rpc)
print("Number of runs:", len(runs))
print("First run parameters:", runs[0])
# print("Final data (first 5 rows):")
# print(final_data.head())


general_config = load_general_config("lookUpTable_general.txt")
XRange = general_config["ranges"]["XRange"]
YRange = general_config["ranges"]["YRange"]

XY_data = generate_XY_maps(final_data, rpc)

#final_data, XY_data = calculate_XY(de_rpc, rpc)

plots. plot_heatmap(XY_data[f"XY_RPC{rpc}"], XRange, YRange, rpc, "XY Hits")
plots. plot_heatmap(XY_data[f"XY_Qmean_RPC{rpc}"], XRange, YRange, rpc, "XY Q Mean")
plots. plot_heatmap(XY_data[f"XY_Qmedian_RPC{rpc}"], XRange, YRange, rpc, "XY Q Median")
plots. plot_heatmap(XY_data[f"XY_ST_RPC{rpc}"], XRange, YRange, rpc, "XY Streamer Threshold")

#file_path = "/home/lidka/SWGO/4RPC/sest25287163557.mat"
#file_path = "/home/lidka/SWGO/4RPC/sest25287163815.mat"
#file_path = "/home/lidka/SWGO/4RPC/sest25287164033.mat"
#file_path = "/home/lidka/SWGO/4RPC/sest25287164250.mat"
#n = single_file(file_path)
#print(n)

# Index(['EBtime', 'triggerType', 'QF_RPC1', 'QB_RPC1', 'TF_RPC1', 'TB_RPC1',
#        'QF_RPC2', 'QB_RPC2', 'TF_RPC2', 'TB_RPC2', 'QF_RPC3', 'QB_RPC3',
#        'TF_RPC3', 'TB_RPC3', 'QF_scint', 'TF_scint', 'QF_crew', 'TF_crew'],