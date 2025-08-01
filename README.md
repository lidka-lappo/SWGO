SWGO/
├── main.py                  # Main execution script – entry point for data processing & plotting
├── calculate_parameters.py  # Computes physics parameters (e.g. Qmean, Qmedian, efficiency)
├── filters.py               # Filtering functions, includes trigger logic and data cleaning
├── plots.py                 # All visualization logic (heatmaps, efficiency, time distributions)
├── read_data.py             # Core data loading + pre-processing (called by main)
├── files_to_open.py         # Defines data file lists to open for batch processing
├── load_lookUpTable.py      # Parses lookup tables for detector geometry/config
│
├── lookUpTable_RPC1.txt     # Detector-specific lookup tables 
├── lookUpTable_RPC2.txt
├── lookUpTable_general.txt  # General lookup tables
├── lookUpTable_swgo.txt  # mapping

