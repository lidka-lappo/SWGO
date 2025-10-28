import os
import pandas as pd
import numpy as np

def save_processed_data(final_data, file_path):
    folder, filename = os.path.split(file_path)
    name, ext = os.path.splitext(filename)
    #processed_folder = os.path.join(folder, f"processed_{os.path.basename(folder)}")
    processed_file = f"processed_{name}{ext}"
    processed_folder = f"processed_{os.path.basename(folder)}"

    # ensure processed folder exists
    os.makedirs(processed_folder, exist_ok=True)

    # full path to save file
    output_path = os.path.join(processed_folder, processed_file)

    # save DataFrame
    final_data.to_csv(output_path, index=False)

    print(f"Saved processed file to: {output_path}")

current_output_state = {
    1: {"timestamp": None, "rows": 0},
    2: {"timestamp": None, "rows": 0},
    3: {"timestamp": None, "rows": 0},
    4: {"timestamp": None, "rows": 0},
}

bronze_output_state = {
    1: {"timestamp": None, "rows": 0},
}



import os
import pandas as pd
import numpy as np

def save_run_parameters(rpc, run_parameters, file_path, output_dir="results"):
    """
    Save run parameters to a CSV file. Each call creates a new file.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract timestamp from file name
    timestamp = os.path.splitext(os.path.basename(file_path))[0][7:]
    print(timestamp)
    run_param_file = os.path.join(output_dir, f"run_parameters_RPC{rpc}_{timestamp}.csv")
    
    # Flatten pandas Series if needed
    flat_params = {k: v.iloc[0] if hasattr(v, "iloc") else v for k, v in run_parameters.items()}
    df = pd.DataFrame([flat_params])
    
    # Save to CSV
    df.to_csv(run_param_file, index=False)
    print(f"Saved run parameters to {run_param_file}")


def save_final_results(rpc, final_data, file_path, output_dir="results"):
    """
    Save final results to a TXT file (tab-delimited). Each call creates a new file.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract timestamp from file name
    timestamp = os.path.splitext(os.path.basename(file_path))[0][7:]
    final_data_file = os.path.join(output_dir, f"final_data_RPC{rpc}_{timestamp}.txt")
    
    # Convert to array if not a DataFrame
    if isinstance(final_data, pd.DataFrame):
        final_data.to_csv(final_data_file, sep='\t', index=False)
    else:
        final_data = np.array(final_data)
        with open(final_data_file, 'w') as f:
            np.savetxt(f, final_data, fmt='%s', delimiter='\t')
    
    print(f"Saved final results to {final_data_file}")


def save_rpc_results(rpc, run_parameters, final_data, file_path, output_dir="results", max_rows=10000):
    # Pick the correct RPC state dictionary
    state = current_output_state[rpc]

    os.makedirs(output_dir, exist_ok=True)

    # Extract timestamp from current input file (e.g. "sest25287163557.mat" → "25287163557")
    timestamp = os.path.splitext(os.path.basename(file_path))[0][4:]

    # --- Decide which file to write to ---
    if state["timestamp"] is None or state["rows"] >= max_rows:
        state["timestamp"] = timestamp
        state["rows"] = 0

    out_timestamp = state["timestamp"]
    final_data_file = os.path.join(output_dir, f"final_data_RPC{rpc}_{out_timestamp}.txt")
    run_param_file = os.path.join(output_dir, f"run_parameters_RPC{rpc}_{out_timestamp}.csv")

    # --- Convert run parameters to DataFrame row ---
    # Flatten Series (e.g. pandas outputs) into scalars
    flat_params = {k: v.iloc[0] if hasattr(v, "iloc") else v for k, v in run_parameters.items()}
    df = pd.DataFrame([flat_params])

    # --- Append or create file ---
    header = not os.path.exists(run_param_file)
    df.to_csv(run_param_file, index=False, mode='a', header=header)
    print(f"Appended run parameters to {run_param_file}")

    # --- Prepare and save final_data ---
    if isinstance(final_data, pd.DataFrame):
        rows_to_write = len(final_data)
    else:
        final_data = np.array(final_data)
        rows_to_write = final_data.shape[0] if final_data.ndim > 1 else 1

    header = not os.path.exists(final_data_file)
    if isinstance(final_data, pd.DataFrame):
        final_data.to_csv(final_data_file, sep='\t', index=False, mode='a', header=header)
    else:
        with open(final_data_file, 'a') as f:
            np.savetxt(f, np.array(final_data), fmt='%s', delimiter='\t')

    state["rows"] += rows_to_write
    print(f"Appended {rows_to_write} rows to {final_data_file}")

    # --- Reset if full ---
    if state["rows"] >= max_rows:
        print(f"✅ File {final_data_file} reached {state['rows']} rows. Next file will use new timestamp.")
        state["timestamp"] = None
        state["rows"] = 0

def save_pipeline(bronze_data, file_path, output_dir="bronze", max_rows=10000):
    # Pick the correct RPC state dictionary
    state = bronze_output_state[1]

    os.makedirs(output_dir, exist_ok=True)

    # Extract timestamp from current input file (e.g. "sest25287163557.mat" → "25287163557")
    timestamp = os.path.splitext(os.path.basename(file_path))[0][4:]

    # --- Decide which file to write to ---
    if state["timestamp"] is None or state["rows"] >= max_rows:
        state["timestamp"] = timestamp
        state["rows"] = 0

    out_timestamp = state["timestamp"]
    bronze_data_file = os.path.join(output_dir, f"bronze_{out_timestamp}.txt")
    if os.path.exists(bronze_data_file):
        try:
            with open(bronze_data_file, 'r') as f:
                # Count lines excluding header
                line_count = sum(1 for _ in f) - 1
            if line_count > 0:
                state["rows"] = line_count
                print(f"Resuming bronze file '{bronze_data_file}' with {line_count} existing rows.")
        except Exception as e:
            print(f"Warning: Could not count existing rows in {bronze_data_file}: {e}")

    # --- Prepare and save final_data ---
    if isinstance(bronze_data, pd.DataFrame):
        rows_to_write = len(bronze_data)
    else:
        bronze_data = np.array(bronze_data)
        rows_to_write = bronze_data.shape[0] if bronze_data.ndim > 1 else 1

    header = not os.path.exists(bronze_data_file)
    if isinstance(bronze_data, pd.DataFrame):
        bronze_data.to_csv(bronze_data_file, sep='\t', index=False, mode='a', header=header)
    else:
        with open(bronze_data_file, 'a') as f:
            np.savetxt(f, np.array(bronze_data), fmt='%s', delimiter='\t')

    state["rows"] += rows_to_write
    print(f"Appended {rows_to_write} rows to {bronze_data_file} Rows: {state['rows']}/Max:{max_rows}")

    # --- Reset if full ---
    if state["rows"] >= max_rows:
        print(f"✅ File {bronze_data_file} reached {state['rows']} rows. Next file will use new timestamp.")
        state["timestamp"] = None
        state["rows"] = 0
    return bronze_data_file