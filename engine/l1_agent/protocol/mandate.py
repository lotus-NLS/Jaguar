from __future__ import annotations
from typing import Union, Optional

from uuid import uuid4
# ---------------------------------------------------------

class Mandate:
    all_mandates : dict[str, Mandate] = {}

    def __init__(self, desc : str, parent : Optional[Mandate] = None):
        self._parent = parent
        self.desc: str = f'{desc}'

        self.uuid : str = self.get_uuid()
        self._complete : bool = False
        self._children : list[Mandate] = []

        if parent:
            self.level : int = parent.level+1
        else:
            self.level : int = 0

        attr_dict = self.__dict__.items()
        self.actions =  {name: attr for name, attr in attr_dict if callable(attr) and not name.startswith('_')}


    def complete(self):
        self._complete = True


    def add_subobjective(self, desc : str):
        new = Mandate(desc=desc, parent=self)
        self._children.append(new)
        return new


    def get_uuid(self):
        while True:
            uuid = f'{uuid4()}'[:4]
            if not uuid in self.all_mandates:
                self.all_mandates[uuid] = self
                return uuid

    @classmethod
    def mark_done(cls, uuid : str):
        mandate = cls.all_mandates.get(uuid)
        if mandate:
            mandate.complete()

    # ----------------------------------------------------
    # get

    def _get_parent(self) -> Mandate:
        return self._parent


    def _as_msg(self) -> Optional[str]:
        conditional_check = 'x' if self.complete() else ' '
        the_str = f' '*self.level + f'[{conditional_check}]: {self.desc}'
        for child in self._children:
            the_str += child._as_msg()

        return the_str

