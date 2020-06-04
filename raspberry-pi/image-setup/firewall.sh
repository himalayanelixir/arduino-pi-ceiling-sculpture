#!/bin/bash

# disable ufw
sudo ufw --force disable
# disable and reset all rule tables
sudo ufw --force reset
# deny all out going connections
sudo ufw default deny outgoing
# allow local ssh 
sudo ufw allow from 192.168.0.0/16 to any port 22
# allow mDNS discovery on local network
sudo ufw allow out 5353/udp
# enable ufw
sudo ufw --force enable
