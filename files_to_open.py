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

# def run_tests():
#     test_folder = "sweap4"

#     tests = [
#         # (description, start_date, end_date, expected_count)
#         ("No dates (full folder)", None, None, 6),
#         #startdate
#         ("Start date only - '03-07-2025'", "03-07-2025", None, 5),
#         ("Start date only with dots - '05.07.2025'", "05.07.2025", None, 3),
#         ("Start date + hour - '02-07-2025 13'", "02-07-2025 08", None, 5),
#         ("Start date + hour:min - '03-07-2025 13:10'", "03-07-2025 13:10", None, 5),
#         ("Start date + hour:min:sec - '03-07-2025 13:33:38'", "03-07-2025 13:33:38", None, 4),
#         #enddate
#         ("Only end date - '06-07-2025 13'", None, "06-07-2025 13", 4), 
#         ("Only end date only with dots - '06.07.2025 13'", None, "06.07.2025 13", 4), 
#         ("End date + hour - '02-07-2025 13'", None, "02-07-2025 13", 1),
#         ("End date + hour:min - '03-07-2025 13:33'", None, "03-07-2025 13:10", 1),
#         ("End date + hour:min:sec - '03-07-2025 13:33:38'", None, "03-07-2025 13:33:37", 2),
        
#         #both start and end date
#         ("Just dates, full days", "03-07-2025", "06-07-2025", 2),
#         ("Start date + hour, end date just date", "02-07-2025 08", "06-07-2025", 2),
#         ("Start date with hour:min, end date with hour:min", "03-07-2025 13:33", "09-07-2025 19:50", 3),
#         ("Start date + hour:min:sec, end date + hour:min:sec", "03-07-2025 13:33:37", "09-07-2025 19:50:47", 4),
#         ("Start and end same day, hour:min precision", "03-07-2025 13:33", "03-07-2025 13:34", 2),
#         ("Start and end narrow window (seconds)", "03-07-2025 13:33:37", "03-07-2025 13:33:38", 2),

#         #DOY
#         ("DOY range '184' to '189'", "184", "189", 3),
#         ("DOY range '184 13' to '190 19'", "184 13", "190 19", 3)
#     ]

#     i = 0
#     passed = 0
#     for desc, start, end, expected_count in tests:
#         i += 1
#         print(f"\n--- Test {i}: {desc} ---")
#         try:
#             files = list_files_in_date_range(test_folder, start, end)
#             actual_count = len(files)
#             if actual_count == expected_count:
#                 print("TEST PASSED")
#                 passed += 1
#             else:
#                 print("TEST FAILED")
#                 print(f"Expected {expected_count} files, found {actual_count} files.")
#             #if actual_count > 0:
#                 #for f in files:
#                 #    print(f)
#         except Exception as e:
#             print(f"Error: {e}")
#     print(f"\nTotal tests: {i}, Passed: {passed}, Failed: {i - passed}")
# if __name__ == "__main__":
#     run_tests()
 


###########################################################################################