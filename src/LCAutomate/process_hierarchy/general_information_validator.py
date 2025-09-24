import os
import math
import shutil

# General information column names
from src.LCAutomate.common import GeneralInformationKeys
from src.LCAutomate.common import SheetNames


class GeneralInformationValidator:
    def __init__(self, general_information: dict):
        self.general_information = general_information
        self.validation_errors = []

    def validate(self) -> list:
        try:
            self.required_rows_present()
        except Exception as e:
            self.validation_errors.append(e)

        return self.validation_errors

    def required_rows_present(self):
        if GeneralInformationKeys.NAME not in self.general_information:
            self.validation_errors.append(
                f"{SheetNames.GENERAL_INFORMATION} - Missing required row: {GeneralInformationKeys.NAME}"
            )
        elif not isinstance(self.general_information[GeneralInformationKeys.NAME], str):
            self.validation_errors.append(
                f"{SheetNames.GENERAL_INFORMATION} - {GeneralInformationKeys.NAME} must be a non-blank string"
            )
