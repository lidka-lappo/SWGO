import os
import pandas as pd

def save_processed_data(final_data, file_path):
    folder, filename = os.path.split(file_path)
    name, ext = os.path.splitext(filename)
    #processed_folder = os.path.join(folder, f"processed_{os.path.basename(folder)}")
    processed_file = f"processed_{name}{ext}"
    processed_folder = f"processed_{os.path.basename(folder)}"

    # ensure processed folder exists
    os.makedirs(processed_folder, exist_ok=True)

    # full path to save file
    output_path = os.path.join(processed_folder, processed_file)

    # save DataFrame
    final_data.to_csv(output_path, index=False)

    print(f"Saved processed file to: {output_path}")