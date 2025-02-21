import os.path

from engine import LotusEngine
from engine.l1_agents.guidance.workflowy import Mandate
from eval.nlunittest import NLUnittest

# ---------------------------------------------------

class HardwareTask(NLUnittest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        script_dirpath = os.path.dirname(__file__)
        tasks_fpath = os.path.join(script_dirpath, 'tasks.txt')
        with open(tasks_fpath, 'r') as f:
            content = f.read()
            parts = content.split('++')
            parts = parts[1:]

        cls.mandate_dict = {}
        for p in parts:
            lines = p.split('\n')
            name = lines[0]
            remaining = '\n'.join(lines[1:-1])
            mandate = Mandate.from_yaml(s=remaining)
            cls.mandate_dict[name] = mandate
            print(f'Mandate {name}:\n {mandate.get_tree()}')


    def test_gpu_research(self):
        engine = LotusEngine()
        engine.work(mandate=self.mandate_dict['simplehardware'], max_steps=10)
        user_msg = f'What is my GPU'
        answer = engine.converse(msg=user_msg)

        print(f'+------------------------+')
        print(f'User: {user_msg}')
        print(f'Agent: {answer}')

        # property_query = ('The #msg gives information about each of the following hardware devices:'
        #                   f'CPU, GPU, RAM, Disks and Motherboard. If information cannot be retrieve a reason is given')
        # evaluation = self.evaluateProperty(msg=answer, prop=property_query)
        # self.assertTrue(evaluation == True)


if __name__ == "__main__":
    HardwareTask.execute_all()
