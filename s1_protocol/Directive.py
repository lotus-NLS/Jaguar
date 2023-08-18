from AgendaEntry import Objective,Task
from s1_conversation.Conversation import Conversation_Entry
from s1_conversation.Roles import Dialogue_Roles


class Directive:
    def __init__(self,task, objective):
        self.current_task : Task = task
        self.current_objective : Objective = objective

    def get_system_message(self):
        objective_msg = f'Your current objective is:\n' \
                        f'{self.current_objective}\n'
        task_msg = f'In achieving this objective you are charged with the following task\n' \
                   f'{self.current_task}\n'

        return Conversation_Entry(role=Dialogue_Roles.system,msg=objective_msg+task_msg)


