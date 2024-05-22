import iperf3
import csv
import time

def run_iperf(server_ip, interval, duration, output_file, measurements):
    # Open CSV file for writing
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
            start_time = time.time()
            
            # Run iperf measurement
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
                #disconnect the iperf client
                time.sleep(interval)

if __name__ == "__main__":
    server_ip = "192.168.43.188"
    interval = 5  # seconds
    duration = 5  # seconds
    output_file = "iperf_results.csv"
    measurements = 5  # Number of measurements to perform
    run_iperf(server_ip, interval, duration, output_file, measurements)
