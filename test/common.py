# LCAutomate CLI calls
class LCAutomateCLICalls:
    MODEL = ["LCAutomate", "-i", "resources/CRSC_Barley_No_SOC-simplified/", "model"]

    @staticmethod
    def list():
        return [
            LCAutomateCLICalls.MODEL,
        ]
