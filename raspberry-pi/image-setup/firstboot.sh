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

# create virtual environment for python scripts 
python3 -m venv /home/pi/code/pi_env
# download the requirements.txt from Github
wget -P /home/pi/code https://raw.githubusercontent.com/himalayanelixir/arduino-pi-ceiling-sculpture/master/raspberry-pi/requirements.txt
# install pip dependencies from requirements.txt in the virtual environment
source /home/pi/code/pi_env/bin/activate
python3 -m pip install -r /home/pi/code/requirements.txt
deactivate
# remove requirements.txt
rm /home/pi/code/requirements.txt

# download the controller program from github with it's requirements.txt
wget -P /home/pi/code https://raw.githubusercontent.com/himalayanelixir/arduino-pi-ceiling-sculpture/master/raspberry-pi/controller.py
# create empty csv files to store the state of the sculpture
touch /home/pi/code/current-state.csv
touch /home/pi/example.csv

# download leds program from github
wget -P /home/pi/code https://raw.githubusercontent.com/himalayanelixir/arduino-pi-ceiling-sculpture/master/raspberry-pi/leds.py
cat <<EOT >/etc/systemd/system/leds.service
[Unit]
Description= Program that controlls the leds on the Raspberry Pi
After=network.target

[Service]
User=pi
ExecStart=/home/pi/code/leds.py

[Install]
WantedBy=multi-user.target
EOT
sudo systemctl enable leds.service

# download button program from github
wget -P /home/pi/code https://raw.githubusercontent.com/himalayanelixir/arduino-pi-ceiling-sculpture/master/raspberry-pi/button.py
cat <<EOT >/etc/systemd/system/button.service
[Unit]
Description= Program that controlls the button on the Raspberry Pi
After=network.target

[Service]
User=pi
ExecStart=/home/pi/code/button.py

[Install]
WantedBy=multi-user.target
EOT
sudo systemctl enable button.service

# download firewall script from github
wget -P /home/pi/code https://raw.githubusercontent.com/himalayanelixir/arduino-pi-ceiling-sculpture/master/raspberry-pi/image-setup/firewall.sh
cat <<EOT >/etc/systemd/system/firewall.service
[Unit]
Description= Script that resets and enables the firewall on the Raspberry Pi
After=network.target

[Service]
User=pi
ExecStart=/home/pi/code/firewall.sh

[Install]
WantedBy=multi-user.target
EOT
sudo systemctl enable firewall.service

# download shutdown/restart program from github
wget -P /home/pi/code https://raw.githubusercontent.com/himalayanelixir/arduino-pi-ceiling-sculpture/master/raspberry-pi/shutdown_restart.py

# make all the files we downloaded executable
chmod +x /home/pi/code/controller.py /home/pi/code/leds.py /home/pi/code/button.py /home/pi/code/shutdown_restart.py /home/pi/code/firewall.sh
# make pi user owner of all the files we downloaded (needed since this program runs as root on firstboot)
chown -R pi /home/pi
# setup aliases
echo 'alias controller="/home/pi/code/controller.py"' >>/home/pi/.zshrc
echo 'alias shutdown="/home/pi/code/shutdown_restart.py shutdown"' >>/home/pi/.zshrc
echo 'alias restart="/home/pi/code/shutdown_restart.py restart"' >>/home/pi/.zshrc
# add /home/pi to path
echo "export PATH=\"/home/pi/code:$PATH\"" >>/home/pi/.zshrc
# set so that the controller starts up when a user logs in a virtual environment
echo "controller.py" >>/home/pi/.zshrc

# change Rasberry Pi's hostname so we can use sculpture.local instead of raspberrpi.local
sed -i 's/raspberrypi/sculpture/g' /etc/hostname
sed -i 's/raspberrypi/sculpture/' /etc/hosts

# tell pi to restart after one minute
shutdown -r 1
