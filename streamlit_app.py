import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import pandas as pd

# Load file

url = 'https://github.com/samhuang1805/AI_in_public_library/raw/main/AI_in_Library_case_repository_for_map.xlsx'
library_data_df = pd.read_excel(url)

# Convert date into year
library_data_df['Year'] = library_data_df['Date'].apply(lambda x: x.strftime('%Y') if not pd.isnull(x) else x)


# Streamlit UI
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
            popup=folium.Popup(popup_content, max_width=600),
            tooltip="Click for more info"
        ).add_to(library_map)

# Display Folium map in Streamlit with dynamic full-width
st_folium(library_map, width='100%', height=600)


creds = ServiceAccountCredentials.from_json_keyfile_dict({
  "type": "service_account",
  "project_id": "ai-in-public-library-sheet",
  "private_key_id": "2ac748eed9c920b7701dd53f19fd342d8350ad9f",
  "private_key": "-----BEGIN PRIVATE KEY----- MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDNBN1Z/iKryP0V i9Tg3uX7CvFJAnLLfNQjnvqMG436JmY1ffhle6UlWKP7TtD8mXcI8en0jgAXEZco oAblffeueb6pXS7De90TF4vN+ZkwhJw2vG2Fg8eu2oTXmVW8aIRoycK9ZmgQes+x e0Q6bq09g2s/bwgUHgJfk4dlXDf9HCj3kJC1yCaQB6Z4ogJFA07sv5AnCsR/SgUb ah/if1o0404w/bQ0+7NnDRLV6AHtsyJ48A0rD+Vfo5c8vtdCCNxW2kWnpEAWxIgE dJzDXFPOiFe8JiNFtVBGvHjOKhXZmZ9cdl80V6Jb6WBn0mz42idaBw67P3MdItv1 jglV2TSlAgMBAAECggEASu3MOGe5JC+Az68bTlQomWeWZ6iNa/FjVuFzkGFBsnr2 P/aaIfzejpem1uInXyp3Zr2DU+3R+pxjMmXKH3W6X/n+xMdZn/hVA/VHEzB13FWb AiY7oOBYyn7yrhlMTF+mhOW4VqBmyB8aaTMz7GcmyaSOPdDGkxOkqmmwwkrB668H b0Asax6M7bhC0rRdQUZS6qa/YBa6iXE2g4jlehTaD14dORVNKTaByYBZyCsB7ott BleY/jf01fQRTF76B5VaaNMBHJy2OgpedSW/IEhUPS5eAVwv/U04hefpcAM4Lup7 CrA3sfq5uZ4/QfeD/8KjnNG6znxplGx+uv3oAjD4wQKBgQDu1ba1oQG/Gb3127yW AIUX9V7l/VmIbyGhLO0KvSlmCuKdqtwz6VnGrbCa8sdvu2zybC9Do8ObiQHcZdVh 9viT2QLp9a3vnPUTsE74nNmeGRaLWt79qqnGd1qwjG1+Rl4LePDEBViBUh3s9f8X LnapOomEFaP+Q+5OOhVvJAzoNwKBgQDbwPqQkllitrPhZ3bzpWqsx+enhlBUg/ng YAtvv6VttMY9s0ALgyvPpwpZW0uOrJLY0QWKMXEFzJ47bu+Ly9b5VYLGERD2HG7q KKp4IwK/OfLKVK9yoQ9oxaE7xiIVaimD7gEMifKFM/Lb7bwDoO7/7KTKxdnJ1LGy wtxEsGtkAwKBgGjNUu2Eh1WqIBdAoxJXjA+lVk0pzR33VhR5uFKcCwyB/ksdbJ9C 6GgsU3DK1AUNg5MlMeBGflFD35MtBGOGkjGeao7rhbW9dDV9iknB2iRr8d6Ys30w ZGt4eE08cdeVXTM/kLcTeXDV7dfLYnJzqxI7Y5iYPmwWtv2Qs1MfyKIlAoGAO2ra VOy9LmuoB3IqP4aiaUVD5Y/zeGaW0Ywmi3iOCjOuxlAJKRO2bNcFfVOqAlG3AtjB XrQvkxnYTsmYC3x6C8CLM3K521Gky7tjHEibHYlVlE+BgMT7naCSD89qt8+Umg9o STOjV1DMgZquE20YMiqSBCGq2V+hDGyTkh8BanECgYA6bOTHclpNo/2owTN35uGM 1RnUZZfq6duV1shQPKCUbUphIGh1rukc5aQco6kCjFr0JaF6B/wwhCYzZQSduK1u bT/FyjQCO7hLAKMJxpjj/ZSb89JqsjXuiTNc6zHd3XIEf3gmBqfUt8j0YaP7wbtT u6SM+PJkz7Prn8xKQ43zjQ== -----END PRIVATE KEY-----",
  "client_id": "108920853886427588910",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/lib-store-acconut%40ai-in-public-library-sheet.iam.gserviceaccount.com"
    }, scope)

client = gspread.authorize(creds)

# Open the sheet
sheet = client.open("AI-library-response-sheet").sheet1  # Name of your Google Sheet


# Open the sheet by name
sheet = client.open("AI-library-response-sheet").sheet1  # Name of your Google Sheet


# Create input fields in the sidebar
with st.sidebar:
    st.header("Share programs in your library!")
    lib_name = st.text_input("Library name")
    event_title = st.text_input("Program title")
    descrition = st.text_area("Description of program")
    event_page = st.text_input("Program page")
    contact = st.text_input("Contact information")
    submit_button = st.button('Submit')

# When the submit button is pressed
if submit_button:
    # Write data to Google Sheet
    sheet.append_row([lib_name, event_title, descrition, event_page, contact])
    st.sidebar.success("Data submitted successfully!")
