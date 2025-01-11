from engine import LotusEngine
from holytools.devtools import InputSimulator

if __name__ == "__main__":
    the_engine = LotusEngine(use_local_credentials=True)
    input_simulator = InputSimulator(inputs=['Please open the Workflowy tool with yaml_str = ""'])
    input_simulator.redirect_input()

    the_engine.run()