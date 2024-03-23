import os.path
from engine.l1_agent import Agent, Task, Identity
from engine.l3_models import OpenAIModel
import uuid
from hollarek.devtools import Unittest


class TestAgentContext(Unittest):
    def setUp(self):
        self.agent = Agent(model=OpenAIModel.get_gpt4_turbo(), identity=Identity.GOTO())
        self.context = self.agent.get_active_context()


    def test_context_ok(self):
        entries = self.context.entries
        self.assertTrue(len(entries) > 0)
        self.assertTrue(len(self.context.docs) > 0)
        # print(f'Tools are {self.context.docs} and entries are {entries}')
        first_entry = entries[0]
        self.assertIsInstance(obj=first_entry.msg, cls=str)
        self.assertEqual(first_entry.msg, self.agent.identity.get_str())


    def test_identity_query(self):
        explain_identity_task = Task.make_default(msg=f'If your capabilities include helping with software development'
                                                f'and you can interact with/use the system you are deployed with simply'
                                                f'respond with "yes". The response needs to be exact for testing purposes')
        response = self.agent.handle(explain_identity_task)

        buffer = ''
        for text in response.get_text_stream():
            buffer += text
        self.assertIn('yes', buffer)


        explain_os = Task.make_default(msg=f'If you have access to an open/close tools that allow you to open/close applications'
                                           f'simply reply with "yes". The response needs to be exact for testing purposes')
        response = self.agent.handle(explain_os)
        buffer = ''
        for text in response.get_text_stream():
            buffer += text
        self.assertIn('yes', buffer)


class TestApplicationUsage(Unittest):
    def setUp(self):
        self.agent = Agent(model=OpenAIModel.get_gpt4_turbo(), identity=Identity.GOTO())
        self.context = self.agent.get_active_context()


    def test_text_application(self):
        fpath = f'/tmp/{uuid.uuid4()}'
        open_task = Task.make_default(msg=f'Please open the text editor tool in {fpath}')
        response = self.agent.handle(open_task)
        for text in response.get_text_stream():
            print(text, end='')

        write_task = Task.make_default(msg=f'Now please write anything at all in the text file')
        response = self.agent.handle(write_task)
        for text in response.get_text_stream():
            print(text, end='')
        self.assertTrue(os.path.isfile(fpath))
        open_apps = self.get_open_workspace()
        self.assertTrue(len(open_apps)==1)

        close_task = Task.make_default(msg=f'Now please close the text application again')
        response = self.agent.handle(close_task)
        for text in response.get_text_stream():
            print(text, end='')
        open_apps = self.get_open_workspace()
        self.assertTrue(len(open_apps)==0)


    def get_open_workspace(self):
        workspaces= self.agent.os.get_workspaces()
        return [workspace for workspace in workspaces if workspace.is_active]


if __name__ == '__main__':
    # TestAgentContext.execute_all()
    TestApplicationUsage.execute_all()
