# from engine import LotusEngine
#
# from holytools.devtools import InputSimulator

# if __name__ == "__main__":
#     the_engine = LotusEngine()
#     input_simulator = InputSimulator(inputs=['Please open the Workflowy tool and work for 5 minutes'])
#     input_simulator.redirect_input()
#
#     the_engine.user_routine()

from engine.l0_engine.dev_monitor import DevServer
if __name__ == "__main__":
    server = DevServer()
    server.serve()