import streamlit as st
import pandas as pd
st.title('Hello-world')

# st.write():  prints text, data, figures

st.write("Here's our first attempt at using data to create a table:")
st.write(pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40]
}))

# Functions to display dataframes/tables:  st.dataframe(), st.table()

# A variable alone on a line will be printed.

# Charting libraries Matplotlib, Altair, Deck.GI etc.

map_data = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns=['lat', 'lon'])

st.map(map_data)
