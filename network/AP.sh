#!/bin/bash

# Define variables
CONNECTION_NAME="RASPIAPCON"
SSID="RASPIAP"
PASSWORD="edgarsousa"
ETH_INTERFACE="enp2s0f2"
WLAN_INTERFACE=$(nmcli device | grep wlan | awk '{print $1}')

# Create hotspot connection
sudo nmcli connection add type wifi ifname "$WLAN_INTERFACE" con-name "$CONNECTION_NAME" autoconnect no ssid "$SSID" password "$PASSWORD"

# Assign IP address to the Wi-Fi interface
sudo nmcli connection modify "$CONNECTION_NAME" 802-11-wireless.mode ap 802-11-wireless.band bg ipv4.method shared

# Enable IP forwarding
sudo sysctl net.ipv4.ip_forward=1

# Activate the hotspot
sudo nmcli connection up "$CONNECTION_NAME"

sudo /iptables.sh wlp1s0 enx00e04c720855

sudo /iptables.sh enx00e04c720855 wlan0



