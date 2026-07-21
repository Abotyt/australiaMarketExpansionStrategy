# Library imports
from importlib.resources import files
from typing import Any
import os
import pandas as pd
from pathlib import Path

import string

# Functions
# get list of file names in a directory
def get_file_names_in_directory(directory: str):
    folder_path = Path(directory)

    files = [
        f.name for f in folder_path.iterdir() 
            if f.is_file() and  f.suffix in ('.text', '.xlsx', '.csv', '.parquet')
    ]
    return files

def create_filepaths_dict(directory: str, file_names: list[str]):
    filepaths_dict = {}
    for file_name in file_names:
        key = f"{file_name.split('.')[0]}_Path"
        file_path = os.path.join(directory, file_name)
        filepaths_dict[key] = {
            'file': file_path,
        }
    return filepaths_dict

# read files in a directory
def read_files_in_directory(directory: dict[str, Any]):
    dataframes = {}
    status_tracker = {key: False for key in directory}
    print(f'Tracking initialized. Total files to read: {len(status_tracker)}')

    for key, path in directory.items():
        #Quick check to ensure the file exists physically before reading
        file_path = Path(path['file'])
        if os.path.exists(file_path):
            clean_name = key.replace('_Path', '_Original')

            if file_path.suffix.lower() == '.csv' :
                with open(file_path, 'r') as file:
                    dataframes[clean_name] = pd.read_csv(file, encoding='utf-8')
                    status_tracker[key] = True  # Flip status to True ONLY if read succeeds
                
            elif file_path.suffix.lower() == '.xlsx':
                sheet_name = path['sheet']
                try:
                    dataframes[clean_name] = pd.read_excel(file_path, sheet_name)
                except:
                    print(f'Can\'t detect the sheet: {sheet_name}')
                else:
                    status_tracker[key] = True  # Flip status to True ONLY if read succeeds
            
            elif file_path.suffix.lower() == '.parquet':
                dataframes[clean_name] = pd.read_parquet(file_path)
                status_tracker[key] = True  # Flip status to True ONLY if read succeeds

            else:
                print(f'Can\'t detect the file type of this file: {file_path}')
                
        else:
            print(f'!!!Warning: File not found at: {file_path}')


    #Count how many files were successfully read
    successful_reads = sum(status_tracker.values())
    expected_reads = len(directory)

    print(f'Expected files to read: {expected_reads}')
    print(f'Successfully read files: {successful_reads}')

    # Final Verification Check
    if successful_reads == expected_reads:
        print('Success: Every single file path was successfully read!')
        print('All dataframes are listed below:')
        for key in dataframes:
            print(key)
    else:
        print('Error: Some file paths were skipped or failed to read.')
        # Show exactly which files failed
        for key, status in status_tracker.items():
            if not status:
                print(f'   - Failed to read: {key}')
    
    return dataframes