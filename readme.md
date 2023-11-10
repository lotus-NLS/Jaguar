## Overview
The Lotus framework facilitates interaction with the computer and the internet through natural language.
For more information see the "Wiki" section on the [Project management page](https://furtive-point-c71.notion.site/GPT-pyWrite-Lotus-7a44993ddb1b42edbba4d6275d7c9628?pvs=4).

<p align="center">
  <img src="_documentation/logo.jpg" alt="Logo" width="200">
  <br>
  <em> Nelumbo Nucifera the most widely known Lotus Flower</em>
</p>

## Setup for Ubuntu 22.04

Clone repo into home directory:
```
git clone https://github.com/Somerandomguy10111/Lotus
```

Setup venv:
```
python3 -m venv venv
source venv/bin/activate
```

Install required packages:
```
export GIT_TOKEN=[access_token]
pip install -r requirements.txt
```

## Usage

Run the following commands in the root of the repo:
```
export PYTHONPATH="$(pwd)"
source venv/bin/activate
python3 run.py
```

