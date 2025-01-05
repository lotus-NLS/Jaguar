from __future__ import annotations

from typing import Optional
from queue import Queue, Empty
from typing import Iterator
from holytools.logging import LoggerFactory


pipeLogger = LoggerFactory.get_logger(name=__name__)

# ----------------------------------------------


class TextPipe(Queue):
    stop_token = '⊥'

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
                pipeLogger.warning(f'Text queue timed out after {timeout}s')
                break
            except Exception as e:
                pipeLogger.error(f'Error in getting text from queue: {e}')
                break
            if text == self.stop_token:
                pipeLogger.debug(f'\nReceived stop token from text queue')
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



