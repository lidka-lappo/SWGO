import os
import re
from datetime import datetime, timedelta

def parse_date(date_input):
    """Parses date from:
    - dd-mm-yyyy [hh[:mm[:ss]]]
    - dd.mm.yyyy [hh[:mm[:ss]]]
    - DOY
    Missing hh/mm/ss are filled as 00.
    """
    if not date_input:
        return None

    # Try to split date and time
    parts = date_input.strip().split()
    date_str = parts[0]
    time_str = parts[1] if len(parts) > 1 else "00:00:00"

    # Normalize time string to hh:mm:ss
    time_parts = time_str.split(":")
    while len(time_parts) < 3:
        time_parts.append("00")
    try:
        h, m, s = map(int, time_parts)
    except ValueError:
        raise ValueError(f"Invalid time format in: {time_str}")

    # Try parsing date
    for fmt in ("%d-%m-%Y", "%d.%m.%Y"):
        try:
            base_date = datetime.strptime(date_str, fmt)
            return base_date.replace(hour=h, minute=m, second=s)
        except ValueError:
            continue

    # If date_str is DOY
    try:
        doy = int(date_str)
        year = datetime.now().year
        base_date = datetime(year, 1, 1) + timedelta(days=doy - 1)
        return base_date.replace(hour=h, minute=m, second=s)
    except ValueError:
        raise ValueError(f"Invalid date format: {date_input}")

def extract_file_datetime(filename):
    """Extracts datetime from filename like sest{yy}{doy}{hhmmss}.mat."""
    match = re.match(r"sest(\d{2})(\d{3})(\d{6})?\.mat$", filename)
    if not match:
        return None
    yy, doy, hms = match.groups()
    year = 2000 + int(yy)
    doy = int(doy)
    dt = datetime(year, 1, 1) + timedelta(days=doy - 1)
    if hms:
        dt = dt.replace(hour=int(hms[:2]), minute=int(hms[2:4]), second=int(hms[4:6]))
    return dt

def list_files_in_date_range(folder, start_date=None, end_date=None):
    """
    Returns a list of .mat files in a folder whose timestamps (from filenames)
    fall between start_date and end_date (inclusive). Supported formats:
    - dd-mm-yyyy [hh[:mm[:ss]]]
    - dd.mm.yyyy [hh[:mm[:ss]]]
    - DOY [hh[:mm[:ss]]]
    """
    start_dt = parse_date(start_date)
    end_dt = parse_date(end_date)

    file_list = []

    for file in os.listdir(folder):
        if not file.endswith('.mat') or not file.startswith('sest'):
            continue
        file_dt = extract_file_datetime(file)
        if not file_dt:
            continue
        if start_dt and file_dt < start_dt:
            continue
        if end_dt and file_dt > end_dt:
            continue
        file_list.append(os.path.join(folder, file))

    return sorted(file_list)



###########################################################################################
#TESTS 
#files = list_files_in_date_range("sweap_202_205", start_date="21-07-2025", end_date="205")
#files = list_files_in_date_range("sweap_202_205", "21-07-2025")                    
#files = list_files_in_date_range("sweap_202_205", "21-07-2025 11")                 
#files = list_files_in_date_range("sweap_202_205", "21-07-2025 11:04")             
#files = list_files_in_date_range("sweap_202_205", "21-07-2025 11:02:50")          
#files = list_files_in_date_range("sweap_202_205", "202", "205"),                     
#files = list_files_in_date_range("sweap_202_205", "21-07-2025 11:01:50", "23-07-2025")          
#files = list_files_in_date_range("sweap_202_205", "21-07-2025 11:01:50", "22-07-2025 14:00:00")

#for f in files:
#    print(f)
###########################################################################################