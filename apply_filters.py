from filters import  filter_rpc, find_Qmax_strips
from filters import  apply_rpc_offsets

from calculate_parameters import calculate_parameters, calculate_Q_T, calculate_XY

import numpy as np
import pandas as pd

def apply_filters(data, rpc, all_rpc_results, raw_events=None, verbose=True):       
    if verbose:
        print(f"\n=== Processing RPC{rpc} ===")

    # filter 1 
    mask1 = filter_rpc(data, rpc)
    if verbose:
        print(f"Events passing RPC{rpc} filter: {np.sum(mask1)} / {len(mask1)}")
    data = data[mask1]
    # print(data.head())
    # # find Qmax strips
    preprocessed_data, mask2 = find_Qmax_strips(data, rpc)
    if verbose:
        print(f"After finding Qmax strips: {np.sum(mask2)} / {len(mask2)}")
    preprocessed_data = pd.concat([preprocessed_data, data], axis=1)
    preprocessed_data = preprocessed_data[mask2]


    # results
    processed_data = calculate_Q_T(preprocessed_data, rpc)
    processed_data = pd.concat([preprocessed_data, processed_data], axis=1)

    run_parameters = calculate_parameters(processed_data, raw_events, rpc, verbose=0)

    #all_rpc_results.update(run_parameters)

    final_data, XY_data = calculate_XY(processed_data, rpc)
    
    return final_data, XY_data, processed_data, run_parameters
