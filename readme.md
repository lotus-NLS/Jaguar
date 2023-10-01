# Roseus
<p align="center">
  <img src="documentation/logo.jpg" alt="Logo" width="200">
  <br>
  <em>Nelumbo Nucifera</em>
</p>

## Overview
Roseus aims to provide a natural language interface to your software and to formal computer languages through the usage of LLMs. \
Its aim is to write software modules by specification and integrate them with existing software, provide intuitive explanations and add comments
for existing software, rewrite local source files and enable usage of auxiliary 
tools like the Terminal on Windows or Linux, git, AutoDevOps or Docker through natrual language
specifications.

In particular, agents in the Roseus framework can make use of the following tools:

-> READ: Read text files on the computer \
-> WRITE: Write out text files locally \
-> RUN: Execute python or Terminal code \
-> BROWSE: Search for information on the web in text form 


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

If the program is run for the first time you will be prompted for your OpenAI API key. After entering the key it will be
saved in a config file in the home directory in plain text form. In subsequent runs the API key will be read from that location.

## Usage

Navigate to src/l0_run and run the following command:
```
python3 run_handler.py
```

For further information simply ask the agent: "Who are you and what you can do?"


## Links

[Project management page](https://furtive-point-c71.notion.site/GPT-pyWrite-Lotus-7a44993ddb1b42edbba4d6275d7c9628?pvs=4): \
On this page you can view current objectives, tasks and notes relevant to development

[Code Rulebook](documentation/code_rulebook.md): \
All contributed code must adhere to the code rulebook
