import os
from files_to_open import list_files_in_date_range
from plot_hist_Q import plot_hist_Q
from read_data import read_data

def main():
    folder = "sweap4"
    detector = "scint"  #  1, 2, 3, "scint", "crew"
    start_date = None   #  "01-01-2024" or DOY or + hh:mm:ss
    end_date = "184"      #  "01-07-2024" or DOY or + hh:mm:ss

    files = list_files_in_date_range(folder, start_date, end_date)


    print(f"{len(files)} files found in date range {start_date} to {end_date} in folder '{folder}':")

    for file_path in files:
         print(f"\n Opening file: {file_path}")
         try:
             data = read_data(file_path, verbose = False)
             plot_hist_Q(data, detector=detector, verbose=False)
         except Exception as e:
             print(f" Error in file {file_path}: {e}")

if __name__ == "__main__":
    main()
