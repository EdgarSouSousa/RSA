#!/bin/bash

# Define variables
CONNECTION_NAME="RASPIAP"
SSID="RASPIAP"
PASSWORD="edgarsousa"
ETH_INTERFACE="enx00e04c720855"
WLAN_INTERFACE="wlp1s0"
IP_RANGE="192.168.4.0/24"

# Create hotspot connection with custom IP range
sudo nmcli connection add type wifi ifname "$WLAN_INTERFACE" con-name "$CONNECTION_NAME" autoconnect no ssid "$SSID" password "$PASSWORD" 802-11-wireless.mode ap ipv4.method shared ipv4.addresses "$IP_RANGE"

# Enable IP forwarding
sudo sysctl net.ipv4.ip_forward=1

# Enable NAT
sudo iptables -t nat -A POSTROUTING -o "$ETH_INTERFACE" -j MASQUERADE

# Forward traffic from hotspot to Ethernet
sudo iptables -A FORWARD -i "$WLAN_INTERFACE" -o "$ETH_INTERFACE" -j ACCEPT
sudo iptables -A FORWARD -i "$ETH_INTERFACE" -o "$WLAN_INTERFACE" -m state --state RELATED,ESTABLISHED -j ACCEPT

# Activate the hotspot
sudo nmcli connection up "$CONNECTION_NAME"
