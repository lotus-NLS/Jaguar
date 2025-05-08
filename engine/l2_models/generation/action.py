from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from queue import Queue, Empty
from typing import Iterator

from engine.l2_models.language import Context
from engine.l3_aos.tools import ToolOutput
from holytools.abstract import JsonDataclass
from holytools.logging import LoggerFactory


pipeLogger = LoggerFactory.get_logger(name=__name__)

# ----------------------------------------------

@dataclass
class Action:
    text_pipe : TextPipe
    tool_outputs : list[ToolOutput]
    pre_ctx : Context
    post_ctx: Context
    ckpt_label: Optional[str] = None
    err_msg : Optional[str] = None

    def is_failed(self) -> bool:
        return self.ckpt_label == 'failed'

    def get_state(self, uuid : str) -> State:
        return State(post_context=self.post_ctx, ckpt_label=self.ckpt_label, sess_uuid=uuid)

    @classmethod
    def failed(cls, context : Context, err_msg : str):
        return cls(text_pipe=TextPipe.failed(), post_ctx=context, ckpt_label='failed', tool_outputs=[], pre_ctx=context, err_msg=err_msg)

    def get_writing(self) -> str:
        text_stream = self.text_pipe.get_text_stream()
        content = ''
        for w in text_stream:
            content += w
        return content

@dataclass
class State(JsonDataclass):
    post_context : Context
    ckpt_label : Optional[str]
    sess_uuid : str
    msg: str = ''

    @classmethod
    def from_str(cls, json_str: str) -> State:
        return super().from_str(json_str=json_str)


class TextPipe(Queue):
    stop_token = '⊥'

    def __init__(self):
        super().__init__()
        self.content : str = ''

    @classmethod
    def failed(cls, msg: Optional[str] = None) -> TextPipe:
        pipeline: TextPipe = TextPipe()
        conditional_msg = f':{msg}'
        pipeline.put(f'Pipeline failed{conditional_msg}')
        pipeline.stop()
        return pipeline

    # ------------------------------------------------------

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

            if text == self.stop_token:
                pipeLogger.debug(f'\nReceived stop token from text queue')
                break
            if text:
                yield text


@dataclass
class Report(JsonDataclass):
    summary : str
    is_successful : bool
    sess_uuid : str
