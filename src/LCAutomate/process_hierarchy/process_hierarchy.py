import json
from src.LCAutomate.calculation.calculation import Calculation
from src.LCAutomate.model.template_process import TemplateProcess, TemplateProcessEncoder, TemplateProcessShortEncoder
from src.LCAutomate.product_system.product_system import ProductSystem
from src.LCAutomate.state import State
from src.olca__patched import ipc as olca

from src.LCAutomate.common_simplified import DRIVER_FILENAME, DriverColumnNames
from src.LCAutomate.common_simplified import ReplicationColumnNames

from src.LCAutomate.process_hierarchy.single_process_creator import SingleProcessCreator


DC = DriverColumnNames
RC = ReplicationColumnNames


class ProcessHierarchy:
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

        # Load state, saved in previous operation
        state_loaded = self.load_state()
        if not state_loaded:
            print(f"ERROR: Failed to load state from {self.state.filepath}")
            return False
        
        created = self.create()
        if not created:
            print("\n*** Correct the errors indicated above before proceeding ***", flush=True)
            return False

        state_saved = self.save_state()
        if state_saved:
            print(f"State saved to {self.state.filepath}")
            return True
        else:
            print(f"ERROR: Failed to save state to {self.state.filepath}")
            return False

    def create(self) -> bool:
        print(f"\nCreating process hierarchies in OpenLCA...", flush=True)
        template_process = self.template_processes[self.top_level_process_uuid]
        ancestry = "root"
        created = self.recursively_create_replicants(template_process, ancestry)
        return created

    def recursively_create_replicants(self, template_process: TemplateProcess, ancestry: str) -> bool:
        print(f"\n{ancestry} -> {template_process.name}")
        for child_process in template_process.child_processes:
            created = self.recursively_create_replicants(child_process, f"{ancestry} -> {template_process.name}")
            if not created:
                return False

        if len(template_process.child_processes) > 0:    
            print(f"\n{ancestry} -> {template_process.name}")

        single_process_creator = SingleProcessCreator(self.client, template_process)
        for data_column_name in template_process.replicants.keys():
            if template_process.replicants[data_column_name] is None:
                template_process.replicants[data_column_name] = {}
            process_uuid = template_process.replicants[data_column_name].get("process_uuid", None)
            process_name = template_process.replicants[data_column_name].get("process_name", None)
            if process_uuid is not None:
                print('Process: \033[1m' + process_name, '\033[0m' +'already exists in olca database', flush=True)
                continue

            created = single_process_creator.create(data_column_name)
            if not created:
                return False
            
            # Set the replicant process uuid and name
            template_process.replicants[data_column_name]["process_uuid"] = single_process_creator.created_process_uuid
            template_process.replicants[data_column_name]["process_name"] = single_process_creator.created_process_name

            state_saved = self.save_state()
            if not state_saved:
                print(f"Failed to save state to {self.state.filename}")
                return False

        return True
    
    def reset(self):
        print("Resetting process hierarchies...")
        state = self.load_state()
        if state is not None:
            for template_process in self.template_processes.values():
                single_process_creator = SingleProcessCreator(self.client, template_process)
                for data_column_name in template_process.replicants.keys():
                    # Remove process_name and process_uuid from replicants
                    if template_process.replicants[data_column_name] is None:
                        template_process.replicants[data_column_name] = {}
                    else:
                        if template_process.replicants[data_column_name].get("process_name", None) is not None:
                            del template_process.replicants[data_column_name]["process_name"]
                        if template_process.replicants[data_column_name].get("process_uuid", None) is not None:
                            del template_process.replicants[data_column_name]["process_uuid"]

                    # Delete created processes
                    single_process_creator.delete(data_column_name)
                    print('Process: \033[1m' + single_process_creator.get_process_name(data_column_name), '\033[0m' +'deleted from olca database', flush=True)
                    
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
    