import pandas as pd


def rank_courses(df, Q):
    '''
    One-hot encoded
    Return the input dataframe ranked according to preferences.
    '''

    #from sklearn.metrics.pairwise import cosine_similarity
    #from scikit-learn.preprocessing import OneHotEncoder
    from scikit-learn.metrics.pairwise import cosine_similarity

    #from sklearn.metrics.pairwise import cosine_similarity
    #from sklearn.preprocessing import OneHotEncoder

    import streamlit as st


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



    # Scale course rating attribute to balance its impact on recommendation
    #df.loc[:, 'rating'] = df.rating.apply(lambda x: x / 2)
    #df.loc[:, 'rating'] = df['rating'].div(2)
    #df['rating'] = df['rating'].apply(lambda x: x/2)
    df.loc[:, 'rating'] *= 0.5

    df['recommendation'] = cosine_similarity(df.iloc[:, 1:], pd.DataFrame(a).transpose(), dense_output=True)

    return df.sort_values(by='recommendation', ascending=False)



def convert_df(df, p):
    '''
    Implementing one-hot encoding
    Function to recast course database by information in dictionary.

    '''

    import streamlit as st

    df_altered = df[['dgcr_id', 'rating']]

    excluded_columns = ['rating', 'starting_location', 'n_destinations', 'max_travel_hours']

    for key, value in p.items():
        # Remove columns for which the user has no preference
        if key not in excluded_columns and value != 'No preference':
            df_altered = pd.concat([df_altered, pd.get_dummies(df[key], prefix=key)], axis=1)

            # Alternate get_dummies scheme:
            # temp = pd.get_dummies(df[key], prefix=key, prefix_sep = '')
            # temp = temp.T.reindex(['0', '1', '2']).T.fillna(0)
            # df_altered = pd.concat([df_altered, temp], axis=1)


    return df_altered


def convert_prefs(p):
    '''
    Refactor user preferences to include only non-trivial ones.
    '''

    excluded_columns = {'rating', 'starting_location', 'n_destinations', 'max_travel_hours'}

    # Enter scaling of the rating component of the vector
    p_new = {'rating': 2}


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
