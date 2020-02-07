import pandas as pd


def rank_courses(df, Q):
    '''
    Return the input dataframe ranked according to preferences.
    '''

    from sklearn.metrics.pairwise import cosine_similarity
    import streamlit as st

    Q = convert_prefs(Q)
    df = convert_df(df, Q)

    # st.write('Data going into cosine')
    # st.dataframe(df)
    # st.write(Q)

    df['recommendation'] = cosine_similarity(df.iloc[:, 1:], [list(Q.values())], dense_output=True)

    return df


    # Naive ranking - rank soley by course rating
    #return df.sort_values('rating', ascending= False)


def convert_df(df, p):
    '''
    Function to recast course database by information in dictionary.

    :param df: data frame of full categories; p
    :return: A featurized pandas dataframe
    '''

    df_altered = df[['dgcr_id', 'rating']]

    excluded_columns = ['rating', 'starting_location', 'n_destinations', 'max_travel_hours']

    for key, value in p.items():
        # Remove columns for which the user has no preference
        if key not in excluded_columns and value != 'No preference':
            df_altered = pd.concat([df_altered, df[key]], axis = 1)
            #df_altered = df_altered.assign(key = df[key])

    return df_altered


def convert_prefs(p):
    '''
    :param p:
    :return:
    '''

    excluded_columns = {'rating', 'starting_location', 'n_destinations', 'max_travel_hours'}

    p_new = {'rating': 10}


    #p_new.update({k:v for k, v in p.items() if v != 'No preference' and k not in excluded_columns})
    for key, value in p.items():

        # Remove columns for which the user has no preference

         if key not in excluded_columns and value != 'No preference':
            p_new[key] = value


    return p_new



def get_sample_prefs():
    '''
    Acquires user preferences for course features.
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