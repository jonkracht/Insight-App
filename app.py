import streamlit as st
import pandas as pd
st.title('Hello-world')

# st.write():  prints text, data, figures

st.write("Here's our first attempt at using data to create a table:")
st.write(pd.DataFrame({
    'first column': [1, 2, 3, 4],
    'second column': [10, 20, 30, 40]
}))
