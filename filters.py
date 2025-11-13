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
import pandas as pd
import numpy as np

def filter_by_charge(data, rpc):
    """Filter out negative charges in QF and QB arrays."""
    qf_key = f"QF_RPC{rpc}"
    qb_key = f"QB_RPC{rpc}"

    try:
        QF = pd.DataFrame(data[qf_key].tolist(), columns=[f"QF{i}" for i in range(4)], index=data.index)
        QB = pd.DataFrame(data[qb_key].tolist(), columns=[f"QB{i}" for i in range(4)], index=data.index)

        # Replace negative charges with NaN
        QF = QF.mask(QF <= 0)
        QB = QB.mask(QB <= 0)

        # Write masked data back
        data[qf_key] = QF.values.tolist()
        data[qb_key] = QB.values.tolist()

        # Valid rows are those that have at least one non-NaN charge
        valid_qf = ~QF.isna().all(axis=1)
        valid_qb = ~QB.isna().all(axis=1)
        valid_idx = valid_qf & valid_qb

        return valid_idx

    except KeyError as e:
        print(f"Missing expected charge column for RPC{rpc}: {e}")
        return pd.Series([False] * len(data), index=data.index)


def filter_by_time(data, rpc):
    tf_key = f"TF_RPC{rpc}"
    tb_key = f"TB_RPC{rpc}"

    try:
        TF = pd.DataFrame(data[tf_key].tolist(), columns=[f"TF{i}" for i in range(4)], index=data.index)
        TB = pd.DataFrame(data[tb_key].tolist(), columns=[f"TB{i}" for i in range(4)], index=data.index)

        # Ensure numeric
        TF = TF.apply(pd.to_numeric, errors='coerce')
        TB = TB.apply(pd.to_numeric, errors='coerce')

        # Valid if TF or TB is non-zero (negative is valid)
        mask_time = (TF.values != 0) & (TB.values != 0)
        valid_idx = mask_time.any(axis=1)

        print(f"Valid rows by time: {valid_idx.sum()} / {len(valid_idx)}")
        return valid_idx

    except KeyError as e:
        print(f"Missing expected time column for RPC{rpc}: {e}")
        return pd.Series([False] * len(data), index=data.index)



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
        
        # print(QF.dtypes)
        # print(QF.head())

        # Replace negative charges with NaN
        QF = QF.mask(QF < 0)
        QB = QB.mask(QB < 0)
    
        # Mask charges where times are invalid (TF or TB == 0)
        mask_time = (TF.values != 0) & (TB.values != 0)
        QF = QF.where(mask_time)
        QB = QB.where(mask_time)


     # --- Write masked data back into the main DataFrame ---
        data[qf_key] = QF.values.tolist()
        data[qb_key] = QB.values.tolist()

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
            f"XBmax_RPC{rpc}": XBmax
        })
                # Filtering conditions
        valid_idx = valid_qfmax & valid_qbmax #&  valid_front_equal_back

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

    #print(data[qf_key])
    print(type(data[qf_key].iloc[0]))

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

def rpc_fired(TF, TB):
    if TF is None or TB is None:
        return False
    return (TF != 0).any() and (TB != 0).any()



def at_least_two_rpcs_fired(rpc_data):
    fired_counts = []
    for i in range(1, 5):  # RPC1 to RPC4
        fired = rpc_data.apply(
            lambda row: rpc_fired(row[f'TF_RPC{i}'], row[f'TB_RPC{i}']), axis=1
        )
        fired_counts.append(fired)

    # Combine all RPC fired results into one DataFrame
    fired_df = pd.concat(fired_counts, axis=1)
    fired_df.columns = [f'RPC{i}_fired' for i in range(1, 5)]

    # Count how many RPCs fired per row
    rpc_data['num_rpc_fired'] = fired_df.sum(axis=1)

    # Keep only rows with at least 2 RPCs fired
    filtered = rpc_data[rpc_data['num_rpc_fired'] >= 2].copy()
        

    return filtered

import pandas as pd

import pandas as pd

