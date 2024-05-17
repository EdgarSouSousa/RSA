import os
import time
import gps
import csv
import iperf3
import pandas as pd
from datetime import datetime

def get_gps_data():
    session = gps.gps("localhost", "2947")
    session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
    try:
        report = session.next()
        if report['class'] == 'TPV':
            if hasattr(report, 'lat') and hasattr(report, 'lon'):
                return report.lat, report.lon
    except Exception as e:
        print("Error:", e)
    return None, None

def run_iperf_test(server_ip,duration,output_file,measurements,interval):
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Measurement', 'Timestamp', 'Throughput (Mbps)'])

        # Run iperf measurements at intervals
        for measurement in range(1, measurements + 1):
            print(f"Starting measurement {measurement}...")
            
            # Initialize the iperf client
            client = iperf3.Client()

            # Set server
            client.server_hostname = server_ip

            # Set duration
            client.duration = duration

            print(f"Running iperf measurement for {duration} seconds...")

            result = client.run()
            if result.error:
                print(result.error)
            else:
                throughput_mbps = result.sent_Mbps
                current_time = time.time()
                writer.writerow([measurement, current_time, throughput_mbps])
                print(f"Measurement {measurement}: Throughput: {throughput_mbps} Mbps")
            
            # Wait for the next interval
            if measurement < measurements:
                print(f"Waiting {interval} seconds for next measurement...")
                time.sleep(interval)

def main():
    output_file = "network_quality_data.csv"
    server_ip = "192.168.39.115"
    interval = 5  
    duration = 5  
    measurements = 5

    if os.path.exists(output_file):
        df = pd.read_csv(output_file)
    else:
        df = pd.DataFrame(columns=['Latitude', 'Longitude', 'Sent_Mbps', 'Received_Mbps', 'Timestamp'])

    while True:
        lat, lon = get_gps_data()
        if lat is not None and lon is not None:
            sent, received = run_iperf_test(server_ip,duration,output_file,measurements,interval)
            if sent is not None and received is not None:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                data = {'Latitude': [lat], 'Longitude': [lon], 'Sent_Mbps': [sent], 'Received_Mbps': [received], 'Timestamp': [timestamp]}
                df = df.append(pd.DataFrame(data), ignore_index=True)
                df.to_csv(output_file, index=False)
                print("Data saved:", lat, lon, sent, received, timestamp)
            else:
                print("Failed to perform iPerf test")
        else:
            print("Failed to get GPS data")
        time.sleep(60)

if __name__ == "__main__":
    main()
