# import time
# from tests.test_module import TestModule
# from engine.l2_agent.m0_language.conversation_participant import ConversationParticipant, DialogueRole, Channel
#
#
# class ConversationTestModule(TestModule):
#     class RowdyParticipant(ConversationParticipant):
#         def _reaction_protocol(self, dialogue_line: dict):
#             role = dialogue_line['role']
#             if role == DialogueRole.agent():
#                 self.speak('Actually, leave me alone! Let me talk to another user')
#
#
#     def __init__(self):
#         super().__init__()
#         self.basic_channel = Channel()
#
#         # Create participants and add them to the handler
#         self.agent_participant1 = ConversationParticipant(role=DialogueRole.agent())
#         self.agent_participant2 = ConversationParticipant(role=DialogueRole.agent())
#         self.agent_participant3 = ConversationParticipant(role=DialogueRole.agent())
#
#         self.rowdy_user_participant = ConversationTestModule.RowdyParticipant(role=DialogueRole.user())
#         self.agent_participant_list = [self.agent_participant1, self.agent_participant2, self.agent_participant3]
#
#         ConversationParticipant.enter_into_conversation(channel=self.basic_channel, participant_list=self.agent_participant_list)
#
#         self.all_participants = self.agent_participant_list + [self.rowdy_user_participant]
#
#     # assistant said: Hello from participant 1!
#     # assistant said: Hello from participant 2!
#     # assistant thought: I do not even want to say hello to that guy!
#     # Logs for Participant1:
#     # [...]
#
#     def clear_logs(self):
#         for participant in self.all_participants:
#             participant._personal_log = []
#
#     @TestModule.test
#     def test_speak_and_think(self):
#         self.agent_participant1.speak('Hello from participant 1!')
#         self.agent_participant2.speak('Hello from participant 2!')
#         self.agent_participant2.think('I do not even want to say hello to that guy!')
#
#         time.sleep(0.5)
#         print("Logs for Participant1:")
#         self.agent_participant1.get_memory()
#
#         print("Logs for Participant2:")
#         self.agent_participant2.get_memory()
#
#         print("Logs for Participant3:")
#         self.agent_participant3.get_memory()
#
#     @TestModule.test
#     def test_reaction(self):
#         self.rowdy_user_participant.join_channel(self.basic_channel)
#         self.agent_participant1.speak('How are you :)')
#
#         time.sleep(1)
#         # Participants print their logs
#         print("Logs for Participant1:")
#         self.agent_participant2.get_memory()
#
#         print("Logs for Participant2:")
#         self.agent_participant3.get_memory()
#
#
# if __name__ == "__main__":
#     test = ConversationTestModule()
#     test.test_speak_and_think()
#     test.clear_logs()
#     test.test_reaction()
#     test.basic_channel.stop_after_next_timeout()
