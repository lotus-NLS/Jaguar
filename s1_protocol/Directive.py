from s1_protocol.AgendaEntry import Objective,Task
from s1_conversation.Conversation import Conversation_Entry, Dialogue_Roles
from typing import Union

# ----------------------------------------------------


class Directive:
    def __init__(self,task : Union[None,Task], objective : Union[None,Task]):
        self.current_task : Union[None,Task] = task
        self.current_objective : Union[None, Objective] = objective

    def get_system_message(self):
        if not self.current_task is None:
            task_msg = f'In achieving this objective you are charged with the following task\n' \
                       f'{self.current_task}\n'
        else:
            task_msg = f'You do not currently have any task to work on'

        if not self.current_objective is None:
            objective_msg = f'Your current objective is:\n' \
                            f'{self.current_objective}\n'
        else:
            objective_msg = f'You do not currently have any objective to fulfill. All done for now :)'

        return Conversation_Entry(role=Dialogue_Roles.system,msg=objective_msg+task_msg)


