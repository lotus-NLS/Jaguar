from __future__ import annotations

from typing import Iterator, Optional

from openai import APITimeoutError, APIError

from engine.l1_agents.guidance import Core
from engine.l1_agents.guidance.tasktracker import TaskTracker, Task
from engine.l2_models import Generation, InfConfig
from engine.l2_models.generation.step import TextPipe, Step
from engine.l2_models.language import Message, Context
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

    def talk(self, msg : str) -> Step:
        self.memory.append(Message.user(msg=msg))
        return self.handle()

    def work(self, task : Task, max_steps : int) -> Iterator[Step]:
        self.info(f'- {Agent.__name__}.{Agent.work.__name__}: Starting work on task')

        self.task_tracker.root = task
        open_tool = self.task_tracker.open_action
        self.act(tool_calls=[open_tool.get_toolcall()], temp_tool=open_tool)

        require_update = InfConfig(required_tool=self.task_tracker.update_tool)
        report_frequency = 5

        self.update_memory(entry=Message.system(msg=f'Now entering work mode. Please complete the outlined tasks'))
        self.update_memory(entry=Message.system(msg=f'Start by exploring your options for how you can realize this task, then\n'
                                                    f'outline a plan of action\n'
                                                    f'This plan should include:\n'
                                                    f'  - Major steps: What are the major steps of your plan?\n'
                                                    f'  - Tools needed: What Tools are needed to realize this plan?\n'
                                                    f'  - Execution: How are you going to use these tools?'))
        yield self.handle(inf_config=InfConfig.text_only())
        for j in range(max_steps):
            inf_options = require_update if (j+1) % report_frequency == 0 else InfConfig()
            step = self.handle(inf_config=inf_options)
            print()

            yield step
            if not self.task_tracker.is_open:
                break

        if self.task_tracker.is_open:
            new_root = self.task_tracker.root.collect_retry()
            if new_root:
                self.update_memory(entry=Message.system(msg=f'Some tasks have been marked for a second go around'
                                                            f'Please start by reflecting on the issues with attempting this task'
                                                            f'and then explore alternative ways of accomplishing these tasks'))
                self.work(task=new_root, max_steps=max_steps)

        if self.task_tracker.is_open:
            self.act([self.task_tracker.close_action.get_toolcall()])

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
    # context

    def update_memory(self, entry : Message):
        self.memory.append(entry)

    def get_context(self, inf_config : InfConfig) -> Context:
        context = Context(messages=[self.identity.as_system_entry()])
        context += Context(docs=self.aos.get_docs(required_tool=inf_config.required_tool))
        context += Context(messages=self.memory)
        context.interweave_workspaces(aos=self.aos)

        if self.task_tracker.is_open:
            work_entry = Message.system(msg=self.task_tracker.work_notice)
            context += Context.singleton(entry=work_entry)

        return context
