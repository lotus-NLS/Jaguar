from __future__ import annotations

from typing import Optional


# -----------------------------------------------------

class Task:
    def __init__(self, content : str = '', identifier : str = '', is_root : bool = False):
        self.is_root : bool = is_root
        self._content : str = content
        self.identifier : str = identifier

        self.comment : str = ''
        self.is_complete : bool = False
        self.is_retry : bool = False
        self.subtasks : list[Task] = []

    def collect_retry(self) -> Optional[Task]:
        if len(self.subtasks) == 0:
            return Task(content=self._content) if self.is_retry else None
        else:
            if self.is_retry:
                retryable_subtasks = [Task(content=t._content) for t in self.subtasks]
            else:
                retryable_subtasks = [st.collect_retry() for st in self.subtasks]
                retryable_subtasks = [st for st in retryable_subtasks if st is not None]

            new_task = Task(content=self._content, is_root=self.is_root)
            for st in retryable_subtasks:
                new_task.subtasks.append(st)
            return new_task if len(retryable_subtasks) > 0 else None

    def is_recursively_handled(self) -> bool:
        if not self.subtasks:
            return self.is_complete or self.is_retry
        else:
            return all(st.is_recursively_handled() for st in self.subtasks)

    def get_content(self) -> str:
        if self.is_root:
            raise ValueError('Root task is only placeholder')
        else:
            return self._content

    @classmethod
    def get_example(cls) -> Task:
        return cls.from_yaml(s=f'- Example')

    @classmethod
    def from_yaml(cls, s : str) -> Task:
        lines = s.split('\n')
        root = Task(is_root=True)
        ancestors = [root]

        def get_ancestor_indent():
            return len(ancestors) - 2

        for l in lines:
            blank_spaces = len(l) - len(l.lstrip(' '))
            if not blank_spaces % 4 == 0:
                raise ValueError(f'Indentation error at line: {l}. Indentation must be multiple of 4, is {blank_spaces}')
            indentation = blank_spaces // 4
            if indentation > get_ancestor_indent() + 1:
                raise ValueError(f'Indentation is more than two increments larger than parent at line: {l}')

            while indentation < get_ancestor_indent() + 1:
                ancestors.pop()
            if indentation == get_ancestor_indent() + 1:
                a = ancestors[-1]
                new = a.add_subtask(msg=l.strip(' -'))
                ancestors.append(new)
        return root

    def add_comment(self, msg : str):
        self.comment += msg

    def add_subtask(self, msg : str) -> Task:
        new_task = Task(content=msg, identifier=f'{self.identifier}{len(self.subtasks) + 1}')
        self.subtasks.append(new_task)
        return new_task

    def complete(self):
        self.is_complete = True
        for st in self.subtasks:
            st.complete()

    def retry(self):
        self.is_retry = True
        for st in self.subtasks:
            st.retry()

    # --------------------------------------------
    # get

    def get_descendant(self, identifier : str) -> Task:
        if len(identifier) == 0:
            return self

        first_num = int(identifier[0])
        partial_id = identifier[1:]

        parent_idx = first_num-1
        if parent_idx < 0:
            raise ValueError(f'Invalid task id: {identifier}. Must be greater than 0')

        return self.subtasks[parent_idx].get_descendant(partial_id)

    def get_tree(self, pre_indent : str = '') -> str:
        if not self.is_root:
            if self.is_complete:
                mark = 'x'
            elif self.is_retry:
                mark = '🚫'
            else:
                mark = ' '
            status_and_id = f'[{mark}] {self.identifier}: '
            tree = f'{pre_indent}{status_and_id}{self._content}\n'
            if self.comment:
                tree += f'{pre_indent}{len(status_and_id)*" "}{self.comment}\n'
        else:
            tree = ''

        for st in self.subtasks:
            indent = '\t' + pre_indent if not self.is_root else ''
            tree += f'{st.get_tree(pre_indent=indent)}'

        if self.is_root:
            tree = tree.rstrip()

        return tree