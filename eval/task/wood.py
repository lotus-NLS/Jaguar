from eval.nlu import NLU

# ---------------------------------------------------

class TerminalTask(NLU):
    def test_gpu_research(self):
        task = self.task_provider.get_task('simplehardware')
        self.engine.do_task(task=task, max_steps=10)
        response = self.engine.do_talk(query='Please summarize the gathered information')
        property_query = ('The #msg provides information about the GPU model. It states that the grpahics card is'
                          'an NVIDIA GeForce GTX 1060')

        gpu_research_successful = self.evaluateProperty(msg=response, prop=property_query)
        self.assertTrue(gpu_research_successful)

    def test_hardware_summary(self):
        task = self.task_provider.get_task('hardware')
        property_query = ('The #msg gives information about each of the following hardware devices:'
                          f'CPU, GPU, RAM, Disks and Motherboard. If information cannot be retrieve a reason is given')
        self.engine.do_task(task=task, max_steps=15)
        response = self.engine.do_talk(query='Please summarize the gathered information')

        hardware_summary_successful = self.evaluateProperty(msg=response, prop=property_query)
        self.assertTrue(hardware_summary_successful)


class BrowserTask(NLU):
    def test_cat_search(self):
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
    hw_test.setUpClass()
    hw_test.test_hardware_summary()
