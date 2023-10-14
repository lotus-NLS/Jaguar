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
tools like the Terminal on Windows or Linux, git, AutoDevOps or Docker through natrual language specifications.

## Setup for Ubuntu 22.04

Clone repo into the home directory:
```
git clone https://github.com/Somerandomguy10111/Roseus
```

Setup venv:
```
python3 -m venv venv
source venv/bin/activate
```

Install required packages:
```
pip install -r requirements.txt
```

If the program is run for the first time you will be prompted for your OpenAI API key and other credentials.
After entering the credentials they will be saved in a config file in the home directory as plain text. In subsequent runs the credentials will be read from that location.

## Usage

Navigate to the repo root
```
cd ~/Roseus
```

then run the following commands:
```
export PYTHONPATH=/"/home/[username]/Roseus:$PYTHONPATH/"
source venv/bin/activate
python3 /home/[username]/Roseus/src/l0_lotus_run/main.py
```

For further information simply ask the agent: "Who are you and what you can do?"


## Links

[Project management page](https://furtive-point-c71.notion.site/GPT-pyWrite-Lotus-7a44993ddb1b42edbba4d6275d7c9628?pvs=4): \
On this page you can view current objectives, tasks and notes relevant to development

[Code Rulebook](documentation/code_rulebook.md): \
All contributed code must adhere to the code rulebook
