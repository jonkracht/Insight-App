import streamlit as st
import pandas as pd
import numpy as np
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

# Incorporate widget
if st.checkbox('Show dataframe'):
    chart_data = pd.DataFrame(
       np.random.randn(20, 3),
       columns=['a', 'b', 'c'])

    st.line_chart(chart_data)
    
    
# option = st.selectbox(
#     'Which number do you like best?',
#      df['first column'])

# 'You selected: ', option



#option = st.sidebar.selectbox(
#    'Which number do you like best?',
#     df['first column'])

#'You selected:', option

# Add items to sidebar:  st.sidebar.[element_name]()
# st.sidebar.markdown(), st.sidebar.slider(), st.sidebar.linechart()

# Show progress of a lengthy action:  st.progress()
