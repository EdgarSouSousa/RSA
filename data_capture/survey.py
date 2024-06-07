import subprocess
import csv
import time
import gpsd
from geopy.distance import geodesic

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
            
def is_within_area(current_location, center_location, radius):
    distance = geodesic(current_location, center_location).meters
    return distance <= radius

def main():
    # Connect to the local gpsd
    print("Starting Survey...")
    gpsd.connect()
    center_location = (40.634561925146194, -8.659231214846358) # Entre o IT e o DEM
    radius = 1000  # meters
    interval = 5  # seconds
    output_file = "wifi_signal_quality_with_gps.csv"
    
    data = []
    in_area = False

    while True:
        current_location = get_gps_location()
        if is_within_area(current_location, center_location, radius):
            if not in_area:
                print("You entered the area, Starting Scan...!")
                in_area = True
            
            networks = scan_wifi_networks()
            if networks:
                print(f"Found {len(networks)} networks:")
                for network in networks:
                    print(f"SSID: {network['SSID']}, Signal: {network['Signal']}%")
                
                latitude, longitude = current_location
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
        else:
            if in_area:
                print("You left the area, Stopping Scan...!")
                in_area = False

                if data:
                    save_to_csv(data, output_file)
                    data = []  # Clear data after saving
        
            time.sleep(interval)

if __name__ == "__main__":
    main()
