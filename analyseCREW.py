import ast
import shutil
from filters import apply_rpc_offsets_crew, at_least_two_rpcs_and_one_scint, at_least_two_rpcs_fired, fancy_trigger, filter_by_charge, filter_by_charge_crew, filter_by_time, filter_by_time_crew
from read_data import read_data
from save import save_pipeline
from load_lookUpTable import load_rpc_parameters
from load_lookUpTable import load_general_config
from filters import apply_rpc_offsets
from filters import filter_rpc, find_Qmax_strips
from calculate_parameters import calculate_parameters, calculate_Q_T, calculate_XY, calculate_parameters_crew
from calculate_parameters import generate_XY_maps, calculate_XY_positions
from save import save_rpc_results, save_final_results, save_run_parameters
from readXY import readXY, load_all_steps
import numpy as np
import pandas as pd
import plots

def bronze_pipe(file_path, triggerType):
    data = read_data(file_path, verbose=0)
    if data is None:
        print("Failed to read data.")
    rawcounts=len(data)
    filtered_data = fancy_trigger(data, triggerType=triggerType, include_general_rule=False)
    print(f"Events after bronze pipe: {len(filtered_data)}/{rawcounts}")
    


    # Count non-zero elements in QF_crew BEFORE filtering
    before_nonzero = data["QF_crew"].apply(lambda arr: np.count_nonzero(arr))
    total_before = before_nonzero.sum()

    # Count non-zero elements in QF_crew AFTER filtering
    after_nonzero = filtered_data["QF_crew"].apply(lambda arr: np.count_nonzero(arr))
    total_after = after_nonzero.sum()

    print("Non-zero QF_crew before filtering:", total_before)
    print("Non-zero QF_crew after filtering :", total_after)

    return filtered_data
import pandas as pd
import numpy as np
import os
import ast
import re

def parse_space_array(s):
    if pd.isna(s) or s.strip() == "":
        return np.array([])
    s = s.strip()[1:-1]  # remove brackets
    nums = [float(x) for x in re.split(r'\s+', s) if x]
    return np.array(nums)


def silver_pipe(input_dir, output_dir, triggerType,file_path=None):

    full_input_dir = os.path.join(input_dir, f"bronze{triggerType}")
        # If file_path not provided, auto-find one in input_dir
    if file_path is None:
        bronze_files = sorted(
            glob.glob(os.path.join(full_input_dir, "bronze_*")),
            key=os.path.getmtime,  # sort by modification time
            reverse=True            # most recent first
        )
        if not bronze_files:
            raise FileNotFoundError(f"No file starting with 'bronze_' found in {full_input_dir}")
        file_path = bronze_files[0]
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

    for col in array_cols:
        df[col] = df[col].apply(parse_space_array)

    raw_events = len(df)
    print(f"Loaded {raw_events} raw events from {file_path}")

        # --- Load global configs ---
    general_config = load_general_config("lookUpTable_general.txt")
    XRange = general_config["ranges"]["XRange"]
    YRange = general_config["ranges"]["YRange"]

    # --- Base columns and per-RPC split ---
    base_cols = ['EBtime', 'triggerType']
    rpc_dfs = []
    for i in range(1, 5):
        cols = base_cols + [col for col in df.columns if f'_RPC{i}' in col]
        rpc_dfs.append(df[cols].copy())



    processed_rpcs = []

    # --- Process each RPC ---
    for rpc in range(1, 5):
        print(f"\n=== Processing RPC{rpc} ===")
        de_rpc = rpc_dfs[rpc - 1].copy()

        rpc_params = load_rpc_parameters(f"lookUpTable_RPC{rpc}.txt")
        apply_rpc_offsets(de_rpc, rpc_params, rpc)

        # --- Filter by charge ---
        mask_charge = filter_by_charge(de_rpc, rpc)
        print(f"Charge filter passed: {np.sum(mask_charge)} / {len(mask_charge)}")
        de_rpc = de_rpc[mask_charge].copy()

        #plots.plot_hist_Q(de_rpc, detector=rpc, verbose=False)


        # --- Filter by time ---
        mask_time = filter_by_time(de_rpc, rpc)
        print(f"Time filter passed: {np.sum(mask_time)} / {len(mask_time)}")
        de_rpc = de_rpc[mask_time].copy()




        # # # --- Filter 1 ---
        # mask1 = filter_rpc(de_rpc, rpc)
        # print(f"Filter 1 passed: {np.sum(mask1)} / {len(mask1)}")
        # de_rpc = de_rpc[mask1].copy()

        

        # --- Filter 3 (Qmax) ---
        de_rpc_max, mask2 = find_Qmax_strips(de_rpc, rpc)
        print(f"Filter 3 passed: {np.sum(mask2)} / {len(mask2)}")
        print(f"Efficiency of RPC{rpc}: {np.sum(mask2) / len(mask_charge)}")

        de_rpc = pd.concat([de_rpc, de_rpc_max], axis=1)
        de_rpc = de_rpc[mask2].copy()

        # --- Compute Q-T and positions ---
        if(len(de_rpc) == 0):
            print(f"No events left after filtering for RPC{rpc}. Skipping calculations.")
            continue
        de_rpc = calculate_Q_T(de_rpc, rpc)

        hv_folder = "/home/lidka/SWGO/SKAN3/HV"
        thp_folder = "/home/lidka/SWGO/SKAN3/THP"

        

        run_parameters = calculate_parameters(de_rpc, raw_events, rpc, hv_folder=hv_folder, thp_folder=thp_folder, verbose=0)

        final_data = calculate_XY_positions(de_rpc, rpc)
        XY_data = generate_XY_maps(final_data, rpc)

        # --- Save RPC-specific results ---
        save_final_results(rpc, final_data, file_path, input_dir, output_dir)
        save_run_parameters(rpc, run_parameters, file_path, input_dir, output_dir)

        processed_rpcs.append(final_data)
        rpc_dfs[rpc - 1] = de_rpc 

    # --- Combine all RPCs if needed ---
    combined_data = pd.concat(processed_rpcs, axis=0, ignore_index=True)
    return combined_data


