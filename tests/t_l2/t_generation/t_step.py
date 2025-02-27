import threading
import time

from engine.l2_models.generation.step import TextPipe
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
    pass



if __name__ == "__main__":
    TestTextPipe.execute_all()