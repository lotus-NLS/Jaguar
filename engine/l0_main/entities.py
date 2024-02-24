from pyutils import DaemonThread
import copy

from api import Entry, DialogueRole, Flag
from engine.l3_singletons.io import EngineIO
from engine.l1_agent import LingualEntity
from engine.l1_agent import Agent, Task
from engine.l3_tools import COMMAND,FILE_IO,SEARCH, UPDATE_MANDATE, INITIALIZE_MANDATE, Tool


# ---------------------------------------------------------

class Alpha(Agent):
    def __init__(self):
        super().__init__()
        self.setup_tools()
        self.launch()
        self.model.enable_debugging()

    # ---------------------------------------------------
    # Loop

    def launch(self):
        launch_thread = DaemonThread(target=self.loop)
        launch_thread.start()


    def loop(self):
        while True:
            active_task : Task = self.task_queue.get()
            self.do(task=active_task)

            if self.mandate.is_active() and not self.task_queue.get_work_task_present():
                self.task_queue.put(Task(mandate=self.mandate))
                self.task_queue.put(Task(mandate=self.mandate,
                                         required_funct_name=UPDATE_MANDATE.__name__))


    def react(self, entry: Entry):
        if entry.get_role() == DialogueRole.user_role() and not self.task_queue.dialogue_task_is_enqueued():

            required_funct_name = None if not entry.flags.get(flag=Flag.MANDATE) else INITIALIZE_MANDATE.__name__
            entries_to_process = self.get_unread_entries()
            new_dialogue_task = Task(mandate = None,
                                     entries_to_respond_to=entries_to_process,
                                     required_funct_name=required_funct_name)
            self.task_queue.put(new_dialogue_task)

            for entry in entries_to_process:
                entry.mark_processed()

    # ---------------------------------------------------
    # Tool setup

    def setup_tools(self):
        public_tools = [COMMAND.make(), FILE_IO.make(), SEARCH.make()]
        private_tools = [UPDATE_MANDATE.make(is_public_tool=False), INITIALIZE_MANDATE.make(is_public_tool=False)]
        all_tools : list[Tool] = public_tools + private_tools
        self.tool_handler.tool_dict = {tool.name : tool for tool in all_tools}

        for tool in all_tools:
            self.add_tool(tool)


    def add_tool(self, tool : Tool):
        tool.external_log = self.get_tool_logger(tool_name=tool.name)
        tool.acting_agent = self


    def get_tool_logger(self,tool_name: str) -> callable:
        max_tokens_tool = 1000

        def tool_log(msg: str):
            num_tokens = self.model.get_token_count(the_str=msg)

            if num_tokens > max_tokens_tool:
                msg = self.model.get_limited_string(the_str=msg, max_tokens=max_tokens_tool)

            self.log_tool_msg(msg=msg, tool_name=tool_name)
            if num_tokens > max_tokens_tool:
                warning_msg = '[Progress]: The tool output exceeded the maximum number of tokens of 1000 and was shortened to that length ...'
                self.log_tool_msg(msg=warning_msg, tool_name=tool_name)

        return tool_log


class User(LingualEntity):
    def __init__(self):
        super().__init__(role=DialogueRole.user_role())
        self.user_id = 'the_user'


    def logger(self, new_entry : Entry):
        if new_entry.get_role() == DialogueRole.user_role():
            return

        the_entry = copy.deepcopy(new_entry)
        the_entry.flags.set(flag=Flag.IS_ENTRY_START,value=self.current_entry is None)

        # print(f'{the_entry.get_content()}'.__repr__())
        EngineIO().send(entry=the_entry)


    def react(self, entry : Entry):
        pass
