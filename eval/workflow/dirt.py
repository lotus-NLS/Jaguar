from engine.l0_main import LotusEngine
from engine.l1_agents.guidance.workflow import testWorkflow

if __name__ == "__main__":
    engine = LotusEngine()
    engine.do_workflow(testWorkflow)

