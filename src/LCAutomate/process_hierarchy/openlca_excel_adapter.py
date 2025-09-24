import os
import math
import shutil
import pandas
import json

from src.LCAutomate.common import SheetNames
from src.LCAutomate.common import GeneralInformationKeys
from src.LCAutomate.common import InputsKeys
from src.LCAutomate.common import OutputsKeys
from src.LCAutomate.common import AllocationKeys
from src.LCAutomate.common import FlowsKeys
from src.LCAutomate.common import UnitsKeys
from src.LCAutomate.common import OpenLCAUnitsKeys
from src.LCAutomate.common import ConsolidatedFlowKeys
from src.LCAutomate.common import INPUT, OUTPUT

from src.LCAutomate.process_hierarchy.general_information_validator import GeneralInformationValidator


class OpenLCAExcelAdapter:
    def __init__(self, input_root_folder_path: str, file_relpath: str):
        self.input_root_folder_path = input_root_folder_path
        self.file_relpath = file_relpath
        self.input_file_path = os.path.join(self.input_root_folder_path, self.file_relpath)
        self.sheets = {}
        self.validation_errors = self.validate()
        self.flow_addresses = {}
        if len(self.validation_errors) == 0:
            self.get_flows()

    def validate(self) -> list:
        validation_errors = []
        # Check if file exists
        if not os.path.isfile(self.input_file_path):
            validation_errors.append(f"Not a file: {self.file_relpath}")
            return validation_errors

        # Validate as Excel spreadsheet
        validation_errors.extend(self._validate_as_excel())
        if validation_errors:
            return validation_errors

        # Check sheet names
        for sheet_name in SheetNames.list():
            sheet_df = self._get_sheet_df(sheet_name)
            if sheet_df is None:
                validation_errors.append(f"Missing worksheet: {sheet_name}")
        if validation_errors:
            return validation_errors

        # Store the sheets as dicts
        df = pandas.ExcelFile(self.input_file_path, engine="openpyxl")
        for sheet_name in df.sheet_names:
            sheet_df = self._get_sheet_df(sheet_name)
            sheet = sheet_df.to_dict()
            self.sheets[sheet_name] = sheet

        return validation_errors

    def _validate_as_excel(self) -> list:
        # Try to import file as Excel, ignore exception as indicating that file is not Excel
        try:
            pandas.read_excel(self.input_file_path, engine="openpyxl")
            return []
        except Exception as e:
            return [f"Error on test read of Excel file: {e}"]

    def _get_sheet_df(self, sheet_name: str) -> pandas.DataFrame:
        try:
            sheet_df = pandas.read_excel(self.input_file_path, sheet_name, engine="openpyxl")
            return sheet_df
        except Exception as e:
            return None

    def get_general_information(self) -> dict:
        general_information = {}

        sheet = self.sheets[SheetNames.GENERAL_INFORMATION]
        general_information_column = sheet["General information"]
        column_1 = sheet["Unnamed: 1"]
        for i in range(len(general_information_column)):
            row_name = general_information_column[i]
            if row_name in GeneralInformationKeys.list():
                if row_name == GeneralInformationKeys.NAME:
                    general_information[row_name] = os.path.splitext(os.path.basename(self.file_relpath))[0]
                else:
                    general_information[row_name] = column_1[i]

        return general_information

    def put_general_information(self, general_information: dict):
        sheet = self.sheets[SheetNames.GENERAL_INFORMATION]
        general_information_column = sheet["General information"]
        column_1 = sheet["Unnamed: 1"]
        for i in range(len(general_information_column)):
            row_name = general_information_column[i]
            if row_name in GeneralInformationKeys.list():
                column_1[i] = general_information[row_name]

        return

    def get_flows(self) -> dict:
        flows = {}
        flows_sheet = self.sheets[SheetNames.FLOWS]
        flow_count = len(flows_sheet[FlowsKeys.UUID])
        for i in range(flow_count):
            flow = {}
            flow_addresses = {}
            for column_name in FlowsKeys.list():
                flow[column_name] = flows_sheet[column_name][i]
                flow_addresses[column_name] = {"sheet": SheetNames.FLOWS, "column": column_name, "row": i}
            flows[i] = {"values": flow, "addresses": flow_addresses}

        inputs = {}
        inputs_sheet = self.sheets[SheetNames.INPUTS]
        input_count = len(inputs_sheet[InputsKeys.FLOW])
        for i in range(input_count):
            input_dict = {}
            input_addresses = {}
            for column_name in InputsKeys.list():
                input_dict[column_name] = inputs_sheet[column_name][i]
                input_addresses[column_name] = {"sheet": SheetNames.INPUTS, "column": column_name, "row": i}
            inputs[i] = {"values": input_dict, "addresses": input_addresses}

        outputs = {}
        outputs_sheet = self.sheets[SheetNames.OUTPUTS]
        output_count = len(outputs_sheet[OutputsKeys.FLOW])
        for i in range(output_count):
            output_dict = {}
            output_addresses = {}
            for column_name in OutputsKeys.list():
                output_dict[column_name] = outputs_sheet[column_name][i]
                output_addresses[column_name] = {"sheet": SheetNames.OUTPUTS, "column": column_name, "row": i}
            outputs[i] = {"values": output_dict, "addresses": output_addresses}

        allocations = {}
        allocation_sheet = self.sheets[SheetNames.ALLOCATION]
        product_column = allocation_sheet["Default allocation method"]
        physical_column = allocation_sheet["Unnamed: 2"]
        allocation_count = len(product_column)
        for i in range(2, allocation_count):
            if product_column[i] == AllocationKeys.CAUSAL_ALLOCATION:
                break
            allocation = {}
            allocation_addresses = {}
            allocation[AllocationKeys.PRODUCT] = product_column[i]
            allocation[AllocationKeys.PHYSICAL] = physical_column[i]
            allocation_addresses[AllocationKeys.PRODUCT] = {"sheet": SheetNames.ALLOCATION, "column": "Default allocation method", "row": i}
            allocation_addresses[AllocationKeys.PHYSICAL] = {"sheet": SheetNames.ALLOCATION, "column": "Unnamed: 2", "row": i}
            allocations[i] = {"values": allocation, "addresses": allocation_addresses}

        # Now loop through inputs/outputs.  For each input/output, loop through flows and allocations.
        # Look for matches between input/output.flow and flow.name or allocation.product
        #   - add columns when matches found
        #   - add Flow direction column = Input/Output

        consolidated_flows = {}
        consolidated_flow_index = 0

        # Start with inputs
        for input_dict in inputs.values():
            consolidated_flow = {}
            consolidated_flow_addresses = {}
            consolidated_flow[ConsolidatedFlowKeys.FLOW_DIRECTION] = INPUT
            for inputs_key in InputsKeys.list():
                if inputs_key == InputsKeys.DESCRIPTION:
                    key = ConsolidatedFlowKeys.INPUT_OUTPUT_DESCRIPTION
                else:
                    key = inputs_key

                consolidated_flow[key] = input_dict["values"][inputs_key]
                consolidated_flow_addresses[key] = input_dict["addresses"][inputs_key]

            input_flow_name = input_dict["values"][InputsKeys.FLOW]
            for flow in flows.values():
                if flow["values"][FlowsKeys.NAME] == input_flow_name:
                    for flows_key in FlowsKeys.list():
                        if flows_key == FlowsKeys.NAME:
                            pass
                        else:
                            if flows_key == FlowsKeys.DESCRIPTION:
                                key = ConsolidatedFlowKeys.FLOW_DESCRIPTION
                            else:
                                key = flows_key

                            consolidated_flow[key] = flow["values"][flows_key]
                            consolidated_flow_addresses[key] = flow["addresses"][flows_key]

            for allocation in allocations.values():
                if allocation["values"][AllocationKeys.PRODUCT] == input_flow_name:
                    for allocation_key in AllocationKeys.list():
                        if allocation_key != AllocationKeys.PRODUCT:
                            consolidated_flow[allocation_key] = allocation["values"][allocation_key]
                            consolidated_flow_addresses[allocation_key] = allocation["addresses"][allocation_key]

            consolidated_flows[consolidated_flow_index] = consolidated_flow
            self.flow_addresses[consolidated_flow_index] = consolidated_flow_addresses
            consolidated_flow_index += 1

        # Then do outputs
        for output_dict in outputs.values():
            consolidated_flow = {}
            consolidated_flow_addresses = {}
            consolidated_flow[ConsolidatedFlowKeys.FLOW_DIRECTION] = OUTPUT
            for outputs_key in OutputsKeys.list():
                if outputs_key == OutputsKeys.DESCRIPTION:
                    key = ConsolidatedFlowKeys.INPUT_OUTPUT_DESCRIPTION
                else:
                    key = outputs_key

                consolidated_flow[key] = output_dict["values"][outputs_key]
                consolidated_flow_addresses[key] = output_dict["addresses"][outputs_key]

            output_flow_name = output_dict["values"][OutputsKeys.FLOW]
            for flow in flows.values():
                if flow["values"][FlowsKeys.NAME] == output_flow_name:
                    for flows_key in FlowsKeys.list():
                        if flows_key == FlowsKeys.NAME:
                            pass
                        else:
                            if flows_key == FlowsKeys.DESCRIPTION:
                                key = ConsolidatedFlowKeys.FLOW_DESCRIPTION
                            else:
                                key = flows_key

                            consolidated_flow[key] = flow["values"][flows_key]
                            consolidated_flow_addresses[key] = flow["addresses"][flows_key]

            for allocation in allocations.values():
                if allocation["values"][AllocationKeys.PRODUCT] == output_flow_name:
                    for allocation_key in AllocationKeys.list():
                        if allocation_key != AllocationKeys.PRODUCT:
                            allocation_value = allocation["values"].get(allocation_key, None)
                            if allocation_value is not None:
                                    consolidated_flow[allocation_key] = allocation_value
                                    consolidated_flow_addresses[allocation_key] = allocation["addresses"][allocation_key]

            consolidated_flows[consolidated_flow_index] = consolidated_flow
            self.flow_addresses[consolidated_flow_index] = consolidated_flow_addresses
            consolidated_flow_index += 1

        # It is also necessary to add the unit group corresponding to the unit of each flow
        units_lookup = {}
        units_sheet = self.sheets[SheetNames.UNITS]
        unit_count = len(units_sheet[UnitsKeys.UUID])
        for i in range(unit_count):
            unit_name = units_sheet[UnitsKeys.NAME][i]
            if unit_name not in units_lookup:
                units_lookup[unit_name] = {
                    OpenLCAUnitsKeys.ID: units_sheet[UnitsKeys.UUID][i],
                    OpenLCAUnitsKeys.OLCA_TYPE: "Unit",
                    OpenLCAUnitsKeys.NAME: unit_name,
                    OpenLCAUnitsKeys.DESCRIPTION: units_sheet[UnitsKeys.DESCRIPTION][i],
                    OpenLCAUnitsKeys.CONVERSION_FACTOR: units_sheet[UnitsKeys.CONVERSION_FACTOR][i],
                }

        for index in consolidated_flows:
            consolidated_flow = consolidated_flows[index]
            unit_name = consolidated_flow[ConsolidatedFlowKeys.UNIT]
            unit_descriptor = units_lookup[unit_name]
            consolidated_flow[ConsolidatedFlowKeys.UNIT_DESCRIPTOR] = unit_descriptor

        return consolidated_flows
    
    def put_flows(self, consolidated_flows):
        for index in consolidated_flows:
            consolidated_flow = consolidated_flows[index]
            consolidated_flow_addresses = self.flow_addresses[index]
            for key in ConsolidatedFlowKeys.list():
                value = consolidated_flow.get(key)
                address = consolidated_flow_addresses.get(key)
                if value and address:
                    sheet = self.sheets[address["sheet"]]
                    sheet[address["column"]][address["row"]] = value

    def write(self, output_root_folder_path, output_file_relpath=None):
        if not output_file_relpath:
            output_file_relpath = self.file_relpath
        output_file_path = os.path.join(output_root_folder_path, output_file_relpath)
 
        parts = output_file_relpath.split("\\")
        if len(parts) == 1:
            # No action required
            pass
        elif len(parts) == 2:
            # May need to create the sub-folder
            sub_folder = parts[0]
            output_sub_folder_path = os.path.join(output_root_folder_path, sub_folder)
            if not os.path.isdir(output_sub_folder_path):
                os.mkdir(output_sub_folder_path)
        else:
            # This is an error condition
            print(f"ERROR: {output_file_relpath} must be a simple filename or a single sub-folder plus a filename, stopping")
            return

        with pandas.ExcelWriter(output_file_path) as writer:
            for sheet_name in self.sheets:
                sheet = self.sheets[sheet_name]
                sheet_df = pandas.DataFrame.from_dict(sheet)
                sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
  