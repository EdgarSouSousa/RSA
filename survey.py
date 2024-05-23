import subprocess
import csv
import time
import gpsd

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
        if ':' in line:
            ssid, signal = line.split(':')
            networks.append({'SSID': ssid, 'Signal': int(signal)})

    return networks

def get_gps_location():
    packet = gpsd.get_current()
    latitude = packet.lat
    longitude = packet.lon
    return latitude, longitude

def save_to_csv(data, output_file):
    # Save the networks and GPS information to a CSV file
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['SSID', 'Signal', 'Latitude', 'Longitude'])
        for entry in data:
            writer.writerow([entry['SSID'], entry['Signal'], entry['Latitude'], entry['Longitude']])

def main():
    # Connect to the local gpsd
    gpsd.connect()
    interval = 5  # seconds
    duration = 30  # seconds
    output_file = "wifi_signal_quality_with_gps.csv"

    end_time = time.time() + duration
    data = []

    while time.time() < end_time:
        print("Scanning for Wi-Fi networks...")
        networks = scan_wifi_networks()
        if networks:
            print(f"Found {len(networks)} networks:")
            for network in networks:
                print(f"SSID: {network['SSID']}, Signal: {network['Signal']}%")
            
            latitude, longitude = get_gps_location()
            print(f"Current Location: Latitude {latitude}, Longitude {longitude}")

            for network in networks:
                data.append({
                    'SSID': network['SSID'],
                    'Signal': network['Signal'],
                    'Latitude': latitude,
                    'Longitude': longitude
                })
        else:
            print("No networks found.")
        
        time.sleep(interval)

    save_to_csv(data, output_file)

if __name__ == "__main__":
    main()
