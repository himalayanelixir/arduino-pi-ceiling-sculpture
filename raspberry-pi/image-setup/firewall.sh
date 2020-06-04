#!/bin/bash

# disable ufw
ufw --force disable
# disable and reset all rule tables
ufw --force reset
# deny all out going connections
ufw default deny outgoing
# allow local ssh 
ufw allow from 192.168.0.0/16 to any port 22
# allow mDNS discovery on local network
ufw allow out 5353/udp
# enable ufw
sudo ufw --force enable
