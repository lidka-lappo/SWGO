import os
import re
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




    # folder = "4RPC/silverTriggerScint"
    # files = [
    #     "25296110150",
    # ]
    # folder = "6000V_results"
    # files = [
    #     "25296110150",
    # ]



    # --- Configuration ---
    #folder = "6000V/silverTriggerUP"
    #folder = "6000V/silverTriggerDOWN"


def readXY(folder):


    # Automatically find all timestamps present in filenames
    timestamps = sorted({
        f.split("_")[-1].split(".")[0]
        for f in os.listdir(folder)
        if "run_parameters_RPC" in f
    })

    general_config = load_general_config("lookUpTable_general.txt")
    XRange = general_config["ranges"]["XRange"]
    YRange = general_config["ranges"]["YRange"]

    # --- Loop through all timestamps and RPCs ---
    for timestamp in timestamps:
        print(f"\n--- Timestamp: {timestamp} ---")

        for rpc in range(1, 5):
            print(f"\n=== RPC{rpc} ===")

            try:
                runs_df = load_run_parameters_csv(rpc, timestamp, folder)
                final_data = load_final_data(rpc, timestamp, folder)
            except Exception as e:
                print(f"⚠️ Could not load RPC{rpc}: {e}")
                continue

            if runs_df.empty:
                print(f"⚠️ No run parameters found for RPC{rpc}.")
                continue

            # --- Read efficiency values ---
            efficiency = runs_df.get('efficiency', pd.Series([None])).iloc[0]
            efficiency_error = runs_df.get('efficiency_error', pd.Series([None])).iloc[0]

            print(f"Number of runs: {len(runs_df)}")
            print(f"Efficiency: {efficiency}")
            print(f"Efficiency error: {efficiency_error}")
            # # --- Generate XY maps ---
            XY_data = generate_XY_maps(final_data, rpc)

            # # --- Plot heatmaps ---
            plots.plot_heatmap(XY_data.get(f"XY_RPC{rpc}"), XRange, YRange, rpc, "XY Hits")
            # plots.plot_heatmap(XY_data.get(f"XY_Qmean_RPC{rpc}"), XRange, YRange, rpc, "XY Q Mean")
            # plots.plot_heatmap(XY_data.get(f"XY_Qmedian_RPC{rpc}"), XRange, YRange, rpc, "XY Q Median")
            # plots.plot_heatmap(XY_data.get(f"XY_ST_RPC{rpc}"), XRange, YRange, rpc, "XY Streamer Threshold")
import os
import re
import pandas as pd

def load_all_steps(base_folder, triggerType):
    """
    Loads all CSVs from each STEP*/silverTriggerDOWN/ folder that start with 'run'.
    Uses time_start and time_end columns from each file instead of filename timestamps.
    Returns a single combined DataFrame.
    """
    hv_map = {
        "STEP1": 11500,
        "STEP2": 11300,
        "STEP3": 11100,
        "STEP4": 11000,
        "STEP5": 10800,
        "STEP6": 10600,
        "STEP7": 10400,
        "STEP8": 10200,
    }

    all_data = []
    pattern = re.compile(r"run_parameters_RPC(\d+|crew)_.*\.csv")

    for step_folder in sorted(os.listdir(base_folder)):
        step_path = os.path.join(base_folder, step_folder)
        if not os.path.isdir(step_path):
            continue

        silver_path = os.path.join(step_path, f"silver{triggerType}")
        if not os.path.isdir(silver_path):
            print(f"⚠️ No silver{triggerType} folder in {step_folder}, skipping.")
            continue

        print(f"\n📂 Processing {step_folder}/silver{triggerType} ...")

        for file in os.listdir(silver_path):
            if not file.startswith("run") or not file.endswith(".csv"):
                continue

            match = pattern.match(file)
            if not match:
                print(f"⚠️ Skipped unexpected file name: {file}")
                continue

            rpc_value = match.group(1)

            # Only process files where RPC is a number
            if rpc_value.isdigit():
                rpc = int(rpc_value)
            else:
                rpc = "crew"
            file_path = os.path.join(silver_path, file)

            try:
                df = pd.read_csv(file_path)
            except Exception as e:
                print(f"⚠️ Could not read {file}: {e}")
                continue

            if df.empty:
                continue

            # --- Validate required columns ---
            expected_cols = {"time_start", "time_end", "efficiency"}
            if not expected_cols.issubset(df.columns):
                print(f"⚠️ Missing expected columns in {file}, skipping.")
                continue

            # --- Convert time columns ---
            df["time_start"] = pd.to_datetime(df["time_start"], errors="coerce", utc=True)
            df["time_end"] = pd.to_datetime(df["time_end"], errors="coerce", utc=True)

            # Drop rows with invalid timestamps
            df = df.dropna(subset=["time_start", "time_end"])

            # Compute a single representative time (e.g., midpoint)
            df["timestamp"] = df["time_start"] + (df["time_end"] - df["time_start"]) / 2

            # Add metadata
            df["rpc"] = rpc
            df["step"] = step_folder

             # --- Apply meanHV override for RPC4 ---
            if rpc == 4 and step_folder in hv_map:
                df["mean_HV"] = hv_map[step_folder]
                #df["mean_HV"] = 11100
                print(f"⚙️ meanHV for RPC4 in {step_folder} set to {hv_map[step_folder]}")


            all_data.append(df)

    if not all_data:
        print(f"❌ No valid data found in any silver{triggerType} folder.")
        return pd.DataFrame()

    # --- Combine all steps ---
    combined = pd.concat(all_data, ignore_index=True)
    print("Total number of entries:", len(combined))


    # --- Sort by time ---
    combined = combined.sort_values("timestamp")

    print(f"\n✅ Loaded total rows: {len(combined)}")
    # print(combined[["step", "rpc", "efficiency", "mean_HV"]])

    # Optional: plot if desired
    try:
        print("plot")
        #plots.plot_efficiency_vs_time(combined, "RPC Efficiency vs Time")
        #plots.plot_efficiency_vs_voltage(combined, title="Efficiency vs Voltage")


        # plots.plot_streamer_fraction_vs_voltage(combined, rpc_list=[1, 2])
        # plots.plot_efficiency_vs_voltage(combined, rpc_list=[1, 2])


        # # plots.plot_medianQ_vs_voltage(combined, rpc_list=[1, 2])
        # # plots.plot_medianQ_vs_voltage(combined, rpc_list=[1, 2])



        # # plots.plot_streamer_fraction_vs_voltage(combined, rpc_list=[3, 4])
        #plots.plot_efficiency_vs_voltage(combined, rpc_list=[3])


        # # # plots.plot_medianQ_vs_voltage(combined, rpc_list=[3, 4])
        # # # plots.plot_medianQ_vs_voltage(combined, rpc_list=[3, 4])

       # plots.plot_efficiency_vs_reduced_field(combined, rpc_list=[3])

    except Exception as e:
        print(f"⚠️ Plotting failed: {e}")

    return combined







# # --- Example usage ---
# base_folder = "/home/lidka/SWGO/SKAN1"  # change this to your main folder path
# df = load_all_steps(base_folder)

# if not df.empty:
#     plots.plot_efficiency_vs_time(df, "RPC Efficiency vs Time")