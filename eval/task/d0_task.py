from multiprocessing import Process

from eval.basetests import TaskUnittest
from eval.zcenarios.browser import run_basic_server
from eval.zcenarios.python import BasicProject

# ---------------------------------------------------


class TerminalTasks(TaskUnittest):
    def test_gpu_research(self):
        prop = ('The #msg provides information about the GPU model. It states that the grpahics card is'
                    'an NVIDIA GeForce GTX 1060')
        report_query = 'Please state the model of the GPU that you found'

        gpu_research = self.evaluate_task_performance(task_name='simplehardware', prop=prop, query=report_query)
        self.assertTrue(gpu_research)

    def test_hardware_summary(self):
        prop = ('The #msg gives information about each of the following hardware devices:'
                    'CPU, GPU, RAM, Disks and Motherboard')
        report_query = ('Please summarize the hardware information that you found. '
                        'Include the CPU, GPU, RAM, Disks and Motherboard')
        is_successful = self.evaluate_task_performance(task_name='hardware', prop=prop, query=report_query)
        self.assertTrue(is_successful)


class BrowserTasks(TaskUnittest):
    def test_enter_info(self):
        p = Process(target=run_basic_server, args=(8000,))
        p.start()

        query = 'What is the word that was presented to you after entering a word into the text box'
        prop = f'The #msg states that the word presented on the webpage was Spaetzle'
        is_successful = self.evaluate_task_performance(task_name='enter', prop=prop, query=query)
        self.assertTrue(is_successful)

        p.kill()

    def test_stackexchange(self):
        query = 'What is the first word on the most upvoted answer from the stackexchange post?'
        prop = 'The #msg provides information about the first result of the search. '
        is_successful = self.evaluate_task_performance(task_name='stackexchange', prop=prop, query=query)
        self.assertTrue(is_successful)


class PythonTasks(TaskUnittest):
    def test_read_file(self):
        proj = BasicProject()

        query = 'What is bottom most function in the calculator module?'
        prop = ('The #msg provides information about the bottom most function in the calculator module. '
                'It states that the bottom most function is called log')
        is_successful = self.evaluate_task_performance(task_name=f'read_{proj.proj_dirpath}', prop=prop, query=query)
        self.assertTrue(is_successful)

    def test_run_api_retriever(self):
        proj = BasicProject()

        query = 'What was the content of the recieved message?'
        prop = 'The #msg states that the content of the received message was Farfalle'
        is_successful = self.evaluate_task_performance(task_name=f'run_{proj.proj_dirpath}', prop=prop, query=query)
        self.assertTrue(is_successful)

    @staticmethod
    def run_api_server():
        from flask import Flask

        app = Flask(__name__)

        @app.route('/')
        def farfalle():
            return {'message': 'Farfalle'}

        if __name__ == '__main__':
            app.run(port=8002)


if __name__ == "__main__":
    bt = BrowserTasks()
    bt.setUpClass()
    bt.setUp()
    bt.test_enter_info()
