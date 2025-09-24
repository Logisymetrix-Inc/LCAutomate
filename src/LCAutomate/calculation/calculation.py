import os
import shutil
import json
from src.LCAutomate.common_simplified import (
    DEFAULT_IMPACT_ASSESSMENT_METHOD, 
    DEFAULT_NUMBER_OF_ITERATIONS, 
    CalculationTypeNames
)
from src.LCAutomate.model.template_process import TemplateProcessShortEncoder
from src.LCAutomate.state import State
from src.olca__patched import ipc as olca
from src.olca__patched import schema as olca_schema


class Calculation:
    def __init__(
            self, client: olca.Client, 
            input_root_folder: str, 
            restart: bool, 
            calculation_type: str = CalculationTypeNames.UPSTREAM_ANALYSIS,
            impact_assessment_method: str = DEFAULT_IMPACT_ASSESSMENT_METHOD,
            number_of_iterations: int = DEFAULT_NUMBER_OF_ITERATIONS
        ):
        self.client = client
        self.base_root_folder = input_root_folder
        self.restart = restart
        self.calculation_type = calculation_type
        self.impact_assessment_method = impact_assessment_method  # 2025-09-01 default: 'CML-IA baseline'
        self.number_of_iterations = number_of_iterations

        self.base_root_folder_path = os.path.abspath(self.base_root_folder)
        self.calculation_type_folder_path = os.path.join("__calculation__", self.calculation_type)
        self.calculation_folder_path = os.path.join(self.calculation_type_folder_path, self.impact_assessment_method)
        self.output_root_folder_path = os.path.join(self.base_root_folder_path, self.calculation_folder_path)
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

        self.create_output_folder()

        # TODO: the calculation results should not be written from olca__patched.ipc methods - those should just return data
        calculations_complete = self.calculate()
        if not calculations_complete:
            print("ERROR: Failed to complete calculations")
            return False

        state_saved = self.save_state()
        if state_saved:
            print(f"Saved state to {self.state.filepath}")
            return True
        else:
            print(f"ERROR: Failed to save state to {self.state.filepath}")
            return False


# =====================================================================================================================
# ***** Calculation.create_output_folder *****
    def create_output_folder(self):
        print(f"\nCreating output root folder {self.calculation_folder_path}, if necessary", flush=True)
        os.makedirs(self.output_root_folder_path, exist_ok=True)

        state_files = []
        top_level_replicants = self.template_processes[self.top_level_process_uuid].replicants
        for replicant in top_level_replicants.values():
            if replicant is None:
                replicant = {}

            calculation_file_group = replicant.get("calculation_files", None)
            if calculation_file_group is not None:
                calculation_type_group = calculation_file_group.get(self.calculation_type, None)
                if calculation_type_group is not None:
                    calculation_files = calculation_type_group.get(self.impact_assessment_method, None)
                    if calculation_files is not None:
                        for calculation_file in calculation_files.values():
                            print(calculation_file)
                            state_files.append(os.path.basename(calculation_file))

        print(f"There are {len(state_files)} file(s) in the saved state.  ")
        if len(state_files) == 0:
            print("File removal step skipped", flush=True)
        else:
            print("Removing any files from here that are not in saved state", flush=True)

        if len(state_files) > 0:
            for root, dirs, files in os.walk(self.output_root_folder_path):
                for file in files:
                    if file not in state_files:
                        print(f"Removing file: {file}")
                        os.unlink(os.path.join(root, file))


