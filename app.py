import streamlit as st
import numpy as np
import pandas as pd
import geopy
import matplotlib.pyplot as plt

from similarity import rank_courses, convert_df, convert_prefs

def _max_width_():
    """
    Increase Streamlit app width to fullscreen.

    Fom https://discuss.streamlit.io/t/custom-render-widths/81/8
    """

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
    """
    Compute travel time between two place specified by their longitude/latitude pairs.

    Returns time in hours.
    """

    from geopy.distance import geodesic

    distance = geodesic(place_1, place_2).miles
    time = distance/speed

    return round(time, 2)


def get_latlon_from_zip(zip_code):
    """
    Determine latitude and longitude for a given zip code.

    """

    from geopy.geocoders import Nominatim

    geolocator = Nominatim(user_agent="LocalRoute")
    result = geolocator.geocode({"postalcode": zip_code})

    return (result.latitude, result.longitude)


# def plot_courses_map(df):
#     """
#     Function to plot a map where locations are determined by the input dataframe df.
#     """
#
#     import matplotlib.pyplot as plt
#     import geopandas as gpd
#     from shapely.geometry import Point, Polygon
#
#     map_file = '/home/jon/PycharmProjects/jon-insight-project/data/external/cb_2018_us_nation_20m/cb_2018_us_nation_20m.shp'
#
#     crs = {'init': 'eosg:4326'}
#
#     street_map = gpd.read_file(map_file)
#
#     geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
#
#     geo_df = gpd.GeoDataFrame(df, crs=crs, geometry=geometry)
#
#     geo_df.head()
#
#     fig, ax = plt.subplots(figsize=(15, 15))
#     street_map.plot(ax=ax, alpha=0.4, color='grey')
#     geo_df.plot(ax=ax, markersize=20, color='green', marker='o', alpha=0.4)
#     ax.set_xlabel('Longitude')
#     ax.set_ylabel('Latitude')
#     # ax.set_title('Disc golf courses in the US')
#     plt.show()
#
#     return


def find_nearby_courses(df, start_zip, max_drive_time):
    """Update dataframe of courses to only those within a certain distance of starting location."""

    #st.write('Start of find_nearby_courses')
    #st.write(df)

    # Cast latitudes/longitudes as tuples
    latlong = list(zip(df['latitude'], df['longitude']))

    starting_zip = get_latlon_from_zip(start_zip)

    df['time'] = [get_driving_time(starting_zip, r) for r in latlong]

    #st.write(df)

    df_close = df[df['time'] <= max_drive_time]

    #st.write(df_close)

    return df_close


def get_user_prefs():
    """Query user for their preferences and return results in a dictionary."""

    st.subheader('Enter some parameters of your trip.')
    st.write('\n')

    prefs = {}

    st.subheader('Required information:')

    prefs['starting_location'] = st.text_input("ZIP code of starting location:")
    prefs['max_travel_hours'] = st.selectbox('Maximum drive time between courses [hours]:', ['' ,0.5, 1.0, 1.5, 2.0, 2.5, 3.0])
    prefs['n_destinations'] = st.text_input("Number of courses to be played:")



    #st.subheader('Optional information:')
    if st.checkbox('Show optional parameters'):

        hill_map = {'No preference': 'No preference', 'Mostly Flat': 0, 'Moderately Hilly': 1, 'Very Hilly': 2}
        wood_map = {'No preference': 'No preference', 'Lightly Wooded': 0, 'Moderately Wooded': 1, 'Heavily Wooded': 2}
        difficulty_map = {'No preference': 'No preference', 'Easy': 0, 'Moderate': 1, 'Difficult': 2}


        prefs['hills'] = hill_map[st.selectbox('Hills:', ['No preference', 'Mostly Flat', 'Moderately Hilly', 'Very Hilly'])]
        prefs['woods'] = wood_map[st.selectbox('Woods:', ['No preference', 'Lightly Wooded', 'Moderately Wooded', 'Heavily Wooded'])]
        prefs['difficulty'] = difficulty_map[st.selectbox('Difficulty:', ['No preference', 'Easy', 'Moderate', 'Difficult'])]

    #prefs['max_length'] = st.text_input("Maximum length course to play:")
    #prefs['max_length'] = st.selectbox("Maximum length course to play:", ['No preference', '3000', '6000', '9000'])


    #submit = st.button('Continue')

    #if submit:
    if is_user_inputs_populated(prefs):
        #if prefs['starting_location'] != '' and prefs['max_travel_hours'] != '' and  prefs['n_destinations'] != '':
        return prefs
    else:
        st.write('Please input additional information.')

    return None
    #return prefs


def find_next_course(df, user_prefs, visited_courses, current_location):

    #st.write('Start of find_next_course')
    #st.write(df)

    df_nearby = find_nearby_courses(df, current_location, user_prefs['max_travel_hours'])



    #st.write('Courses within driving range:')
    #st.write(df_nearby)

    # plot_courses_map(df_nearby)

    #st.write('Before ranking')
    #st.write(df)

    df_nearby_ranked = rank_courses(df_nearby, user_prefs)

    #st.write('Ranked courses within driving range:')
    #st.write(df_nearby)

    # Check if recommendation is already among those visited
    while df_nearby_ranked.iloc[0, :]['dgcr_id'] in visited_courses:
        df_nearby_ranked = df_nearby_ranked.iloc[1:]

    return df_nearby_ranked.iloc[0, :]['dgcr_id']


def is_user_inputs_populated(user_prefs):
    """Takes a dictionary of user preferences and returns a Boolean whether all inputs are filled."""
    return all(value != '' or value != 'No preference' for value in user_prefs.values())


###############################################################

def main():

    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent="LocalRoute")

    # Forces app to full width
    #_max_width_()

    file_name ='all_courses_database_processed.plk'
    df = pd.read_pickle(file_name)
    df_original = df

    st.title('LocalRoute')

    st.header('Planning the ideal disc golf road trip')
    #st.write('\n')

    # Obtain user preferences
    user_prefs = get_user_prefs()
    visited_courses = []

    submit = st.button('Continue')

    if is_user_inputs_populated(user_prefs) and submit:

        st.subheader('\n\n\nRouting from ' + geolocator.geocode(user_prefs['starting_location'], country_codes='US').address)

        current_location = user_prefs['starting_location']

        all_destinations = pd.DataFrame()

        cols_to_display = ['name', 'locality', 'region', 'holes', 'difficulty', 'rating']

        with st.spinner('**Computing optimal route**'):
            for i in range(int(user_prefs['n_destinations'])):

                #st.write('Start of loop.')
                #st.write(current_location)

                visited_courses.append(find_next_course(df, user_prefs, visited_courses, current_location))

                destination = df_original[df_original['dgcr_id'] == visited_courses[-1]]

                all_destinations = pd.concat([all_destinations, destination], ignore_index = True)

                current_location = list(destination['postal_code'])[0]
                #st.write(current_location)

                #st.dataframe(destination[cols_to_display])



            st.subheader('\nYour LocalRoute:')

            # Create a map of the filtered data)
            #st.write(all_destinations[['latitude', 'longitude']])

            st.map(all_destinations[['latitude', 'longitude']])



            st.dataframe(all_destinations)
            #st.dataframe(all_destinations[cols_to_display])


    return


if __name__ == '__main__':
    main()




