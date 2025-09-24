# Filenames
from src.olca__patched.schema import CalculationType


DRIVER_FILENAME = "Processes to be replicated.xlsx"
STATE_FILENAME = "state.dat"

# Flow directions
INPUT = "Input"
OUTPUT = "Output"

# Default calculation parameters
DEFAULT_IMPACT_ASSESSMENT_METHOD = "CML-IA baseline"
DEFAULT_NUMBER_OF_ITERATIONS = 10

# LCAutomate driver file
class DriverTabNames:
    MAIN = "Main"

    @staticmethod
    def list():
        return [
            DriverTabNames.MAIN,
        ]

class DriverColumnNames:
    TOP_LEVEL = "Top-level?"
    TEMPLATE_PROCESS_NAME = "Template process name"
    TEMPLATE_PROCESS_UUID = "Template process UUID"
    REPLICATION_BASE_NAME = "Replication base name"
    REPLICATION_FILE = "Replication file"

    @staticmethod
    def list():
        return [
            DriverColumnNames.TOP_LEVEL,
            DriverColumnNames.TEMPLATE_PROCESS_NAME,
            DriverColumnNames.TEMPLATE_PROCESS_UUID,
            DriverColumnNames.REPLICATION_BASE_NAME,
            DriverColumnNames.REPLICATION_FILE,
        ]


# Replication file
class ReplicationTabNames:
    AMOUNTS = "Amounts"
    PHYSICAL_ALLOCATIONS = "Physical Allocations"
    DQIS = "DQIs"

    @staticmethod
    def list():
        return [
            ReplicationTabNames.AMOUNTS,
            ReplicationTabNames.PHYSICAL_ALLOCATIONS,
            ReplicationTabNames.DQIS,
       ]
    
class ReplicationColumnNames:
    DIRECTION = "Direction"
    IS_REFERENCE = "Is reference?"
    FLOW = "Flow"
    DESCRIPTION = "Description"
    CATEGORY = "Category"

    @staticmethod
    def list():
        return [
            ReplicationColumnNames.DIRECTION,
            ReplicationColumnNames.IS_REFERENCE,
            ReplicationColumnNames.FLOW,
            ReplicationColumnNames.DESCRIPTION,
            ReplicationColumnNames.CATEGORY,
       ]

# DQI Sub-columns
class DQISubColumnNames:
    RELIABILITY = "Reliability"
    COMPLETENESS = "Completeness"
    TEMPORAL_CORRELATION = "Temporal correlation"
    GEOGRAPHICAL_CORRELATION = "Geographical correlation"
    FURTHER_TECHNOLOGICAL_CORRELATION = "Further technological correlation"
    BASE_UNCERTAINTY = "Base uncertainty"

    @staticmethod
    def list():
        return [
            DQISubColumnNames.RELIABILITY,
            DQISubColumnNames.COMPLETENESS,
            DQISubColumnNames.TEMPORAL_CORRELATION,
            DQISubColumnNames.GEOGRAPHICAL_CORRELATION,
            DQISubColumnNames.FURTHER_TECHNOLOGICAL_CORRELATION,
            DQISubColumnNames.BASE_UNCERTAINTY,
       ]

# Calculation types
class CalculationTypeNames:
    SIMPLE_CALCULATION = CalculationType.SIMPLE_CALCULATION.value
    CONTRIBUTION_ANALYSIS = CalculationType.CONTRIBUTION_ANALYSIS.value
    UPSTREAM_ANALYSIS = CalculationType.UPSTREAM_ANALYSIS.value
    REGIONALIZED_CALCULATION = CalculationType.REGIONALIZED_CALCULATION.value
    MONTE_CARLO_SIMULATION = CalculationType.MONTE_CARLO_SIMULATION.value

    @staticmethod
    def list():
        return [
            CalculationTypeNames.SIMPLE_CALCULATION,
            CalculationTypeNames.CONTRIBUTION_ANALYSIS,
            CalculationTypeNames.UPSTREAM_ANALYSIS,
            CalculationTypeNames.REGIONALIZED_CALCULATION,
            CalculationTypeNames.MONTE_CARLO_SIMULATION,
       ]
    
    @staticmethod
    def get_olca_calculation_type(calculation_type: str) -> CalculationType:
        internal_dict = {
            CalculationTypeNames.SIMPLE_CALCULATION: CalculationType.SIMPLE_CALCULATION,
            CalculationTypeNames.CONTRIBUTION_ANALYSIS: CalculationType.CONTRIBUTION_ANALYSIS,
            CalculationTypeNames.UPSTREAM_ANALYSIS: CalculationType.UPSTREAM_ANALYSIS,
            CalculationTypeNames.REGIONALIZED_CALCULATION: CalculationType.REGIONALIZED_CALCULATION,
            CalculationTypeNames.MONTE_CARLO_SIMULATION: CalculationType.MONTE_CARLO_SIMULATION,
        }

        return internal_dict[calculation_type]
