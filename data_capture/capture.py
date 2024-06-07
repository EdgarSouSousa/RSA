import subprocess
import csv
import time

def scan_wifi_networks():
    # Run the `nmcli` command to scan for Wi-Fi networks
    result = subprocess.run(['nmcli', '-t', '-f', 'SSID,SIGNAL', 'device', 'wifi', 'list'], capture_output=True, text=True)

    # Check if the command was successful
    if result.returncode != 0:
        print(f"Error scanning Wi-Fi networks: {result.stderr}")
        return []

    # Parse the output into a list of networks
    networks = []
    for line in result.stdout.strip().split('\n'):
        ssid, signal = line.split(':')
        networks.append({'SSID': ssid, 'Signal': int(signal)})

    return networks

def save_to_csv(networks, output_file):
    # Save the networks information to a CSV file
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['SSID', 'Signal'])
        for network in networks:
            writer.writerow([network['SSID'], network['Signal']])

def main():
    interval = 5  # seconds
    duration = 30  # seconds
    output_file = "wifi_signal_quality.csv"

    end_time = time.time() + duration
    while time.time() < end_time:
        print("Scanning for Wi-Fi networks...")
        networks = scan_wifi_networks()
        if networks:
            print(f"Found {len(networks)} networks:")
            for network in networks:
                print(f"SSID: {network['SSID']}, Signal: {network['Signal']}%")
            save_to_csv(networks, output_file)
        else:
            print("No networks found.")
        
        time.sleep(interval)

if __name__ == "__main__":
    main()
