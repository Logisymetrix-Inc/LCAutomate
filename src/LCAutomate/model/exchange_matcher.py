import pandas
from src.olca__patched import ipc as olca
from src.olca__patched import schema as olca_schema

from src.LCAutomate.common_simplified import ReplicationColumnNames


RC = ReplicationColumnNames


class ExchangeMatcher:

    @staticmethod
    def get_matched_exchange_index_list(client: olca.Client, openlca_process: olca_schema.Process, amounts_sheet_df: pandas.DataFrame) -> list:
        if len(openlca_process.exchanges) != amounts_sheet_df.index.size:
            print(f"ERROR: Number of lines in replication file: {amounts_sheet_df.index.size} must equal number of exchanges: "
                  f"{len(openlca_process.exchanges)} matches for '{openlca_process.name}'"
            )
            return None
        
        exchange_markers = ExchangeMatcher.get_exchange_markers(client, openlca_process)
        if exchange_markers is None:
            return None

        matched_exchange_index_list = []

        for i in range(amounts_sheet_df.index.size):
            flow_name = amounts_sheet_df[RC.FLOW][i]
            description = amounts_sheet_df[RC.DESCRIPTION][i]
            category = amounts_sheet_df[RC.CATEGORY][i]

            # Find test matching exchange(s)
            test_exchange_matches = []
            test_exchange_match_indices = []
            for exchange_index, exchange_marker in enumerate(exchange_markers):
                match = ExchangeMatcher.is_exchange_match(exchange_marker, flow_name, description, category)
                if match:
                    test_exchange_matches.append(exchange_marker)
                    test_exchange_match_indices.append(exchange_index)
            if len(test_exchange_matches) != 1:
                print(f"ERROR: Found {len(test_exchange_matches)} Exchange matches for '{openlca_process.name}': "
                      f"flow='{flow_name}', description='{description}', category='{category}'")
                if len(test_exchange_matches) > 1:
                    print("  - multiple Exchange matches must be distinguished with different descriptions")
                    print("  - sample Exchange shown below:")
                    print(f"\n{openlca_process.exchanges[test_exchange_match_indices[0]]}")
                return None
        
            # Here we know there is a single exchange match
            matched_exchange_index_list.append(test_exchange_match_indices[0])

        return matched_exchange_index_list
    
    @staticmethod
    def get_exchange_markers(client: olca.Client, openlca_process: olca_schema.Process) -> list:
        exchanges = openlca_process.exchanges
        flow_names = []
        descriptions = []
        categories = []
        for exchange in exchanges:
            flow_names.append(exchange.flow.name)
            descriptions.append(exchange.description)
            flow = client.get(olca_schema.Flow, exchange.flow.id)
            category_ref = flow.category
            if category_ref is None:
                category = ""
            else:
                category = category_ref.category_path
            category_path = "/".join(category)
            categories.append(category_path)

        exchange_markers = []
        for i, flow_name in enumerate(flow_names):
            description = None
            category_path = None

            duplicate = False
            for j in range(len(flow_names)):
                if i != j and flow_name == flow_names[j]:
                    duplicate = True
            if duplicate:
                duplicate = False
                description = descriptions[i]
                for j in range(len(flow_names)):
                    if i != j and flow_name == flow_names[j] and description == descriptions[j]:
                        duplicate = True
                if duplicate:
                    duplicate = False
                    category_path = categories[i]
                    for j in range(len(flow_names)):
                        if i != j and flow_name == flow_names[j] and description == descriptions[j] and category_path == categories[j]:
                            duplicate = True
                    if duplicate:
                        print(f"ERROR: The combination\n"
                              f"  - Flow: '{flow_name}'\n"
                              f"  - Description '{description}'\n"
                              f"  - Category '{category_path}'\n"
                              f"is not unique.\n"
                              f"In this case, the exchanges in question must be made unique via the Process > Inputs/Outputs > Description field in OpenLCA")
                        return None
                    
            exchange_markers.append({
                "internal_id": exchange.internal_id,
                "flow_name": flow_name,
                "description": description,
                "category": category_path,
            })

        return exchange_markers

    @staticmethod
    def is_exchange_match(exchange_marker: dict, flow_name: str, description: str, flow_category: str) -> bool:
        # TODO: Provide detailed information on misses - is this still necessary?
        flow_match = False
        description_match = False
        category_match = False

        # Flow name
        if flow_name.strip() == exchange_marker["flow_name"].strip():
            flow_match = True
        
        # Description
        if exchange_marker["description"] is None:
            description_match = True
        elif isinstance(description, str) and description.strip() == exchange_marker["description"].strip():
            description_match = True
         
        # Category
        if exchange_marker["category"] is None:
            category_match = True
        elif isinstance(flow_category, str) and flow_category.strip() == exchange_marker["category"].strip():
            category_match = True
                
        return flow_match and description_match and category_match
