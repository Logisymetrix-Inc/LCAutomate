import pandas as pd
import re
from os import walk
import json


class Ingestion:
    
    @staticmethod
    def get_value_from_filename(column, filename):
        match = re.search(column["spec"], filename)
        value = match.group(1)
        return value
    
    @staticmethod
    def extend_pivot_data(this_pivot_data, next_pivot_data):
        this_len = len(this_pivot_data)
        next_len = len(next_pivot_data)
        if this_len == next_len:
            return(this_pivot_data)
        else:
            # We assume that this_len is <= next_len
            # We further assume that next_len is an integer multiple of this_len
            multiplier = int(next_len / this_len)
            extended_pivot_data = []
            for i in range(this_len):
                extended_pivot_data.extend([this_pivot_data[i]] * multiplier)
            return(extended_pivot_data)

    @staticmethod
    def extract_values_by_spec(json_data, spec_tokens, spec_index):
        values = []
        pivots = {}

        final_index = len(spec_tokens) - 1
        if spec_index > final_index:
            return (values, pivots)
        elif spec_index == final_index:
            spec_token = spec_tokens[spec_index]
            if spec_token == "<>":
                # It's useless to have the list token at the end of the spec
                return (values, pivots)
            elif spec_token == "__keys__<>":
                # It's useless to have the key list token at the end of the spec
                return (values, pivots)
            elif re.search("^<(.+)>$", spec_token):
                match = re.search("^<(.+)>$", spec_token)
                values = [json_data[int(match.group(1))]]
                return (values, pivots)
            elif re.search("^__keys__<(.+)>$", spec_token):
                match = re.search("^__keys__<(.+)>$", spec_token)
                values = [list(json_data.keys())[int(match.group(1))]]
                return (values, pivots)
            else:
                values = [json_data[spec_token]]
                return (values, pivots)
        else:
            # Before the final token, i.e. the general case
            spec_token = spec_tokens[spec_index]
            spec_index += 1
            if spec_token == "<>":
                # iterate over json_data which should be a list at this point
                pivot_name = f"pivot_{spec_index - 1}"
                values = []
                pivots = {pivot_name: []}
                pivot_value = 0
                for item in json_data:
                    temp_spec_index = spec_index
                    (extracted_values, extracted_pivots) = Ingestion.extract_values_by_spec(
                        item, spec_tokens, temp_spec_index)
                    values.extend(extracted_values)
                    pivots[pivot_name].append(pivot_value)
                    pivot_value += 1
                    for extracted_pivot in extracted_pivots:
                        if extracted_pivot not in pivots:
                            pivots[extracted_pivot] = extracted_pivots[extracted_pivot].copy()
                        else:
                            pivots[extracted_pivot].extend(extracted_pivots[extracted_pivot])
                for i in range(len(pivots) - 1):
                    this_pivot_name = list(pivots.keys())[i]
                    next_pivot_name = list(pivots.keys())[i+1]
                    this_pivot_data = pivots[this_pivot_name]
                    next_pivot_data = pivots[next_pivot_name]
                    pivots[this_pivot_name] = Ingestion.extend_pivot_data(this_pivot_data, next_pivot_data)
                return (values, pivots)
            elif spec_token == "__keys__<>":
                # iterate over json_data which should be a dict at this point
                pivot_name = f"pivot_{spec_index - 1}"
                values = []
                pivots = {pivot_name: []}
                pivot_value = 0
                for key in json_data:
                    temp_spec_index = spec_index
                    (extracted_values, extracted_pivots) = Ingestion.extract_values_by_spec(json_data[key], spec_tokens, temp_spec_index)
                    values.extend(extracted_values)
                    pivots[pivot_name].append(pivot_value)
                    pivot_value += 1
                    for extracted_pivot in extracted_pivots:
                        if extracted_pivot not in pivots:
                            pivots[extracted_pivot] = extracted_pivots[extracted_pivot].copy()
                        else:
                            pivots[extracted_pivot].extend(extracted_pivots[extracted_pivot])
                for i in range(len(pivots) - 1):
                    this_pivot_name = list(pivots.keys())[i]
                    next_pivot_name = list(pivots.keys())[i+1]
                    this_pivot_data = pivots[this_pivot_name]
                    next_pivot_data = pivots[next_pivot_name]
                    pivots[this_pivot_name] = Ingestion.extend_pivot_data(this_pivot_data, next_pivot_data)
                return (values, pivots)
            elif re.search("^<(.+)>$", spec_token):
                match = re.search("^<(.+)>$", spec_token)
                (values, pivots) = Ingestion.extract_values_by_spec(json_data[int(match.group(1))], spec_tokens, spec_index)
                return (values, pivots)
            elif re.search("^__keys__<(.+)>$", spec_token):
                match = re.search("^__keys__<(.+)>$", spec_token)
                # Find what the key actually is, i.e. __key__[0] is the 0th key in the list of keys for the json_data at this depth
                key = list(json_data.keys())[int(match.group(1))]
                (values, pivots) = Ingestion.extract_values_by_spec(json_data[key], spec_tokens, spec_index)
                return (values, pivots)
            else:
                (values, pivots) = Ingestion.extract_values_by_spec(json_data[spec_token], spec_tokens, spec_index)
                return (values, pivots)

    @staticmethod
    def get_values_from_json(column, json_data):
        spec = column["spec"]
        spec_tokens = spec.split(".")
        spec_index = 0
        (values, pivots) = Ingestion.extract_values_by_spec(json_data, spec_tokens, spec_index)
        return (values, pivots)

    @staticmethod
    def create_dataframes(dataframe_creation_list):
        """
        This is the key code for ingestion.
        """
        dataframes = {}

        for dataframe_creation in dataframe_creation_list:
            dataframe_name = dataframe_creation["dataframe_name"]
            creation_method = dataframe_creation["creation_method"]
            if creation_method == "read_from_json_files":
                print("\n")
                print(f"Dataframe {dataframe_name} will be created from JSON files")
                column_names = []
                column_data_dict = {}
                for column in dataframe_creation["columns"]:
                    column_names.append(column["column_name"])
                    column_data_dict[column["column_name"]] = {
                        "filenames": [],
                        "values": [],
                        "pivots": {}
                    }

                input_dir = dataframe_creation["input_dir"]
                filenames = next(walk(input_dir), (None, None, []))[2]  # [] if no file
                file_selection_regex = dataframe_creation["file_selection_regex"]

                # Loop through files
                for filename in filenames:
                    match = re.search(file_selection_regex, filename)
                    if match:
                        print(f"Processing {filename}")
                        filepath = f"{input_dir}{filename}"
                        with open(filepath) as fp:
                            json_data = json.load(fp)
                            for column in dataframe_creation["columns"]:
                                column_name = column["column_name"]
                                source = column["source"]
                                if source == "from_filename":
                                    value = Ingestion.get_value_from_filename(column, filename)
                                    column_data_dict[column["column_name"]]["filenames"].append(filename)
                                    column_data_dict[column["column_name"]]["values"].append(value)
                                elif source == "from_json":
                                    (values, pivots) = Ingestion.get_values_from_json(column, json_data)
                                    filenames = [filename] * len(values)
                                    column_data_dict[column["column_name"]]["filenames"].extend(filenames)
                                    column_data_dict[column["column_name"]]["values"].extend(values)
                                    for pivot in pivots:
                                        if pivot not in column_data_dict[column["column_name"]]["pivots"]:
                                            column_data_dict[column["column_name"]]["pivots"][pivot] = pivots[pivot].copy()
                                        else:
                                            column_data_dict[column["column_name"]]["pivots"][pivot].extend(pivots[pivot])
                                else:
                                    print(f"Source '{source} is not recognized")
                                    break

                    merged_df = None
                    left_pivot_list = ["filename"]
                    for column_name in column_names:
                        data = {
                            "filename": column_data_dict[column_name]["filenames"],
                            column_name: column_data_dict[column_name]["values"]
                        }
                        right_pivot_list = ["filename"]
                        for pivot in column_data_dict[column_name]["pivots"]:
                            right_pivot_list.append(pivot)
                            data[pivot] = column_data_dict[column_name]["pivots"][pivot]
                        if merged_df is None:
                            merged_df = pd.DataFrame(data)
                            left_pivot_list = right_pivot_list.copy()
                        else:
                            column_df = pd.DataFrame(data)
                            common_pivot_list = []
                            for pivot in left_pivot_list:
                                if pivot in right_pivot_list:
                                    common_pivot_list.append(pivot)
                            merged_df = merged_df.merge(
                                column_df, how='outer', left_on=common_pivot_list, right_on=common_pivot_list
                            )
                            for pivot in column_data_dict[column_name]["pivots"]:
                                if pivot not in left_pivot_list:
                                    left_pivot_list.append(pivot)
                dataframes[dataframe_name] = merged_df.drop(columns=common_pivot_list)
            elif creation_method == "merge":
                left_df_name = dataframe_creation["left_dataframe"]
                right_df_name = dataframe_creation["right_dataframe"]
                merge_how = dataframe_creation.get("merge_how", "outer")
                print("\n")
                print(f"Dataframe {dataframe_name} will be merged from {left_df_name} and {right_df_name}, merge_how: {merge_how}")
                left_df = dataframes[left_df_name]
                right_df = dataframes[right_df_name]
                left_merge_columns = dataframe_creation["left_merge_columns"]
                right_merge_columns = dataframe_creation["right_merge_columns"]
                dataframes[dataframe_name] = left_df.merge(
                    right_df, how=merge_how, left_on=left_merge_columns, right_on=right_merge_columns
                )
            else:
                print(f"Creation method '{creation_method} is not recognized")
                break

        return dataframes
