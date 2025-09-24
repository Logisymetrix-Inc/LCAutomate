import os
import pandas


class ExcelFile:
    def __init__(self, filepath: str, column_names: list):
        self.filepath = filepath
        self.column_names = column_names
        self.validation_errors = []
        self.sheets = {}

    def load(self) -> bool:
        self.validation_errors = []
        if not os.path.isfile(self.filepath):
            self.validation_errors.append(f"ERROR: '{self.filepath}' does not exist")
            return False
        
        try:
            sheets = pandas.read_excel(self.filepath, sheet_name=None, engine="openpyxl")
        except Exception as e:
            self.validation_errors.append(f"ERROR: Could not read '{self.filepath}' as Excel file")
            return False

        # Check column names
        for sheet_name, sheet_df in sheets.items():
            for column_name in self.column_names:
                if sheet_df.get(column_name, None) is None:
                    self.validation_errors.append(f"ERROR: Sheet '{sheet_name}' in '{self.filepath}' must contain column '{column_name}'")
                    return False
            
        self.sheets = sheets
        return True
    
    def save(self, sheets: list) -> bool:
        # Check column names
        for sheet_name, sheet_df in sheets.items():
            for column_name in self.column_names:
                if sheet_df.get(column_name, None) is None:
                    self.validation_errors.append(f"ERROR: Input DataFrame '{sheet_name}' must contain column '{column_name}'")
                    return False

        self.sheets = sheets

        try:
            with pandas.ExcelWriter(self.filepath) as writer:
                for sheet_name, sheet_df in self.sheets.items():
                    sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
                return True
        except Exception as e:
            self.validation_errors.append(f"ERROR: Error on pandas.ExcelWriter.to_excel() call: {e}")
            return False