def silver_pipe_crew(input_dir, output_dir, triggerType,file_path=None):

    full_input_dir = os.path.join(input_dir, f"bronze{triggerType}")
        # If file_path not provided, auto-find one in input_dir
    if file_path is None:
        bronze_files = sorted(
            glob.glob(os.path.join(full_input_dir, "bronze_*")),
            key=os.path.getmtime,  # sort by modification time
            reverse=True            # most recent first
        )
        if not bronze_files:
            raise FileNotFoundError(f"No file starting with 'bronze_' found in {full_input_dir}")
        file_path = bronze_files[0]
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

    for col in array_cols:
        df[col] = df[col].apply(parse_space_array)

    raw_events = len(df)
    print(f"Loaded {raw_events} raw events from {file_path}")

        # --- Load global configs ---
    general_config = load_general_config("lookUpTable_general.txt")



    # --- Base columns and per-RPC split ---
    base_cols = ['EBtime', "QF_crew", "TF_crew"]
    crew_df = df[base_cols].copy()

    # --- Process CREW ---

    print(f"\n=== Processing CREW ===")

    rpc_params = load_rpc_parameters(f"lookUpTable_CREW.txt")
    apply_rpc_offsets_crew(crew_df, rpc_params)

    ###### --- Filter by charge ---
    mask_charge = filter_by_charge_crew(crew_df)
    print(f"Charge filter passed: {np.sum(mask_charge)} / {len(mask_charge)}")
    crew_df = crew_df[mask_charge].copy()

    # plots.plot_hist_Q(crew_df, detector="crew", verbose=False)


    #####--- Filter by time ---
    mask_time = filter_by_time_crew(crew_df)
    print(f"Time filter passed: {np.sum(mask_time)} / {len(mask_time)}")
    crew_df = crew_df[mask_time].copy()

    # plots.plot_hist_Q(crew_df, detector="crew", verbose=False)



    # # --- Compute positions and final data ---

    hv_folder = "/home/lidka/SWGO/HV"
    thp_folder = "/home/lidka/SWGO/THP"

    run_parameters = calculate_parameters_crew(crew_df, raw_events, hv_folder, thp_folder, verbose=0)

    # # --- Save final data ---
    # # --- Save run parameters ---
    save_run_parameters(run_parameters, file_path, input_dir, rpc="crew", output_dir= output_dir)
    return crew_df





