import pandas as pd
import os
from datetime import datetime

def read_thp_log(file_path):
    # Define column names
    cols = ["datetime", "T1", "T2", "T3", "T4", "h1", "h2", "p1", "p2"]

    # Read file into DataFrame
    df = pd.read_csv(
        file_path,
        sep=r"\s+",
        header=None,
        names=cols,
        parse_dates=["datetime"],
        date_parser=lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%S")
    )

    # Set datetime as index
    df.set_index("datetime", inplace=True)

    return df

df = read_thp_log("thp/THP_2025-05-21.log")
print(df.head())