import pandas as pd

# Read the CSV file into a DataFrame
df = pd.read_csv('wifi_signal_quality_with_gps.csv')

def filter_and_select(data, ssid):
    # Filter data based on SSID
    ssid_data = data[data['SSID'] == ssid]
    
    # Group by location and select row with highest signal quality
    filtered_data = ssid_data.loc[ssid_data.groupby(['Latitude', 'Longitude'])['Signal'].idxmax()]
    
    # Drop unnecessary columns and reset index
    filtered_data = filtered_data[['SSID', 'Signal', 'Latitude', 'Longitude']].reset_index(drop=True)
    
    return filtered_data

# Specify the SSID you want to filter for
desired_ssid = 'eduroam'

# Call the function to filter and select data
filtered_data = filter_and_select(df, desired_ssid)

# Write the filtered data to a CSV file
filtered_data.to_csv('data.csv', index=False)

print("Filtered data saved to data.csv")
