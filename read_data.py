import os
import scipy.io
import pandas as pd
from load_lookUpTable import load_detector_mapping, load_general_config  

def read_data(dataset_file: str, verbose: bool = False) -> pd.DataFrame | None:
    if not os.path.exists(dataset_file):
        print(f"File not found: {dataset_file}")
        return None

    try:
        data = scipy.io.loadmat(dataset_file)

        Q_all = data['Q_F'].toarray()
        T_all = data['T_F'].toarray()
        EBtime = data['EBtime'].flatten()
        triggerType = data['triggerType'].flatten()

        # Load mappings and config
        lookup_table = load_detector_mapping("lookUpTable_swgo.txt")
        general_config = load_general_config("lookUpTable_general.txt")
        n_of_rpcs = general_config["general"]["n_of_rpcs"]

        # Initialize DataFrame
        df = pd.DataFrame({
            'EBtime': EBtime,
            'triggerType': triggerType
        })

        # RPCs
        for rpc in range(1, n_of_rpcs + 1):
            key = f"RPC {rpc}"
            cfg = lookup_table.get(key)
            if not cfg:
                continue

            df[f"QF_RPC{rpc}"] = [Q_all[i, cfg['Q_F']] for i in range(Q_all.shape[0])]
            df[f"QB_RPC{rpc}"] = [Q_all[i, cfg['Q_B']] for i in range(Q_all.shape[0])]
            df[f"TF_RPC{rpc}"] = [T_all[i, cfg['T_F']] for i in range(T_all.shape[0])]
            df[f"TB_RPC{rpc}"] = [T_all[i, cfg['T_B']] for i in range(T_all.shape[0])]

            if verbose:
                print(f"{key} added to DataFrame with matrices of shape {Q_all[:, cfg['Q_F']].shape}")

        # Additional groups
        for group in ['scint', 'crew']:
            cfg = lookup_table.get(group)
            if not cfg:
                continue

            df[f"QF_{group}"] = [Q_all[i, cfg['Q_F']] for i in range(Q_all.shape[0])]
            df[f"TF_{group}"] = [T_all[i, cfg['T_F']] for i in range(T_all.shape[0])]

            if verbose:
                print(f"{group} added to DataFrame with matrices of shape {Q_all[:, cfg['Q_F']].shape}")

        return df

    except Exception as e:
        print(f"Error reading {dataset_file}: {e}")
        return None


    except Exception as e:
        print(f"Error reading {dataset_file}: {e}")
        return None


########################################################
#TEST

# df = read_data("rise2/sest25146081425.mat", verbose=0)
# QF_RPC1 = df['QF_RPC1'].to_list()  # list of matrices per event
# print("  Number of events:", len(QF_RPC1))
# print("  Shape of first event QF_RPC1:", QF_RPC1[0].shape)

# # Get scintillator TF matrix
# TF_scint = df['TF_scint'].to_list()
# print("  Number of events:", len(TF_scint))
# print("  Shape of first event TF_scint:", TF_scint[0].shape)

########################################################
#TEST

