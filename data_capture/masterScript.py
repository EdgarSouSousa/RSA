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
base_station_ip = "10.1.1.16"  # Update with the correct IP
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
    center_location = (40.63448121104729, -8.659492953517972)  # Entre o IT e o DEM
    radius =25 # meters
    interval = 3  # seconds
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
                    return  # Exit the function after saving data
            time.sleep(interval)

def get_final_heatmap():
        # List of SSIDs
    SSIDs = ['PIPA', 'Claro']  # List of Client SSID's

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

    # Initialize map centered at the centroid of intersection
    map_center = best_point
    mymap = folium.Map(location=map_center, zoom_start=18)

    # add a marker for the best point
    folium.Marker(location=best_point, popup='Best Point', icon=folium.Icon(color='green')).add_to(mymap)


    #add a heatmap layer for each SSID
    for ssid, points in networks.items():
        folium.FeatureGroup(name=ssid).add_to(mymap)
        folium.plugins.HeatMap(points, name=ssid).add_to(mymap)


    # Save the map to an HTML file
    mymap.save('network_coverage_map.html')


    print("Map saved as 'network_coverage_map.html'.")


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
    
def create_network_quality_heatmap(df, ssid, lat_col, lon_col, quality_col, zoom_start=18, radius=15):
    """
    Create a heatmap of network quality for a specific SSID.
    
    Parameters:
        df (DataFrame): DataFrame containing network quality data.
        ssid (str): SSID for which the heatmap is generated.
        lat_col (str): Name of the column containing latitude values.
        lon_col (str): Name of the column containing longitude values.
        quality_col (str): Name of the column containing network quality metric.
        zoom_start (int, optional): Initial zoom level of the map. Default is 18.
        radius (int, optional): Radius of each point on the heatmap. Default is 15.
    
    Returns:
        folium.Map: Folium Map object with the heatmap layer added.
    """
    # Filter data for the specified SSID
    ssid_data = df[df['SSID'] == ssid]
    
    # Group by location and select row with highest signal quality
    filtered_data = ssid_data.loc[ssid_data.groupby([lat_col, lon_col])[quality_col].idxmax()]

    #save the filtered data to a CSV file for later use with name SSID_data.csv
    filtered_data.to_csv(f'csvs/{ssid}_data.csv', index=False)

    
    # Initialize Folium Map centered on the mean of coordinates
    m = folium.Map(location=[df[lat_col].mean(), df[lon_col].mean()], zoom_start=zoom_start)

    # Convert DataFrame to list of lists
    heat_data = [[row[lat_col], row[lon_col], row[quality_col]] for index, row in filtered_data.iterrows()]

    # Create HeatMap layer
    HeatMap(heat_data, radius=radius).add_to(m)
    
    return m

if __name__ == "__main__":
    # Step 1: Run the survey to generate the CSV file
    run_survey_in_area()
    
        # Read the CSV file into a DataFrame
    df = pd.read_csv('wifi_signal_quality_with_gps.csv')

    # Get unique SSIDs
    unique_ssids = df['SSID'].unique()

    # Generate heatmap for each SSID
    for ssid in unique_ssids:
        heatmap = create_network_quality_heatmap(df, ssid, 'Latitude', 'Longitude', 'Signal')
        heatmap.save(f"heatmaps/network_quality_heatmap_{ssid}.html")

    get_final_heatmap()
    
    send_file('network_coverage_map.html', base_station_ip, 12345)
