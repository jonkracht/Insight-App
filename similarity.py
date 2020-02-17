import pandas as pd


# def rank_courses(df, Q):
#     '''
#     Return the input dataframe ranked according to preferences.
#     '''
#
#     from sklearn.metrics.pairwise import cosine_similarity
#     from sklearn.preprocessing import OneHotEncoder
#     import streamlit as st
#
#     Q = convert_prefs(Q)
#     df = convert_df(df, Q)
#
#     # st.write('Data going into cosine')
#     # st.dataframe(df)
#     # st.write(Q)
#
#     df['rating'] = df['rating'].divide(2.5)
#
#     st.write(df)
#
#     df['recommendation'] = cosine_similarity(df.iloc[:, 1:], [list(Q.values())], dense_output=True)
#     #st.write(df)
#     return df



def rank_courses(df, Q):
    '''
    One-hot encoded
    Return the input dataframe ranked according to preferences.
    '''

    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.preprocessing import OneHotEncoder
    import streamlit as st

    # st.write('Inside rank_courses')
    # st.write(df)

    Q = convert_prefs(Q)
    df = convert_df(df, Q)


    a = []
    for key, value in Q.items():
        if len(a) == 0:
            a.append(value)
        else:
            if value == 0:
                a.append(1)
                a.append(0)
                a.append(0)
            elif value == 1:
                a.append(0)
                a.append(1)
                a.append(0)
            else:
                a.append(0)
                a.append(0)
                a.append(1)




    df['rating'] = df['rating'].divide(2)

    # st.write('df')
    # st.table(df)
    #
    # st.write('a')
    # st.table(pd.DataFrame(a).transpose())

    df['recommendation'] = cosine_similarity(df.iloc[:, 1:], pd.DataFrame(a).transpose(), dense_output=True)
    #st.table(df.sort_values(by='recommendation', ascending= False))

    return df.sort_values(by='recommendation', ascending= False)
    #return df


# def convert_df(df, p):
#     '''
#     Original version
#     Function to recast course database by information in dictionary.
#
#     :param df: data frame of full categories; p
#     :return: A featurized pandas dataframe
#     '''
#
#     df_altered = df[['dgcr_id', 'rating']]
#
#     excluded_columns = ['rating', 'starting_location', 'n_destinations', 'max_travel_hours']
#
#     for key, value in p.items():
#         # Remove columns for which the user has no preference
#         if key not in excluded_columns and value != 'No preference':
#             df_altered = pd.concat([df_altered, df[key]], axis = 1)
#             #df_altered = df_altered.assign(key = df[key])
#
#     return df_altered

def convert_df(df, p):
    '''
    Implementing one-hot encoding
    Function to recast course database by information in dictionary.

    :param df: data frame of full categories; p
    :return: A featurized pandas dataframe
    '''

    import streamlit as st

    # st.write('inside convert_df')
    # st.write(df)

    df_altered = df[['dgcr_id', 'rating']]

    excluded_columns = ['rating', 'starting_location', 'n_destinations', 'max_travel_hours']

    for key, value in p.items():
        # Remove columns for which the user has no preference
        if key not in excluded_columns and value != 'No preference':
            df_altered = pd.concat([df_altered, pd.get_dummies(df[key], prefix=key)], axis=1)

            # temp = pd.get_dummies(df[key], prefix=key)
            # temp = temp.T.reindex([0, 1, 2])
            # df_altered = pd.concat([df_altered, temp], axis=1)

        #st.table(df_altered)


    return df_altered


def convert_prefs(p):
    '''
    :param p:
    :return:
    '''

    excluded_columns = {'rating', 'starting_location', 'n_destinations', 'max_travel_hours'}

    # Enter scaling of the rating component of the vector
    p_new = {'rating': 1.5}


    for key, value in p.items():

        # Remove columns for which the user has no preference

         if key not in excluded_columns and value != 'No preference':
            p_new[key] = value

    return p_new



def get_sample_prefs():
    '''
    Generate data representative of expected user input.
    '''

    prefs = {}

    prefs['starting_location'] = '18960'
    prefs['max_travel_hours'] = '1'
    prefs['n_destinations'] = '1'
    prefs['hills'] = 0
    prefs['woods'] = 2
    prefs['difficulty'] = 'No preference'

    return prefs



def main():

    # Load dataframe
    file_name = 'all_courses_database_processed.plk'
    df = pd.read_pickle(file_name)

    prefs = get_sample_prefs()

    df_ranked= rank_courses(df, prefs)
    df_ranked = df_ranked.sort_values('recommendation', ascending=False)

    print('hi')

    return



if __name__ == '__main__':
    main()