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


###############################################################
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
        mask_time = (TF.values != 0) & (TB.values != 0)
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

#############################################################

def find_Qmax_strips(data, rpc):
    qf_key = f"QF_RPC{rpc}"
    qb_key = f"QB_RPC{rpc}"
    tf_key = f"TF_RPC{rpc}"
    tb_key = f"TB_RPC{rpc}"
    
    try:
        # Expand array columns into separate columns
        QF = pd.DataFrame(data[qf_key].tolist(), index=data.index, columns=[f"QF{i}" for i in range(4)])
        QB = pd.DataFrame(data[qb_key].tolist(), index=data.index, columns=[f"QB{i}" for i in range(4)])
        TF = pd.DataFrame(data[tf_key].tolist(), index=data.index, columns=[f"TF{i}" for i in range(4)])
        TB = pd.DataFrame(data[tb_key].tolist(), index=data.index, columns=[f"TB{i}" for i in range(4)])

        

        def get_max_and_index(df):
            qmax = df.max(axis=1)
            xmax = df.idxmax(axis=1).str.extract(r'(\d+)')
            xmax = xmax[0].fillna(-1).astype(int)
            return qmax, xmax

        QFmax, XFmax = get_max_and_index(QF)
        QBmax, XBmax = get_max_and_index(QB)

        #print(XFmax.head())
        valid_qfmax = ~QFmax.isna()
        valid_qbmax = ~QBmax.isna()
        valid_front_equal_back = (XFmax == XBmax)

    

        # Save results back to DataFrame
        df = pd.DataFrame({
            f"QFmax_RPC{rpc}": QFmax,
            f"QBmax_RPC{rpc}": QBmax,
            f"Xmax_RPC{rpc}": XFmax,
            #f"XBmax_RPC{rpc}": XBmax
        })
                # Filtering conditions
        valid_idx = valid_qfmax & valid_qbmax &  valid_front_equal_back

        return df, valid_idx


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
