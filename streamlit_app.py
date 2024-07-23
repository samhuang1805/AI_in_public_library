import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium, folium_static
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

social_links_html = """
<div style='text-align: left;'>
    <a href='https://www.ctg.albany.edu/' target='_blank'>
        <img src='https://media.licdn.com/dms/image/D4E0BAQFVSVlZhcDIFw/company-logo_200_200/0/1693395291995?e=2147483647&v=beta&t=CWHo7yPFoN2eyabf5o4jb40sqSiT7EZkAtL8_9PCHtI' alt='CTG-logo' style='width:128px;height:128px;margin:0 10px;'>
    </a>
    <a href='https://www.urbanlibraries.org/' target='_blank'>
        <img src='https://www.infodocket.com/wp-content/uploads/2022/01/logo_dark_text.png' alt='ULC-logo' style='width:128px;height:64px;margin:0 10px;'>
</div>
"""
st.markdown(social_links_html, unsafe_allow_html=True)

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

# Adding text to the sidebar
st.sidebar.markdown("# Data Filter")
st.sidebar.write("Use the filters below to narrow down the AI programs and services shown on the map. If you encounter any issues, please feel free to contact Program Assistant Zong-Xian Huang at zhuang7@albany.edu.")

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
folium_static(library_map, width=1200, height=950)


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

# Adding social media links with icons
social_links_html = """
<div style='text-align: center;'>
    <a href='https://www.ctg.albany.edu/' target='_blank'>
        <img src='https://media.licdn.com/dms/image/D4E0BAQFVSVlZhcDIFw/company-logo_200_200/0/1693395291995?e=2147483647&v=beta&t=CWHo7yPFoN2eyabf5o4jb40sqSiT7EZkAtL8_9PCHtI' alt='CTG-logo' style='width:128px;height:128px;margin:0 10px;'>
    <a href='https://www.urbanlibraries.org/' target='_blank'>
        <img src='https://www.infodocket.com/wp-content/uploads/2022/01/logo_dark_text.png' alt='ULC-logo' style='width:128px;height:64px;margin:0 10px;'>
    <a href='https://twitter.com/CTGUAlbany' target='_blank'>
        <img src='https://upload.wikimedia.org/wikipedia/commons/5/53/X_logo_2023_original.svg' alt='X-logo' style='width:48px;height:48px;margin:0 10px;'>
    </a>
    <a href='https://www.linkedin.com/company/ctg-ualbany/' target='_blank'>
        <img src='https://upload.wikimedia.org/wikipedia/commons/8/81/LinkedIn_icon.svg' alt='LinkedIn' style='width:48px;height:48px;margin:0 10px;'>
    </a>
</div>
"""
st.markdown(social_links_html, unsafe_allow_html=True)
