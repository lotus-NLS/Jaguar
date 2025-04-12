import os

from engine.l1_agents import Task


class TaskProvider:
    def __init__(self):
        script_dirpath = os.path.dirname(__file__)
        tasks_fpath = os.path.join(script_dirpath, 'tasks.txt')
        with open(tasks_fpath, 'r') as f:
            content = f.read()
            parts = content.split('++')
            parts = parts[1:]

        self.yaml_dict = {}
        for p in parts:
            lines = p.split('\n')
            name = lines[0]
            remaining = '\n'.join(lines[1:])
            self.yaml_dict[name] = remaining

    def get_task(self, identifier : str) -> Task:
        segments = identifier.split('_')
        name = segments[0]
        args = segments[1:]
        task_content = self.yaml_dict[name]

        for j, seg in enumerate(args):
            task_content = task_content.replace(f'#{j+1}', seg)

        task_content = task_content.strip()
        task = Task.from_yaml(s=task_content)
        return task

if __name__ == "__main__":
    prov = TaskProvider()
    asdf_task = prov.get_task(identifier='read_/tmp/asdf')
    print(asdf_task.get_tree())

