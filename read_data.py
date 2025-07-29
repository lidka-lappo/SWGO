import os
import scipy.io
from scipy.sparse import coo_matrix

def load_lookup_table(filepath):
    lookup = {}
    with open(filepath, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            parts = line.split(',')
            if len(parts) != 5:
                raise ValueError(f"Expected 5 columns per line, got {len(parts)}: {line}")

            group = parts[0].strip()  # can be '1', 'scintillators', etc.
            Q_F = list(map(int, parts[1].strip().split())) if parts[1].strip() else []
            Q_B = list(map(int, parts[2].strip().split())) if parts[2].strip() else []
            T_F = list(map(int, parts[3].strip().split())) if parts[3].strip() else []
            T_B = list(map(int, parts[4].strip().split())) if parts[4].strip() else []

            lookup[group] = {
                'Q_F': Q_F,
                'Q_B': Q_B,
                'T_F': T_F,
                'T_B': T_B,
            }
    return lookup

def read_data(dataset_file, verbose=False):
    import os
    import scipy.io

    if not os.path.exists(dataset_file):
        print(f"File not found: {dataset_file}")
        return None

    try:
        from scipy.sparse import coo_matrix

        data = scipy.io.loadmat(dataset_file)

        Q_all = data['Q_F'].toarray()
        T_all = data['T_F'].toarray()

        EBtime = data['EBtime'].flatten()
        triggerType = data['triggerType'].flatten()

        lookup_table = load_lookup_table("lookUpTable_swgo.txt")
        n_of_rpcs = 3

        # Initialize return dictionary
        result = {
            'EBtime': EBtime,
            'triggerType': triggerType
        }

        # RPCs
        for rpc in range(1, n_of_rpcs + 1):
            key = f"RPC {rpc}"
            cfg = lookup_table.get(key)
            if cfg:
                result[f"QF_RPC{rpc}"] = Q_all[:, cfg['Q_F']]
                result[f"QB_RPC{rpc}"] = Q_all[:, cfg['Q_B']]
                result[f"TF_RPC{rpc}"] = T_all[:, cfg['T_F']]
                result[f"TB_RPC{rpc}"] = T_all[:, cfg['T_B']]

                if verbose:
                    print(f"{key}:")
                    print("  Q_F shape:", result[f"QF_RPC{rpc}"].shape)
                    print("  Q_B shape:", result[f"QB_RPC{rpc}"].shape)
                    print("  T_F shape:", result[f"TF_RPC{rpc}"].shape)
                    print("  T_B shape:", result[f"TB_RPC{rpc}"].shape)
                    print()

        # scintillators
        cfg = lookup_table.get("scintillators")
        if cfg:
            result['QF_scint'] = Q_all[:, cfg['Q_F']]
            result['TF_scint'] = T_all[:, cfg['T_F']]

            if verbose:
                print("scintillators:")
                print("  Q_F shape:", result['QF_scint'].shape)
                print("  T_F shape:", result['TF_scint'].shape)
                print()

        # crew
        cfg = lookup_table.get("crew")
        if cfg:
            result['QF_crew'] = Q_all[:, cfg['Q_F']]
            result['TF_crew'] = T_all[:, cfg['T_F']]

            if verbose:
                print("crew:")
                print("  Q_F shape:", result['QF_crew'].shape)
                print("  T_F shape:", result['TF_crew'].shape)
                print()

        return result

    except Exception as e:
        print(f"Error reading {dataset_file}: {e}")
        return None



data = read_data("sweap4/sest25184133338.mat", verbose=0)
QF_RPC1 = data['QF_RPC1']
TF_scint = data['TF_scint']
QB_RPC2 = data['QB_RPC2']
print("  T_F shape:", TF_scint.shape)

