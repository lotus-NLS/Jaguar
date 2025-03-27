from engine import LotusEngine
from engine.l1_agents import Workflow

if __name__ == "__main__":
    engine = LotusEngine()

    engine.converse()

    # unittest_workflow = Workflow.unittest(module_name=f'LotusEngine in lotus_engine.py',
    #                                       tests_directory='tests',
    #                                       project_dirpath=f'/home/daniel/lotus/engine')
    # engine.do_workflow(wf=unittest_workflow)