from pathlib import Path
import os
import glob
base_folder = Path("/home/lidka/SWGO/SKANcrew2") # change this to your main folder path
input_dir = base_folder / "STEP1"

# Find all .mat files in the folder, sorted by name
input_files = sorted(glob.glob(os.path.join(input_dir, "*.mat")))
triggerType = "Trigger4RPC"

for file_path in input_files:
    bronze_data = bronze_pipe(file_path, triggerType)
    bronze_file_path = save_pipeline(bronze_data, file_path, input_dir, output_dir=f"bronze{triggerType}", max_rows=10000)
    done_dir = os.path.join(input_dir, "done")
    os.makedirs(done_dir, exist_ok=True)  # create folder if it doesn't exist

    # Construct destination path
    dest_path = os.path.join(done_dir, os.path.basename(file_path))
    
    # Move the file
    shutil.move(file_path, dest_path)
    
    print(f"Moved {file_path} → {dest_path}")


silver_data = silver_pipe_crew(input_dir, output_dir=f"{input_dir}/silver{triggerType}", triggerType=triggerType)
base_folder = "/home/lidka/SWGO/SKANcrew2"  # change this to your main folder path
df = load_all_steps(base_folder, triggerType)

plots.plot_efficiency_vs_voltage(df)
plots.plot_streamer_fraction_vs_voltage(df)
plots.plot_meanQ_vs_voltage(df)
plots.plot_medianQ_vs_voltage(df)

plots.plot_efficiency_vs_reduced_field(df)
plots.plot_streamer_vs_reduced_field(df)
plots.plot_Qmean_vs_reduced_field(df)
plots.plot_Qmedian_vs_reduced_field(df)



# df1 = load_all_steps("/home/lidka/SWGO/SKAN3", "TriggerDOWN")
# df2= load_all_steps("/home/lidka/SWGO/SKAN2", "TriggerUP")
# df3= load_all_steps("/home/lidka/SWGO/SKAN4", "TriggerUP")
# df4= load_all_steps("/home/lidka/SWGO/SKANcrew2", "Trigger4RPC")

# df1_sel = df1[df1["rpc"].isin([1, 2])]
# df2_sel = df2[df2["rpc"].isin([4])]
# df3_sel = df3[df3["rpc"].isin([3])]
# df4_sel = df4[df4["rpc"].isin(["crew"])]

# # # # Combine them
# df_combined = pd.concat([df1_sel, df2_sel, df3_sel, df4_sel], ignore_index=True)
# df_combined["rpc"] = df_combined["rpc"].astype(str)


# Plot using the combined filtered data

# plots.plot_efficiency_vs_voltage(df_combined)
# plots.plot_streamer_fraction_vs_voltage(df_combined)
# plots.plot_meanQ_vs_voltage(df_combined)
# plots.plot_medianQ_vs_voltage(df_combined)

# plots.plot_efficiency_vs_reduced_field(df_combined)
# plots.plot_streamer_vs_reduced_field(df_combined)
# plots.plot_Qmean_vs_reduced_field(df_combined)
# plots.plot_Qmedian_vs_reduced_field(df_combined)



# print(silver_data.head())
# plots.plot_hist_Q(silver_data, detector="crew", verbose=False)
# plots.plot_hist_T(silver_data, detector="crew", verbose=False)

# file_path = "/home/lidka/SWGO/SKANcrew2/STEP3/bronzeTrigger4RPC/bronze_25321111049.txt"
# bronze_data = pd.read_csv(file_path, sep='\t')

# # Columns that contain arrays
# array_cols = [col for col in bronze_data.columns if "RPC" in col or "scint" in col or "crew" in col]

# for col in array_cols:
#     bronze_data[col] = bronze_data[col].apply(parse_space_array)
# #print(bronze_data.head())
# plots.plot_hist_Q(bronze_data, detector="crew", verbose=False)






