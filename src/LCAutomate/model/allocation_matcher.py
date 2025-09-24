import pandas
from src.olca__patched import ipc as olca
from src.olca__patched import schema as olca_schema

from src.LCAutomate.common_simplified import ReplicationColumnNames


RC = ReplicationColumnNames


class AllocationMatcher:

    @staticmethod
    def get_matched_allocation_index_list(client: olca.Client, openlca_process: olca_schema.Process, allocations_sheet_df: pandas.DataFrame) -> list:
        matched_allocation_index_list = []

        allocation_markers = AllocationMatcher.get_allocation_markers(client, openlca_process)
        for i in range(allocations_sheet_df.index.size):
            flow_name = allocations_sheet_df[RC.FLOW][i]
            category = allocations_sheet_df[RC.CATEGORY][i]

            # Find test matching allocation(s)
            test_allocation_matches = []
            test_allocation_match_indices = []
            for allocation_index, allocation_marker in enumerate(allocation_markers):
                match = AllocationMatcher.is_allocation_match(allocation_marker, flow_name, category)
                if match:
                    test_allocation_matches.append(allocation_marker)
                    test_allocation_match_indices.append(allocation_index)
        
            if len(test_allocation_matches) == 0:
                matched_allocation_index_list.append(None)
            elif len(test_allocation_matches) == 1:
                matched_allocation_index_list.append(test_allocation_match_indices[0])
            else:
                print(f"ERROR: Found {len(test_allocation_matches)} Physical Allocation matches for '{openlca_process.name}': "
                      f"flow='{flow_name}', category='{category}'")
                return None

        return matched_allocation_index_list
    
    @staticmethod
    def get_allocation_markers(client: olca.Client, openlca_process: olca_schema.Process) -> list:
        # We assume that for Physical Allocations the Product is a Flow
        physical_allocation_factors = []
        for allocation_factor in openlca_process.allocation_factors:
            if allocation_factor.allocation_type == olca_schema.AllocationType.PHYSICAL:
                physical_allocation_factors.append(allocation_factor)
        
        flow_names = []
        categories = []
        for allocation in physical_allocation_factors:
            flow_names.append(allocation.product.name)
            flow = client.get(olca_schema.Flow, allocation.product.id)
            category_ref = flow.category
            if category_ref is None:
                category = ""
            else:
                category = category_ref.category_path
            category_path = "/".join(category)
            categories.append(category_path)

        allocation_markers = []
        for i, flow_name in enumerate(flow_names):
            category_path = None

            duplicate = False
            for j in range(len(flow_names)):
                if i != j and flow_name == flow_names[j]:
                    duplicate = True
            if duplicate:
                duplicate = False
                category_path = categories[i]
                for j in range(len(flow_names)):
                    if i != j and flow_name == flow_names[j] and category_path == categories[j]:
                        duplicate = True
                if duplicate:
                    print(f"ERROR: The combination\n"
                            f"  - Flow: '{flow_name}'\n"
                            f"  - Category '{category_path}'\n"
                            f"is not unique.")
                    return None
                    
            allocation_markers.append({
                "flow_name": flow_name,
                "category": category_path,
            })

        return allocation_markers

    @staticmethod
    def is_allocation_match(allocation_marker: dict, flow_name: str, flow_category: str) -> bool:
        # TODO: Provide detailed information on misses - is this still necessary?
        flow_match = False
        category_match = False

        # Flow name
        if flow_name.strip() == allocation_marker["flow_name"].strip():
            flow_match = True
        
        # Category
        if allocation_marker["category"] is None:
            category_match = True
        elif isinstance(flow_category, str) and flow_category.strip() == allocation_marker["category"].strip():
            category_match = True
                
        return flow_match and category_match
