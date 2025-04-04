from engine import LotusEngine
from eval.nlu import NLU

# ---------------------------------------------------

class TerminalTask(NLU):
    def setUp(self):
        super().setUpClass()
        self.engine = LotusEngine()

    def test_gpu_research(self):
        task = self.task_provider.get_task('simplehardware')
        property_query = 'The #msg provides information about the GPU model'
        self.engine.do_task(task=task, max_steps=10, dos=property_query)

        # user_msg = f'What is the model of my GPU?'
        # answer = self.engine.converse(msg=user_msg)
        #

        #
        # evaluation = self.evaluateProperty(msg=answer.writing, prop=property_query)
        # self.assertTrue(evaluation == True)


    def test_hardware_summary(self):
        task = self.task_provider.get_task('hardware')
        property_query = ('The #msg gives information about each of the following hardware devices:'
                          f'CPU, GPU, RAM, Disks and Motherboard. If information cannot be retrieve a reason is given')
        self.engine.do_task(task=task, max_steps=15, dos=property_query)

        # user_msg = f'Please provide me with a summary of my hardwrae including CPU, GPU, RAM, disks and motherboard'
        # answer = self.engine.converse(msg=user_msg)

        # print(f'+------------------------+')
        # print(f'User: {user_msg}')
        # print(f'Agent: {answer}')
        #
        # evaluation = self.evaluateProperty(msg=answer.writing, prop=property_query)
        # self.assertTrue(evaluation == True)



class BrowserTask(NLU):
    def setUp(self):
        super().setUpClass()
        self.engine = LotusEngine()

    def test_search_for_cat(self):
        task = self.task_provider.get_task('cat')
        self.engine.do_task(task=task, max_steps=10)
        user_msg = f'What is the first result from your search for cat videos?'
        answer = self.engine.agent.talk(msg=user_msg)

        print(f'+------------------------+')
        print(f'User: {user_msg}')
        print(f'Agent: {answer}')

        property_query = 'The #msg provides information about the GPU model'
        evaluation = self.evaluateProperty(msg=answer.text, prop=property_query)
        self.assertTrue(evaluation == True)



if __name__ == "__main__":
    hw_test = TerminalTask()
    hw_test.setUp()
    hw_test.test_gpu_research()