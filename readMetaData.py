import pandas as pd
import os
from datetime import datetime

def read_thp(folder_path, start_date=None, end_date=None):
    cols = ["datetime", "T1", "T2", "T3", "T4", "h1", "h2", "p1", "p2"]
    all_dfs = []

    for fname in sorted(os.listdir(folder_path)):
        if not fname.startswith("THP_") or not fname.endswith(".log"):
            continue
        file_date = datetime.strptime(fname[4:14], "%Y-%m-%d").date()
        
        if start_date and file_date < datetime.strptime(start_date, "%Y-%m-%d").date():
            continue
        if end_date and file_date > datetime.strptime(end_date, "%Y-%m-%d").date():
            continue
        
        file_path = os.path.join(folder_path, fname)
        df = pd.read_csv(
            file_path,
            sep=r"\s+",
            header=None,
            names=cols,
            parse_dates=["datetime"],
            date_format="%Y-%m-%dT%H:%M:%S"
        )
        all_dfs.append(df)

    if not all_dfs:
        return pd.DataFrame(columns=cols).set_index("datetime")
    
    merged_df = pd.concat(all_dfs).sort_values("datetime")
    merged_df.set_index("datetime", inplace=True)
    return merged_df

def read_hv(folder_path, start_date=None, end_date=None):
    cols = ["datetime",
            "RPC1_setHV_1", "RPC1_readHV_1", "RPC1_I_1",
            "RPC1_setHV_2", "RPC1_readHV_2", "RPC1_I_2",
            "RPC2_setHV_1", "RPC2_readHV_1", "RPC2_I_1",
            "RPC2_setHV_2", "RPC2_readHV_2", "RPC2_I_2",
            "RPC3_setHV_1", "RPC3_readHV_1", "RPC3_I_1",
            "RPC3_setHV_2", "RPC3_readHV_2", "RPC3_I_2"
           ]
    
    all_dfs = []

    for fname in sorted(os.listdir(folder_path)):
        if not fname.endswith(".txt"):
            continue
        try:
            file_date = datetime.strptime(fname[:10], "%Y-%m-%d").date()
        except ValueError:
            continue
        
        if start_date and file_date < datetime.strptime(start_date, "%Y-%m-%d").date():
            continue
        if end_date and file_date > datetime.strptime(end_date, "%Y-%m-%d").date():
            continue
        
        file_path = os.path.join(folder_path, fname)
        df = pd.read_csv(
            file_path,
            sep=r";\s*|\s+",
            engine="python",
            header=None,
            names=cols,
            parse_dates=["datetime"],
            date_format="%Y-%m-%dT%H:%M:%S"
        )
        all_dfs.append(df)

    if not all_dfs:
        return pd.DataFrame(columns=cols).set_index("datetime")
    
    merged_df = pd.concat(all_dfs).sort_values("datetime")
    merged_df.set_index("datetime", inplace=True)
    return merged_df




#####################TEST########################
# Read THP from 2025-05-20 to 2025-05-22
df_thp = read_thp("thp", start_date="2025-05-26", end_date="2025-05-30")
print(df_thp.head())



# Read HV from 2025-05-28 to 2025-05-30
df_hv = read_hv("hv", start_date="2025-05-28", end_date="2025-05-30")
print(df_hv.head())
#####################################################