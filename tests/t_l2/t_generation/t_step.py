import threading
import time

from engine.l2_models import State
from engine.l2_models.generation.step import TextPipe, Step
from engine.l2_models.language import Context
from holytools.devtools import Unittest

# ------------------------------------------------

class TestTextPipe(Unittest):
    def setUp(self):
        self.text_pipe : TextPipe = TextPipe()

    def test_get_text_stream(self):
        phrase = f'This is a test'
        words = phrase.split()
        for w in words:
            self.text_pipe.put(w)
        self.text_pipe.stop()

        text_stream = self.text_pipe.get_text_stream()
        for j, w in enumerate(text_stream):
            self.assertTrue(w == words[j])

    def test_thread_safe_stop(self):
        def stop_pipe():
            time.sleep(0.1)
            self.text_pipe.stop()

        threading.Thread(target=stop_pipe).start()

        for w in self.text_pipe.get_text_stream():
            stop_token = w
            self.assertTrue(stop_token == TextPipe.stop_token)


class TestStep(Unittest):
    def setUp(self):
        self.tp = TextPipe()
        context = Context.get_example_context()
        ckpt_label = f'Checkpoint'
        self.step = Step(text_pipe=self.tp, gen_ctx=context, ckpt_label=ckpt_label, outputs=[])

    def test_roundtrip(self):
        state = self.step.get_state(uuid='uuid4')
        s = state.to_str()
        restored_state = State.from_str(s)

        self.assertSame(state.__dict__, restored_state.__dict__)


if __name__ == "__main__":
    TestTextPipe.execute_all()
    TestStep.execute_all()