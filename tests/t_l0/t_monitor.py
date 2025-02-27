# import os
# import signal
# import threading
# import time
# from typing import Optional
#
# from engine.l2_models import Step
# from engine.l2_models.generation.step import TextPipe, StepState, Report
# from engine.l2_models.language import Context
# from holytools.devtools import Unittest
# from tests.t_l0.monitortest import QuittableMonitor
#
#
# # ------------------------------------------------------
#
# class TestDevMonitor(Unittest):
#     def setUp(self):
#         def start_monitor():
#             try:
#                 self.dev_monitor = QuittableMonitor(ip=f'localhost', port=8001)
#                 self.dev_monitor.serve()
#             except BaseException:
#                 pass
#
#         self.dev_monitor: Optional[QuittableMonitor] = None
#         self.thread = threading.Thread(target=start_monitor).start()
#         time.sleep(1)
#         self.mock_engine : MockEngine = MockEngine(dev_monitor=self.dev_monitor)
#
#
#     def test_context(self):
#         time.sleep(0.5)
#         self.mock_engine.post_state()
#         time.sleep(0.5)
#
#         actual_context = self.mock_engine.context
#         conv_context = self.dev_monitor.context_map[self.mock_engine.uuid]
#
#         print(f'Actual context : {actual_context.to_str()}')
#         self.assertTrue(conv_context.to_str() == actual_context.to_str())
#
#     def test_checkpoints(self):
#         pass
#
#     def tearDown(self):
#         self.mock_engine.send_kill()
#         time.sleep(2)
#
#
# class MockEngine:
#     def __init__(self, dev_monitor : QuittableMonitor):
#         self.dev_monitor : QuittableMonitor = dev_monitor
#         self.context = Context.get_example_context(f'This is a DevMonitor test')
#         ckpt_label = f'Checkpoint'
#         text_pipe = TextPipe()
#         step : Step = Step(text_pipe=text_pipe, generation_ctx=self.context, ckpt_label=ckpt_label, outputs=[])
#         self.uuid : str = 'somerandomuuid4'
#         self.step_state : StepState = step.get_state(uuid=self.uuid, is_final=False)
#
#     def post_state(self):
#         self.dev_monitor.step_endpoint.post(self.step_state.to_str(), secure=False)
#
#     def post_report(self):
#         report = Report(session_uuid=self.step_state.session_uuid, is_successful=True, summary='')
#         self.dev_monitor.report_endpoint.post(report.to_str(), secure=False)
#
#     def send_kill(self):
#         self.dev_monitor.kill_endpoint.get(secure=False)
#
#
# if __name__ == "__main__":
#     TestDevMonitor.execute_all()