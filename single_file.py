import os
from filters import at_least_two_rpcs_and_one_scint, trigger_filter_scint

from read_data import read_data
import plots
from load_lookUpTable import load_rpc_parameters, load_general_config
from apply_filters import apply_rpc_offsets
import numpy as np
from filters import filter_rpc, find_Qmax_strips
from calculate_parameters import calculate_parameters, calculate_Q_T, calculate_XY
from calculate_parameters import generate_XY_maps, calculate_XY_positions
from filters import at_least_two_rpcs_fired, filter_rpc
from save import save_rpc_results
from readXY import load_rpc_results

import pandas as pd
import numpy as np

def single_file(file_path, first_file_name):
    data = read_data(file_path, verbose=0)
    if data is None:
        print("Failed to read data.")
    rawcounts=len(data)
   # plots. plot_hist_Q(data, detector=4, verbose=False)
    # print(data.head())
    # print(data.columns)
    #print(data.dtypes)


    filtered_data = at_least_two_rpcs_fired(data)
    #filtered_data = at_least_two_rpcs_and_one_scint(data)
    print(f"Events after 2 or more RPCs fired filter: {len(filtered_data)}/{rawcounts}")

    
    
    # raw_events = len(data)
    # df = data

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
        # plots.plot_hist_Q(de_rpc, detector=rpc, verbose=False)

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
        
        #save_rpc_results(rpc, run_parameters, final_data, output_dir="results")
        save_rpc_results(
            rpc=rpc,
            run_parameters=run_parameters,
            final_data=final_data,
            file_path=file_path,
            output_dir="6000V_results",
            max_rows=10000
        )
        # Optional: store or process de_rpc further
        rpc_dfs[rpc - 1] = de_rpc  # update with filtered version



    return 0




# rpc=4
# runs, final_data = load_rpc_results(rpc)
# print("Number of runs:", len(runs))
# print("First run parameters:", runs[0])
# # print("Final data (first 5 rows):")
# # print(final_data.head())

# input_files = [
#     "/home/lidka/SWGO/4RPC/sest25287163557.mat",
#    "/home/lidka/SWGO/4RPC/sest25287163815.mat",
#    "/home/lidka/SWGO/4RPC/sest25287164033.mat",
#    "/home/lidka/SWGO/4RPC/sest25287164250.mat"
# ]
import os
import glob

input_dir = "/home/lidka/SWGO/6000V"

# Find all .mat files in the folder, sorted by name
input_files = sorted(glob.glob(os.path.join(input_dir, "*.mat")))

rpc = 1
first_file_name = input_files[0]
for file_path in input_files:
    n = single_file(file_path, first_file_name)

# general_config = load_general_config("lookUpTable_general.txt")
# XRange = general_config["ranges"]["XRange"]
# YRange = general_config["ranges"]["YRange"]

# XY_data = generate_XY_maps(final_data, rpc)

#final_data, XY_data = calculate_XY(de_rpc, rpc)

# plots. plot_heatmap(XY_data[f"XY_RPC{rpc}"], XRange, YRange, rpc, "XY Hits")
# plots. plot_heatmap(XY_data[f"XY_Qmean_RPC{rpc}"], XRange, YRange, rpc, "XY Q Mean")
# plots. plot_heatmap(XY_data[f"XY_Qmedian_RPC{rpc}"], XRange, YRange, rpc, "XY Q Median")
# plots. plot_heatmap(XY_data[f"XY_ST_RPC{rpc}"], XRange, YRange, rpc, "XY Streamer Threshold")

#file_path = "/home/lidka/SWGO/4RPC/sest25287163557.mat"
#file_path = "/home/lidka/SWGO/4RPC/sest25287163815.mat"
#file_path = "/home/lidka/SWGO/4RPC/sest25287164033.mat"
#file_path = "/home/lidka/SWGO/4RPC/sest25287164250.mat"
#n = single_file(file_path)
#print(n)

# Index(['EBtime', 'triggerType', 'QF_RPC1', 'QB_RPC1', 'TF_RPC1', 'TB_RPC1',
#        'QF_RPC2', 'QB_RPC2', 'TF_RPC2', 'TB_RPC2', 'QF_RPC3', 'QB_RPC3',
#        'TF_RPC3', 'TB_RPC3', 'QF_scint', 'TF_scint', 'QF_crew', 'TF_crew'],