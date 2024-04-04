pip install openpyxl

import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import pandas as pd

# Load file

url = 'https://github.com/samhuang1805/AI_in_public_library/raw/main/AI_in_Library_case_repository_for_map.xlsx'
library_data_df = pd.read_excel(url)

# Streamlit UI
st.title('Library Events Map')

# Search box
search_query = st.text_input("Enter search term:", "")

# Filter data based on search query
if search_query:
    filtered_data = library_data_df[library_data_df['Library'].str.contains(search_query, case=False, na=False) |
                                    library_data_df['Event Title'].str.contains(search_query, case=False, na=False) |
                                    library_data_df['Description'].str.contains(search_query, case=False, na=False)]
else:
    filtered_data = library_data_df

# Group by library location after filtering
grouped = filtered_data.groupby(['Latitude', 'Longitude'])
    
# Initialize the folium map
library_map = folium.Map(location=[40.7128, -74.0060], zoom_start=4)        
        
# Initialize the folium map
library_map = folium.Map(location=[40.7128, -74.0060], zoom_start=4)
    
# Iterate over each group (unique location) and create a popup with all cases for that location
for (lat, lng), group in grouped:
        popup_content = ''
        for idx, row in group.iterrows():
            date_str = row['Date'].strftime('%Y-%m-%d') if pd.notnull(row['Date']) else "Date not available"
            case_content = (
                f"<div style='margin-bottom: 10px; padding: 5px; border: 1px solid #ddd; border-radius: 5px;'>"
                f"<b>{row['Library']}</b><br>"
                f"<b>Event:</b> {row['Event Title']}<br>"
                f"<b>Date:</b> {date_str}<br>"
                f"<b>Description:</b> {row['Description']}<br>"
                f"<b>Link:</b> <a href='{row['Links of the event']}'>Event Page</a><br>"
                f"<b>Contact:</b> {row['Contact person']} - {row['Contact information']}"
                f"</div>"
            )
            popup_content += case_content

        folium.Marker(
            [lat, lng],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip="Click for more info"
        ).add_to(library_map)

# Display Folium map in Streamlit
st_folium(library_map, width=725, height=525)
