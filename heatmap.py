import pandas as pd
import folium
from folium.plugins import HeatMap

def create_network_quality_heatmap(df, lat_col, lon_col, quality_col, zoom_start=4, radius=15):
    """
    Create a heatmap of network quality based on survey data.
    
    Parameters:
        df (DataFrame): DataFrame containing survey data.
        lat_col (str): Name of the column containing latitude values.
        lon_col (str): Name of the column containing longitude values.
        quality_col (str): Name of the column containing network quality metric.
        zoom_start (int, optional): Initial zoom level of the map. Default is 4.
        radius (int, optional): Radius of each point on the heatmap. Default is 15.
    
    Returns:
        folium.Map: Folium Map object with the heatmap layer added.
    """
    # Initialize Folium Map centered on the mean of coordinates
    m = folium.Map(location=[df[lat_col].mean(), df[lon_col].mean()], zoom_start=zoom_start)

    # Convert DataFrame to list of lists
    heat_data = [[row[lat_col], row[lon_col], row[quality_col]] for index, row in df.iterrows()]

    # Create HeatMap layer
    HeatMap(heat_data, radius=radius).add_to(m)
    
    return m

# Sample DataFrame (replace with your actual data)
data = {
    'latitude': [40.7128, 34.0522, 37.7749],  # Sample latitudes
    'longitude': [-74.0060, -118.2437, -122.4194],  # Sample longitudes
    'quality_metric': [50, 70, 60]  # Sample network quality metric
}

df = pd.DataFrame(data)

# Create heatmap using the function
heatmap = create_network_quality_heatmap(df, 'latitude', 'longitude', 'quality_metric')

# Save map to an HTML file
heatmap.save("network_quality_heatmap.html")
