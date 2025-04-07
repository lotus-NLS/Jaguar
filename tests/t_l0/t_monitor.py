import uuid

from engine.l0_main.dev_monitor import DevMonitor
from engine.l2_models import Step
from engine.l2_models.generation.step import TextPipe, State, Report
from engine.l2_models.language import Context
from holytools.devtools import Unittest
from holytools.devtools.testing.runner import BlockedTester


# ------------------------------------------------------

class TestDevMonitor(Unittest):
    def setUp(self):
        self.server_tester : ServerTester = ServerTester()

    def test_context(self):
        context_ok = self.server_tester.check_ok(case='context', delay=0.5)
        print(context_ok)
        self.assertTrue(context_ok)

    def test_checkpoints(self):
        ckpts_ok = self.server_tester.check_ok(case='checkpoints', delay=0.5)
        print(ckpts_ok)
        self.assertTrue(ckpts_ok)

    def test_report(self):
        report_ok = self.server_tester.check_ok(case='report', delay=0.5)
        print(report_ok)
        self.assertTrue(report_ok)

class ServerTester(BlockedTester):
    def __init__(self):
        super().__init__()
        self.port : int = 5006
        self.dev_monitor : DevMonitor = DevMonitor.localhost(port=self.port)
        self.mock_engine : MockEngine = MockEngine(self.dev_monitor)

    def blocked(self):
        self.dev_monitor.serve()

    def perform_check(self, case : str) -> bool:
        sess_uuid = self.mock_engine.uuid

        if case == 'context':
            self.mock_engine.post_state()
            actual_context = self.mock_engine.context
            conv_context = self.dev_monitor.context_map[self.mock_engine.uuid]
            print(f'Conversation context = {conv_context.get_view()}')
            return conv_context.to_str() == actual_context.to_str()

        elif case == 'checkpoints':
            self.mock_engine.post_state()
            ckpts = self.dev_monitor.ckpt_map[sess_uuid]

            print(f'Checkpoints = {ckpts}')
            ckpt_len_ok = len(ckpts) == 1
            ckpt_content_ok = ckpts[0] == self.mock_engine.ckpt_label
            return ckpt_len_ok and ckpt_content_ok

        elif case == 'report':
            self.mock_engine.post_report()
            ckpts = self.dev_monitor.ckpt_map[sess_uuid]
            return ckpts[-1] == '✓'

        else:
            raise ValueError(f'Unknown case: {case}')

class MockEngine:
    def __init__(self, dev_monitor : DevMonitor):
        self.dev_monitor : DevMonitor = dev_monitor
        self.context = Context.get_example_context(f'This is a DevMonitor test')
        self.ckpt_label = f'Checkpoint'

        text_pipe = TextPipe()
        step : Step = Step(text_pipe=text_pipe, post_ctx=self.context, ckpt_label=self.ckpt_label, tool_outputs=[])
        self.uuid : str = str(uuid.uuid4())
        self.step_state : State = step.get_state(uuid=self.uuid)
        self.report : Report = Report(sess_uuid=self.uuid, is_successful=True, summary='')

    def post_state(self):
        self.dev_monitor.step_endpoint.post(self.step_state.to_str(), secure=False)

    def post_report(self):
        self.dev_monitor.report_endpoint.post(self.report.to_str(), secure=False)


if __name__ == "__main__":
    TestDevMonitor.execute_all()
