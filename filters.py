import numpy as np
import pandas as pd

def trigger_filter_scint(data):

    try:
        # Split arrays into separate columns
        TF = pd.DataFrame(data['TF_scint'].tolist(), columns=['TF_S1','TF_S2','TF_S3','TF_S4'])
        QF = pd.DataFrame(data['QF_scint'].tolist(), columns=['QF_S1','QF_S2','QF_S3','QF_S4'])

        # Time difference
        diff = TF['TF_S1'] - TF['TF_S2']

        # Conditions S1 and S2
        cond_S1S2 = (
            diff.between(-20, 20) &
            QF['QF_S1'].between(600, 1500) &
            QF['QF_S2'].between(600, 1500)
        )

        # Optional S3/S4 condition
        cond_S3S4 = (
            QF['QF_S3'].between(350, 550) &
            QF['QF_S4'].between(350, 550)
        )

        # Combine conditions if needed
        valid_mask = cond_S1S2  # or cond_S1S2 | cond_S3S4

        return valid_mask

    except KeyError as e:
        print(f"Missing expected column: {e}")
        return pd.Series([False]*len(data))


import pandas as pd
import numpy as np

def filter_rpc(data, rpc):
    qf_key = f"QF_RPC{rpc}"
    qb_key = f"QB_RPC{rpc}"
    tf_key = f"TF_RPC{rpc}"
    tb_key = f"TB_RPC{rpc}"

    try:
        # Expand array/list columns into separate DataFrames with matching index
        QF = pd.DataFrame(data[qf_key].tolist(), 
                          columns=[f"QF{i}" for i in range(4)], 
                          index=data.index)
        QB = pd.DataFrame(data[qb_key].tolist(), 
                          columns=[f"QB{i}" for i in range(4)], 
                          index=data.index)
        TF = pd.DataFrame(data[tf_key].tolist(), 
                          columns=[f"TF{i}" for i in range(4)], 
                          index=data.index)
        TB = pd.DataFrame(data[tb_key].tolist(), 
                          columns=[f"TB{i}" for i in range(4)], 
                          index=data.index)

        # Replace negative charges with NaN
        QF = QF.mask(QF < 0)
        QB = QB.mask(QB < 0)

        # Mask charges where times are invalid (TF or TB == 0)
        mask_time = (TF != 0) & (TB != 0)
        QF = QF.where(mask_time)
        QB = QB.where(mask_time)

        # Filtering conditions
        valid_qf = ~QF.isna().all(axis=1)
        valid_qb = ~QB.isna().all(axis=1)
        valid_time = mask_time.any(axis=1)

        valid_idx = valid_qf & valid_qb & valid_time
        return valid_idx

    except KeyError as e:
        print(f"Missing expected RPC{rpc} data column: {e}")
        return pd.Series([False] * len(data), index=data.index)



def find_Qmax_strips(data, rpc):
    qf_key = f"QF_RPC{rpc}"
    qb_key = f"QB_RPC{rpc}"
    tf_key = f"TF_RPC{rpc}"
    tb_key = f"TB_RPC{rpc}"
    
    try:
        # Expand array columns into separate columns
        QF = pd.DataFrame(data[qf_key].tolist(), columns=[f"QF{i}" for i in range(4)])
        QB = pd.DataFrame(data[qb_key].tolist(), columns=[f"QB{i}" for i in range(4)])
        TF = pd.DataFrame(data[tf_key].tolist(), columns=[f"TF{i}" for i in range(4)])
        TB = pd.DataFrame(data[tb_key].tolist(), columns=[f"TB{i}" for i in range(4)])

        # Replace negative charges with NaN
        QF = QF.mask(QF < 0)
        QB = QB.mask(QB < 0)

        # Mask out strips where timing is zero
        mask_time = (TF != 0) & (TB != 0)
        QF = QF.where(mask_time)
        QB = QB.where(mask_time)

        # QF max and index
        QFmax = QF.max(axis=1)
        XFmax = QF.idxmax(axis=1).str.extract('(\d+)').astype(int)
        XFmax = XFmax[0].fillna(-1).astype(int)

        # QB max and index
        QBmax = QB.max(axis=1)
        XBmax = QB.idxmax(axis=1).str.extract('(\d+)').astype(int)
        XBmax = XBmax[0].fillna(-1).astype(int)

        # Final valid row condition
        valid_rows = (
            QFmax.notna() &
            QBmax.notna() &
            mask_time.any(axis=1)
            # & (XFmax == XBmax)  # optional check
        )

        # Save results back to DataFrame
        data[f"QFmax_RPC{rpc}"] = QFmax
        data[f"QBmax_RPC{rpc}"] = QBmax
        data[f"Xmax_RPC{rpc}"] = XFmax

        return valid_rows

    except KeyError as e:
        print(f"Missing expected data column: {e}")
        return pd.Series([False]*len(data))




def apply_rpc_offsets(data, rpc_params, rpc):

    qf_key = f"QF_RPC{rpc}"
    qb_key = f"QB_RPC{rpc}"

    # Load offsets
    offsets = np.array(rpc_params["offsets"])  # shape (4,2)
    x_offsets = offsets[:, 0]
    y_offsets = offsets[:, 1]

    # Convert array columns to separate columns
    QF_df = pd.DataFrame(data[qf_key].tolist(), columns=[f"QF{i}" for i in range(4)])
    QB_df = pd.DataFrame(data[qb_key].tolist(), columns=[f"QB{i}" for i in range(4)])

    # Apply offsets
    for i in range(4):
        QF_df[f"QF{i}"] -= x_offsets[i]
        QB_df[f"QB{i}"] -= y_offsets[i]

    # Combine back into list/array columns
    data[qf_key] = QF_df.values.tolist()
    data[qb_key] = QB_df.values.tolist()

    return data
