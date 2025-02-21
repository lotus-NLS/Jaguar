import os.path

from engine import LotusEngine
from engine.l1_agents.guidance.workflowy import Mandate
from eval.nlunittest import NLUnittest

# ---------------------------------------------------

# class HardwareTask(NLUnittest):
#     def test_research(self):
#         engine = LotusEngine()
#         answer = engine.resarch_routine(workflowy=TaskWS._hardware_summary(),
#                                         query=f'Please give me a summary of my hardware', max_steps=5)
#
#         property_query = ('The #msg gives information about each of the following hardware devices:'
#                           f'CPU, GPU, RAM, Disks and Motherboard. If information cannot be retrieve a reason is given')
#         evaluation = self.evaluateProperty(msg=answer, prop=property_query)
#         self.assertTrue(evaluation == True)


if __name__ == "__main__":
    script_dirpath = os.path.dirname(__file__)
    tasks_fpath = os.path.join(script_dirpath, 'tasks.txt')
    with open(tasks_fpath, 'r') as f:
        content = f.read()
        parts = content.split('++')
        parts = parts[1:]

    mandate_dict = {}
    for p in parts:
        lines = p.split('\n')
        name = lines[0]
        remaining = '\n'.join(lines[1:])
        mandate_dict[name] = remaining
        mandate = Mandate.from_yaml(s=remaining)
        print(mandate.get_tree())





    # def resarch_routine(self, workflowy : Workflowy, query : str, max_steps : int) -> str:
    #     aos = AOS(workspaces=[browser], workflowy=workflowy)
    #     agent = self._get_default_agent(aos=aos)
    #
    #     num_steps = 0
    #     while agent.is_working() and num_steps < max_steps:
    #         self._work_step(agent)
    #         num_steps += 1
    #     task = Step(memory=Entry.user(msg=query))
    #     response = agent.handle(step=task)
    #     answer = ''
    #     for text in response.get_text_stream():
    #         answer += text
    #     print(f'The following answer was provided: {answer}')