import pandas as pd
from datetime import datetime

def read_hv_file(file_path):

    cols = ["datetime",
            "RPC1_setHV_1", "RPC1_readHV_1", "RPC1_I_1",
            "RPC1_setHV_2", "RPC1_readHV_2", "RPC1_I_2",

            "RPC2_setHV_1", "RPC2_readHV_1", "RPC2_I_1",
            "RPC2_setHV_2", "RPC2_readHV_2", "RPC2_I_2",

            "RPC3_setHV_1", "RPC3_readHV_1", "RPC3_I_1",
            "RPC3_setHV_2", "RPC3_readHV_2", "RPC3_I_2"
        ]

    
    # Read file, semicolon separates timestamp from rest
    df = pd.read_csv(
        file_path,
        sep=r";\s*|\s+",   # split on semicolon+space or whitespace
        engine="python",
        header=None,
        names=cols,
        parse_dates=["datetime"],
        date_parser=lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%S")
    )
    
    df.set_index("datetime", inplace=True)
    return df


df_hv = read_hv_file("hv/2025-05-28.txt")
print(df_hv.head())
