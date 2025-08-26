from filters import  filter_rpc, find_Qmax_strips
from filters import  apply_rpc_offsets

from calculate_parameters import calculate_parameters, calculate_Q_T, calculate_XY

import numpy as np

def apply_filters(data, rpc, all_rpc_results, raw_events=None, verbose=True):       
    if verbose:
        print(f"\n=== Processing RPC{rpc} ===")

    # filter 1 
    mask1 = filter_rpc(data, rpc)
    if verbose:
        print(f"Events passing RPC{rpc} filter: {np.sum(mask1)} / {len(mask1)}")
    data = data[mask1]

    # find Qmax strips
    mask2 = find_Qmax_strips(data, rpc)
    if verbose:
        print(f"After finding Qmax strips: {np.sum(mask2)} / {len(mask2)}")
    data = data[mask2]

    # results
    final_data = calculate_Q_T(data, rpc)

    results = calculate_parameters(final_data, raw_events, rpc, verbose=0)
    if verbose and f'mean_HV_RPC{rpc}' in results:
        print(results[f'mean_HV_RPC{rpc}'])
    all_rpc_results.update(results)

    calculate_XY(final_data, rpc)
    
    return data
