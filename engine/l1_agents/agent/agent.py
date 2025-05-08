from __future__ import annotations

import threading
from typing import Iterator, Optional

from openai import APITimeoutError, APIError

from engine.l1_agents.agent.core import Core
from engine.l1_agents.tasks.task import Task
from engine.l1_agents.tasks.tasktracker import TaskTracker
from engine.l2_models import Generation, InfConfig
from engine.l2_models.generation.step import TextPipe, Step
from engine.l2_models.language import Message, Context
from engine.l2_models.llm import LLM
from engine.l3_aos import AOS
from engine.l3_aos.tools import ToolOutput, ToolCall, Tool
from engine.l3_aos.workspaces import Workspace

# ---------------------------------------------------------

class Agent:
    def __init__(self, model : LLM, aos : AOS, core : Core = Core.GOTO()):
        super().__init__()
        self.model: LLM = model
        self.task_tracker : TaskTracker = TaskTracker()
        self.aos : AOS = aos
        self.identity : Core = core
        self.memory: list[Message] = []

        def get_freeze_hook(ws : Workspace):
            def freeze_ws(frozen_ws: Workspace = ws):
                entry = Message.from_workspace(ws=frozen_ws, active=False)
                entry.add(msg=f'## [Closed workspace] ## {frozen_ws.get_name()} with following final state:', at_start=True)
                self.update_memory(entry=entry)
            return freeze_ws

        self.aos.add_workspace(ws=self.task_tracker)
        for w in self.aos.get_workspaces(include_system_opened=True):
            hook = get_freeze_hook(ws=w)
            w.close_action.add_prehook(hook)

    @classmethod
    def project(cls, project_dirpath : str, project_desc : str, model : LLM, aos : AOS, core : Core = Core.GOTO()):
        core.identity += (f'You are currently working on the project located at {project_dirpath}.'
                          f'Here is a description of this project: {project_desc}')
        agent = cls(model=model, aos=aos, core=core)
        agent.aos.ide.open_action.execute(args_dict={'project_dirpath' : project_dirpath})
        agent.aos.ide.prevent_close = True

    def talk(self, msg : str) -> Iterator[Step]:
        self.memory.append(Message.user(msg=msg))
        for action in self.handle():
            yield action

    def work(self, task : Task, max_turns : int) -> Iterator[Step]:
        self.task_tracker.root = task
        open_tool = self.task_tracker.open_action
        self.act(tool_calls=[open_tool.get_toolcall()], temp_tool=open_tool)

        self.update_memory(entry=Message.system(msg=f'Now entering work mode. Please complete the outlined tasks'))
        self.update_memory(entry=Message.system(msg=f'Start by exploring your options for how you can realize this task, then outline a plan of action. This plan of action should include: \n'
                                                    f'- Major steps: What are the major steps of your plan?\n'
                                                    f'  - Tools needed: What Workspaces are needed to realize this step?\n'
                                                    f'  - Execution: How are you going to use these tools to realize this step?'))
        yield self.handle(inf_config=InfConfig.text_only()).__next__()

        require_update = InfConfig(required_tool=self.task_tracker.update_tool)
        for work_step in range(max_turns - 1):
            inf_options = require_update if (work_step+2) % self.get_report_frequency() == 0 else InfConfig()
            for action in self.handle(inf_config=inf_options):
                yield action

            if not self.task_tracker.is_open:
                break

        if self.task_tracker.is_open:
            new_root = self.task_tracker.root.collect_retry()
            if new_root:
                self.update_memory(entry=Message.system(msg=f'Some tasks have been marked for a second go around'
                                                            f'Please start by reflecting on the issues with attempting this task'
                                                            f'and then explore alternative ways of accomplishing these tasks'))
                self.work(task=new_root, max_turns=max_turns)

        if self.task_tracker.is_open:
            self.act([self.task_tracker.close_action.get_toolcall()])

    # ---------------------------------------------------
    # Main routine

    def handle(self, inf_config : InfConfig = InfConfig()) -> Iterator[Step]:
        context = self.get_context(inf_config=inf_config)

        def make_action(pipe : Optional[TextPipe], tool_outputs : list[ToolOutput]):
            headline = self.task_tracker.headline
            self.task_tracker.headline = None
            post_context = self.get_context(inf_config=inf_config)
            return Step(text_pipe=pipe, tool_outputs=tool_outputs, ckpt_label=headline, pre_ctx=context, post_ctx=post_context)

        try:
            generation = self.model.get_generation(context=context, config=inf_config)
            the_pipe = TextPipe()
            thread = threading.Thread(target=self.process, args=(generation, the_pipe))
            thread.start()

            yield make_action(pipe=the_pipe, tool_outputs=[])
            thread.join()
            yield make_action(pipe=None, tool_outputs=self.act(tool_calls=generation.get_tool_calls(), temp_tool=inf_config.required_tool))
        except APITimeoutError:
            yield Step.failed(context=context, err_msg=f'OpenAI API request timed out after {inf_config.timeout} seconds')
        except APIError:
            yield Step.failed(context=context, err_msg=f'OpenAI API request failed')

    def process(self, generation : Generation, pipe : TextPipe) -> TextPipe:
        for chunk in generation:
            pipe.put(chunk.get_text())

        text = generation.get_text()
        if text:
            self.update_memory(entry=Message.agent(msg=text))
            pipe.put('\n')

        pipe.stop()
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
    # context

    @classmethod
    def get_report_frequency(cls) -> int:
        return 5

    def update_memory(self, entry : Message):
        self.memory.append(entry)

    def get_context(self, inf_config : InfConfig) -> Context:
        ws_names = [ws.get_name() for ws in self.aos.get_workspaces()]
        context = Context(messages=[self.identity.as_system_entry(ws_names=ws_names)])
        context += Context(docs=self.aos.get_docs(required_tool=inf_config.required_tool))
        context += Context(messages=self.memory)

        msg_map = Context.get_entry_map(aos=self.aos)
        tokenizer = self.model.tokenizer
        WS_TOKEN_LIMIT = inf_config.input_tokens_max//4
        for v in msg_map.values():
            if tokenizer.count_string_tokens(v.text) > WS_TOKEN_LIMIT:
                limited_str = tokenizer.get_limited_string(v.text, max_tokens=inf_config.input_tokens_max//4)
                v.text = f'{limited_str}. View is limited, workspace context too large to display!'
        context.interweave_workspaces(ws_msg_map=msg_map)

        if self.task_tracker.is_open:
            work_entry = Message.system(msg=self.task_tracker.work_notice)
            context += Context.singleton(entry=work_entry)

        return context