# =====================================================================================================================
# ***** Calculation.calculate *****
    def calculate(self) -> bool:

        # # uuids of production processes
        # with open(os.path.join(self.input_root_folder_path, "process-hierarchy.json"), "r") as f:
        #     process_hierarchy = json.load(f)

        top_level_replicants = self.template_processes[self.top_level_process_uuid].replicants
        for data_column_name, replicant in top_level_replicants.items():
            if replicant is None:
                replicant = {}

            product_system_name = replicant.get("product_system_name", None)
            product_system_uuid = replicant.get("product_system_uuid", None)
            if product_system_uuid is None:
                print(f"No top-level product system found for data column '{data_column_name}'")
                return False
            
            calculation_file_group = replicant.get("calculation_files", None)
            if calculation_file_group is not None:
                calculation_type_group = calculation_file_group.get(self.calculation_type)
                if calculation_type_group is not None:
                    calculation_files = calculation_type_group.get(self.impact_assessment_method)
                    if calculation_files is not None:
                        print('Calculation files for: \033[1m' + product_system_name, '\033[0m ',
                              f"'{self.calculation_type}' - '{self.impact_assessment_method}' "
                              'already created',
                              flush=True
                        )
                        continue
            
            print('\nCalculations for: \033[1m' + product_system_name, '\033[0m', flush=True)
            
            impact_method = self.client.find(olca_schema.ImpactMethod, self.impact_assessment_method)
            print(f"Getting product system '{product_system_name}' ({product_system_uuid})...", flush=True)
            product_system = self.client.get(olca_schema.ProductSystem, product_system_uuid)

            setup = olca_schema.CalculationSetup(
                calculation_type   =  CalculationTypeNames.get_olca_calculation_type(self.calculation_type),
                allocation_method  =  olca_schema.AllocationType.PHYSICAL,
                impact_method      =  impact_method,
                product_system     =  product_system,
                amount             =  1.0,
                with_costs         =  False
            )

            print(f"Doing '{self.calculation_type}' calculation with impact assessment method '{self.impact_assessment_method}'...", flush=True)
            if self.calculation_type == CalculationTypeNames.MONTE_CARLO_SIMULATION:
                # Monte Carlo simulation
                simulator_response, err = self.client.simulator(setup)
                if err is not None:
                    print(f"ERROR: client.simulator() returned error '{err}'")
                    return False
                else:
                    simulator = olca_schema.Ref.from_json(simulator_response)
                    for i in range(self.number_of_iterations):
                        print('\n\033[1m' + product_system_name, f'(iteration {i + 1})\033[0m', flush=True)
                        result, err = self.client.next_simulation(simulator)
                        if err is not None:
                            print(f"ERROR: client.next_simulation() returned error '{err}'")
                            return False
                        else:
                            result_id = result.get('@id')
                            base_name = f"{product_system_name} - {i}"
                            exported = self.export_results(result_id, base_name)
                            if not exported:
                                self.client.dispose(simulator_response)
                                return False

                self.client.dispose(simulator_response)

            else:
                # Regular calculation
                result, err = self.client.calculate(setup)
                if err is not None:
                    print(f"ERROR: client.calculate() returned error '{err}'")
                    return False
                else:
                    result_id = result.get('@id')
                    base_name = product_system_name
                    exported = self.export_results(result_id, base_name)
                    self.client.dispose(result)
                    if not exported:
                        return False

            filepaths = self.get_calculation_filepaths(data_column_name)
            if replicant.get("calculation_files", None) is None:
                replicant["calculation_files"] = {}
            if replicant["calculation_files"].get(self.calculation_type, None) is None:
                replicant["calculation_files"][self.calculation_type] = {}
            replicant["calculation_files"][self.calculation_type][self.impact_assessment_method] = filepaths

            state_saved = self.save_state()
            if not state_saved:
                print(f"ERROR: Failed to save state to {self.state.filepath}")
                return False

        return True
    
    def get_calculation_filepaths(self, data_column_name) -> dict:
        base_filepath = os.path.join(
            self.output_root_folder_path, 
            self.template_processes[self.top_level_process_uuid].replication_base_name
            )
        if self.calculation_type == CalculationTypeNames.MONTE_CARLO_SIMULATION:
            calculation_filepaths = {}
            for i in range(self.number_of_iterations):
                base = f"{base_filepath} - {data_column_name} - {i}"
                calculation_filepaths[f"flows-of-impact-category - {i}"] = f"{base}-result-flows-of-impact-category.json"
                calculation_filepaths[f"total-flows - {i}"] = f"{base}-result-total-flows.json"
                calculation_filepaths[f"total-impacts - {i}"] = f"{base}-result-total-impacts.json"
                calculation_filepaths[f"upstream-of-impact-category - {i}"] = f"{base}-result-upstream-of-impact-category.json"
        else:
            base = f"{base_filepath} - {data_column_name}"
            calculation_filepaths = {
                "flows-of-impact-category": f"{base}-result-flows-of-impact-category.json",
                "total-flows": f"{base}-result-total-flows.json",
                "total-impacts": f"{base}-result-total-impacts.json",
                "upstream-of-impact-category": f"{base}-result-upstream-of-impact-category.json",
            }
        return calculation_filepaths

    def export_results(self, result_id, base_name) -> bool:
        print('client.json_export_result_detail("result/total-impacts")', flush=True)
        data, err = self.client.json_export_result_detail("result/total-impacts", {"@id": result_id}, self.output_root_folder_path, base_name)
        if err is not None:
            print(f"ERROR: client.json_export_result_detail('result/total-impacts') returned error '{err}'")
            return False
        else:
            impact_params = {
                "@id": result_id,
                "totalImpacts": data
            }
            print('client.json_export_upstream_of_impact_category()', flush=True)
            self.client.json_export_upstream_of_impact_category(impact_params, self.output_root_folder_path, base_name)

            print('client.json_export_result_detail("result/total-flows")', flush=True)
            data, err = self.client.json_export_result_detail(
                "result/total-flows", {"@id": result_id}, self.output_root_folder_path, base_name
            )
            if err is not None:
                print(f"ERROR: client.json_export_result_detail('result/total-flows') returned error '{err}'")
                return False
            else:
                print('client.json_export_flows_of_impact_category()', flush=True)
                self.client.json_export_flows_of_impact_category(impact_params, self.output_root_folder_path, base_name)
                # TODO: Isn't there an error path here?

        return True

    def reset(self):
        print(f"Resetting calculations for {self.impact_assessment_method}...")
        state = self.load_state()

        if state is not None:
            template_process = self.template_processes[self.top_level_process_uuid]
            for data_column_name in template_process.replicants.keys():
                # Remove calculation_files from replicants
                if template_process.replicants[data_column_name] is None:
                    template_process.replicants[data_column_name] = {}
                else:
                    calculation_file_group = template_process.replicants[data_column_name].get("calculation_files", None)
                    if calculation_file_group is not None:
                        calculation_type_group = calculation_file_group.get(self.calculation_type, None)
                        if calculation_type_group is not None:
                            calculation_files = calculation_type_group.get(self.impact_assessment_method, None)
                            if calculation_files is not None:
                                del calculation_file_group[self.calculation_type][self.impact_assessment_method]

                # Delete created calculation results files
                calculation_filepaths = self.get_calculation_filepaths(data_column_name)
                for filepath in calculation_filepaths.values():
                    try:
                        os.unlink(filepath)
                        print('\033[1m' + os.path.basename(filepath), '\033[0m' +f'deleted from {self.calculation_folder_path} folder', flush=True)
                    except FileNotFoundError:
                        print('\033[1m' + os.path.basename(filepath), '\033[0m' +f'not found in {self.calculation_folder_path} folder', flush=True)
                    except Exception as e:
                        print(f"ERROR: Could not delete {os.path.basename(filepath)} - {e}")

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
