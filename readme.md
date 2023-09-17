# Nucifera
<p align="center">
  <img src="documentation/logo.jpg" alt="Logo" width="200">
  <br>
  <em>Nelumbo Nucifera</em>
</p>

## Overview
Nucifera aims to enable LLMs to do highly independent and autonomous software development.
The first development objective of pyWrite is to provide the LLM with the necessary tools to
perform software development, like reading or writing files or running code and reading the outputs.

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
