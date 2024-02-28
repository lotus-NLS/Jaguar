from __future__ import annotations
from typing import Optional
from uuid import uuid4
# ---------------------------------------------------------

class Mandate:
    def __init__(self, desc : str, parent : Optional[Mandate] = None):
        self.parent = parent
        self.desc: str = f'{desc}'

        self.uuid : str = self._create_free_uuid()
        self.is_complete : bool = False
        self.child_map : dict[str, Mandate] = {}

        if parent:
            self.level : int = parent.level+1
        else:
            self.level : int = 0

        attr_dict = self.__dict__.items()
        self.actions =  {name: attr for name, attr in attr_dict if callable(attr) and not name.startswith('_')}


    def complete(self):
        self.is_complete = True


    def discard(self, uuid : str):
        self.parent._remove_child(uuid=uuid)


    def add_subobjective(self, desc : str) -> Mandate:
        new = Mandate(desc=desc, parent=self)
        self.child_map[new.uuid] = new
        return new


    def update(self, info_dict : dict):
        for item in info_dict:
            obj = self.add_subobjective(desc=item)
            obj.update(info_dict=info_dict[item])

    def _remove_child(self, uuid : str):
        del self.child_map[uuid]

    # ----------------------------------------------------
    # repr

    def _as_msg(self) -> Optional[str]:
        conditional_check = 'x' if self.complete() else ' '
        the_str = f' '*self.level + f'[{conditional_check}]: {self.desc}'
        for child in list(self.child_map.values()):
            the_str += child._as_msg()

        return the_str

    # ----------------------------------------------------
    # tree navigation

    def _get_descendant(self, uuid : str) -> Optional[Mandate]:
        desc_map = self._get_descendants_map()
        return desc_map.get(uuid)


    def _get_root(self) -> Mandate:
        up, now = self.parent, self
        while up:
            up, now = up.parent, up
        return now


    def _get_descendants_map(self) -> dict[str, Mandate]:
        desc_map = {}
        for child in list(self.child_map.values()):
            desc_map[child.uuid] = child
            desc_map.update(child._get_descendants_map())
        return desc_map


    def _create_free_uuid(self) -> str:
        root = self._get_root()
        desc_map = root._get_descendants_map()
        while True:
            uuid = f'{uuid4()}'[:4]
            if not desc_map.get(uuid):
                return uuid