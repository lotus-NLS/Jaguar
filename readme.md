# pyWriter : Current state


## Overview
pyWriter is a framework which aims to enable LLMs to do highly independent and autonomous software development.

## Setup 

Setup venv
```
python3 -m venv venv
source venv/bin/activate
```

Install required packages
```
pip install -r requirements.txt
```

## Usage

Run either on command line or as GUI:
```
python3 s4_UI/run_GUI.py
```
OR:
```
python3 s4_UI/run_command_line.py
```

Currently, the available tools are:
- READ: Read a local text file
- WRITE: Write out a local text file

Disclaimer: Since even state-of-the-art models are still prone to hallucinations it can also occur that the agent claim to have access to other tools.
As of the 19.08.23, these are the only tools implemented in the framework.

# Roadmap
## LLM as python devs: Hard limitations
Bare LLMs are very good at producing python code snippets. Yet they cannot act as autonomous python developers, as they face several limitations. LLMs cannot:
- Run code and view output including error messages 
- Use the command line to install packages, interact with VCS etc.
- Look up documentation online\
- Look up existing work online that can serve as a starting off point
- Read or write files

The first development objective of pyWriter is to remedy this by providing the LLM with the necessary tools to\
perform those actions, thereby enabling autonomous python software development.

## LLM as python devs: Soft limitations
However, LLMs also face "soft" limitations. These are things that they should be able to do in theory\
with a good enough model but state-of-the-art models nonethless struggle with. These include:\
- Planning out large scale objectives and keeping track of tasks over a large span of time\
- Producing consistent and throughly checked outputs\
- Taking into account and paying attention to information far back in the conversation history

These issues are likely related to the fact that current models are optimized for the chatbot use case\
of a ~30-minute conversation between the model and the user. In particular the limited context window\
of 4k to 32k tokens presents a huge barrier in making the model work on larger bodies of code. And even things which appear
within the context window are readily overlooked by the model.\
The second development objective of pyWriter is to also remedy these limitations 
by providing the models with the necessary guidance to ensure that the software development is carried out with a consistent and predictable protocol, to keep track of the current
tasks and objectives and to distribute responsibilites so that each python developer agent can do his work within a single-module context.\

## Beyond pyWriter
pyWriter itself is just the first step of development. Beyond pyWriter other features are planned:\
to make up for some more functionalities that human software developers offer:
- Other software development: pyWriter is developed and tested and developed only for python code. But in principle
- Visual runtime analysis: A lot of applications run with a GUI, crucially websites.
The model should review how its code plays out visually as well. There is a version of GPT-4 which can work with image input
which hasn't been released yet.\
there is no reason why the program could not also be applied to other kinds of software. 
- Audio interface : You should be able to enter commands via voice, ideally without even pressing enter 
- Persistent memory: In order to effectively work in multiple sessions, 
- Self acquiring skills : Humans often learn by performing a task with great care and attention for several times \
until it becomes an integrated action that they can perform without thinking. In the same way the agent could 
develop its own skill library and work on tasks on a higher level of abstraction. 
- Self acquire tools: You can only plan out so much in terms of tools. If the agent decides that its current tools
do not suffice to accomplish the task it could simply build the tool itself. 

## Links

[Project management page](https://furtive-point-c71.notion.site/GPT-pyWriter-Lotus-7a44993ddb1b42edbba4d6275d7c9628?pvs=4): \
On this page you can view current objectives, tasks and notes relevant to development

[Code Rulebook](_documentation/code_rulebook.md): \
All contributed code must adhere to the code rulebook
