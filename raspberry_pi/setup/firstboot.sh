#!/bin/bash

sleep 20
# enable ssh
sudo systemctl enable ssh
sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install expect git zsh python3-pip -y
sudo chsh -s /bin/zsh pi
sudo chsh -s /bin/zsh
sudo -u pi sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
sudo sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/adafruit-pitft.sh
chmod +x adafruit-pitft.sh
cat <<EOT > script.exp
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
chmod 755 script.exp
./script.exp
rm adafruit-pitft.sh
rm script.exp

wget -P /home/pi https://raw.githubusercontent.com/himalayanelixir/Arduino_Ceiling_Sculpture_Platform/master/raspberry_pi/contoller.py
wget -P /home/pi https://raw.githubusercontent.com/himalayanelixir/Arduino_Ceiling_Sculpture_Platform/master/raspberry_pi/requirements.txt
pip3 install -r /home/pi/requirements.txt

sudo shutdown -r 1