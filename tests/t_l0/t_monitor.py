from engine.l0_main.dev_monitor import DevMonitor
from engine.l2_models import Step
from engine.l2_models.generation.step import TextPipe, StepState, Report
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
        pass

class ServerTester(BlockedTester):
    def __init__(self):
        super().__init__()
        self.port : int = 5006
        self.dev_monitor : DevMonitor = DevMonitor.localhost(port=self.port)
        self.mock_engine : MockEngine = MockEngine(self.dev_monitor)

    def blocked(self):
        self.dev_monitor.serve()

    def perform_check(self, case : str) -> bool:
        if case == 'context':
            self.mock_engine.post_state()
            actual_context = self.mock_engine.context
            conv_context = self.dev_monitor.context_map[self.mock_engine.uuid]
            return conv_context.to_str() == actual_context.to_str()
        if case == 'checkpoints':
            raise NotImplementedError()
        else:
            raise ValueError(f'Unknown case: {case}')


class MockEngine:
    def __init__(self, dev_monitor : DevMonitor):
        self.dev_monitor : DevMonitor = dev_monitor
        self.context = Context.get_example_context(f'This is a DevMonitor test')
        ckpt_label = f'Checkpoint'
        text_pipe = TextPipe()
        step : Step = Step(text_pipe=text_pipe, generation_ctx=self.context, ckpt_label=ckpt_label, outputs=[])
        self.uuid : str = 'somerandomuuid4'
        self.step_state : StepState = step.get_state(uuid=self.uuid, is_final=False)

    def post_state(self):
        self.dev_monitor.step_endpoint.post(self.step_state.to_str(), secure=False)

    def post_report(self):
        report = Report(session_uuid=self.step_state.session_uuid, is_successful=True, summary='')
        self.dev_monitor.report_endpoint.post(report.to_str(), secure=False)


if __name__ == "__main__":
    TestDevMonitor.execute_all()