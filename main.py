import os
import numpy as np

from files_to_open import list_files_in_date_range

from read_data import read_data
from plots import plot_hist_Q, plot_hist_T, plot_diffT
from filters import trigger_filter_scint
from filters import apply_mask


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
        
        plot_diffT(data)
        #plot_hist_Q(data, detector='scint', verbose=False)
        #plot_hist_T(data, detector='scint', verbose=False)
        mask = trigger_filter_scint(data)
        print(f"Events passing trigger filter: {np.sum(mask)} / {len(mask)}")
        filtered_data = apply_mask(data, mask) 

        plot_diffT(filtered_data)
        #plot_hist_Q(filtered_data, detector='scint', verbose=False)
        #plot_hist_T(filtered_data, detector='scint', verbose=False)



        #  plot_hist_Q(data, detector=1, verbose=False)
        #  plot_hist_Q(data, detector=2, verbose=False)
        #  plot_hist_Q(data, detector='scint', verbose=False)
        #  plot_hist_Q(data, detector='crew', verbose=False)


        # detector =  1, 2, 3, "scint", "crew"
        #plot_hist_T(data, detector=1, verbose=False)
        #plot_hist_T(data, detector=2, verbose=False)
        #plot_hist_T(data, detector='scint', verbose=False)
        #plot_hist_T(data, detector='crew', verbose=False)

if __name__ == "__main__":
    main()
