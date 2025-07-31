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


def apply_mask(data: dict, mask: np.ndarray) -> dict:
    """
    Returns a masked copy of the data dict.
    """
    masked = {}
    for k, v in data.items():
        if isinstance(v, np.ndarray) and v.shape[0] == len(mask):
            masked[k] = v[mask]
        else:
            masked[k] = v
    return masked
