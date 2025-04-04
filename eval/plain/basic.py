import os
import random
import tempfile

from engine.l2_models import OpenAIModel, InfConfig
from engine.l2_models.language import Context, Message
from holytools.fsys import Directory
from tests.credtest import CredTest


# ---------------------------------------------------------------

class TestFileStructure(CredTest):
    def setUp(self):
        fsys_structure = set()

        self.tmp_dirpath = tempfile.mkdtemp()
        root_folder = VirtualFolder(name='root', path = self.tmp_dirpath)
        fsys_structure.add(root_folder)
        for j in range(200):
            random_element : VirtualFolder = random.choice(list(fsys_structure))

            child_dirpath = os.path.join(random_element.path, f'Directory{j}')
            directory = VirtualFolder(name=f'Directory{j}', path=child_dirpath)
            random_element.add_child(child=directory)
            fsys_structure.add(directory)

        def create_childs(root_dirpath : str, the_dir : VirtualFolder):
            dirpaths = [os.path.join(root_dirpath, d.name) for d in the_dir.children]
            for d in dirpaths:
                os.makedirs(d)
            for c in the_dir.children:
                create_childs(root_dirpath=os.path.join(root_dirpath, c.name), the_dir=c)


        self.random_folder : VirtualFolder = random.choice(list(fsys_structure))
        create_childs(root_dirpath=self.tmp_dirpath, the_dir=root_folder)
        print(f'- Created file structure at {self.tmp_dirpath}')

    def test_path_access(self):
        root_dir = Directory(path=self.tmp_dirpath)
        dir_view = root_dir.get_tree()
        model = OpenAIModel.default_model(api_key=self.openai_apikey)

        ctx = Context.singleton(entry=Message.agent(msg=dir_view))
        ctx += Context.singleton(entry=Message.user(msg=f'Give the file path of file {self.random_folder.name}'
                                                      f' relative to the root'))

        reps = 5
        successes = []
        for j in range(reps):
            generation = model.get_generation(context=ctx, config=InfConfig())
            print(f'- Context = {ctx}')

            generation.exhaust()
            text = generation.get_text()
            print(text)

            relative_path = os.path.relpath(self.random_folder.path, start=self.tmp_dirpath)
            successes.append(relative_path in text)
        symbol = '✅' if sum(successes) == reps else '❌'
        print(f'- Successs score = {sum(successes)}/{reps}:\n'
              f'- Eval status = {symbol}')
        self.assertTrue(sum(successes) == reps)


class VirtualFolder:
    def __init__(self, name : str, path : str, children=None):
        self.name : str = name
        self.path : str = path
        self.children : list[VirtualFolder] = children if children is not None else []

    def add_child(self, child):
        self.children.append(child)

if __name__ == "__main__":
    TestFileStructure.execute_all()