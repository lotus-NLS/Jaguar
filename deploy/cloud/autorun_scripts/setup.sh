#!/bin/bash
#wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
#sudo dpkg -i google-chrome-stable_current_amd64.deb
#sudo apt-get install -f
#sudo apt-get update --fix-missing



access_token=$(aws secretsmanager get-secret-value --secret-id github --query 'SecretString' --output text)
export GIT_TOKEN=$access_token

#TODO: Remove
echo $access_token

cd /home/ubuntu
git clone https://$GIT_TOKEN@github.com/Somerandomguy10111/Lotus
git clone https://$GIT_TOKEN@github.com/Somerandomguy10111/pystuff

export PYTHONPATH="$(pwd)/Lotus"
export PYTHONPATH="$(pwd)/pystuff"
cd Lotus

apt update
apt install python3.10-venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt