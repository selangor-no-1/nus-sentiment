import streamlit as st

from deta import Deta
import pandas as pd
import plotly.express as px

# instantiate deta agent
deta = Deta(st.secrets["deta_key"])
db = deta.Base("usage-db")

##############################################################################################
### UI Start
##############################################################################################

hide_streamlit_style = """
        <style>
        #MainMenu {visibility: hidden;}
        code, h1 {color: #ff5138;}
        h3, p {color: #fff;}
        footer {visibility: hidden;}
        input {color: #fff !important;}
        button:hover {background-color: #ff5138;}
        button:focus {box-shadow: #ff5138;}
        </style>
        <h1>About Us</h1>
        """

st.markdown(hide_streamlit_style, unsafe_allow_html=True) 


st.markdown('')
st.markdown("Made for Hack & Roll 2023")
st.markdown('Made By: Jake Khoo, Hew Li Yang, Minh Tuan, Utkarsh Pundir')


d = db.fetch().items
counts = pd.DataFrame.from_records(d).sort_values(by = "value")
fig = px.bar(counts, y = "key", x = "value")
fig.update_yaxes(tickmode='linear')
st.plotly_chart(fig, use_container_width=True)
