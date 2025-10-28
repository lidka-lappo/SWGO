import ast
from filters import at_least_two_rpcs_and_one_scint
from read_data import read_data
from save import save_pipeline
from load_lookUpTable import load_rpc_parameters
from load_lookUpTable import load_general_config
from filters import apply_rpc_offsets
from filters import filter_rpc, find_Qmax_strips
from calculate_parameters import calculate_parameters, calculate_Q_T, calculate_XY
from calculate_parameters import generate_XY_maps, calculate_XY_positions
from save import save_rpc_results, save_final_results, save_run_parameters
import numpy as np
import pandas as pd

def bronze_pipe(file_path, first_file_name):
    data = read_data(file_path, verbose=0)
    if data is None:
        print("Failed to read data.")

    rawcounts=len(data)
    filtered_data = at_least_two_rpcs_and_one_scint(data)
    print(f"Events after 2 or more RPCs fired filter: {len(filtered_data)}/{rawcounts}")
    return filtered_data
import pandas as pd
import numpy as np
import os
import ast
import re


def silver_pipe(file_path, first_file_name):
    # --- Load data ---
    try:
        df = pd.read_csv(file_path, sep='\t')
    except Exception as e:
        print(f"❌ Failed to read {file_path}: {e}")
        return None
    
    if df.empty:
        print("❌ Input file is empty.")
        return None

    # Columns that contain arrays
    array_cols = [col for col in df.columns if "RPC" in col or "scint" in col or "crew" in col]

    def parse_space_array(s):
        if pd.isna(s) or s.strip() == "":
            return np.array([])
        s = s.strip()[1:-1]  # remove brackets
        nums = [float(x) for x in re.split(r'\s+', s) if x]
        return np.array(nums)

    for col in array_cols:
        df[col] = df[col].apply(parse_space_array)

    raw_events = len(df)
    print(f"Loaded {raw_events} raw events from {file_path}")

    # --- Base columns and per-RPC split ---
    base_cols = ['EBtime', 'triggerType']
    rpc_dfs = []
    for i in range(1, 5):
        cols = base_cols + [col for col in df.columns if f'_RPC{i}' in col]
        rpc_dfs.append(df[cols].copy())

    # --- Load global configs ---
    general_config = load_general_config("lookUpTable_general.txt")
    XRange = general_config["ranges"]["XRange"]
    YRange = general_config["ranges"]["YRange"]

    processed_rpcs = []

    # --- Process each RPC ---
    for rpc in range(1, 5):
        print(f"\n=== Processing RPC{rpc} ===")
        de_rpc = rpc_dfs[rpc - 1].copy()

        rpc_params = load_rpc_parameters(f"lookUpTable_RPC{rpc}.txt")
        apply_rpc_offsets(de_rpc, rpc_params, rpc)

        # --- Filter 1 ---
        mask1 = filter_rpc(de_rpc, rpc)
        print(f"Filter 1 passed: {np.sum(mask1)} / {len(mask1)}")
        de_rpc = de_rpc[mask1].copy()

        # --- Filter 2 (Qmax) ---
        de_rpc_max, mask2 = find_Qmax_strips(de_rpc, rpc)
        print(f"Filter 2 passed: {np.sum(mask2)} / {len(mask2)}")

        de_rpc = pd.concat([de_rpc, de_rpc_max], axis=1)
        de_rpc = de_rpc[mask2].copy()

        # --- Compute Q-T and positions ---
        de_rpc = calculate_Q_T(de_rpc, rpc)
        run_parameters = calculate_parameters(de_rpc, raw_events, rpc, verbose=0)
        final_data = calculate_XY_positions(de_rpc, rpc)
        XY_data = generate_XY_maps(final_data, rpc)

        # --- Save RPC-specific results ---
        save_final_results(rpc, final_data, file_path, output_dir="silver")
        save_run_parameters(rpc, run_parameters, file_path, output_dir="silver")

        processed_rpcs.append(final_data)
        rpc_dfs[rpc - 1] = de_rpc 

    # --- Combine all RPCs if needed ---
    combined_data = pd.concat(processed_rpcs, axis=0, ignore_index=True)
    return combined_data


