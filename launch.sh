#!/bin/bash


create_and_activate_venv() {
  echo "- Creating venv"
  python3 -m venv venv
  echo "- Activating venv"
  source venv/bin/activate
  echo "- Installing requirements"
  pip install -r requirements.txt --no-cache
}

# setup engine
echo "-> engine setup"
sudo apt update > /dev/null 2>&1 && sudo apt install python3-venv
create_and_activate_venv

# setup webapp
echo "-> webapp setup"
ORIGINAL_DIR=$(pwd)
cd ~ || exit
git clone https://github.com/Somerandomguy10111/webapp
cd webapp || exit
create_and_activate_venv

cd "$ORIGINAL_DIR" || exit


