import os
import numpy as np

from files_to_open import list_files_in_date_range

from read_data import read_data
from plots import plot_hist_Q, plot_hist_T, plot_diffT, plot_heatmap, plot_efficiency_vs_time, plot_efficiency_vs_voltage
from plots import plot_voltage_vs_time, plot_temp_vs_time, plot_humidity_vs_time, plot_pressure_vs_time
from plots import plot_efficiency_vs_reduced_field

from apply_filters import proccess_data
from filters import trigger_filter_scint
from filters import apply_rpc_offsets

from load_lookUpTable import load_rpc_parameters, load_general_config
from calculate_parameters import calculate_parameters, calculate_Q_T, calculate_XY


from datetime import datetime, timedelta
import re
import pandas as pd

'''

detector =  1, 2, 3, "scint", "crew"

'''

def main():

    #folder = "sweap4"
    folder = "rise2"
    start_date = None  #  "01-01-2024" or DOY or + hh:mm:ss
    end_date = "148"      #  "01-07-2024" or DOY or + hh:mm:ss\

    # start_date = "146 22:40"   #  "01-01-2024" or DOY or + hh:mm:ss
    # end_date = "146 23:50"      #  "01-07-2024" or DOY or + hh:mm:ss\

    files = list_files_in_date_range(folder, start_date, end_date)
    print(f"{len(files)} file(s) found in date range {start_date} to {end_date} in folder '{folder}':")

    times = []
    results = []

    for file_path in files:
        print(f"\n Opening file: {file_path}")
        data = read_data(file_path, verbose=0)
        if data is None:
            print("Failed to read data.")
            continue
        print("done")
        #####
        #plot_diffT(data)
        #plot_hist_Q(data, detector='scint', verbose=False)
        #plot_hist_T(data, detector='scint', verbose=False)
        
        #triggre filter
        mask = trigger_filter_scint(data)
        print(f"Events passing trigger filter: {mask.sum()} / {len(mask)}")
        data = data[mask]

        # plot_diffT(data)
        # plot_hist_Q(data, detector='scint', verbose=False)
        # plot_hist_T(data, detector='scint', verbose=False)


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

        
        data_without_filters = data.copy()
        #

        for rpc in range(1, n_of_rpcs + 1):
            final_data, XY_data, run_parameters = proccess_data(data, rpc, raw_events, verbose=True)
            #all_rpc_results.update(run_parameters)
            # plot_heatmap(XY_data[f"XY_RPC{rpc}"], XRange, YRange, rpc, "XY Hits")
            # plot_heatmap(XY_data[f"XY_Qmean_RPC{rpc}"], XRange, YRange, rpc, "XY Q Mean")
            # plot_heatmap(XY_data[f"XY_Qmedian_RPC{rpc}"], XRange, YRange, rpc, "XY Q Median")
            # plot_heatmap(XY_data[f"XY_ST_RPC{rpc}"], XRange, YRange, rpc, "XY Streamer Threshold") 
            run_parameters["rpc"] = rpc
            results.append(run_parameters)

        # Concatenate all into one big DataFrame
        all_results = pd.concat(results, ignore_index=True)
        #print(all_results.head())      

    plot_efficiency_vs_reduced_field(all_results)
    plot_voltage_vs_time(all_results)
    plot_temp_vs_time(all_results)
    plot_humidity_vs_time(all_results)
    plot_pressure_vs_time(all_results)
    plot_efficiency_vs_voltage(all_results)
    plot_efficiency_vs_time(all_results)
# #####TO DO filter by space

if __name__ == "__main__":
    main()
