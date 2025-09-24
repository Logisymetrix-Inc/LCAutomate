import os
import pickle
from src.LCAutomate.common_simplified import STATE_FILENAME


class State:
    def __init__(self, input_root_folder: str):
        self.base_root_folder = input_root_folder
        self.filepath = os.path.join(self.base_root_folder, STATE_FILENAME)

    def load(self) -> dict:
        # Load state from previous operations
        try:
            with open(self.filepath, "rb") as f:
                state = pickle.load(f)
            return state
        except:
            return None
    
    def save(self, state: dict) -> bool:
        # Save state for use in subsequent operations
        try:
            with open(self.filepath, "wb") as f:
                pickle.dump(state, f)
            return True
        except:
            return False

    def delete(self) -> bool:
        try:
            os.unlink(self.filepath)
            return True
        except:
            return False
