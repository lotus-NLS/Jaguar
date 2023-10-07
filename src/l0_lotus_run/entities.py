import threading
from src.l3_lotus_core import LingualEntity, DialogueRole, Entry
from src.l2_lotus_agent import Agent, Task
from src.l1_lotus_tools import RUN,FILE_IO,SEARCH, UPDATE_MANDATE, INITIALIZE_MANDATE, Tool

# ---------------------------------------------------------

class Alpha(Agent):
    def __init__(self):
        super().__init__()
        self.setup_tools()
        self.launch()

    # ---------------------------------------------------
    # Loop

    def launch(self):
        threading.Thread(target=self.loop).start()


    def loop(self):
        while True:
            active_task : Task = self.task_queue.get()

            if active_task.requires_mandate_init:
                self.do(required_funct_name=INITIALIZE_MANDATE.__name__)
            else:
                self.do()

            if self.mandate.is_active() and not self.task_queue.get_work_task_present():
                self.task_queue.put(Task(mandate=self.mandate))

            self.task_queue.complete_active_task()


    def react(self, entry: Entry):
        if entry.get_role() == DialogueRole.user_role() and not self.task_queue.get_dialogue_task_present():
            entries_to_process = self.get_unread_entries()
            new_dialogue_task = Task.make_dialogue_task(enforce_init_mandate=entry.get_enforce_mandate_flag(),
                                                        entries_to_process=entries_to_process)
            self.task_queue.put(new_dialogue_task)

            for entry in entries_to_process:
                entry.mark_processed()

    # ---------------------------------------------------
    # Tool setup

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



class User(LingualEntity):
    def __init__(self):
        super(User, self).__init__(role=DialogueRole.user_role())

    def react(self, entry : Entry):
        pass
