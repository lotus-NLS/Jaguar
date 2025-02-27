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
class Step:
    text_pipe : TextPipe
    generation_ctx: Context
    ckpt_label: str
    outputs : list[ToolOutput]
    is_final : bool = False

    def get_state(self, uuid : str, writing : Optional[str], is_final : bool = False) -> StepState:
        return StepState(generation_ctx=self.generation_ctx,
                         ckpt_label=self.ckpt_label,
                         session_uuid=uuid, writing=writing,
                         is_final=is_final)

    @classmethod
    def failed(cls, context : Context):
        return cls(text_pipe=TextPipe.failed(), generation_ctx=context, ckpt_label='failed', outputs=[])


@dataclass
class StepState(JsonDataclass):
    generation_ctx : Context
    writing : str
    ckpt_label : str
    session_uuid : str
    is_final : bool = False

    @classmethod
    def from_str(cls, json_str: str) -> StepState:
        return super().from_str(json_str=json_str)


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
            if text == self.stop_token:
                pipeLogger.debug(f'\nReceived stop token from text queue')
                break
            if not text:
                continue
            yield text

    @classmethod
    def failed(cls, msg: Optional[str] = None) -> TextPipe:
        pipeline: TextPipe = TextPipe()
        conditional_msg = f':{msg}'
        pipeline.put(f'Pipeline failed{conditional_msg}')
        pipeline.stop()
        return pipeline



@dataclass
class Report(JsonDataclass):
    summary : str
    is_successful : bool
    session_uuid : str
