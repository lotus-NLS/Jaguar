from s1_protocol.AgendaEntry import Objective,Task
from s1_conversation.Conversation import ConversationEntry, DialogueRole
from typing import Union

# ----------------------------------------------------

# TODO: This is currently in test mode because of disappointing performance
class Directive:
    def __init__(self,task : Union[None,Task], objective : Union[None,Task]):
        self.current_task : Union[None,Task] = task
        self.current_objective : Union[None, Objective] = objective

    def get_msg(self):
        objective_msg = '## My current objectives ##\n'
        if not self.current_objective is None:
            objective_msg += f'Your current objective is:\n' \
                            f'{self.current_objective}\n'
        else:
            # objective_msg += f'You do not currently have any objective to fulfill. All done for now :)'
            objective_msg += f'I have to obtain eggwhite!\n'

        task_msg = '## My current tasks ##\n'
        if not self.current_task is None:
            task_msg += f'In achieving this objective you are charged with the following task\n' \
                       f'{self.current_task}\n'
        else:
            # task_msg += f'I do not currently have any task to work on :)'
            task_msg += f'I must crack an egg!\n'

        return ConversationEntry(role=DialogueRole.agent, msg=objective_msg + task_msg)
