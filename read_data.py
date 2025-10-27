import os
import scipy.io
import pandas as pd
import numpy as np
from load_lookUpTable import load_detector_mapping, load_general_config  


def read_data(dataset_file: str, verbose: bool = False):
    if not os.path.exists(dataset_file):
        print(f"File not found: {dataset_file}")
        return None

    try:
        data = scipy.io.loadmat(dataset_file)
        
        Q_all = data['Q_F'].toarray() if hasattr(data['Q_F'], "toarray") else data['Q_F']
        T_all = data['T_F'].toarray() if hasattr(data['T_F'], "toarray") else data['T_F']
        T_all34 = data['T_F34'].toarray() if hasattr(data['T_F34'], "toarray") else data['T_F34']
        Q_all34 = data['Q_F34'].toarray() if hasattr(data['Q_F34'], "toarray") else data['Q_F34']
        EBtime = data['EBtime'].ravel()
        triggerType = data['triggerType'].ravel()



        # Load mappings and config
        lookup_table = load_detector_mapping("lookUpTable_swgo.txt")
        general_config = load_general_config("lookUpTable_general.txt")
        #n_of_rpcs = general_config["general"]["n_of_rpcs"]
        n_of_rpcs = 2
        # Initialize DataFrame
        df = pd.DataFrame({
            'EBtime': EBtime,
            'triggerType': triggerType,

        })
        
        


        # RPCs 1 2
        for rpc in range(1, n_of_rpcs + 1):
            key = f"RPC {rpc}"
            cfg = lookup_table.get(key)
            if not cfg:
                continue

            # Vectorized extraction (no Python loop)
            df[f"QF_RPC{rpc}"] = list(Q_all[:, cfg['Q_F']])
            df[f"QB_RPC{rpc}"] = list(Q_all[:, cfg['Q_B']])
            df[f"TF_RPC{rpc}"] = list(T_all[:, cfg['T_F']])
            df[f"TB_RPC{rpc}"] = list(T_all[:, cfg['T_B']])

            if verbose:
                print(f"{key} added with matrices of shape {Q_all[:, cfg['Q_F']].shape}")
        
        # RPCs 3 4
        for rpc in range(3, 5):
            key = f"RPC {rpc}"
            cfg = lookup_table.get(key)
            if not cfg:
                continue

            # Vectorized extraction (no Python loop)
            df[f"QF_RPC{rpc}"] = list(Q_all34[:, cfg['Q_F']])
            df[f"QB_RPC{rpc}"] = list(Q_all34[:, cfg['Q_B']])
            df[f"TF_RPC{rpc}"] = list(T_all34[:, cfg['T_F']])
            df[f"TB_RPC{rpc}"] = list(T_all34[:, cfg['T_B']])

            if verbose:
                print(f"{key} added with matrices of shape {Q_all34[:, cfg['Q_F']].shape}")

        # Additional groups
        for group in ['scint', 'crew']:
            cfg = lookup_table.get(group)
            if not cfg:
                continue

            df[f"QF_{group}"] = list(Q_all[:, cfg['Q_F']])
            df[f"TF_{group}"] = list(T_all[:, cfg['T_F']])

            if verbose:
                print(f"{group} added with matrices of shape {Q_all[:, cfg['Q_F']].shape}")

        return df

    except Exception as e:
        print(f"Error reading {dataset_file}: {e}")
        return None



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


# ########################################################
#TEST

# #df = read_data("rise2/sest25146081425.mat", verbose=0)
#df = read_data("/home/lidka/SWGO/4RPC/sest25287163557.mat", verbose=1)
# QF_RPC3 = df['QF_RPC3'].to_list()  # list of matrices per event
# print("  Number of events:", len(QF_RPC3))
# print("  Shape of first event QF_RPC3:", QF_RPC3[0].shape)

# QF_RPC4 = df['QF_RPC4'].to_list()  # list of matrices per event
# print("  Number of events:", len(QF_RPC4))
# print("  Shape of first event QF_RPC4:", QF_RPC4[0].shape)

# # Get scintillator TF matrix
# TF_scint = df['TF_scint'].to_list()
# print("  Number of events:", len(TF_scint))
# print("  Shape of first event TF_scint:", TF_scint[0].shape)

# ########################################################
# #TEST

