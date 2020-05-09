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
python3 -m venv /home/pi/pi_env
# download the controller program from github with it's requirements.txt
wget -P /home/pi https://raw.githubusercontent.com/himalayanelixir/arduino-pi-ceiling-sculpture/master/raspberry-pi/controller.py
wget -P /home/pi https://raw.githubusercontent.com/himalayanelixir/arduino-pi-ceiling-sculpture/master/raspberry-pi/requirements.txt
# install pip dependencies from requirements.txt in the virtual environment
source /home/pi/pi_env/bin/activate
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

# download leds program from github
wget -P /home/pi https://raw.githubusercontent.com/himalayanelixir/arduino-pi-ceiling-sculpture/master/raspberry-pi/leds.py
cat <<EOT >/etc/systemd/system/leds.service
[Unit]
Description= Python3 script that runs the leds on the Raspberry Pi
After=network.target

[Service]
User=pi
ExecStart=/home/pi/leds.py 

[Install]
WantedBy=multi-user.target
EOT
chmod +x /home/pi/leds.py 
sudo systemctl enable leds.service

# download button program from github
wget -P /home/pi https://raw.githubusercontent.com/himalayanelixir/arduino-pi-ceiling-sculpture/master/raspberry-pi/button.py
cat <<EOT >/etc/systemd/system/button.service
[Unit]
Description= Python3 script that runs the button on the Raspberry Pi
After=network.target

[Service]
User=pi
ExecStart=/home/pi/button.py 

[Install]
WantedBy=multi-user.target
EOT
chmod +x /home/pi/button.py 
sudo systemctl enable button.service

# download restart program from github
wget -P /home/pi https://raw.githubusercontent.com/himalayanelixir/arduino-pi-ceiling-sculpture/master/raspberry-pi/restart.py
chmod +x /home/pi/restart.py

# download shutdown program from github
wget -P /home/pi https://raw.githubusercontent.com/himalayanelixir/arduino-pi-ceiling-sculpture/master/raspberry-pi/shutdown.py
chmod +x /home/pi/shutdown.py

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
