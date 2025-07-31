import os
import scipy.io
from load_lookUpTable import load_detector_mapping, load_general_config  

def read_data(dataset_file: str, verbose: bool = False) -> dict | None:
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


        result = {
            'EBtime': EBtime,
            'triggerType': triggerType
        }

        general_config = load_general_config("lookUpTable_general.txt")
        n_of_rpcs = general_config["general"]["n_of_rpcs"]

        # RPCs
        for rpc in range(1, n_of_rpcs + 1):
            key = f"RPC {rpc}"
            cfg = lookup_table.get(key)
            if not cfg:
                continue

            result.update({
                f"QF_RPC{rpc}": Q_all[:, cfg['Q_F']],
                f"QB_RPC{rpc}": Q_all[:, cfg['Q_B']],
                f"TF_RPC{rpc}": T_all[:, cfg['T_F']],
                f"TB_RPC{rpc}": T_all[:, cfg['T_B']],
            })

            if verbose:
                print(f"{key}:")
                print("  Q_F shape:", result[f"QF_RPC{rpc}"].shape)
                print("  Q_B shape:", result[f"QB_RPC{rpc}"].shape)
                print("  T_F shape:", result[f"TF_RPC{rpc}"].shape)
                print("  T_B shape:", result[f"TB_RPC{rpc}"].shape)
                print()

        # Additional groups
        for group in ['scint', 'crew']:
            cfg = lookup_table.get(group)
            if not cfg:
                continue

            result[f'QF_{group}'] = Q_all[:, cfg['Q_F']]
            result[f'TF_{group}'] = T_all[:, cfg['T_F']]

            if verbose:
                print(f"{group}:")
                print("  Q_F shape:", result[f'QF_{group}'].shape)
                print("  T_F shape:", result[f'TF_{group}'].shape)
                print()

        return result

    except Exception as e:
        print(f"Error reading {dataset_file}: {e}")
        return None


########################################################
#TEST


# data = read_data("sweap4/sest25184133338.mat", verbose=0)
# QF_RPC1 = data['QF_RPC1']
# print("  Q_F RPC1 shape:", QF_RPC1.shape)
# TF_scint = data['TF_scint']
# print("  T_F scint shape:", TF_scint.shape)

########################################################
#TEST

