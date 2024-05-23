import pandas as pd
import folium
from folium.plugins import HeatMap

def create_network_quality_heatmap(df, lat_col, lon_col, quality_col, zoom_start=19, radius=15):
    # Initialize Folium Map centered on the mean of coordinates
    m = folium.Map(location=[df[lat_col].mean(), df[lon_col].mean()], zoom_start=zoom_start)

    # Convert DataFrame to list of lists
    heat_data = [[row[lat_col], row[lon_col], row[quality_col]] for index, row in df.iterrows()]

    # Create HeatMap layer
    HeatMap(heat_data, radius=radius).add_to(m)
    
    return m

# Read the CSV file into a DataFrame
df = pd.read_csv('data.csv')

# Create heatmap using the function
heatmap = create_network_quality_heatmap(df, 'Latitude', 'Longitude', 'Signal')

# Save map to an HTML file
heatmap.save("network_quality_heatmap.html")
