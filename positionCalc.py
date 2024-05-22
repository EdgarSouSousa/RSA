import folium
import numpy as np
from shapely.geometry import Polygon

def parse_folium_heatmap(folium_map):
    """
    Parse a Folium heatmap and return the heatmap data as a NumPy array.
    
    Parameters:
    - folium_map: Folium Map object containing the heatmap
    
    Returns:
    - heatmap_data: NumPy array representing the heatmap data
    """
    heatmap_layer = None
    for layer in folium_map._children.values():
        if isinstance(layer, folium.plugins.HeatMap):
            heatmap_layer = layer
            break
    
    if heatmap_layer is None:
        raise ValueError("Folium map does not contain a heatmap layer")
    
    heatmap_data = np.array(heatmap_layer.data)
    return heatmap_data

def intersection_centroid(heatmap_data1, heatmap_data2):
    """
    Calculate the centroid of the intersection between two heatmaps.
    
    Parameters:
    - heatmap_data1: NumPy array representing the first heatmap data
    - heatmap_data2: NumPy array representing the second heatmap data
    
    Returns:
    - centroid: Tuple containing the centroid coordinates (latitude, longitude)
    """
    # Convert heatmap data to polygons
    polygon1 = Polygon(heatmap_data1)
    polygon2 = Polygon(heatmap_data2)
    
    # Calculate intersection area
    intersection_area = polygon1.intersection(polygon2).area
    
    # Calculate centroid of the intersection area
    centroid = polygon1.intersection(polygon2).centroid
    centroid_lat = centroid.y
    centroid_lon = centroid.x
    
    return (centroid_lat, centroid_lon)

# Example usage
heatmap_data1 = [[37.75, -122.40], [37.80, -122.40], [37.80, -122.45], [37.75, -122.45]]  # Example heatmap data 1
heatmap_data2 = [[37.77, -122.42], [37.78, -122.42], [37.78, -122.43], [37.77, -122.43]]  # Example heatmap data 2

# Create Folium map with heatmaps
folium_map = folium.Map(location=[37.775, -122.42], zoom_start=12)
folium_map.add_child(folium.plugins.HeatMap(heatmap_data1))
folium_map.add_child(folium.plugins.HeatMap(heatmap_data2))
folium_map.save("heatmap_intersection_example.html")

# Parse the heatmaps
parsed_heatmap_data1 = parse_folium_heatmap(folium_map)
parsed_heatmap_data2 = parse_folium_heatmap(folium_map)

# Calculate intersection centroid
centroid = intersection_centroid(parsed_heatmap_data1, parsed_heatmap_data2)
print("Centroid of the intersection:", centroid)
