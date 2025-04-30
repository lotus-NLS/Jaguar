import os.path
import tempfile
from multiprocessing import Process

from engine.l3_aos.workspaces import Terminal, Browser
from engine.l3_aos.workspaces.python_ide import PythonIDE
from eval.taskbase import TaskUnittest
from eval.scenarios.browser import run_basic_server
from eval.scenarios.python import BasicProject

# ---------------------------------------------------


class TerminalTasks(TaskUnittest):
    def test_gpu_research(self):
        query = ('Please state the model of the GPU that you found. Like so'
                 '[Manufacturer] [Product line] [Model]. This full information consitutes the #keyword')

        gpu_model = 'NVIDIA GeForce GTX 1060'
        gpu_research = self.keyword_task_eval(task_name='simplehardware', query=query, keyword=gpu_model, fuzzy=True)
        self.assertTrue(gpu_research)

    def test_hardware_summary(self):
        query = 'Please use the dict report tool to report your findings'
        target_dict = {
            'GPU': 'GeForce GTX 1060 6GB',
            'CPU': 'Intel Core i3-8100 CPU',
            'RAM storage in GB': '32GiB',
            'Downrounded Root drive storage in GB': '931',
            'Motherboard': 'ASRock Z390 Pro4'
        }

        is_accurate = self.dict_task_eval(task_name='hardware', query=query, target_dict=target_dict)
        self.assertTrue(is_accurate)

    def test_nano(self):
        fpath = tempfile.mktemp()
        content = 'Ramen'
        task = self.task_provider.get_task(f'nano_{fpath}_{content}')
        self.engine.do_task(task, max_steps=10)

        workspaces = self.engine.agent.aos.get_workspaces()
        terminal = [ws for ws in workspaces if ws.get_name() == Terminal.get_name()][0]

        text = terminal.get_text()
        self.assertTrue('GNU nano' not in text)

        if not os.path.isfile(fpath):
            self.fail('File was not created')

        with open(fpath, 'r') as f:
            file_content = f.read()
            print(f'-Actual content  : "{file_content}"')
            print(f'-Expected content: "{content}"')
            self.assertTrue(file_content == content)

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

    def test_installation_navigation(self):
        task = self.task_provider.get_task('rosinstall')
        self.engine.do_task(task=task, max_steps=10)

        browser : Browser = self.engine.agent.aos.browser
        url = browser.emulator.get_url()
        self.assertTrue(url == 'https://docs.ros.org/en/humble/Installation.html')


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

    def test_build_and_run(self):
        proj = BasicProject()

        task = self.task_provider.get_task(f'build_{proj.proj_dirpath}')
        self.engine.do_task(task=task, max_steps=10)

        python_ide : PythonIDE = self.engine.agent.aos.ide
        hello_fpath = os.path.join(proj.proj_dirpath, 'hello.py')
        output = python_ide.output_map[hello_fpath]
        expected_output = 'Hello World :)'

        print(f'- Output:\n{output}')
        print(f'- Expected output:\n{expected_output}')

        self.assertTrue(expected_output in output)


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
    tt = TerminalTasks.ready()
    # bt = BrowserTasks.ready()
    # pt = PythonTasks.ready()

    tt.test_hardware_summary()
