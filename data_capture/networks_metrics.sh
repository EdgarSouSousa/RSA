#!/bin/bash

TARGET="8.8.8.8"
IPERF_SERVER="192.168.3.1"
IPERF_PORT="5201" 
INTERFACE="wlp1s0"  

echo "===== Network Metrics ====="

# Measure average delay (latency)
echo "Ping to $TARGET to measure average delay:"
ping -c 30 $TARGET | tail -1 | awk -F '/' '{print "Average Delay: " $5 " ms"}'


## Measuring jitter
echo "Calculating jitter from ping results:"
ping -c 30 $TARGET | awk -F'[=/ ]+' '/time=/{print $10}' | awk '{
    if (NR > 1) {
        diff = $1 - prev;
        if (diff < 0) diff = -diff;
        sum += diff;
        count++;
    }
    prev = $1
} END {
    if (count > 0)
        print "Jitter: " sum/count " ms";
    else
        print "Jitter: 0 ms"
}'

# Measure SNR
echo "Measuring Signal-to-Noise Ratio (SNR):"
SNR=$(iwconfig $INTERFACE | grep -i --color=never 'signal level' | awk '{print $4}' | cut -d'=' -f2)
if [ -z "$SNR" ]; then
    echo "SNR data not available."
else
    echo "SNR: $SNR dBm"
fi

# Measure throughput with iperf3
echo "Measuring throughput with iperf3:"
iperf3 -c $IPERF_SERVER -p $IPERF_PORT -t 10

echo "Network metrics measurement completed."
