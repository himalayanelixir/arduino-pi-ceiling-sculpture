#!/bin/bash

# gives a bit of time for the wifi to connect
sleep 20
# enable ssh
systemctl enable ssh
# update and upgrade 
apt-get update -y
apt-get upgrade -y
# install programs
apt-get install git zsh ufw python3-pip python3-venv -y
# change default shell for pi user
chsh -s /bin/zsh pi
# install ohmyzsh for pi user
sudo -u pi sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
# disable ohmyzsh auto update
sed -i 's/# DISABLE_AUTO_UPDATE="true"/DISABLE_AUTO_UPDATE="true"/g' /home/pi/.zshrc

# create virtual environment for controller 
python3 -m venv /home/pi/controller_env
# download the controller program from github with it's requirements.txt
wget -P /home/pi https://raw.githubusercontent.com/himalayanelixir/arduino-pi-ceiling-sculpture/master/raspberry-pi/controller.py
wget -P /home/pi https://raw.githubusercontent.com/himalayanelixir/arduino-pi-ceiling-sculpture/master/raspberry-pi/requirements.txt
# install pip dependencies from requirements.txt in the virtual environment
source /home/pi/controller_env/bin/activate
pip3 install -r /home/pi/requirements.txt
deactivate
# make controller program executable
chmod +x /home/pi/controller.py
# add controller program to PATH
echo "export PATH=\"/home/pi:$PATH\"" >>/home/pi/.zshrc
# set so that the controller starts up when a user logs in a virtual environment
echo "controller.py" >>/home/pi/.zshrc
# download state csvs
wget -P /home/pi https://raw.githubusercontent.com/himalayanelixir/arduino-pi-ceiling-sculpture/master/raspberry-pi/current-state.csv
wget -P /home/pi https://raw.githubusercontent.com/himalayanelixir/arduino-pi-ceiling-sculpture/master/raspberry-pi/desired-state.csv
# remove requirements.txt
rm /home/pi/requirements.txt

# download gui program from github
wget -P /home/pi https://raw.githubusercontent.com/himalayanelixir/arduino-pi-ceiling-sculpture/master/raspberry-pi/gui.py
cat <<EOT >/etc/systemd/system/gui.service
[Unit]
Description= Python3 script that runs the gui for the ceiling sculpture
After=network.target

[Service]
User=pi
ExecStart=/home/pi/gui.py 

[Install]
WantedBy=multi-user.target
EOT
chmod +x /home/pi/gui.py 
sudo systemctl enable gui.service

# make pi user owner of all the files we downloaded
chown -R pi /home/pi

# block all internet access other than incomming ssh from local network
# outgoing isn't blocked by default, we don't want updates unless we explicitly disable the firewall 
ufw default deny outgoing
# allow local ssh
ufw allow from 192.168.1.0/24 to any port 22
# enable ufw, will auto start on boot
echo "y" | ufw enable

# tell pi to restart after one minute. This is needed for the ssh changes to work and for the adafruit screen drivers
shutdown -r 1
