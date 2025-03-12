import streamlit as st
import pandas as pd
import numpy as np

st.title("Hallo, Streamlit!")
st.write("Das ist meine erste Streamlit-App.")

st.header("This is a header with a divider", divider="gray")

chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])

st.area_chart(chart_data)





