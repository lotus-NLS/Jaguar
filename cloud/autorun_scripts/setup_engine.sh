#!/bin/bash


apt update
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f
sudo apt-get update --fix-missing

# Fetch credentials
apt install awscli -y
apt install jq -y
github_secret=$(aws secretsmanager get-secret-value --region eu-north-1 --secret-id github --query 'SecretString' --output text)
export GIT_TOKEN=$(echo $github_secret | jq -r '.token')

# Fetch repo
cd /home/ubuntu
git clone https://$GIT_TOKEN@github.com/Somerandomguy10111/Lotus

# Install requirements
cd Lotus
apt install python3-pip -y
apt install python3.10-venv -y
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Launch
export PYTHONPATH="$(pwd)"