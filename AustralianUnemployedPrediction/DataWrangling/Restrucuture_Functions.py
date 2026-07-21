# Library imports
from typing import Any

import pandas as pd
import string

# Functions
# Update the column names of the dataset
def update_column_names(dataset: pd.DataFrame):
    column_names = dataset.columns.tolist()
    for i in range(len(column_names)):
        column_name = column_names[i].lower()
        punctuation_removed = column_name.translate(
            str.maketrans(
                '',
                '',
                string.punctuation.replace('_', '')
            )
        )
        column_names[i] = punctuation_removed.replace(' ', '_')
    dataset.columns = column_names
    return dataset

def transpose_dataset (dataset: pd.DataFrame):
    
    # Extract the first eight rows into metadata and transpose the matrix
    meta_data = dataset.iloc[:9].copy().T

    # reset index
    meta_data = meta_data.reset_index()

    return meta_data

def parse_column(dataset: pd.DataFrame, column: str, split_by = ';', labels = None):
    
    # assign values to a list in first column
    variables_original = dataset[column]

    records = []
    strip_chars = string.whitespace + string.punctuation + string.digits


    for a_row in variables_original:    
        splited_object = a_row.split(split_by)

        splited_object = [
            item.strip(strip_chars) 
            for item in splited_object
        ]

        # create a labels if there is no labels provided
        if labels is None:
            current_labels = [
                f"attribute_{i+1}" 
                for i in range(len(splited_object))
            ]
        else:
            current_labels = labels
        
        # append the values to the list
        records.append(
            dict(
                zip(
                    current_labels, 
                    splited_object
                )
            )
        )

        records_dataframes = pd.DataFrame(records)
    
    return records_dataframes


# extract metadata from the original dataset
def extract_metadata (dataset: pd.DataFrame, split_by = ';', labels = None):
    # transpose dataset and reset index
    meta_data = transpose_dataset(dataset)

    # extract first row and use it as column names
    new_columns = list(meta_data.iloc[0])

    # update column format
    for i in range(len(new_columns)):
        column_name = new_columns[i].lower()
        punctuation_removed = column_name.translate(
            str.maketrans(
                '',
                '',
                string.punctuation.replace('_', '')
            )
        )
        new_columns[i] = punctuation_removed.replace(' ', '_')
        
    # assign, remove first row, reset index
    meta_data.columns = new_columns
    mata_data_updated_columns = meta_data.iloc[1:].reset_index(drop = True)

    # update the first column name
    column_name = 'parse_column'

    first_column = mata_data_updated_columns.columns[0]
    mata_data_updated_columns.rename(
        columns={first_column : column_name}, 
        inplace = True
    )
    # parsed the first column into multiple columns
    parsed_data = parse_column(mata_data_updated_columns, column_name, split_by, labels)

    # combine the parsed data with the original metadata and remove the parsed column
    number_of_info = 0
    threshold = 10
    for col in parsed_data.columns:
        mata_data_updated_columns[col] = parsed_data[col]
        number_of_info += 1
        if number_of_info == threshold:
            print(f'First {threshold} columns parsed.')
            break

    final_data = mata_data_updated_columns.drop(columns=[column_name])
    
    return final_data



# # extract metadata from the original dataset
# def extract_metadata (dataset: pd.DataFrame, column: str, split_by = ';', labels = None):
#     # transpose dataset and reset index
#     meta_data = transpose_dataset(dataset)

#     # extract first row and use it as column names
#     new_columns = list(meta_data.iloc[0])

#     # update column format
#     for i in range(len(new_columns)):
#         column_name = new_columns[i].lower()
#         punctuation_removed = column_name.translate(
#             str.maketrans(
#                 '',
#                 '',
#                 string.punctuation.replace('_', '')
#             )
#         )
#         new_columns[i] = punctuation_removed.replace(' ', '_')
        
#     # assign, remove first row, reset index
#     meta_data.columns = new_columns
#     mata_data_updated_columns = meta_data.iloc[1:].reset_index(drop = True)

#     # update the first column name
#     first_column = mata_data_updated_columns.columns[0]
#     mata_data_updated_columns.rename(
#         columns={first_column : 'variable'}, 
#         inplace = True
#     )
    
#     # assign values to a list in first column
#     variables_original = list(mata_data_updated_columns['variable'])

#     # Split the variable with genders
#     variables = []
#     genders = []
#     for i, o in enumerate(variables_original):
#         splited_object = o.split(';')

#         #get the variable and gender from the string
#         one_variable = splited_object[0].strip()

#         # remove whitespace, punctuation and digits
#         strip_chars = string.whitespace + string.punctuation + string.digits
#         one_gender = splited_object[1].strip(strip_chars)

#         # append the values to the list
#         variables.append(one_variable)
#         genders.append(one_gender)

#     # add gender and variable to the dataset
#     mata_data_updated_columns.insert(
#         loc = 1, 
#         column = 'gender', 
#         value = genders
#     )
#     mata_data_updated_columns['variable'] = variables
    
#     return mata_data_updated_columns

# melt and update the columns names
def melt_and_update_columns(dataset: pd.DataFrame, add_columns: dict[str, Any] |None = None):
    # get data below row 9 where stored series ID, values and record date
    value_dataset = dataset.iloc[9:].copy()

    # Get series ID
    series_id = dataset.loc[8]
    
    # use series ID as new columnnames
    value_series_id = value_dataset.rename(columns = series_id)

    # update the first column name to 'date'
    value_date = value_series_id.rename(columns = {'Series ID': 'date'})

    #melt the data set
    value_melted = pd.melt(
        value_date, 
        id_vars = 'date', 
        var_name = 'series_id', 
        value_name='value'
    )

    if add_columns is not None:
        for column, value in add_columns.items():
            value_melted[column] = value

    return value_melted

# merge the metadata and the melted dataset
def merge_metadata_and_melted_dataset(
    metadata: pd.DataFrame, 
    melted_dataset: pd.DataFrame,
    selected_columns: list
):

    # select column to merge
    selected_metadata = metadata[selected_columns]

    # Merge df1 and df2 using the shared column 'series_id'
    final_dataset = pd.merge(
        melted_dataset, 
        selected_metadata, 
        on='series_id', 
        how='left'
    )

    return final_dataset
