from __future__ import annotations

from typing import Optional
from queue import Queue, Empty
from typing import Iterator
from hollarek.logging import LogLevel, get_logger, Logger

# ----------------------------------------------


class TextPipe(Queue):
    stop_token = '⊥'
    logger : Optional[Logger] = None

    def put(self, msg : Optional[str], *args, **kwargs):
        if msg is None:
            return
        if not isinstance(msg, str):
            raise TypeError("Can only put strings inTextQueue.")
        super().put(msg, *args, **kwargs)

    def get(self, *args, **kwargs) -> str:
        item = super().get(*args, **kwargs)
        return item

    def stop(self):
        self.put(self.stop_token)

    def get_text_stream(self) -> Iterator[str]:
        timeout = 10
        while True:
            try:
                text = self.get(timeout=timeout)
            except Empty:
                self.log(f'Text queue timed out after {timeout}s', level=LogLevel.WARNING)
                break
            except Exception as e:
                self.log(f'Error in getting text from queue: {e}', level=LogLevel.ERROR)
                break
            if text == self.stop_token:
                self.log(f'\nReceived stop token from text queue', level=LogLevel.DEBUG)
                break
            if not text:
                continue
            yield text

    @classmethod
    def failed(cls, msg: Optional[str] = None):
        pipeline: TextPipe = TextPipe()
        conditional_msg = f':{msg}'
        pipeline.put(f'Pipeline failed{conditional_msg}')
        pipeline.stop()
        return pipeline


    @classmethod
    def log(cls, msg : str, level : LogLevel):
        if not cls.logger:
            cls.logger = get_logger()
        cls.logger.log(msg=msg, level=level)


class BytePipe(Queue):
    def get(self, block = True, timeout = None) -> bytes:
        return super().get(block, timeout)

    def put(self, item : bytes, block = True, timeout = None):
        super().put(item, block, timeout)
