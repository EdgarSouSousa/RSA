import pandas as pd
import folium
from folium.plugins import HeatMap

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

# Read the CSV file into a DataFrame
df = pd.read_csv('wifi_signal_quality_with_gps.csv')

# Get unique SSIDs
unique_ssids = df['SSID'].unique()

# Generate heatmap for each SSID
for ssid in unique_ssids:
    heatmap = create_network_quality_heatmap(df, ssid, 'Latitude', 'Longitude', 'Signal')
    heatmap.save(f"heatmaps/network_quality_heatmap_{ssid}.html")
