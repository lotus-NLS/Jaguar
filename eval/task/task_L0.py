from multiprocessing import Process

from eval.base import TaskUnittest
from eval.zcenarios.browser import run_basic_server
from eval.zcenarios.python import BasicProject

# ---------------------------------------------------


class TerminalTasks(TaskUnittest):
    def test_gpu_research(self):
        prop = ('The #msg provides information about the GPU model. It states that the grpahics card is'
                    'an NVIDIA GeForce GTX 1060')
        report_query = 'Please state the model of the GPU that you found'

        gpu_research = self.semantic_task_eval(task_name='simplehardware', prop=prop, query=report_query)
        self.assertTrue(gpu_research)

    def test_hardware_summary(self):
        prop = ('The #msg gives information about each of the following hardware devices:'
                    'CPU, GPU, RAM, Disks and Motherboard')
        report_query = ('Please summarize the hardware information that you found. '
                        'Include the CPU, GPU, RAM, Disks and Motherboard')
        is_successful = self.semantic_task_eval(task_name='hardware', prop=prop, query=report_query)
        self.assertTrue(is_successful)


class BrowserTasks(TaskUnittest):
    def test_enter_info(self):
        p = Process(target=run_basic_server, args=(8000,))
        p.start()

        query = ('What is the word that was presented to you after entering a word into the text box?'
                 'The word that was presented to you is the #keyword')
        is_successful = self.keyword_task_eval(task_name='enter', query=query, keyword='Spaetzle')
        self.assertTrue(is_successful)

        p.kill()

    def test_stackexchange(self):
        query = ('What is the first word on the most upvoted answer from the stackexchange post?'
                 'The first word is the required #keyword')
        is_successful = self.keyword_task_eval(task_name='stackexchange', query=query, keyword='Increasing')
        self.assertTrue(is_successful)


class PythonTasks(TaskUnittest):
    def test_read_file(self):
        proj = BasicProject()

        query = 'What is bottom most function in the calculator module? The name of this function is the #keyword'
        is_successful = self.keyword_task_eval(task_name=f'read_{proj.proj_dirpath}', keyword='log', query=query)
        self.assertTrue(is_successful)

    def test_run_api_retriever(self):
        proj = BasicProject()

        query = 'What was the content of the recieved message? The content of this function is the #keyword'
        is_successful = self.keyword_task_eval(task_name=f'run_{proj.proj_dirpath}', query=query, keyword='Farfalle')
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
