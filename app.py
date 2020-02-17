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
    Compute travel time between two places specified by their longitude/latitude pairs.

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

    geolocator = Nominatim(user_agent="LocalRoute", country_bias = 'US')
    result = geolocator.geocode({"postalcode": zip_code})

    return (result.latitude, result.longitude)



def find_nearby_courses(df, start_zip, max_drive_time):
    """Update dataframe of courses to only those within a certain distance of starting location."""

    # st.write('Start of find_nearby_courses')
    # st.write(df.sort_values(by='region'))

    # Cast latitudes/longitudes as tuples
    latlong = list(zip(df['latitude'], df['longitude']))

    starting_location = get_latlon_from_zip(start_zip)

    # st.write(starting_location)

    df['time'] = [get_driving_time(starting_location, r) for r in latlong]

    # st.write('After computing time')
    # st.write(df.sort_values(by = 'region'))

    df_close = df[df['time'] <= max_drive_time]

    #st.table(df_close)

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

        st.sidebar.markdown('Optional parameters:')
        prefs['hills'] = hill_map[st.sidebar.selectbox('Hills:', ['No preference', 'Mostly Flat', 'Moderately Hilly', 'Very Hilly'])]
        prefs['woods'] = wood_map[st.sidebar.selectbox('Woods:', ['No preference', 'Lightly Wooded', 'Moderately Wooded', 'Heavily Wooded'])]


        #prefs['difficulty'] = difficulty_map[st.sidebar.selectbox('Difficulty:', ['No preference', 'Easy', 'Moderate', 'Difficult'])]

        prefs['difficulty'] = 'No preference'
        diff = st.sidebar.selectbox('Difficulty:', ['No preference', 'Easy', 'Moderate', 'Difficult'])


        #prefs['max_length'] = st.text_input("Maximum length course to play:")
        #prefs['max_length'] = st.selectbox("Maximum length course to play:", ['No preference', '3000', '6000', '9000'])


    #submit = st.button('Continue')

    #if submit:
    if is_user_inputs_populated(prefs):
        return prefs
    else:
        st.write('Please input additional information.')

    return None


def find_next_course(df, user_prefs, visited_courses, current_location):

    df_nearby = find_nearby_courses(df, current_location, user_prefs['max_travel_hours'])

    df_nearby_ranked = rank_courses(df_nearby, user_prefs)

    # Check if recommendation is already among those visited
    while df_nearby_ranked.iloc[0, :]['dgcr_id'] in visited_courses:
        df_nearby_ranked = df_nearby_ranked.iloc[1:, :]

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

        with st.spinner('**Computing route**'):
            for i in range(int(user_prefs['n_destinations'])):

                #visited_courses.append(find_next_course(df, user_prefs, visited_courses, current_location))

                try:
                    visited_courses.append(find_next_course(df, user_prefs, visited_courses, current_location))
                except:
                    st.write('Failed to reach sufficient destinations.  Displaying partial route.')
                    break


                destination = df_original[df_original['dgcr_id'] == visited_courses[-1]]

                all_destinations = pd.concat([all_destinations, destination], ignore_index = True)

                current_location = list(destination['postal_code'])[0]
                #st.write(current_location)

                #st.dataframe(destination[cols_to_display])


            st.subheader('\nYour LocalRoute:')

            plot_df = all_destinations[['latitude', 'longitude']]

            st.deck_gl_chart(
                viewport = {
                    'latitude': plot_df['latitude'].mean(),
                    'longitude': plot_df['longitude'].mean(),
                    'zoom': 8,
                    'angle': 0
                },
                layers = [ # STARTING LOCATION
                           {'type': 'ScatterplotLayer',
                           'data': pd.DataFrame(get_latlon_from_zip(user_prefs['starting_location']), index = ['latitude', 'longitude']).T,
                           'radiusScale': 10,
                           'radiusMinPixels': 10,
                           'getFillColor': [238, 0, 0],
                           'extruded': True,
                           'pickable': True,
                            },
                        { # VISITED COURSES
                            'type': 'ScatterplotLayer',
                           'data': plot_df,
                           'radiusScale': 20,
                           'radiusMinPixels': 20,
                           'getFillColor': [113, 179, 255],
                           'extruded': True
                            },
                            { # OTHER COURSES
                            'type': 'ScatterplotLayer',
                            'data': df,
                            'radiusScale': 5,
                            'radiusMinPixels': 5,
                            'getFillColor': [112, 131, 203],
                            'opacity': .1,
                            'extruded': True
                            }
                          ])

            st.table(all_destinations[cols_to_display])

    return


if __name__ == '__main__':
    main()




