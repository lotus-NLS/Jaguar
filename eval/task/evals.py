import os.path
import tempfile
from multiprocessing import Process

from engine.l3_aos.workspaces import Terminal, Browser
from engine.l3_aos.workspaces.python_ide import PythonIDE
from eval.task.frame.servers import BrowserServers
from eval.uniteval import Uniteval
from holytools.logging import CaptureLogs
from holytools.network import IpProvider


# ---------------------------------------------------

class TerminalEval(Uniteval):
    def test_gpu_research(self):
        query = ('Please state the model of the GPU that you found. Like so'
                 '[Manufacturer] [Product line] [Model]. This full information consitutes the #keyword')
        gpu_model = 'NVIDIA GeForce GTX 1060'

        is_accurate = self.keyword_eval(task_name='gpu', query=query, keyword=gpu_model, fuzzy=True)
        self.assertTrue(is_accurate)

    def test_hardware_summary(self):
        query = ('Please use the dict report tool to report your findings in the following format:'
                 '  - GPU: [Manufacturer, Series, Model, Memory]'
                 '  - CPU: [Manufacturer, Series Model, Clock rate]'
                 '  - RAM : [Int value]'
                 '  - Largest storage: [Rounded down int value]'
                 '  - Motherboard: [Manufacturer, Model]')
        target_dict = {
            'GPU': 'GeForce GTX 1060 6GB',
            'CPU': 'Intel Core i3-8100 CPU @ 3.60 GHz',
            'RAM storage in GB': '32||31',
            'Largest drive storage in GiB': '931',
            'Motherboard': 'ASRock Z390 Pro4'
        }

        is_accurate = self.dict_eval(task_name='hardware', query=query, target_dict=target_dict, fuzzy=True)
        self.assertTrue(is_accurate)

    def test_nano(self):
        fpath = tempfile.mktemp()
        content = 'Ramen'
        task = self.task_provider.get_task(f'nano\0{fpath}\0{content}')
        self.engine.do_task(task, max_steps=15)

        workspaces = self.engine.agent.aos.get_workspaces()
        terminal = [ws for ws in workspaces if ws.get_name() == Terminal.get_name()][0]
        text = terminal.get_text()
        self.assertTrue('GNU nano' not in text)

        if not os.path.isfile(fpath):
            self.fail('File was not created')

        with open(fpath, 'r') as f:
            file_content = f.read()
            expected_content = f'{content}\n'
            print(f'-Actual content  : "{file_content}"')
            print(f'-Expected content: "{expected_content}"')
            self.assertTrue(file_content == expected_content)


class BrowserEval(Uniteval):
    def test_enter_text(self):
        port = IpProvider.get_free_port()
        p = Process(target=BrowserServers.run_enter_server, args=(port,))
        p.start()

        query = ('What is the word that was presented to you after entering a word into the text box?'
                 'The word that was presented to you is the #keyword')
        is_successful = self.keyword_eval(task_name=f'enter_text\0{port}', query=query, keyword='Spaetzle')
        self.assertTrue(is_successful)
        p.kill()

    def test_stackexchange(self):
        query = ('What is the first word on the most upvoted answer from the stackexchange post?'
                 'The first word is the required #keyword')
        is_successful = self.keyword_eval(task_name='stackexchange', query=query, keyword='Increasing')
        self.assertTrue(is_successful)

    def test_rosinstall(self):
        task = self.task_provider.get_task('rosinstall')
        self.engine.do_task(task=task, max_steps=10)

        browser : Browser = self.engine.agent.aos.browser
        url = browser.emulator.get_url()
        self.assertTrue(url == 'https://docs.ros.org/en/humble/Installation.html')


class PythonEval(Uniteval):
    def test_read_file(self):
        query = 'What is bottom most function in the calculator module? The name of this function is the #keyword'

        is_successful = self.keyword_eval(task_name=f'read_file\0{self.proj_dirpath}', keyword='log', query=query)
        self.assertTrue(is_successful)

    def test_run_api_call(self):
        port = IpProvider.get_free_port()
        p = Process(target=BrowserServers.run_api_server, args=(port,))
        p.start()

        query = 'What was the content of the recieved message? The content of this function is the #keyword'
        is_successful = self.keyword_eval(task_name=f'run_api_call\0{self.proj_dirpath}\0{port}', query=query, keyword='Farfalle')
        self.assertTrue(is_successful)

    def test_build_and_run(self):
        task = self.task_provider.get_task(f'build_and_run\0{self.proj_dirpath}')
        self.engine.do_task(task=task, max_steps=10)

        python_ide : PythonIDE = self.engine.agent.aos.ide
        hello_fpath = os.path.join(self.proj_dirpath, 'hello.py')
        output = python_ide.output_map[hello_fpath]
        expected_output = 'Hello World :)'

        print(f'- Output:\n{output}')
        print(f'- Expected output:\n{expected_output}')
        self.assertTrue(expected_output in output)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--script', type=str, required=True)
    args = parser.parse_args()
    
    log_capture = CaptureLogs()
    with log_capture:
        if args.script == 'nano':
            TerminalEval.evaluate(test_names=['test_nano'])
        elif args.script == 'python':
            PythonEval.evaluate(reps=1)
        elif args.script == 'terminal':
            TerminalEval.evaluate()
        else:
            raise ValueError(f'Unknown script: {args.script}')