def fancy_trigger(data, triggerType, include_general_rule=False):
    """
    Keeps events that meet any of these conditions:
      1. RPC1 & RPC4 fired
      2. RPC1 & Scintillator 3 fired
      3. RPC4 & Scintillator 4 fired
      4. RPC3 & Scintillator 4 fired
      5. RPC2 & Scintillator 3 fired
      6. Scintillator 3 & Scintillator 4 fired
    Optionally includes the general rule:
      - At least two RPCs and at least one scintillator, or >=3 RPCs
    """

    # --- Check RPC firing ---
    fired_counts = []
    for i in range(1, 5):
        fired = data.apply(
            lambda row: rpc_fired(row[f'TF_RPC{i}'], row[f'TB_RPC{i}']), axis=1
        )
        fired_counts.append(fired)

    rpc_fired_df = pd.concat(fired_counts, axis=1)
    rpc_fired_df.columns = [f'RPC{i}_fired' for i in range(1, 5)]
    num_rpc_fired = rpc_fired_df.sum(axis=1)

    # --- Check scintillator firing ---
    try:
        TF = pd.DataFrame(data['TF_scint'].tolist(), columns=['TF_S1', 'TF_S2', 'TF_S3', 'TF_S4'])
    except KeyError:
        TF = pd.DataFrame(0, index=data.index, columns=['TF_S1', 'TF_S2', 'TF_S3', 'TF_S4'])

    scint_fired = (TF != 0)
    S1, S2, S3, S4 = [scint_fired[f'TF_S{i}'] for i in range(1, 5)]

        # --- Define specific combinations ---
    # --- Define specific combinations ---
    cond1 = rpc_fired_df['RPC1_fired'] & rpc_fired_df['RPC2_fired'] & S2
    cond2 = rpc_fired_df['RPC4_fired'] & rpc_fired_df['RPC3_fired'] & S1
    # cond3 = S3 & S4
    cond4 = S1 & S2  

    # --- Choose mask based on trigger type ---
    if triggerType == "TriggerDOWN":
        special_mask = cond2 | cond4
    elif triggerType == "TriggerUP":
        special_mask = cond1 | cond4
    elif triggerType == "TriggerScint":
        special_mask = cond4 
    else:
        special_mask = cond1 | cond2 | cond4

    # --- General rule (optional) ---
    if include_general_rule:
        general_mask = ((num_rpc_fired >= 2) & scint_fired.any(axis=1)) | (num_rpc_fired >= 3)
        final_mask = special_mask | general_mask
    else:
        final_mask = special_mask
    #final_mask = (num_rpc_fired >= 0) 
    # --- Return filtered subset only ---
    return data.loc[final_mask].copy()



def at_least_two_rpcs_and_one_scint(data):
    """

    Keeps only events where at least two RPC detectors fired
    AND at least one scintillator fired.
    """

    # --- Check RPC firing ---
    fired_counts = []
    for i in range(1, 5):  # RPC1 to RPC4
        fired = data.apply(
            lambda row: rpc_fired(row[f'TF_RPC{i}'], row[f'TB_RPC{i}']), axis=1
        )
        fired_counts.append(fired)

    fired_df = pd.concat(fired_counts, axis=1)
    fired_df.columns = [f'RPC{i}_fired' for i in range(1, 5)]
    data['num_rpc_fired'] = fired_df.sum(axis=1)

    # --- Check scintillator firing ---
    try:
        TF = pd.DataFrame(data['TF_scint'].tolist(), columns=['TF_S1','TF_S2','TF_S3','TF_S4'])
        QF = pd.DataFrame(data['QF_scint'].tolist(), columns=['QF_S1','QF_S2','QF_S3','QF_S4'])

        # A scintillator is considered "fired" if TF > 0 (or True)
        scint_fired = (TF > 0).any(axis=1)
        #scint3_fired = TF['TF_S3'] > 0

    except KeyError as e:
        print(f"Missing expected column: {e}")
        scint_fired = pd.Series([False]*len(data))
        #scint3_fired = pd.Series([False]*len(data))


    # --- Apply combined condition ---
    mask = ((data['num_rpc_fired'] >= 2) & scint_fired) | (data['num_rpc_fired'] >= 3)

    # --- Return filtered data ---
    return data[mask].copy()

