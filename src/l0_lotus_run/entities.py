from src.l2_lotus_agent import Agent, ConversationParticipant, DialogueRole
from src.l1_lotus_tools import RUN,FILE_IO,SEARCH
from src.l1_lotus_tools import UPDATE_MANDATE, INITIALIZE_MANDATE
from src.l1_lotus_tools import Tool

# ---------------------------------------------------------


class DefaultAgent(Agent):
    def __init__(self):
        super().__init__()
        self.setup_tools()

    # ---------------------------------------------------
    # Setup

    def setup_tools(self) -> None:
        all_tools = [RUN(), FILE_IO(), SEARCH(), UPDATE_MANDATE(), INITIALIZE_MANDATE()]

        self.tool_dict = {tool.name : tool for tool in all_tools}
        for tool in self.tool_dict.values():
            self.add_tool(tool)

            if tool.name == UPDATE_MANDATE.__name__:
                tool.disable()


    def add_tool(self, tool : Tool):
        tool.external_log = self.get_tool_logger(tool_name=tool.name)
        tool.acting_agent = self


    def get_tool_logger(self,tool_name: str):
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


class User(ConversationParticipant):
    def __init__(self):
        super(User, self).__init__(role=DialogueRole.user_role())


