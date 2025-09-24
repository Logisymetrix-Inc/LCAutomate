import json
import uuid
import pandas
import copy

from src.LCAutomate.excel_file import ExcelFile
from src.olca__patched import schema as olca_schema

from src.LCAutomate.common_simplified import DRIVER_FILENAME, DriverColumnNames
from src.LCAutomate.common_simplified import ReplicationColumnNames


DC = DriverColumnNames
RC = ReplicationColumnNames


class TemplateProcess:
    def __init__(
            self, 
            openlca_process: olca_schema.Process, 
            replication_base_name: str, 
            replication_file: ExcelFile,
            ):
        self.openlca_process = openlca_process
        self.name = openlca_process.name
        self.uuid = openlca_process.id
        self.replication_base_name = replication_base_name
        self.replication_file = replication_file

        self.is_referenced = False
        self.matched_exchange_index_list = None
        self.matched_allocation_index_list = None
        self.child_processes = []
        self.replicants = {}
        self.product_systems = {}

    def clone_openlca_process(self) -> olca_schema.Process:
        clone = copy.deepcopy(self.openlca_process)
        clone.id = str(uuid.uuid4())
        return clone


class TemplateProcessEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, TemplateProcess):
            sheets = []
            for sheet_df in obj.replication_file.sheets:
                sheet_json = json.loads(sheet_df.to_json())
                sheets.append(sheet_json)
            return {
                "name": obj.name,
                "uuid": obj.uuid,
                "is_referenced": obj.is_referenced,
                "matched_exchange_index_list": obj.matched_exchange_index_list,
                "matched_allocation_index_list": obj.matched_allocation_index_list,
                "child_processes": obj.child_processes,
                "replicants": obj.replicants,
                "openlca_process": obj.openlca_process.to_json(),
                "replication_base_name": obj.replication_base_name,
                "replication_file": sheets,
                }
        return super().default(obj)


class TemplateProcessShortEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, TemplateProcess):
            suppressed_str = "Suppressed, use TemplateProcessEncoder for full JSON"

            openlca_process_short_json = obj.openlca_process.to_json()
            openlca_process_short_json["allocationFactors"] = suppressed_str
            openlca_process_short_json["exchanges"] = suppressed_str

            replication_file_df_short_json = {}
            for sheet_name, sheet_df in obj.replication_file.sheets.items():
                sheet_short_json = {}
                for column_name in sheet_df:
                    if column_name in RC.list():
                        sheet_short_json[column_name] = json.loads(sheet_df[column_name].to_json())
                sheet_short_json["data_columns"] = suppressed_str
                replication_file_df_short_json[sheet_name] = sheet_short_json

            child_processes = []
            for child_process in obj.child_processes:
                child_processes.append(child_process.name)

            return {
                "name": obj.name,
                "uuid": obj.uuid,
                "is_referenced": obj.is_referenced,
                "matched_exchange_index_list": obj.matched_exchange_index_list,
                "matched_allocation_index_list": obj.matched_allocation_index_list,
                "child_processes": child_processes,
                "replicants": obj.replicants,
                "openlca_process": openlca_process_short_json,
                "replication_base_name": obj.replication_base_name,
                "replication_file": replication_file_df_short_json,
                }
        return super().default(obj)

