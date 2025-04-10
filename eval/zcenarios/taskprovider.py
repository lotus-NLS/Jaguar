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

        self.mandate_dict = {}
        for p in parts:
            lines = p.split('\n')
            name = lines[0]
            remaining = '\n'.join(lines[1:])
            task = Task.from_yaml(s=remaining)
            self.mandate_dict[name] = task

    def get_task(self, name : str) -> Task:
        return self.mandate_dict[name]


if __name__ == "__main__":
    testtask = Task.from_yaml(s='- Test: Mark this task in the TaskTracker as completed. It only serves to test the tasktracker completion functionality.')
    print(f'done')
