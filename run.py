from engine import LotusEngine
from holytools.devtools import InputSimulator

if __name__ == "__main__":
    the_engine = LotusEngine()
    input_simulator = InputSimulator(inputs=['Please open the Workflowy tool and work for 5 minutes'])
    input_simulator.redirect_input()

    the_engine.run()