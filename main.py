import os
import numpy as np

from files_to_open import list_files_in_date_range

from read_data import read_data
from plots import plot_hist_Q, plot_hist_T, plot_diffT, plot_heatmap
from filters import trigger_filter_scint, filter_rpc, find_Qmax_strips
from filters import apply_mask, apply_rpc_offsets

from load_lookUpTable import load_rpc_parameters, load_general_config
from calculate_parameters import calculate_parameters, calculate_Q_T, calculate_XY



'''

detector =  1, 2, 3, "scint", "crew"

'''

def main():

    folder = "sweap4"
    start_date = None   #  "01-01-2024" or DOY or + hh:mm:ss
    end_date = "184"      #  "01-07-2024" or DOY or + hh:mm:ss

    files = list_files_in_date_range(folder, start_date, end_date)


    print(f"{len(files)} file(s) found in date range {start_date} to {end_date} in folder '{folder}':")

    for file_path in files:
        print(f"\n Opening file: {file_path}")
        data = read_data(file_path, verbose=0)
        if data is None:
            print("Failed to read data.")
            continue
        
        #plot_diffT(data)
        #plot_hist_Q(data, detector='scint', verbose=False)
        #plot_hist_T(data, detector='scint', verbose=False)
        
        #triggre filter
        mask = trigger_filter_scint(data)
        print(f"Events passing trigger filter: {np.sum(mask)} / {len(mask)}")
        apply_mask(data, mask)
        raw_events = np.sum(mask)

        rpc=1

        #offset
        rpc_params = load_rpc_parameters(f"lookUpTable_RPC{rpc}.txt")
        apply_rpc_offsets(data, rpc_params, rpc=1)
        #plot_hist_Q(data, detector=1, verbose=False)

        general_config = load_general_config("lookUpTable_general.txt")
        XRange = general_config["ranges"]["XRange"]
        YRange = general_config["ranges"]["YRange"]
        n_of_rpcs = general_config["general"]["n_of_rpcs"]
        n_of_rpcs = 2

        all_final_data = {}
        all_results = {}

        data_without_filters = data.copy()
        for rpc in range(1, n_of_rpcs + 1):
            print(f"\n=== Processing RPC{rpc} ===")

            #filter 1 
            mask1 = filter_rpc(data, rpc)
            print(f"Events passing RPC1 filter: {np.sum(mask1)} / {len(mask1)}")
            apply_mask(data, mask1)

            #find Qmax strips
            mask2 = find_Qmax_strips(data, rpc)
            print(f"After finding Qmax strips: {np.sum(mask2)} / {len(mask2)}")
            apply_mask(data, mask2)


            ###############results
            final_data = calculate_Q_T(data, rpc)
            

            results = calculate_parameters(final_data, raw_events, rpc, verbose=0)
            calculate_XY(final_data, rpc)

            all_final_data[rpc] = final_data
            all_results[rpc] = results


            #plot_heatmap(final_data[f"XY_RPC{rpc}"], XRange, YRange, rpc, "XY Hits")
            #plot_heatmap(final_data[f"XY_Qmean_RPC{rpc}"], XRange, YRange, rpc, "XY Q Mean")
            #plot_heatmap(final_data[f"XY_Qmedian_RPC{rpc}"], XRange, YRange, rpc, "XY Q Median")
            #plot_heatmap(final_data[f"XY_ST_RPC{rpc}"], XRange, YRange, rpc, "XY Streamer Threshold")       
            data = data_without_filters.copy()

#TO DO filter by space

if __name__ == "__main__":
    main()
