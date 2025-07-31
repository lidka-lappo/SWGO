import numpy as np

def trigger_filter_scint(data: dict) -> np.ndarray:
    
    """
    #maybe TO DO add small scintillators 3 and 4
    Filters events based on conditions for scintillators S1 and S2.

    Returns:
        valid_idx (np.ndarray): Boolean mask of valid events.
    """
    try:
        T_S1 = data["TF_scint"][:, 0]
        T_S2 = data["TF_scint"][:, 1]

        Q_S1 = data["QF_scint"][:, 0]
        Q_S2 = data["QF_scint"][:, 1]
        Q_S3 = data["QF_scint"][:, 2]
        Q_S4 = data["QF_scint"][:, 3]

        diff = T_S1 - T_S2

        cond_S1S2 = (
            (diff >= -20) & (diff <= 20) &
            (Q_S1 >= 600) & (Q_S1 <= 1500) &
            (Q_S2 >= 600) & (Q_S2 <= 1500)
        )

        cond_S3S4 = (
            (Q_S3 > 350) & (Q_S3 < 550) &
            (Q_S4 > 350) & (Q_S4 < 550)
        )
        
        #valid_idx = cond_S1S2 | cond_S3S4
        valid_idx = cond_S1S2
        #valid_idx = cond_S3S4
        return valid_idx

    except KeyError as e:
        print(f"Missing expected data key: {e}")
        return np.array([], dtype=bool)




def filter_rpc(data: dict, rpc) -> np.ndarray:
    """
    Filters events in RPC1 based on:
      - at least one strip has non-zero T_F and T_B
      - not all QF or QB values are NaN

    Returns:
    Boolean mask of valid events.
    """
    try:
        QF = data[f"QF_RPC{rpc}"]
        QB = data[f"QB_RPC{rpc}"]
        TF = data[f"TF_RPC{rpc}"]
        TB = data[f"TB_RPC{rpc}"]

        QF = np.where(QF < 0, np.nan, QF)
        QB = np.where(QB < 0, np.nan, QB)

        # Apply time mask per strip
        strips = QF.shape[1]
        for ind in range(strips):
            mask = (TF[:, ind] != 0) & (TB[:, ind] != 0)
            QF[~mask, ind] = np.nan
            QB[~mask, ind] = np.nan

        # Final filtering conditions
        valid_qf = ~np.isnan(QF).all(axis=1)
        valid_qb = ~np.isnan(QB).all(axis=1)
        valid_time = np.any((TF != 0) & (TB != 0), axis=1)

        valid_idx = valid_qf & valid_qb & valid_time

        return valid_idx

    except KeyError as e:
        print(f"Missing expected RPC{rpc} data key: {e}")
        return np.array([], dtype=bool)




def find_Qmax_strips(data: dict, rpc: int) -> None:
    """
    Computes and saves:
      - maximum QF and QB per event (QFmax, QBmax)
      - corresponding strip indices (XFmax, XBmax)
      - valid event mask based on Q and timing info

    Updates data in-place with:
      - QFmax_RPC, QBmax_RPC
      - XFmax_RPC, XBmax_RPC
      - valid_RPC
    """
    try:
        QF = data[f"QF_RPC{rpc}"]
        QB = data[f"QB_RPC{rpc}"]
        TF = data[f"TF_RPC{rpc}"]
        TB = data[f"TB_RPC{rpc}"]

        # Replace negative charges with NaN
        QF = np.where(QF < 0, np.nan, QF)
        QB = np.where(QB < 0, np.nan, QB)

        # Mask out strips where timing is zero
        strips = QF.shape[1]
        for ind in range(strips):
            mask = (TF[:, ind] != 0) & (TB[:, ind] != 0)
            QF[~mask, ind] = np.nan
            QB[~mask, ind] = np.nan

        # QF max values and indices
        QFmax = np.nanmax(QF, axis=1)
        valid_qf = ~np.isnan(QF).all(axis=1)
        XFmax = np.full(QF.shape[0], -1, dtype=int)
        XFmax[valid_qf] = np.nanargmax(QF[valid_qf, :], axis=1)

        # QB max values and indices
        QBmax = np.nanmax(QB, axis=1)
        valid_qb = ~np.isnan(QB).all(axis=1)
        XBmax = np.full(QB.shape[0], -1, dtype=int)
        XBmax[valid_qb] = np.nanargmax(QB[valid_qb, :], axis=1)

        # Final valid row condition
        valid_rows = (
            ~np.isnan(QFmax) &
            ~np.isnan(QBmax) &
            np.any(TF != 0, axis=1) &
            np.any(TB != 0, axis=1) 
            ##&
            ##(XBmax == XFmax)
            ##TO DO: check why they are so often different
        )

        # Save to data
        data[f"QFmax_RPC{rpc}"] = QFmax
        data[f"QBmax_RPC{rpc}"] = QBmax
        data[f"Xmax_RPC{rpc}"] = XFmax
        return valid_rows

    except KeyError as e:
        print(f"Missing expected data key: {e}")




################################################################
def apply_mask(data: dict, mask: np.ndarray) -> None:
    """
    Modifies the data dict in place using the boolean mask.
    """
    for k, v in data.items():
        if isinstance(v, np.ndarray) and v.shape[0] == len(mask):
            data[k] = v[mask]


def apply_rpc_offsets(data: dict, rpc_params: dict, rpc):
    qf_key = f"QF_RPC{rpc}"
    qb_key = f"QB_RPC{rpc}"

    # Fetch the Q arrays
    QF = data[qf_key]  # shape (N, 4)
    QB = data[qb_key]  # shape (N, 4)

    # Load offsets for this RPC
    offsets = np.array(rpc_params[f"offsets"])  # shape (4, 2), each row [x_offset, y_offset]
    x_offsets = offsets[:, 0]
    y_offsets = offsets[:, 1]

    # Apply offsets to QF and QB
    # Assumes QF and QB are arrays of shape (N, 4) for values (could be e.g. positions or charges)
    for i in range(4):  # 4 strips
        QF[:, i] -= x_offsets[i]  # Apply x-offset
        QB[:, i] -= y_offsets[i]  # Apply y-offset

    # Update the result
    data[qf_key] = QF
    data[qb_key] = QB
