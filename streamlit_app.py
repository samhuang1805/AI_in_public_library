import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import pandas as pd
import gspread
import datetime
from oauth2client.service_account import ServiceAccountCredentials
  
# Load file

url = 'https://github.com/samhuang1805/AI_in_public_library/raw/main/AI_in_Library_case_repository_for_map.xlsx'
library_data_df = pd.read_excel(url)

# Convert date into year
library_data_df['Year'] = library_data_df['Date'].apply(lambda x: x.strftime('%Y') if not pd.isnull(x) else x)


# Streamlit UI
st.set_page_config(layout="wide")
st.title('AI Programs and Services Offered by Public Libraries')

# Creating time filter
def display_time_filter(df):
    year_list = [''] + sorted(list(df['Year'].unique()))
    return st.sidebar.selectbox('Year', options=year_list)

# Creating state filter
def display_state_filter(df):
    state_list = [''] + list(df['State'].unique())
    state_list.sort()
    return st.sidebar.selectbox('State', state_list)

# Creating search filter
def display_search_filter():
    return st.sidebar.text_input("Enter search term:", "")

# Display Filters
selected_year = display_time_filter(library_data_df)
selected_state = display_state_filter(library_data_df)
search_query = display_search_filter()

# Applying filters
filtered_data = library_data_df

# Filter by year
if selected_year:
    filtered_data = filtered_data[filtered_data['Year'] == selected_year]

# Filter by state
if selected_state:
    filtered_data = filtered_data[filtered_data['State'] == selected_state]
    
# Filter by search query
if search_query:
    filtered_data = filtered_data[
        filtered_data['Library'].str.contains(search_query, case=False, na=False) |
        filtered_data['Event Title'].str.contains(search_query, case=False, na=False) |
        filtered_data['Description'].str.contains(search_query, case=False, na=False)
    ]

### Start to create the interactive map ###
# Group by library location after filtering
grouped = filtered_data.groupby(['Latitude', 'Longitude'])
    
# Initialize the folium map
library_map = folium.Map(location=[41.266, -96.068], zoom_start=4)        

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
            popup=folium.Popup(popup_content, max_width=750),
            tooltip="Click for more info"
        ).add_to(library_map)

# Display Folium map in Streamlit with dynamic full-width
st_folium(library_map, width='100%', height=1200)


# Creating an interactive table to input data

creds_json = st.secrets["service_account"]
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
client = gspread.authorize(creds)

# Open the sheet
sheet = client.open("AI-library-response-sheet").sheet1  # Name of your Google Sheet
 

# Create input fields in the below space
st.header("Tell us about AI programs in your library")
st.subheader('If you have further information about any of the programs/services on the map or you want to share a new program/service, please fill the fields below.')
lib_name = st.text_input("Library name")
event_title = st.text_input("Program title")
description = st.text_area("Description of program")
event_page = st.text_input("Program page")
contact = st.text_input("Contact information")
Others = st.text_area("Other Information")
submit_button = st.button('Submit')

if submit_button:
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime('%Y-%m-%d %H:%M:%S')  # Format as 'YYYY-MM-DD HH:MM:SS'
    sheet.append_row([formatted_time, lib_name, event_title, description, event_page, contact, Others])
    st.success("Program information submitted successfully!")
