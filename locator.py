import streamlit as st
import pandas as pd
import requests
import os
import time

# Streamlit app title
st.title("Geolocation App")
st.write("Upload a CSV file with latitude and longitude columns to get State and LGA information.")

# Get the API key from Streamlit secrets
api_key = st.text_input("Enter your Google Maps API key", type="password")

# Function to get State and LGA from latitude and longitude
def get_location_info(latitude, longitude, api_key):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()

        if data['status'] == 'OK':
            state, lga = None, None
            for component in data['results'][0]['address_components']:
                if 'administrative_area_level_1' in component['types']:
                    state = component['long_name']
                if 'administrative_area_level_2' in component['types']:
                    lga = component['long_name']
            return state, lga
        else:
            st.warning(f"Geocoding API error: {data['status']}")
    except requests.exceptions.RequestException as e:
        st.error(f"Request failed: {e}")
    
    return None, None



# Check if the API key is available
if not api_key:
    st.error("API key for Google Maps is not set. Please set it as an environment variable.")
else:
    # File upload
    uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])
    if uploaded_file:
        # Read the file based on its type
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)

        # Standardize column names to lowercase
        df.columns = df.columns.str.strip().lower()

        # Check for latitude and longitude columns
        if 'latitude' in df.columns and 'longitude' in df.columns:
            if 'state' not in df.columns:
                df['state'] = None
            if 'lga' not in df.columns:
                df['lga'] = None

            for index, row in df.iterrows():
                if pd.isna(row['state']) or pd.isna(row['lga']):
                    latitude = row['latitude']
                    longitude = row['longitude']
                    state, lga = get_location_info(latitude, longitude, api_key)
                    df.at[index, 'state'] = state
                    df.at[index, 'lga'] = lga
                    time.sleep(0.1)  # Adjust as necessary

            st.write("Updated DataFrame:")
            st.dataframe(df)

            # Option to download the updated DataFrame as CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download updated CSV",
                data=csv,
                file_name="updated_geolocation.csv",
                mime="text/csv"
            )
        else:
            st.error("The CSV file must contain 'latitude' and 'longitude' columns.")
       
