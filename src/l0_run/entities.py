from src.l2_lotus_core import Agent, ConversationParticipant, DialogueRole
from src.l1_lotus_tools import RUN,READ,WRITE,SEARCH
from src.l1_lotus_tools import UPDATE_DIRECTIVE, INITIALIZE_DIRECTIVE

# ---------------------------------------------------------

class DefaultAgent(Agent):
    def __init__(self):
        super().__init__()
        self.setup_tools()

    # ---------------------------------------------------
    # Setup

    def setup_tools(self) -> None:
        file_io_tools = [READ(), WRITE()]
        run_tools = [RUN()]
        search_tools = [SEARCH()]
        directive_tools = [UPDATE_DIRECTIVE(self.directive), INITIALIZE_DIRECTIVE(self.directive)]

        self.tool_list = file_io_tools + run_tools + directive_tools + search_tools
        for tool in self.tool_list:
            tool.external_log = self.get_tool_logger(tool_name=tool.name)

        self._tool_docs = [tool.get_tool_json_doc() for tool in self.tool_list]


class User(ConversationParticipant):
    def __init__(self):
        super(User, self).__init__(role=DialogueRole.user())


