import streamlit as st
import numpy as np
import pandas as pd


def _max_width_():
    """Decrease left margin of the app; from https://discuss.streamlit.io/t/custom-render-widths/81/8"""

    max_width_str = f"max-width: 2000px;"
    st.markdown(
        f"""
    <style>
    .reportview-container .main .block-container{{
        {max_width_str}
    }}
    </style>    
    """,
        unsafe_allow_html=True,
    )


def get_driving_time(place_1, place_2, speed = 40):
    """Compute travel time between two points specified by their longitude and latitude."""

    from geopy.distance import geodesic

    distance = geodesic(place_1, place_2).miles
    time = distance/speed

    return round(time, 2)


def get_latlon_from_zip(zip_code):
    """Determine latitude and longitude for a zip code."""

    from geopy.geocoders import Nominatim

    geolocator = Nominatim(user_agent="specify_your_app_name_here")
    result = geolocator.geocode({"postalcode": zip_code})

    return (result.latitude, result.longitude)


def plot_courses_map(df):
    """Function to plot map with course locations."""
    import matplotlib.pyplot as plt
    import geopandas as gpd
    from shapely.geometry import Point, Polygon

    map_file = '/home/jon/PycharmProjects/jon-insight-project/data/external/cb_2018_us_nation_20m/cb_2018_us_nation_20m.shp'

    crs = {'init': 'eosg:4326'}

    street_map = gpd.read_file(map_file)

    geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]

    geo_df = gpd.GeoDataFrame(df, crs=crs, geometry=geometry)

    geo_df.head()

    fig, ax = plt.subplots(figsize=(15, 15))
    street_map.plot(ax=ax, alpha=0.4, color='grey')
    geo_df.plot(ax=ax, markersize=20, color='green', marker='o', alpha=0.4)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    # ax.set_title('Disc golf courses in the US')
    plt.show()

    return


def find_nearby_courses(df, start_zip, max_drive_time):
    """Update dataframe of courses to only those within a certain distance of starting location."""

    # Cast latitudes/longitudes as tuples
    latlong = list(zip(df['latitude'], df['longitude']))

    starting_zip = get_latlon_from_zip(start_zip)

    df['time'] = [get_driving_time(starting_zip, r) for r in latlong]

    df_close = df[df['time'] <= max_drive_time]

    return df_close


def get_user_prefs():
    """Query user for their preferences and return results in a dictionary."""

    st.write('')
    st.subheader('Enter some parameters of your trip.')

    prefs = {}

    prefs['starting_location'] = st.text_input("ZIP code of starting location:")
    prefs['max_travel_hours'] = st.selectbox('Maximum drive time between courses [hours]:', ['' ,0.5, 1.0, 1.5, 2.0, 2.5, 3.0])
    prefs['n_destinations'] = st.text_input("Number of courses to be played:")

    submit = st.button('Continue')

    if submit:
        if prefs['starting_location'] != '' and prefs['max_travel_hours'] != '' and  prefs['n_destinations'] != '':
            return prefs
        else:
            st.write('Please input additional information.')
    return prefs


def rank_courses(df, prefs):
    """Pick a course for the user to travel to based on their preferences."""

    return df.sort_values('rating', ascending= False)


def find_next_course(df, user_prefs, visited_courses, current_location):
    df_nearby = find_nearby_courses(df, current_location, user_prefs['max_travel_hours'])

    # plot_courses_map(df_nearby)

    df_nearby_ranked = rank_courses(df_nearby, user_prefs)

    # Check if recommendation is already in visited
    while df_nearby_ranked.iloc[0, :]['dgcr_id'] in visited_courses:
        df_nearby_ranked = df_nearby_ranked.iloc[1:]

    return df_nearby_ranked.iloc[0, :]['dgcr_id']



###############################################################

def main():

    # Forces app to full width
    _max_width_()

    file_name ='all_courses_database_processed.plk'
    df = pd.read_pickle(file_name)

    st.title('LocalRoute')

    st.header('Planning the ideal disc golf road trip')

    # Obtain user preferences
    user_prefs = get_user_prefs()
    visited_courses = []

    if user_prefs['starting_location'] != '' and user_prefs['max_travel_hours'] != '' and  user_prefs['n_destinations'] != '':

        location = user_prefs['starting_location']

        with st.spinner('**Computing optimal route**'):
            for i in range(int(user_prefs['n_destinations'])):
                visited_courses.append(find_next_course(df, user_prefs, visited_courses, location))

        # Display results
        st.write(100*'\n')
        st.header('LocalRoute:')

        cols_to_display = ['name', 'locality', 'region', 'holes', 'length', 'difficulty', 'rating']
        for entry in visited_courses:
            st.table(df[df['dgcr_id'] == entry])

    return


if __name__ == '__main__':
    main()




