import os
import folium
from shapely.geometry import Polygon
from collections import defaultdict
import csv
from folium.plugins import HeatMap

# List of SSIDs
SSIDs = ['Client_1', 'Client_2']  # List of Client SSID's

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

# # Pseudocode to determine the best position for the relay node

# # Step 1: Initialize Variables
# base_station_x = <BaseStationLongitude>
# base_station_y = <BaseStationLatitude>
# best_point_x = <BestPointLongitude>
# best_point_y = <BestPointLatitude>

# # Step 2: Calculate Midpoint
# relay_node_x = (base_station_x + best_point_x) / 2
# relay_node_y = (base_station_y + best_point_y) / 2

# # Step 3: Output Midpoint
# output("Optimal Position for Relay Node: (" + relay_node_x + ", " + relay_node_y + ")")
