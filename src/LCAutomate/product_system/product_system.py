import os
import shutil
import json
from src.LCAutomate.calculation.calculation import Calculation
from src.LCAutomate.state import State
from src.olca__patched import ipc as olca
from src.olca__patched import schema as olca_schema


class ProductSystem:
    def __init__(self, client: olca.Client, input_root_folder: str, restart: bool):
        self.client = client
        self.base_root_folder = input_root_folder
        self.restart = restart
        self.top_level_process_uuid = None
        self.template_processes = {}
        self.state = State(self.base_root_folder)

    def do(self) -> bool:
        if self.restart:
            self.reset()

        state_loaded = self.load_state()
        if not state_loaded:
            print(f"ERROR: Failed to load state from {self.state.filepath}")
            return False

        created = self.create()
        if not created:
            print("ERROR: Failed to create product systems")
            return False

        # self.write_summary()
        state_saved = self.save_state()
        if state_saved:
            print(f"Saved state to {self.state.filepath}")
            return True
        else:
            print(f"ERROR: Failed to save state to {self.state.filepath}")
            return True


# =====================================================================================================================
# ***** ProductSystem.create *****
    def create(self) -> bool:

        top_level_replicants = self.template_processes[self.top_level_process_uuid].replicants
        for data_column_name, replicant in top_level_replicants.items():
            if replicant is None:
                replicant = {}

            process_name = replicant.get("process_name", None)
            process_uuid = replicant.get("process_uuid", None)
            if process_uuid is None:
                print(f"No top-level process found for data column '{data_column_name}'")
                return False
            
            product_system_uuid = replicant.get("product_system_uuid", None)
            product_system_name = replicant.get("product_system_name", None)
            if product_system_uuid is not None:
                print('Product system: \033[1m' + product_system_name, '\033[0m' +'already exists in olca database', flush=True)
                continue

            product_system_name = process_name
            # print("{id}: {name}".format(id=process_uuid, name=process_name), flush=True)
            
            # Delete any pre-existing instances
            deleted = self.delete(product_system_name)
            if not deleted:
                return False
            
            # print('client.create_product_system()', flush=True)
            product_system_ref = self.client.create_product_system(
                process_id         =  process_uuid,
                default_providers  =  'prefer',
                preferred_type     =  'LCI_RESULT'
            )

            print('Product system: \033[1m' + product_system_name, '\033[0m' +'succesfully imported to olca database', flush=True)
            replicant["product_system_uuid"] = product_system_ref.id
            replicant["product_system_name"] = product_system_ref.name
            
            state_saved = self.save_state()
            if not state_saved:
                print(f"Failed to save state to {self.state.filename}")
                return False
        return True
    
    def get_product_system_name(self, data_column_name: str) -> str:
        return f"{self.template_processes[self.top_level_process_uuid].replication_base_name} - {data_column_name}"
    
    def delete(self, product_system_name: str) -> bool:
        try:
            pre_existing_instance = self.client.find(olca_schema.ProductSystem, product_system_name)
            while pre_existing_instance:
                self.client.delete(pre_existing_instance)
                pre_existing_instance = self.client.find(olca_schema.ProductSystem, product_system_name)
            return True
        except Exception as e:
            print(f"ERROR: Problem deleting pre-existing product systems: {e}")
            return False
    
    def reset(self):
        print("Resetting product systems...")
        state = self.load_state()
        if state is not None:
            template_process = self.template_processes[self.top_level_process_uuid]
            for data_column_name in template_process.replicants.keys():
                # Remove product_system_name and product_system_uuid from replicants
                if template_process.replicants[data_column_name] is None:
                    template_process.replicants[data_column_name] = {}
                else:
                    if template_process.replicants[data_column_name].get("product_system_name", None) is not None:
                        del template_process.replicants[data_column_name]["product_system_name"]
                    if template_process.replicants[data_column_name].get("product_system_uuid", None) is not None:
                        del template_process.replicants[data_column_name]["product_system_uuid"]

                # Delete created product systems
                product_system_name = self.get_product_system_name(data_column_name)
                self.delete(product_system_name)
                print('Product system: \033[1m' + product_system_name, '\033[0m' +'deleted from olca database', flush=True)

        self.save_state()

    def load_state(self) -> bool:
        # Load state, saved in previous operation
        state = self.state.load()
        if state is None:
            print(f"Failed to load state from {self.state.filename}")
            return False
        
        self.top_level_process_uuid = state["top_level_process_uuid"]
        self.template_processes = state["template_processes"]
        return True

    def save_state(self) -> bool:
        state = {
            "top_level_process_uuid": self.top_level_process_uuid,
            "template_processes": self.template_processes,
        }
        state_saved = self.state.save(state)
        return state_saved
