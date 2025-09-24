import json
import math
import os

import pandas

from src.LCAutomate.model.allocation_matcher import AllocationMatcher
from src.LCAutomate.model.dqi import DQI
from src.LCAutomate.model.exchange_matcher import ExchangeMatcher
from src.LCAutomate.state import State
from src.olca__patched import ipc as olca
from src.olca__patched import schema as olca_schema
from src.LCAutomate.excel_file import ExcelFile
from src.LCAutomate.model.template_process import TemplateProcess, TemplateProcessEncoder, TemplateProcessShortEncoder

from src.LCAutomate.common_simplified import DRIVER_FILENAME, DriverColumnNames, DriverTabNames
from src.LCAutomate.common_simplified import INPUT, OUTPUT
from src.LCAutomate.common_simplified import ReplicationColumnNames, ReplicationTabNames


DC = DriverColumnNames
DT = DriverTabNames
RC = ReplicationColumnNames
RT = ReplicationTabNames


class Model:
    def __init__(self, client: olca.Client, input_root_folder: str, restart: bool):
        self.client = client
        self.base_root_folder = input_root_folder
        self.restart = restart
        # self.base_root_folder_path = os.path.abspath(self.base_root_folder)
        self.driver_df = None
        self.top_level_process_uuid = None
        self.template_processes = {}
        self.state = State(self.base_root_folder)

    def do(self) -> bool:
        if self.restart:
            self.reset()

        model_built = self.build_model()
        if not model_built:
            print("\n*** Correct the errors indicated above before proceeding ***", flush=True)
            return False
        
        state_saved = self.save_state()
        if state_saved:
            print(f"\nSaved model to {self.state.filepath}")
            return True
        else:
            print(f"ERROR: Failed to save model to {self.state.filepath}")
            return False

    def build_model(self) -> bool:
        driver_filepath = os.path.join(self.base_root_folder, DRIVER_FILENAME)
        driver_excel_file = ExcelFile(driver_filepath, DC.list())
        loaded = driver_excel_file.load()
        if not loaded:
            print(f"ERROR: Could not load the driver Excel file {DRIVER_FILENAME}:")
            for validation_error in driver_excel_file.validation_errors:
                print(f"  - {validation_error}")
            return False
        
        if driver_excel_file.sheets.get(DT.MAIN, None) is None:
            print(f"ERROR: Driver Excel file '{DRIVER_FILENAME}' must contain a '{DT.MAIN}' tab:")
            return False

        self.driver_df = driver_excel_file.sheets[DT.MAIN]

        # Find top-level process
        top_level_index = None
        top_level_count = 0
        for i, row in enumerate(self.driver_df[DC.TOP_LEVEL]):
            if isinstance(row, str) and row.strip().lower() == "x":
                top_level_index = i
                top_level_count += 1

        if top_level_count != 1:
            print(f"\nERROR: Column '{DC.TOP_LEVEL}' must contain a single 'x', {top_level_count} found", flush=True)
            return False
        
        self.top_level_process_uuid = self.driver_df[DC.TEMPLATE_PROCESS_UUID][top_level_index]

        # Load template processes
        print(f"\nLoading template processes...", flush=True)
        for i in range(self.driver_df.index.size):
            template_process = self.get_template_process(i)
            if template_process is None:
                return False
            
            self.template_processes[template_process.uuid] = template_process

        # Check that all data suffixes match - use top-level process as standard
        standard_data_columns = self.template_processes[self.top_level_process_uuid].replicants.keys()
        for template_process in self.template_processes.values():
            if template_process.replicants.keys() != standard_data_columns:
                print(f"\nERROR: The replication file for template process '{template_process.name}' does not contain the correct data columns", flush=True)
                extra_columns = []
                for data_column in template_process.replicants.keys():
                    if data_column not in standard_data_columns:
                        extra_columns.append(data_column)
                print(f"  - extra columns: {extra_columns}")
                missing_columns = []
                for data_column in standard_data_columns:
                    if data_column not in template_process.replicants.keys():
                        missing_columns.append(data_column)
                print(f"  - missing columns: {missing_columns}")
                return False

        # Check that the Flow direction column is filled
        for template_process in self.template_processes.values():
            replication_file = template_process.replication_file
            replication_file_df = replication_file.sheets[RT.AMOUNTS]
            for i, flow_direction in enumerate(replication_file_df[RC.DIRECTION]):
                if flow_direction not in [INPUT, OUTPUT]:
                    print(f"\nERROR: Row {i + 2} in the replication file '{replication_file.filepath}' does not contain "
                          f"an accepted flow direction: '{flow_direction}'.  Acceptable values are: '{INPUT}' and '{OUTPUT}'.", flush=True)
                    return False

        print(f"\nBuilding process hierarchy model...", flush=True)
        hierarchy_built = self.recursively_build_hierarchy(self.template_processes[self.top_level_process_uuid], ancestry="root")
        if not hierarchy_built:
            return False
        
        for template_process in self.template_processes.values():
            if not template_process.is_referenced:
                print(f"\nERROR: The template process '{template_process.name}' is not referenced", flush=True)
                return False

        return True
    
    def get_template_process(self, driver_df_index: int) -> TemplateProcess:
        process_name = self.driver_df[DC.TEMPLATE_PROCESS_NAME][driver_df_index]
        print(f"\n  {process_name}")

        # Validate replication file
        filename = self.driver_df[DC.REPLICATION_FILE][driver_df_index]
        replication_filepath = os.path.join(self.base_root_folder, filename)
        replication_excel_file = ExcelFile(replication_filepath, RC.list())
        loaded = replication_excel_file.load()
        if not loaded:
            print(f"\nERROR: Replication file '{replication_filepath}' in row {driver_df_index + 2} cannot be loaded", flush=True)
            for validation_error in replication_excel_file.validation_errors:
                print(f"  - {validation_error}")
            return None

        if RT.AMOUNTS not in replication_excel_file.sheets.keys():
            print(f"\nERROR: Sheet name '{RT.AMOUNTS}' must be in replication file '{replication_filepath}'", flush=True)
            return None

        print(f"  - Valid replication file: {replication_filepath}")
        print(f"    - contains sheets: {list(replication_excel_file.sheets.keys())}")
        unrecognized_sheets = []
        for sheet_name in replication_excel_file.sheets.keys():
            if sheet_name not in RT.list():
                unrecognized_sheets.append(sheet_name)
        if len(unrecognized_sheets) > 0:
            print(f"    - note that these sheets are unrecognized and will be ignored: {unrecognized_sheets}")

        if RT.DQIS in replication_excel_file.sheets.keys():
            reformatted_dqis_sheet_df = DQI.reformat_dqis_sheet_df(replication_excel_file.sheets[RT.DQIS])
            if reformatted_dqis_sheet_df is None:
                print(f"\nERROR: Incorrect formatting of '{RT.DQIS}' sheet in '{replication_filepath}'", flush=True)
                return None
            replication_excel_file.sheets[RT.DQIS] = reformatted_dqis_sheet_df
        
        # Get process from OpenLCA DB
        uuid = self.driver_df[DC.TEMPLATE_PROCESS_UUID][driver_df_index]
        openlca_process = self.client.get(olca_schema.Process, uuid)
        if openlca_process is not None:
            print(f"  - Valid process: {openlca_process.name} ({uuid})")
        else:
            print(f"\nERROR: UUID '{uuid}' in row {driver_df_index + 2} is not found in OpenLCA DB", flush=True)
            return None
        
        replication_base_name = self.driver_df[DC.REPLICATION_BASE_NAME][driver_df_index]

        template_process = TemplateProcess(openlca_process, replication_base_name, replication_excel_file)
        for column in replication_excel_file.sheets[RT.AMOUNTS]:
            if column not in RC.list():
                template_process.replicants[column] = None

        return template_process
            
    def recursively_build_hierarchy(self, template_process: TemplateProcess, ancestry: str) -> bool:
        print(f"{ancestry} -> {template_process.name}")
        template_process.is_referenced = True
        openlca_process = template_process.openlca_process

        # Match exchanges returned from OpenLCA with Amounts sheet
        amounts_sheet_df = template_process.replication_file.sheets[RT.AMOUNTS]
        matched_exchange_index_list = ExchangeMatcher.get_matched_exchange_index_list(
            self.client, openlca_process, amounts_sheet_df
        )
        if matched_exchange_index_list is None:
            return False
        template_process.matched_exchange_index_list = matched_exchange_index_list
        
        # Look for child processes and build their hierarchies
        for exchange_index in matched_exchange_index_list:
            exchange = template_process.openlca_process.exchanges[exchange_index]
            if exchange.default_provider:
                uuid = exchange.default_provider.id
                for i in range(self.driver_df.index.size):
                    if uuid == self.driver_df[DC.TEMPLATE_PROCESS_UUID][i]:
                        child_process = self.template_processes[uuid]
                        template_process.child_processes.append(child_process)
                        built = self.recursively_build_hierarchy(child_process, f"{ancestry} -> {template_process.name}")

                        if not built:
                            return False
                        
        # Match allocations returned from OpenLCA with Physical Allocations sheet (if it exists)
        allocations_sheet_df = template_process.replication_file.sheets.get(RT.PHYSICAL_ALLOCATIONS, None)
        if allocations_sheet_df is not None:
            matched_allocation_index_list = AllocationMatcher.get_matched_allocation_index_list(
                self.client, openlca_process, allocations_sheet_df
            )
            if matched_allocation_index_list is None:
                return False
            template_process.matched_allocation_index_list = matched_allocation_index_list
 
        return True
    
    def reset(self):
        self.state.delete()

    def save_state(self) -> bool:
        state = {
            "top_level_process_uuid": self.top_level_process_uuid,
            "template_processes": self.template_processes,
        }
        state_saved = self.state.save(state)
        return state_saved
