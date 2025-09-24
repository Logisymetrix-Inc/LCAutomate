# Sheet names
class SheetNames:
    GENERAL_INFORMATION = "General information"
    INPUTS = "Inputs"
    OUTPUTS = "Outputs"
    ALLOCATION = "Allocation"
    FLOWS = "Flows"
    UNITS = "Units"

    @staticmethod
    def list():
        return [
            SheetNames.GENERAL_INFORMATION,
            SheetNames.INPUTS,
            SheetNames.OUTPUTS,
            SheetNames.ALLOCATION,
            SheetNames.FLOWS,
            SheetNames.UNITS,
        ]


# General information row names
class GeneralInformationKeys:
    NAME = "Name"
    UUID = "UUID"

    @staticmethod
    def list():
        return [
            GeneralInformationKeys.NAME,
            GeneralInformationKeys.UUID,
        ]


# Inputs column names
class InputsKeys:
    IS_REFERENCE = "Is reference?"
    FLOW = "Flow"
    AMOUNT = "Amount"
    UNIT = "Unit"
    PROVIDER = "Provider"
    DESCRIPTION = "Description"

    @staticmethod
    def list():
        return [
            InputsKeys.IS_REFERENCE,
            InputsKeys.FLOW,
            InputsKeys.AMOUNT,
            InputsKeys.UNIT,
            InputsKeys.PROVIDER,
            InputsKeys.DESCRIPTION,
        ]


# Outputs column names
class OutputsKeys:
    IS_REFERENCE = "Is reference?"
    FLOW = "Flow"
    AMOUNT = "Amount"
    UNIT = "Unit"
    PROVIDER = "Provider"
    DESCRIPTION = "Description"

    @staticmethod
    def list():
        return [
            OutputsKeys.IS_REFERENCE,
            OutputsKeys.FLOW,
            OutputsKeys.AMOUNT,
            OutputsKeys.UNIT,
            OutputsKeys.PROVIDER,
            OutputsKeys.DESCRIPTION,
        ]


# Allocation column names
class AllocationKeys:
    PRODUCT = "Product"
    PHYSICAL = "Physical"
    CAUSAL_ALLOCATION = "Causal allocation"

    @staticmethod
    def list():
        return [
            AllocationKeys.PRODUCT,
            AllocationKeys.PHYSICAL,
            AllocationKeys.CAUSAL_ALLOCATION,
        ]


# Flows column names
class FlowsKeys:
    UUID = "UUID"
    NAME = "Name"
    DESCRIPTION = "Description"
    TYPE = "Type"
    REFERENCE_FLOW_PROPERTY = "Reference flow property"

    @staticmethod
    def list():
        return [
            FlowsKeys.UUID,
            FlowsKeys.NAME,
            FlowsKeys.DESCRIPTION,
            FlowsKeys.TYPE,
            FlowsKeys.REFERENCE_FLOW_PROPERTY,
        ]


# Units column names
class UnitsKeys:
    UUID = "UUID"
    NAME = "Name"
    DESCRIPTION = "Description"
    CONVERSION_FACTOR = "Conversion factor"

    @staticmethod
    def list():
        return [
            UnitsKeys.UUID,
            UnitsKeys.NAME,
            UnitsKeys.DESCRIPTION,
            UnitsKeys.CONVERSION_FACTOR,
        ]


# OpenLCA units keys
class OpenLCAUnitsKeys:
    ID = "@id"
    OLCA_TYPE = '@type'
    NAME = "name"
    DESCRIPTION = "description"
    CONVERSION_FACTOR = "conversionFactor"

    @staticmethod
    def list():
        return [
            OpenLCAUnitsKeys.ID,
            OpenLCAUnitsKeys.OLCA_TYPE,
            OpenLCAUnitsKeys.NAME,
            OpenLCAUnitsKeys.DESCRIPTION,
            OpenLCAUnitsKeys.CONVERSION_FACTOR,
        ]


# Flow types
class FlowTypesKeys:
    PRODUCT_FLOW = "Product flow"
    WASTE_FLOW = "Waste flow"
    ELEMENTARY_FLOW = "Elementary flow"
    
    @staticmethod
    def list():
        return [
            FlowTypesKeys.PRODUCT_FLOW,
            FlowTypesKeys.WASTE_FLOW,
            FlowTypesKeys.ELEMENTARY_FLOW,
        ]
    
# Consolidated flow keys
#   - this is the combination of the Flows, Inputs, Outputs and Allocation sheets obtained from OpenLCAExcelAdapter.get_flows()
class ConsolidatedFlowKeys:
    FLOW_DIRECTION = "Flow direction"
    UUID = "UUID"
    FLOW_DESCRIPTION = "Flow description"
    TYPE = "Type"
    REFERENCE_FLOW_PROPERTY = "Reference flow property"
    IS_REFERENCE = "Is reference?"
    FLOW = "Flow"
    AMOUNT = "Amount"
    UNIT = "Unit"
    UNIT_DESCRIPTOR = "Unit descriptor"
    PROVIDER = "Provider"
    INPUT_OUTPUT_DESCRIPTION = "Input/Output description"
    PHYSICAL = "Physical"

    @staticmethod
    def list():
        return [
            ConsolidatedFlowKeys.FLOW_DIRECTION,
            ConsolidatedFlowKeys.UUID,
            ConsolidatedFlowKeys.FLOW_DESCRIPTION,
            ConsolidatedFlowKeys.TYPE,
            ConsolidatedFlowKeys.REFERENCE_FLOW_PROPERTY,
            ConsolidatedFlowKeys.IS_REFERENCE,
            ConsolidatedFlowKeys.FLOW,
            ConsolidatedFlowKeys.AMOUNT,
            ConsolidatedFlowKeys.UNIT,
            ConsolidatedFlowKeys.UNIT_DESCRIPTOR,
            ConsolidatedFlowKeys.PROVIDER,
            ConsolidatedFlowKeys.INPUT_OUTPUT_DESCRIPTION,
            ConsolidatedFlowKeys.PHYSICAL,
        ]

# Flow directions
INPUT = "Input"
OUTPUT = "Output"