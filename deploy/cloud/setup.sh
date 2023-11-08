#!/bin/bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
cd ~/Downloads
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f

cd ~
git clone https://github.com/Somerandomguy10111/Lotus
git clone https://github.com/Somerandomguy10111/pystuff
export PYTHONPATH="$(pwd)/Lotus"
export PYTHONPATH="$(pwd)/pystuff"
cd Lotus
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt