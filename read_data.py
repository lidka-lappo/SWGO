import os
import re
import numpy as np

folder = 'sweap_202_205/'
allowed_days = {"202", "203", "204", "205" }  # as strings to match extracted substrings
# Parameters
#chunkSize = 10000
strTh = 100
strips = 4

QOffSets1 = np.array([[71, 75], [78, 77], [70, 70], [83, 80]])
QOffSets2 = np.array([[77, 80], [80, 85], [75, 75], [60, 70]])


with open(folder + 'list.txt') as f:
    file_list = [line.strip() for line in f]
datasets = [os.path.join(folder, fname) for fname in file_list]
#print("Datasets loaded:")
#for dataset in datasets:
#    print(dataset)


def extract_doy(filename):
    match = re.search(r'sest\d{2}(\d{3})\d{6}\.mat', filename)
    if match:
        return match.group(1)  # returns DOY as string
    return None

# Filter your dataset list
filtered_datasets = [f for f in datasets if extract_doy(os.path.basename(f)) in allowed_days]
# Use filtered list
datasets = filtered_datasets
print(f"Total datasets: {len(datasets)}")

for file_idx in range(len(datasets)):
#for file_idx in range(10):
    dataset_file = datasets[file_idx]
    if not os.path.exists(dataset_file):
      print(f"File not found, skipping: {dataset_file}")
      continue