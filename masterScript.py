import subprocess
import time
import os
import socket
import pandas as pd
import folium
from folium.plugins import HeatMap
import csv
import gpsd
from geopy.distance import geodesic
from shapely.geometry import Polygon
from collections import defaultdict

# Configuration
csv_file = "wifi_signal_quality_with_gps.csv"
base_station_ip = "192.168.3.1"  # Update with the correct IP
server_port = 12345
heatmap_directory = "/home/nap/Desktop/RSA/heatmaps"  # Update with the correct directory

def scan_wifi_networks():
    result = subprocess.run(['nmcli', '-t', '-f', 'SSID,SIGNAL', 'device', 'wifi', 'list'], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error scanning Wi-Fi networks: {result.stderr}")
        return []

    networks = []
    for line in result.stdout.strip().split('\n'):
        if ':' in line:
            ssid, signal = line.split(':')
            networks.append({'SSID': ssid, 'Signal': int(signal)})

    return networks

def get_gps_location():
    packet = gpsd.get_current()
    return packet.lat, packet.lon

def save_to_csv(data, output_file):
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['SSID', 'Signal', 'Latitude', 'Longitude'])
        for entry in data:
            writer.writerow([entry['SSID'], entry['Signal'], entry['Latitude'], entry['Longitude']])

def is_within_area(current_location, center_location, radius):
    distance = geodesic(current_location, center_location).meters
    return distance <= radius

def run_survey_in_area():
    gpsd.connect()
    center_location = (40.634561925146194, -8.659231214846358)  # Entre o IT e o DEM
    radius = 200  # meters
    interval = 3  # seconds
    output_file = csv_file
    
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
                    return  # Exit the function after saving data
            time.sleep(interval)

def calculate_best_point_of_intersection():
    SSIDs = ['eduroam', 'MEO-WiFi']  # List of Client SSID's

    # Read data from CSV files
    networks = defaultdict(list)
    for ssid in SSIDs:
        file_path = f'csvs/{ssid}_data.csv'
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                reader = csv.reader(file)
                next(reader)
                for row in reader:
                    networks[ssid].append((float(row[2]), float(row[3]), int(row[1])))
        else:
            print(f"File for {ssid} not found.")

    # Calculate intersection polygon
    intersection_polygon = Polygon()
    for ssid1, points1 in networks.items():
        for ssid2, points2 in networks.items():
            if ssid1 != ssid2:
                polygon1 = Polygon(points1).buffer(0).simplify(0.1)
                polygon2 = Polygon(points2).buffer(0).simplify(0.1)
                intersection = polygon1.intersection(polygon2)
                if intersection.area > intersection_polygon.area:
                    intersection_polygon = intersection

    # Find centroid of intersection polygon
    centroid = intersection_polygon.centroid
    best_point = (centroid.x, centroid.y)

    print("Best Point in Intersection:", best_point)
    return best_point, networks

def generate_heatmap(best_point, networks):
    print("Generating heatmap...")

    def create_network_quality_heatmap(df, ssid, lat_col, lon_col, quality_col, zoom_start=18, radius=15):
        ssid_data = df[df['SSID'] == ssid]
        filtered_data = ssid_data.loc[ssid_data.groupby([lat_col, lon_col])[quality_col].idxmax()]
        filtered_data.to_csv(f'csvs/{ssid}_data.csv', index=False)
        m = folium.Map(location=[df[lat_col].mean(), df[lon_col].mean()], zoom_start=zoom_start)
        heat_data = [[row[lat_col], row[lon_col], row[quality_col]] for index, row in filtered_data.iterrows()]
        HeatMap(heat_data, radius=radius).add_to(m)
        return m

    df = pd.read_csv(csv_file)
    unique_ssids = df['SSID'].unique()

    if not os.path.exists(heatmap_directory):
        os.makedirs(heatmap_directory)

    for ssid in unique_ssids:
        heatmap = create_network_quality_heatmap(df, ssid, 'Latitude', 'Longitude', 'Signal')
        heatmap_path = os.path.join(heatmap_directory, f"network_quality_heatmap_{ssid}.html")
        heatmap.save(heatmap_path)
        send_file(heatmap_path, base_station_ip, server_port)

    # Generate map with best point
    map_center = best_point
    mymap = folium.Map(location=map_center, zoom_start=18)

    # Add marker for the best point
    folium.Marker(location=best_point, popup='Best Point', icon=folium.Icon(color='green')).add_to(mymap)

    # Add heatmap layer for each SSID
    for ssid, points in networks.items():
        folium.FeatureGroup(name=ssid).add_to(mymap)
        HeatMap(points, name=ssid).add_to(mymap)

    # Save the map to an HTML file
    map_path = os.path.join(heatmap_directory, 'network_coverage_map.html')
    mymap.save(map_path)

    send_file(map_path, base_station_ip, server_port)
    print("Heatmap generated and sent to base station.")

def send_file(filename, server_ip, server_port=12345):
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return

    file_size = os.path.getsize(filename)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))
    print(f"Connected to server {server_ip}:{server_port}")

    # Send the file metadata
    metadata = f"{os.path.basename(filename)}|{file_size}"
    client_socket.send(metadata.encode())

    # Small delay to ensure the server processes metadata before file data
    time.sleep(1)

    # Send the file data
    with open(filename, 'rb') as f:
        while (chunk := f.read(4096)):
            client_socket.send(chunk)

    print(f"File sent: {filename}")
    client_socket.close()

if __name__ == "__main__":
    # Step 1: Run the survey to generate the CSV file
    run_survey_in_area()

    # Step 2: Calculate the best point of intersection and get network data
    best_point, networks = calculate_best_point_of_intersection()

    # Step 3: Generate the heatmap from the CSV file and send it to the base station
    generate_heatmap(best_point, networks)
