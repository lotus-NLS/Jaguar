from src.l2_lotus_core.protocol.agenda_entry import Task,Objective



# Example usage:
root_task = Task.make_root("Complete project", "Finish the software project by end of month.")
root_task.add_subelement("Write code", "Implement the main features.")
root_task.add_subelement("Test", "Make sure there are no bugs.")
print(root_task)

root_objective = Objective.make_root("Increase user engagement", "Aim for 20% more daily active users.")
root_objective.add_subelement("Optimize UI", "Redesign the main landing page for better user experience.")
print(root_objective)
