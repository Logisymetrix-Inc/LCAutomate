from datetime import datetime, timezone
import json
import math
from src.LCAutomate.model.dqi import DQI, PedigreeMatrix
from src.LCAutomate.model.template_process import TemplateProcess, TemplateProcessShortEncoder
from src.olca__patched import ipc as olca
from src.olca__patched import schema as olca_schema

from src.LCAutomate.common_simplified import (
    INPUT,
    OUTPUT,
)
from src.LCAutomate.common_simplified import ReplicationTabNames, ReplicationColumnNames
from src.LCAutomate.common_simplified import DQISubColumnNames


RT = ReplicationTabNames
RC = ReplicationColumnNames

        
class SingleProcessCreator():
    def __init__(self, client: olca.Client, template_process: TemplateProcess):
        self.client = client
        self.template_process = template_process
        self.created_process_uuid = None
        self.created_process_name = None

    def create(self, data_column_name: str) -> bool:
        self.created_process_uuid = None
        self.created_process_name = None

        # We assume that all child processes have been created in advance of this call.  If not, there will be an error return.
        cloned_openlca_process = self.template_process.clone_openlca_process()
        cloned_openlca_process.name = self.get_process_name(data_column_name)

        # Delete any pre-existing instances
        deleted = self.delete(data_column_name)
        if not deleted:
            return False
        
        # Get current UTC datetime
        utc_time_dt = datetime.now(timezone.utc)
        utc_time_iso_format = f"{utc_time_dt.isoformat()[:-9]}Z"

        cloned_openlca_process.description = (
            f'{cloned_openlca_process.name}\n'
            f'Added as a new process using the olca-ipc python API at {utc_time_iso_format}.\n'
            f'Template process: {self.template_process.openlca_process.name} ({self.template_process.openlca_process.id})\n'
            f'Replication file: {self.template_process.replication_file.filepath}'
        )
        cloned_openlca_process.last_change = utc_time_iso_format

        # Substitutions based on Amounts sheet
        amounts_substituted = self.do_amount_substitutions(cloned_openlca_process, data_column_name)
        if not amounts_substituted:
            return False
        
        # Substitutions based on Physical Allocations sheet
        allocations_substituted = self.do_allocation_substitutions(cloned_openlca_process, data_column_name)
        if not allocations_substituted:
            return False

        # Substitutions based on DQIs sheet
        dqis_substituted = self.do_dqi_substitutions(cloned_openlca_process, data_column_name)
        if not dqis_substituted:
            return False

        ipc_server_response = self.client.insert(cloned_openlca_process)
        self.created_process_uuid = ipc_server_response.get("@id", None)
        self.created_process_name = ipc_server_response.get("name", None)
        if (not self.created_process_uuid is None) and (not self.created_process_name is None):
            print('Process: \033[1m' + cloned_openlca_process.name, '\033[0m' +'succesfully imported to olca database', flush=True)
            return True
        else:
            return False

    def get_process_name(self, data_column_name: str) -> str:
        return f"{self.template_process.replication_base_name} - {data_column_name}"
    
    def delete(self, data_column_name: str) -> bool:
        process_name = self.get_process_name(data_column_name)
        try:
            pre_existing_process = self.client.find(olca_schema.Process, process_name)
            while pre_existing_process:
                self.client.delete(pre_existing_process)
                pre_existing_process = self.client.find(olca_schema.Process, process_name)
            return True
        except Exception as e:
            print(f"ERROR: Problem deleting pre-existing processes: {e}")
            return False

    def do_amount_substitutions(self, cloned_openlca_process: olca_schema.Process, data_column_name: str) -> bool:
        # Do substitutions based on the Amounts sheet:
        #   - Exchange directions, reference flow, amounts and child processes
        amounts_sheet_df = self.template_process.replication_file.sheets[RT.AMOUNTS]
        matched_exchange_index_list = self.template_process.matched_exchange_index_list
        for i in range(amounts_sheet_df.index.size):
            exchange = cloned_openlca_process.exchanges[matched_exchange_index_list[i]]        
            # is reference flow?
            is_reference_flow = amounts_sheet_df[RC.IS_REFERENCE][i]
            if isinstance(is_reference_flow, str) == True and is_reference_flow.lower().strip() == "x":
                exchange.quantitative_reference = True
            else:
                exchange.quantitative_reference = False

            # input or output
            if amounts_sheet_df[RC.DIRECTION][i] == INPUT:
                exchange.input = True
            else:
                exchange.input = False

            # amount
            exchange.amount = 0.0 
            amount = amounts_sheet_df[data_column_name][i]
            try:
                float_amount = float(amount)
                if math.isnan(float_amount) == True:
                    print(f"({i + 1}/{amounts_sheet_df.index.size}): {exchange.flow.name} - No amount provided", flush=True)
                else:
                    exchange.amount = float_amount
            except:
                print(f"({i + 1}/{amounts_sheet_df.index.size}): {exchange.flow.name} - Amount not set because amount is not a number", flush=True)

            # link to replicated provider, if necessary
            if not exchange.default_provider is None:
                uuid = exchange.default_provider.id
                for child_process in self.template_process.child_processes:
                    if uuid == child_process.uuid:
                        replicant_uuid = child_process.replicants[data_column_name]["process_uuid"]
                        exchange.default_provider = self.client.get(olca_schema.Process, replicant_uuid)

        return True

    def do_allocation_substitutions(self, cloned_openlca_process: olca_schema.Process, data_column_name: str) -> bool:
        # Do substitutions based on the Physical Allocations sheet
        allocations_sheet_df = self.template_process.replication_file.sheets.get(RT.PHYSICAL_ALLOCATIONS, None)
        if allocations_sheet_df is not None:
            matched_allocation_index_list = self.template_process.matched_allocation_index_list
            if matched_allocation_index_list is not None:
                physical_allocation_factors = []
                for allocation_factor in cloned_openlca_process.allocation_factors:
                    if allocation_factor.allocation_type == olca_schema.AllocationType.PHYSICAL:
                        physical_allocation_factors.append(allocation_factor)
                for i in range(allocations_sheet_df.index.size):
                    if matched_allocation_index_list[i] is not None:
                        allocation = physical_allocation_factors[matched_allocation_index_list[i]]     

                        # value
                        allocation.value = 0.0 
                        value = allocations_sheet_df[data_column_name][i]
                        try:
                            float_value = float(value)
                            if math.isnan(float_value) == True:
                                pass
                                # This is normal, don't print
                                # print(f"({i + 1}/{allocations_sheet_df.index.size}): {allocation.product.name} - No value provided", flush=True)
                            else:
                                allocation.value = float_value
                        except:
                            print(f"({i + 1}/{allocations_sheet_df.index.size}): {allocation.product.name} - Value not set because value is not a number", flush=True)

        return True

    def do_dqi_substitutions(self, cloned_openlca_process: olca_schema.Process, data_column_name: str) -> bool:
        # Do substitutions based on the DQIs sheet
        dqis_sheet_df = self.template_process.replication_file.sheets.get(RT.DQIS, None)
        if dqis_sheet_df is not None:
            amounts_sheet_df = self.template_process.replication_file.sheets[RT.AMOUNTS]
            matched_exchange_index_list = self.template_process.matched_exchange_index_list
            for i in range(dqis_sheet_df.index.size):
                exchange = cloned_openlca_process.exchanges[matched_exchange_index_list[i]]
    
                # DQI string
                # exchange.amount = 0.0 
                dqi_string = dqis_sheet_df[data_column_name][i]
                amount = amounts_sheet_df[data_column_name][i]
                try:
                    if not isinstance(dqi_string, str):
                        # This is often the case, do not print
                        # print(f"({i + 1}/{dqis_sheet_df.index.size}): {exchange.flow.name} - No DQIs provided", flush=True)
                        pass
                    else:
                        dq_entry, base_uncertainty = DQI.parse(dqi_string)
                        # print(f"({i + 1}/{dqis_sheet_df.index.size}): {exchange.flow.name} - {dq_entry};{base_uncertainty}", flush=True)
                        exchange.dq_entry = dq_entry
                        exchange.base_uncertainty = base_uncertainty
                        openlca_sigma_g = PedigreeMatrix.openlca_sigma_g(dq_entry, base_uncertainty)
                        exchange.uncertainty.geom_mean = amount
                        exchange.uncertainty.geom_sd = openlca_sigma_g
                except:
                    # If there is an Exception raised here we need to stop the process
                    print(f"({i + 1}/{dqis_sheet_df.index.size}): {exchange.flow.name} - DQIs not set because DQI string could not be parsed", flush=True)
                    return False

        return True
