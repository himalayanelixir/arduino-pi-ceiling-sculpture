#!/bin/bash

# gives a bit of time for the wifi to connect
sleep 20
# enable ssh
sudo systemctl enable ssh
# update and upgrade 
sudo apt-get update -y
sudo apt-get upgrade -y
# install programs
sudo apt-get install expect git zsh python3-pip python3-venv -y
# change default shell for root and pi users
sudo chsh -s /bin/zsh pi
sudo chsh -s /bin/zsh
# install ohmyzsh for root and pi users
sudo -u pi sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
sudo sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended


# install drivers for adafruit screen
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/adafruit-pitft.sh
# make downloaded script executable
chmod +x adafruit-pitft.sh
# create script that uses expect to automate adafruit installation prompts
cat <<EOT >script.exp
#!/usr/bin/expect -f
set timeout -1
spawn sudo ./adafruit-pitft.sh
match_max 100000
expect -exact "SELECT 1-7: "
send -- "1\r"
expect -exact "SELECT 1-4: "
send -- "1\r"
expect -exact "Would you like the console to appear on the PiTFT display? \[y/n\] "
send -- "y\r"
expect -exact "REBOOT NOW? \[y/N\] "
send -- "N\r"
expect eof
EOT
# make script executable 
chmod 755 script.exp
# run automation script which installs the adafruit screen drivers
./script.exp
# remove the screen installation script
rm adafruit-pitft.sh
# remove expect automation script
rm script.exp


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
sudo chmod +x /home/pi/controller.py
# add controller program to PATH
echo "export PATH=\"/home/pi:$PATH\"" >>/home/pi/.zshrc
# set so that the controller starts up when a user logs in a virtual environment
echo "controller.py" >>/home/pi/.zshrc
# download state csvs
wget -P /home/pi https://raw.githubusercontent.com/himalayanelixir/arduino-pi-ceiling-sculpture/master/raspberry-pi/current-state.csv
wget -P /home/pi https://raw.githubusercontent.com/himalayanelixir/arduino-pi-ceiling-sculpture/master/raspberry-pi/desired-state.csv
# make pi user owner of all the files we downloaded
chown pi /home/pi/controller.py
chown pi /home/pi/current-state.csv
chown pi /home/pi/desired-state.csv
# remove requirements.txt
rm /home/pi/requirements.txt


# create virtual environment for gui
python3 -m venv /root/gui_env
# download gui program from github
wget -P /root https://raw.githubusercontent.com/himalayanelixir/arduino-pi-ceiling-sculpture/master/raspberry-pi/gui.py
# make gui program executable
sudo chmod +x /root/gui.py
# add controller program to PATH
echo "export PATH=\"/root:$PATH\"" >>/root/.zshrc
# set so that the gui starts up on the adafruit screen when booted in a virtual environment
echo "gui.py" >>/root/.zshrc
# tell pi to restart after one minute. This is needed for the ssh changes to work and for the adafruit screen drivers
sudo shutdown -r 1
