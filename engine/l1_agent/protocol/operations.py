# import yaml
# from abc import abstractmethod
#
# from engine.l5_singletons import Query
#
# from .mandate import Mandate
#
# # ---------------------------------------------------------
#
#
# class MandateTool(Tool):
#     def __init__(self, mandate : Mandate):
#         super().__init__()
#         self.mandate : Mandate = mandate
#
#     @abstractmethod
#     def do(self):
#         pass
#
#     def get_mandate(self, uuid : str):
#
#         target = self.mandate.get(uuid=uuid)
#         if not target:
#             raise KeyError(f'No mandate with the given ID: {uuid}')
#
#
# class MandateUpdateTool(MandateTool):
#     def __init__(self, mandate: Mandate):
#         super().__init__(mandate=mandate)
#         self.uuid_arg: ToolArg = ToolArg(name='objective id')
#
#     @abstractmethod
#     def do(self):
#         pass
#
#
# class RequestMandate(MandateTool):
#     def __init__(self, mandate : Mandate, query : Query):
#         super().__init__(mandate=mandate)
#
#         self.query = query
#         self.desc = 'Submits a request to the user to sign off on a plan of action'
#         content_desc = ("""Specify your plan of action in a YAML format e.g. like this:
#                 Overall objective:
#                 - Sub objective 1
#                 - Sub objective 2
#                 - Sub objective 3:
#                   - Sub-sub objective 1
#                 - Sub objective 4
#                 - Sub objective 5:
#                   - Sub-sub objective 2""")
#         self.yaml : ToolArg =  ToolArg(name='objective_specifications', desc=content_desc)
#
#
#     def do(self):
#         request_msg = (f'Here is my plan of action for your request:'
#                        f'\n{self.yaml.val}\n'
#                        f'Do you approve? (y/n)')
#
#         if self.query.get_confirmation(msg=request_msg):
#             info_dict = yaml.safe_load(self.yaml.val)
#             self.mandate.a_update(info_dict=info_dict)
#         else:
#             raise PermissionError(f'User denied permission to approve suggested plan of action: {self.yaml.val}')
#
#
# class MarkObjectiveDone(MandateUpdateTool):
#     def __init__(self, mandate : Mandate):
#         super().__init__(mandate=mandate)
#         self.desc= 'Marks an objective as done'
#
#     def do(self):
#         target = self.get_mandate(uuid=self.uuid_arg.val)
#         target.a_complete()
#
#
# class DiscardObjective(MandateUpdateTool):
#     def __init__(self, mandate : Mandate):
#         super().__init__(mandate=mandate)
#         self.desc = 'Discard an objective'
#
#     def do(self):
#         target = self.get_mandate(uuid=self.uuid_arg.val)
#         target.a_discard(uuid=self.uuid_arg.val)
#
#
# class AddSubobjective(MandateUpdateTool):
#     def __init__(self, mandate : Mandate):
#         super().__init__(mandate=mandate)
#         self.desc = 'Add a subobjective to an existing objective'
#         self.desc_arg : ToolArg = ToolArg(name='desc',desc=f'Description of new subobjective')
#
#     def do(self):
#         target = self.get_mandate(uuid=self.uuid_arg.val)
#         target.a_add_subobjective(desc=self.desc_arg.val)
#
