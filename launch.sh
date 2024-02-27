#!/bin/bash



start_service() {
    local service_name=$1

    echo "-> starting $service_name service in a new tab ..."
    gnome-terminal --tab -- bash -c "echo 'Starting $service_name service...';
    sudo systemctl start $service_name.service;
    sudo systemctl status $service_name.service --lines=0
    sudo journalctl -fu $service_name.service"
}

# Start services in new tabs
start_service "engine"
start_service "webapp"


echo "Press Enter to exit..."; read -r;

sudo systemctl stop "engine"
sudo systemctl stop "webapp"

echo "done"

