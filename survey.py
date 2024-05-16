import os
import time
import gps
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

def run_iperf_test(server, port=5201, protocol='tcp', duration=10):
    client = iperf3.Client()
    client.server_hostname = server
    client.port = port
    client.protocol = protocol
    client.duration = duration
    result = client.run()
    if result.error:
        print("Error:", result.error)
        return None
    else:
        return result.sent_Mbps, result.received_Mbps

def main():
    output_file = "network_quality_data.csv"

    if os.path.exists(output_file):
        df = pd.read_csv(output_file)
    else:
        df = pd.DataFrame(columns=['Latitude', 'Longitude', 'Sent_Mbps', 'Received_Mbps', 'Timestamp'])

    while True:
        lat, lon = get_gps_data()
        if lat is not None and lon is not None:
            sent, received = run_iperf_test(server="your_server_ip")  # Replace with your server IP
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
        time.sleep(60)  # Wait for 1 minute before next iteration

if __name__ == "__main__":
    main()
