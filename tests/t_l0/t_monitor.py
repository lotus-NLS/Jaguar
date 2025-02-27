import threading
from typing import Optional

from engine.l2_models import Step
from engine.l2_models.generation.step import TextPipe, StepState, Report
from engine.l2_models.language import Context
from holytools.devtools import Unittest
from tests.t_l0.monitortest import QuittableMonitor


# ------------------------------------------------------

class TestDevMonitor(Unittest):
    def setUp(self):
        def start_monitor():
            try:
                self.dev_monitor = QuittableMonitor.localhost()
            except RuntimeError as e:
                print(e.__repr__())

        self.dev_monitor: Optional[QuittableMonitor] = None
        self.thread = threading.Thread(target=start_monitor).start()
        self.mock_engine = MockEngine(dev_monitor=self.dev_monitor)


    def test_context(self):
       pass

    def test_checkpoints(self):
        pass

    def tearDown(self):
        self.mock_engine.send_kill()


class MockEngine:
    def __init__(self, dev_monitor : QuittableMonitor):
        self.dev_monitor : QuittableMonitor = dev_monitor
        context = Context.get_example_context()
        ckpt_label = f'Checkpoint'
        text_pipe = TextPipe()
        step : Step = Step(text_pipe=text_pipe, generation_ctx=context, ckpt_label=ckpt_label, outputs=[])
        self.step_state : StepState = step.get_state(uuid=f'uuid4', is_final=False)

    def post_state(self):
        self.dev_monitor.step_endpoint.post(self.step_state.to_str(), secure=False)

    def post_report(self):
        report = Report(session_uuid=self.step_state.session_uuid, is_successful=True, summary='')
        self.dev_monitor.report_endpoint.post(report.to_str(), secure=False)

    def send_kill(self):
        self.dev_monitor.kill_endpoint.get(secure=False)


if __name__ == "__main__":
    TestDevMonitor.execute_all()