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

setup_service() {
    local service_name=$1
    local working_directory=$2
    local exec_start=$3

    echo "-> setting up $service_name service ..."
    echo "[Unit]
Description=$service_name Flask Server
After=network.target

[Service]
User=$USER
WorkingDirectory=$working_directory
ExecStart=$exec_start
Restart=on-failure
Environment=PYTHONPATH=$working_directory

[Install]
WantedBy=multi-user.target" | sudo tee /etc/systemd/system/"$service_name".service
}

start_service_in_new_tab() {
    local service_name=$1

    echo "-> starting $service_name service in a new tab ..."
    gnome-terminal --tab -- bash -c "echo 'Starting $service_name service...';
    sudo systemctl start $service_name.service;
    sudo systemctl status $service_name.service --lines=0
    sudo journalctl -fu $service_name.service"
}


#---------------------------------------------------

#check for setup flag
setup_required=false
for arg in "$@"
do
    if [ "$arg" == "--setup" ]; then
        setup_required=true
        break
    fi
done



if [ "$setup_required" = true ]; then
    # setup engine environment
    echo "-> setting up engine ..."
    sudo apt update > /dev/null 2>&1 && sudo apt install -y python3-venv
    create_and_activate_venv

    ENGINE_DIR=$(pwd)
    ENGINE_VENV="$ENGINE_DIR/venv/bin/python"

    # setup engine service
    setup_service "engine" "$ENGINE_DIR" "$ENGINE_VENV $ENGINE_DIR/engine/run.py"

    # setup webapp environment
    echo "-> setting up webapp ..."
    cd ~ || exit
    git clone git@github.com/Somerandomguy10111/webapp
    cd webapp || exit
    WEBAPP_DIR=$(pwd)
    create_and_activate_venv

    WEBAPP_VENV="$WEBAPP_DIR/venv/bin/python"

    # setup webapp service
    setup_service "webapp" "$WEBAPP_DIR" "$WEBAPP_VENV $WEBAPP_DIR/run.py"

    cd "$ENGINE_DIR" || exit
fi

# Start services in new tabs
start_service_in_new_tab "engine"
start_service_in_new_tab "webapp"


echo "Press Enter to exit..."; read -r;

sudo systemctl stop "engine"
sudo systemctl stop "webapp"

echo "done"
