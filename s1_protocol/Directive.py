from AgendaEntry import Objective,Task


class Directive:
    def __init__(self,task, objective):
        self.current_task : Task = task
        self.current_objective : Objective = objective
