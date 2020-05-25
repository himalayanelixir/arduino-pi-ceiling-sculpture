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
# download state csvs
wget -P /home/pi/code https://raw.githubusercontent.com/himalayanelixir/arduino-pi-ceiling-sculpture/master/raspberry-pi/current-state.csv
wget -P /home/pi/ https://raw.githubusercontent.com/himalayanelixir/arduino-pi-ceiling-sculpture/master/raspberry-pi/desired-state.csv

# download leds program from github
wget -P /home/pi/code https://raw.githubusercontent.com/himalayanelixir/arduino-pi-ceiling-sculpture/master/raspberry-pi/leds.py
cat <<EOT >/etc/systemd/system/leds.service
[Unit]
Description= Python3 script that runs the leds on the Raspberry Pi
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
Description= Python3 script that runs the button on the Raspberry Pi
After=network.target

[Service]
User=pi
ExecStart=/home/pi/code/button.py

[Install]
WantedBy=multi-user.target
EOT
sudo systemctl enable button.service

# download restart program from github
wget -P /home/pi/code https://raw.githubusercontent.com/himalayanelixir/arduino-pi-ceiling-sculpture/master/raspberry-pi/restart.py

# download shutdown program from github
wget -P /home/pi/code https://raw.githubusercontent.com/himalayanelixir/arduino-pi-ceiling-sculpture/master/raspberry-pi/shutdown.py

# make all the files we downloaded executable
chmod +x /home/pi/code/controller.py /home/pi/code/leds.py /home/pi/code/button.py /home/pi/code/shutdown.py /home/pi/code/restart.py
# make pi user owner of all the files we downloaded (needed since this program runs as root on firstboot)
chown -R pi /home/pi
# setup aliases
echo 'alias controller="/home/pi/code/controller.py"' >>/home/pi/.zshrc
echo 'alias shutdown="/home/pi/code/shutdown.py"' >>/home/pi/.zshrc
echo 'alias restart="/home/pi/code/restart.py"' >>/home/pi/.zshrc
# add /home/pi to path
echo "export PATH=\"/home/pi/code:$PATH\"" >>/home/pi/.zshrc
# set so that the controller starts up when a user logs in a virtual environment
echo "controller.py" >>/home/pi/.zshrc

# block all internet access other than incomming ssh from local network
# outgoing isn't blocked by default, we don't want updates unless we explicitly disable the firewall
ufw default deny outgoing
# allow local ssh
ufw allow from 192.168.0.0/16 to any port 22
# allow mDNS discovery on local network so 'ping raspberrypi.local' works
ufw allow out 5353/udp
# enable ufw, will auto start on boot
echo "y" | ufw enable

# change Rasberry Pi's hostname so we can use sculpture.local instead of raspberrpi.local
sed -i 's/raspberrypi/sculpture/g' /etc/hostname
sed -i 's/raspberrypi/sculpture/' /etc/hosts

# tell pi to restart after one minute
shutdown -r 1
