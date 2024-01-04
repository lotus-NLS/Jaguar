#!/bin/bash

create_and_activate_venv() {
  echo "- Creating venv"
  python3 -m venv venv
  echo "- Activating venv"
  source venv/bin/activate
  echo "- Installing requirements"
  pip install -r requirements.txt --no-cache
  deactivate
}

setup_required=false

# Check for the '--setup' flag in the script's arguments
for arg in "$@"
do
    if [ "$arg" == "--setup" ]; then
        setup_required=true
        break
    fi
done

if [ "$setup_required" = true ]; then
    # setup engine
    echo "-> setting up engine ..."
    sudo apt update > /dev/null 2>&1 && sudo apt install -y python3-venv
    create_and_activate_venv

    # setup app
    echo "-> setting up webapp ..."
    ENGINE_DIR=$(pwd)
    cd ~ || exit
    git clone https://github.com/Somerandomguy10111/webapp
    cd webapp || exit
    WEBAPP_DIR=$(pwd)
    create_and_activate_venv

    cd "$ENGINE_DIR" || exit
fi


ENGINE_VENV=$(pwd)/venv/bin/python
echo "$ENGINE_VENV"
export PYTHONPATH="$ENGINE_DIR:$PYTHONPATH"
"$ENGINE_VENV" engine/run.py &


WEBAPP_VENV=~/webapp/venv/bin/python
export PYTHONPATH="$WEBAPP_DIR:$PYTHONPATH"
"$WEBAPP_VENV" ~/webapp/run.py &

wait