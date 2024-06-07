	sudo systemctl stop dhcpcd.service
	sudo ip link set $1 down
	sudo iw $1 set type ibss
	sudo ifconfig $1 mtu 1500
	sudo iwconfig $1 channel 11
	sudo ip link set $1 up
	sudo iw $1 ibss join adhoctest 2462

	sudo modprobe batman-adv
	sudo batctl if add $1
	sudo ip link set up dev $1
	sudo ip link set up dev bat0
	sudo ifconfig bat0 $2

	sudo batctl gw_mode server
