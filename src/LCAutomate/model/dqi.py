import math
import pandas
from src.LCAutomate.common_simplified import ReplicationColumnNames, ReplicationTabNames
from src.LCAutomate.common_simplified import DQISubColumnNames


RC = ReplicationColumnNames
RT = ReplicationTabNames
DQ = DQISubColumnNames


class DQI:

    @staticmethod
    def reformat_dqis_sheet_df(dqis_sheet_df: pandas.DataFrame) -> pandas.DataFrame:
        reformatted_dqis_sheet_df = pandas.DataFrame()
        column_index = 0
        column_name_list = dqis_sheet_df.columns.to_list()
        while column_index < len(column_name_list):
            if column_index < len(RC.list()):
                column_name = column_name_list[column_index]
                column = dqis_sheet_df.iloc[:, column_index]
                reformatted_dqis_sheet_df[column_name] = column[1:]
                column_index += 1
            else:
                column_name = column_name_list[column_index]

                # Get a block of 6 columns
                dqi_column_block = {}
                dqi_sub_headers = []
                for j in range(6):
                    column = dqis_sheet_df.iloc[:, column_index]
                    dqi_sub_header = column.to_list()[0]
                    dqi_column_block[dqi_sub_header] = column.to_list()[1:]
                    dqi_sub_headers.append(dqi_sub_header)
                    column_index += 1
                if dqi_sub_headers != DQISubColumnNames.list():
                    print(f"\nERROR: DQI sub-headers '{dqi_sub_headers}' must match '{DQISubColumnNames.list()}'", flush=True)
                    return None
                
                # Squash the DQI sub-column values into a single string for each row
                """
                DQISubColumnNames.RELIABILITY,
                DQISubColumnNames.COMPLETENESS,
                DQISubColumnNames.TEMPORAL_CORRELATION,
                DQISubColumnNames.GEOGRAPHICAL_CORRELATION,
                DQISubColumnNames.FURTHER_TECHNOLOGICAL_CORRELATION,
                DQISubColumnNames.BASE_UNCERTAINTY
                """
                squashed_column = []
                column_length = len(dqi_column_block[DQISubColumnNames.RELIABILITY])
                for j in range(column_length):
                    base_uncertainty = dqi_column_block[DQISubColumnNames.BASE_UNCERTAINTY][j]
                    try:
                        float_value = float(base_uncertainty)
                        if math.isnan(float_value) == True:
                            base_uncertainty = None
                        else:
                            pass
                    except:
                        base_uncertainty = None

                    if base_uncertainty is not None:
                        squashed_str = (
                            f"("
                            f"{dqi_column_block[DQISubColumnNames.RELIABILITY][j]};"
                            f"{dqi_column_block[DQISubColumnNames.COMPLETENESS][j]};"
                            f"{dqi_column_block[DQISubColumnNames.TEMPORAL_CORRELATION][j]};"
                            f"{dqi_column_block[DQISubColumnNames.GEOGRAPHICAL_CORRELATION][j]};"
                            f"{dqi_column_block[DQISubColumnNames.FURTHER_TECHNOLOGICAL_CORRELATION][j]}"
                            f")|"
                            f"{dqi_column_block[DQISubColumnNames.BASE_UNCERTAINTY][j]}"
                        )
                    else:
                        squashed_str = math.nan
                    squashed_column.append(squashed_str)
                reformatted_dqis_sheet_df[column_name] = squashed_column

        return reformatted_dqis_sheet_df.reset_index()
    
    @staticmethod
    def parse(dqi_string: str) -> tuple[str, float]:
        tokens = dqi_string.split("|")

        dq_entry = tokens[0]
        base_uncertainty = float(tokens[1])
        return dq_entry, base_uncertainty


class PedigreeMatrix:
    table = {
        DQISubColumnNames.RELIABILITY: {
            "1": 1.0,
            "2": 1.05,
            "3": 1.1,
            "4": 1.2,
            "5": 1.5,
        },
        DQISubColumnNames.COMPLETENESS: {
            "1": 1.0,
            "2": 1.02,
            "3": 1.05,
            "4": 1.1,
            "5": 1.2,
        },
        DQISubColumnNames.TEMPORAL_CORRELATION: {
            "1": 1.0,
            "2": 1.03,
            "3": 1.1,
            "4": 1.2,
            "5": 1.5,
        },
        DQISubColumnNames.GEOGRAPHICAL_CORRELATION: {
            "1": 1.0,
            "2": 1.01,
            "3": 1.02,
            "4": 1.05,
            "5": 1.1,
        },
        DQISubColumnNames.FURTHER_TECHNOLOGICAL_CORRELATION: {
            "1": 1.0,
            "2": 1.05,
            "3": 1.2,
            "4": 1.5,
            "5": 2.0,
        },
    }

    @staticmethod
    def openlca_sigma_g(dq_entry: str, base_uncertainty: float) -> float:
        dq_values = PedigreeMatrix.get_dq_values(dq_entry)
        sum = 0.0
        for dq_value in dq_values:
            ln_dq_value = math.log(dq_value)
            sum += ln_dq_value * ln_dq_value

        ln_Ub = math.log(base_uncertainty)
        
        return math.exp(math.sqrt(ln_Ub * ln_Ub + sum))
        
    @staticmethod
    def get_dq_values(dq_entry: str) -> list[float]:
        dq_indicators = dq_entry[1:-1].split(";")
        dq_values = []
        dq_values.append(PedigreeMatrix.table[DQ.RELIABILITY][dq_indicators[0]])
        dq_values.append(PedigreeMatrix.table[DQ.COMPLETENESS][dq_indicators[1]])
        dq_values.append(PedigreeMatrix.table[DQ.TEMPORAL_CORRELATION][dq_indicators[2]])
        dq_values.append(PedigreeMatrix.table[DQ.GEOGRAPHICAL_CORRELATION][dq_indicators[3]])
        dq_values.append(PedigreeMatrix.table[DQ.FURTHER_TECHNOLOGICAL_CORRELATION][dq_indicators[4]])

        return dq_values
