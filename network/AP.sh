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

# Enable NAT
sudo iptables -t nat -A POSTROUTING -o "$ETH_INTERFACE" -j MASQUERADE

# Forward traffic from hotspot to Ethernet
sudo iptables -A FORWARD -i "$WLAN_INTERFACE" -o "$ETH_INTERFACE" -j ACCEPT
sudo iptables -A FORWARD -i "$ETH_INTERFACE" -o "$WLAN_INTERFACE" -m state --state RELATED,ESTABLISHED -j ACCEPT

# Activate the hotspot
sudo nmcli connection up "$CONNECTION_NAME"
