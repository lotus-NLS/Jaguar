from __future__ import annotations

import time
import traceback
from typing import Iterator, Optional

from openai import APITimeoutError, APIError

from engine.l1_agents.guidance import Core
from engine.l1_agents.guidance.tasktracker import TaskTracker, Task
from engine.l2_models import Generation, InfConfig
from engine.l2_models.generation.step import TextPipe, Step
from engine.l2_models.language import Message, Context
from engine.l2_models.language.message import Role
from engine.l2_models.llm import LLM
from engine.l3_aos import AOS
from engine.l3_aos.tools import ToolOutput, ToolCall, Tool
from engine.l3_aos.workspaces import Workspace
from holytools.logging import Timber


# ---------------------------------------------------------

class Agent(Timber):
    def __init__(self, model : LLM, aos : AOS, core : Core = Core.GOTO()):
        super().__init__()
        self.model: LLM = model
        self.task_tracker : TaskTracker = TaskTracker()
        self.aos : AOS = aos
        self.identity : Core = core
        self.memory: list[Message] = []

        self.aos.add_workspace(ws=self.task_tracker)
        for ws in self.aos.get_workspaces(active_only=False):
            hook = self.get_freeze_hook(ws=ws)
            ws.close_action.add_prehook(hook)

    def talk(self, msg : str) -> Step:
        self.memory.append(Message.user(msg=msg))
        return self.handle()

    def work(self, task : Task, max_steps : int) -> Iterator[Step]:
        self.info(f'- {Agent.__name__}.{Agent.work.__name__}: Starting work on task {task.name}')
        self.act(tool_calls=[ToolCall.empty()], temp_tool=self.task_tracker.open_action)
        self.task_tracker.root = task
        require_update = InfConfig(required_tool=self.task_tracker.update_tool)
        report_frequency = 5
        time.sleep(0.1)
        print()

        self.update_memory(entry=Message.system(msg=f'Now entering work mode. Complete the outlined tasks'))
        for j in range(max_steps):
            inf_options = require_update if (j+1) % report_frequency == 0 else InfConfig()
            step = self.handle(inf_config=inf_options)
            yield step
            if not self.is_working():
                break
            print()

        if self.task_tracker.is_active:
            self.task_tracker.close_action.execute({})

    # ---------------------------------------------------
    # Main routine

    def handle(self, inf_config : InfConfig = InfConfig()) -> Step:
        context = self.get_context(inf_config=inf_config)

        try:
            generation = self.model.get_generation(context=context, config=inf_config)
            pipe = self.write(generation=generation)
            outputs = self.act(tool_calls=generation.get_tool_calls(), temp_tool=inf_config.required_tool)
        except APITimeoutError:
            error_msg = f'OpenAI API request timed out after {inf_config.timeout} seconds'
            self.error(f'{Agent.__name__}.{Agent.handle.__name__}: {error_msg}')
            return Step.failed(context=context)
        except APIError:
            error_msg = f'OpenAI API request failed'
            self.error(f'{Agent.__name__}.{Agent.handle.__name__}: {error_msg}')
            return Step.failed(context=context)

        headline = self.task_tracker.headline
        self.task_tracker.headline = None
        post_context = self.get_context(inf_config=inf_config)
        return Step(text_pipe=pipe, ckpt_label=headline, pre_ctx=context, post_ctx=post_context, tool_outputs=outputs)

    def write(self, generation : Generation):
        pipe = TextPipe()
        for chunk in generation:
            pipe.put(chunk.get_text())
        pipe.stop()

        text = generation.get_text()
        if text:
            self.update_memory(entry=Message.agent(msg=text))

        return pipe

    def act(self, tool_calls : list[ToolCall], temp_tool : Optional[Tool] = None) -> list[ToolOutput]:
        if not temp_tool:
            outputs = self.aos.process(tool_calls=tool_calls)
        elif temp_tool and len(tool_calls) > 1:
            raise ValueError('Temporary tool can only be used with a single tool call')
        else:
            outputs = [temp_tool.execute(tool_calls[0].get_args_dict())]

        for out in outputs:
            output_entry = Message.from_tool_output(out)
            self.update_memory(output_entry)
        return outputs

    # ---------------------------------------------------
    # language

    def get_freeze_hook(self, ws : Workspace):
        def freeze_ws(frozen_ws: Workspace = ws):
            entry = Message.from_workspace(ws=frozen_ws, active=False)
            entry.add(msg=f'## [Closed workspace] ## {frozen_ws.get_name()} with following final state:', at_start=True)
            self.update_memory(entry=entry)
        return freeze_ws

    def update_memory(self, entry : Message):
        self.memory.append(entry)

    def get_context(self, inf_config : InfConfig) -> Context:
        context = Context(messages=[self.identity.as_system_entry()])
        context += Context(docs=self.aos.get_docs(required_tool=inf_config.required_tool))
        context += Context(messages=self.memory)

        msg_map = self.get_entry_map(aos=self.aos)
        for j, m in enumerate(reversed(context.messages)):
            matching_ws_name = self.get_matching_ws_name(ws_names=list(msg_map.keys()), tool_name=m.text)
            if m.role == Role.TOOL and not matching_ws_name is None:
                index, msg = len(context.messages)-j, msg_map[matching_ws_name]
                context.messages.insert(index, msg)
                del msg_map[matching_ws_name]

        if self.is_working():
            work_entry = Message.system(msg=self.task_tracker.work_notice)
            context += Context.singleton(entry=work_entry)

        return context

    @staticmethod
    def get_matching_ws_name(ws_names: list[str], tool_name: str):
        for n in ws_names:
            if n in tool_name:
                return n

    def get_entry_map(self, aos : AOS) -> dict[str, Message]:
        msg_map: dict[str, Message] = {}
        for ws in [workspace for workspace in aos.workspaces if workspace.is_active]:
            try:
                msg_map[ws.get_name()] = Message.from_workspace(ws=ws)
            except BaseException as e:
                tb = traceback.format_exc()
                self.error(f'Error in getting entry for app "{ws.get_name()}": {e}\nTraceback: {tb}')
        return msg_map

    def is_working(self) -> bool:
        is_active = self.task_tracker.is_active
        if is_active:
            is_working = not self.task_tracker.root.recursively_complete()
        else:
            is_working = False

        return is_working