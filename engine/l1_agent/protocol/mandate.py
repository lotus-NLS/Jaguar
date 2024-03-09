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
        self.actions =  {name: attr for name, attr in attr_dict if callable(attr) and name.startswith('a')}


    def a_complete(self):
        self.is_complete = True


    def a_discard(self, uuid : str):
        self.parent._remove_child(uuid=uuid)


    def a_add_subobjective(self, desc : str) -> Mandate:
        new = Mandate(desc=desc, parent=self)
        self.child_map[new.uuid] = new
        return new


    def a_update(self, info_dict : dict):
        for item in info_dict:
            obj = self.a_add_subobjective(desc=item)
            obj.a_update(info_dict=info_dict[item])


    def _remove_child(self, uuid : str):
        del self.child_map[uuid]

    # ----------------------------------------------------
    # repr

    def _as_msg(self) -> Optional[str]:
        the_str = f'You have been granted a mandate for the following plan of action'
        conditional_check = 'x' if self.a_complete() else ' '
        the_str += f' '*self.level + f'[{conditional_check}]: {self.desc}'
        for child in list(self.child_map.values()):
            the_str += child._as_msg()

        return the_str

    # ----------------------------------------------------
    # tree navigation

    def get(self, uuid : str) -> Optional[Mandate]:
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

#     def react(self, entry: Entry):
#         if entry.get_role() == DialogueRole.user_role() and not self.task_queue.dialogue_task_is_enqueued():
#
#             required_funct_name = None if not entry.flags.get(flag=Flag.MANDATE) else INITIALIZE_MANDATE.__name__
#             entries_to_process = self.get_unread_entries()
#             new_dialogue_task = Task(mandate = None,
#                                      new_entries=entries_to_process,
#                                      required=required_funct_name)
#             self.task_queue.put(new_dialogue_task)
#
#             for entry in entries_to_process:
#                 entry.mark_processed()


#
#
#     def loop(self):
#         while True:
#             active_task : Task = self.task_queue.get()
#             self.do(task=active_task)
#
#             if self.mandate.is_active() and not self.task_queue.get_work_task_present():
#                 self.task_queue.put(Task(mandate=self.mandate))
#                 self.task_queue.put(Task(mandate=self.mandate,
#                                          required=UpdateMandate.__name__))
#



#
#     # ---------------------------------------------------
#     # Tool setup
#
#     def setup_tools(self):
#         public_tools = [Command.make(), FileIO.make(), WebSearch.make()]
#         private_tools = [UpdateMandate.make(is_public_tool=False), INITIALIZE_MANDATE.make(is_public_tool=False)]
#         all_tools : list[Tool] = public_tools + private_tools
#         self.os.tool_dict = {tool.name : tool for tool in all_tools}
#
#         for tool in all_tools:
#             self.add_tool(tool)