# def silver_pipe(file_path, first_file_name):
#     df= pd.read_csv(file_path, sep='\t')
#     if df is None:
#         print("Failed to read data.")
#     raw_events = len(df)
 
#     # Define the common columns to keep
#     base_cols = ['EBtime', 'triggerType']

#     # Create one DataFrame per RPC detector
#     df_rpc1 = df[base_cols + [col for col in df.columns if '_RPC1' in col]]
#     df_rpc2 = df[base_cols + [col for col in df.columns if '_RPC2' in col]]
#     df_rpc3 = df[base_cols + [col for col in df.columns if '_RPC3' in col]]
#     df_rpc4 = df[base_cols + [col for col in df.columns if '_RPC4' in col]]

#     n_of_rpcs = 4
#     rpc_dfs = [df_rpc1, df_rpc2, df_rpc3, df_rpc4]
    

#     general_config = load_general_config("lookUpTable_general.txt")
#     XRange = general_config["ranges"]["XRange"]
#     YRange = general_config["ranges"]["YRange"]


#     for rpc in range(1, n_of_rpcs + 1):   
#         print(f"\n=== Processing RPC{rpc} ===")

#         de_rpc = rpc_dfs[rpc - 1].copy()
#         rpc_params = load_rpc_parameters(f"lookUpTable_RPC{rpc}.txt")
#         apply_rpc_offsets(de_rpc, rpc_params, rpc)

#         # --- Apply your filter on de_rpc (not the whole data) ---
#         mask1 = filter_rpc(de_rpc, rpc)

#         print(f"\n=== FILTER 1 (both ends) ===")
#         print(f"Events passing RPC{rpc} filter: {np.sum(mask1)} / {len(mask1)}")

#         # Apply the mask only to de_rpc
#         de_rpc = de_rpc[mask1]

#         # filt 2 - find Qmax strips
#         de_rpc_max, mask2 = find_Qmax_strips(de_rpc, rpc)     
#         print(f"\n=== FILTER 2 (found Qmax) ===")
#         print(f"After finding Qmax strips: {np.sum(mask2)} / {len(mask2)}")

#         de_rpc = pd.concat([de_rpc, de_rpc_max], axis=1)
#         de_rpc = de_rpc[mask2]


#         de_rpc = calculate_Q_T(de_rpc, rpc)

#         run_parameters = calculate_parameters(de_rpc, raw_events, rpc, verbose=0)

#         final_data = calculate_XY_positions(de_rpc, rpc)
#         XY_data = generate_XY_maps(final_data, rpc)

       
#         save_rpc_results(
#             rpc=rpc,
#             run_parameters=run_parameters,
#             final_data=final_data,
#             file_path=file_path,
#             output_dir="6000V_results",
#             max_rows=10000
#         )
#         # Optional: store or process de_rpc further
#         rpc_dfs[rpc - 1] = de_rpc  # update with filtered version


import os
import glob
input_dir = "/home/lidka/SWGO/6000V"

# Find all .mat files in the folder, sorted by name
input_files = sorted(glob.glob(os.path.join(input_dir, "*.mat")))

rpc = 1
first_file_name = input_files[0]
# for file_path in input_files:
#     bronze_data = bronze_pipe(file_path, first_file_name)
#     bronze_file_path = save_pipeline(bronze_data, file_path,  output_dir="bronze", max_rows=10000)

#print(f"Saved bronze data to {bronze_file_path}")
bronze_file_path = "bronze/bronze_25296110150.txt"
#bronze_readback = pd.read_csv(bronze_file_path, sep='\t')
silver_data = silver_pipe(bronze_file_path, first_file_name)
print(silver_data.tail())

#print(f"Read {len(bronze_readback)} rows from {bronze_file_path}")


