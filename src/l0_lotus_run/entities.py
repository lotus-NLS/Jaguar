import threading

from src.l1_lotus_tools import RUN,FILE_IO,SEARCH
from src.l1_lotus_tools import UPDATE_MANDATE, INITIALIZE_MANDATE
from src.l1_lotus_tools import Tool
from src.l2_lotus_agent import Agent, Task
from src.l3_lotus_core import LingualEntity, DialogueRole, Entry

# ---------------------------------------------------------


class Alpha(Agent):
    def __init__(self):
        super().__init__()
        self.setup_tools()
        self.launch()

    # ---------------------------------------------------
    # Setup

    def setup_tools(self):
        all_tools = [RUN(), FILE_IO(), SEARCH(), UPDATE_MANDATE(), INITIALIZE_MANDATE()]
        self.tool_handler.tool_dict = {tool.name : tool for tool in all_tools}

        for tool in all_tools:
            self.add_tool(tool)

            if tool.name == UPDATE_MANDATE.__name__:
                tool.disable()


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
                self.log_tool_msg(msg=warning_msg)

        return tool_log

    # ---------------------------------------------------
    # Loop

    def launch(self):
        threading.Thread(target=self.loop).start()

    def loop(self):
        while True:
            active_task = self.task_queue.get()
            entries_to_process = self.get_unread_entries()

            self.do(enforce_mandate_init=active_task.requires_init_mandate())

            if self.mandate.is_active() and not self.task_queue.get_work_task_present():
                self.task_queue.put(Task(is_mandate_task=True))

            for entry in entries_to_process:
                entry.mark_read()
            self.task_queue.complete_active_task()


    def react(self, entry: Entry):
        if entry.get_role() == DialogueRole.user_role() and not self.task_queue.get_dialogue_task_present():
            entry_requires_mandate = entry.get_is_enforce_mandate()
            print(f'[Temp Debug]: Enforcing mandate init: {entry_requires_mandate}')
            self.task_queue.put(Task.make_dialogue_task(enforce_init_mandate=entry_requires_mandate))


class User(LingualEntity):
    def __init__(self):
        super(User, self).__init__(role=DialogueRole.user_role())

    def react(self, entry : Entry):
        pass
