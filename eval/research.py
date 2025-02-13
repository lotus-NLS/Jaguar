from engine import LotusEngine
from engine.l3_aos.workspaces.workflowy import Workflowy
from eval.baseval import SemanticUnittest

# ---------------------------------------------------

class HardwareTask(SemanticUnittest):
    def test_research(self):
        engine = LotusEngine()
        answer = engine.resarch_routine(workflowy=Workflowy._hardware_summary(),
                                       query=f'Please give me a summary of my hardware', max_steps=5)

        property_query = ('The #msg gives information about each of the following hardware devices:'
                          f'CPU, GPU, RAM, Disks and Motherboard. If information cannot be retrieve a reason is given')
        evaluation = self.evaluateProperty(msg=answer, prop=property_query)
        self.assertTrue(evaluation == True)


if __name__ == "__main__":
    HardwareTask.execute_all()