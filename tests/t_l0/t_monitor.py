import uuid

from engine.l0_main.dev_monitor import DevMonitor
from engine.l2_models import Step
from engine.l2_models.generation.step import TextPipe, State, Report
from engine.l2_models.language import Context
from holytools.network import IpProvider
from holytools.devtools import Unittest
from holytools.devtools.testing.unit import BlockedTester


# ------------------------------------------------------

class TestDevMonitor(Unittest):
    def setUp(self):
        self.server_tester : ServerTester = ServerTester()

    def test_context(self):
        context_ok = self.server_tester.check_ok(check_func=self.server_tester.check_context, delay=0.5)
        print(context_ok)
        self.assertTrue(context_ok)

    def test_checkpoints(self):
        ckpts_ok = self.server_tester.check_ok(check_func=self.server_tester.check_endpoints, delay=0.5)
        print(ckpts_ok)
        self.assertTrue(ckpts_ok)

    def test_report(self):
        report_ok = self.server_tester.check_ok(check_func=self.server_tester.check_report, delay=0.5)
        print(report_ok)
        self.assertTrue(report_ok)

class ServerTester(BlockedTester):
    def __init__(self):
        super().__init__()
        self.dev_monitor : DevMonitor = DevMonitor.localhost(port=IpProvider.get_free_port())
        self.mock_engine : MockEngine = MockEngine(self.dev_monitor)
        self.sess_uuid : str = self.mock_engine.uuid

    def blocked(self):
        self.dev_monitor.serve()

    def check_context(self) -> bool:
        self.mock_engine.post_state()
        actual_context = self.mock_engine.context
        conv_context = self.dev_monitor.context_map[self.mock_engine.uuid]
        print(f'Conversation context = {conv_context.get_view()}')
        return conv_context.to_str() == actual_context.to_str()

    def check_endpoints(self) -> bool:
        self.mock_engine.post_state()
        ckpts = self.dev_monitor.ckpt_map[self.sess_uuid]

        print(f'Checkpoints = {ckpts}')
        ckpt_len_ok = len(ckpts) == 1
        ckpt_content_ok = ckpts[0] == self.mock_engine.ckpt_label
        return ckpt_len_ok and ckpt_content_ok

    def check_report(self) -> bool:
        self.mock_engine.post_report()
        ckpts = self.dev_monitor.ckpt_map[self.sess_uuid]
        return ckpts[-1] == '✓'


class MockEngine:
    def __init__(self, dev_monitor : DevMonitor):
        self.dev_monitor : DevMonitor = dev_monitor
        self.context = Context.get_example_context(f'This is a DevMonitor test')
        self.ckpt_label = f'Checkpoint'

        text_pipe = TextPipe()
        step : Step = Step(text_pipe=text_pipe, pre_ctx=self.context, post_ctx=self.context, ckpt_label=self.ckpt_label, tool_outputs=[])
        self.uuid : str = str(uuid.uuid4())
        self.step_state : State = step.get_state(uuid=self.uuid)
        self.report : Report = Report(sess_uuid=self.uuid, is_successful=True, summary='')

    def post_state(self):
        self.dev_monitor.step_endpoint.post(self.step_state.to_str(), secure=False)

    def post_report(self):
        self.dev_monitor.report_endpoint.post(self.report.to_str(), secure=False)


if __name__ == "__main__":
    TestDevMonitor.execute_all()
