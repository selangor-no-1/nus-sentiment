import streamlit as st
import pandas as pd

def display_post(dict: dict):
    for k,v in dict.items():
        a, b = st.columns([1,4])
        a.write(f"**{k}**")
        b.write(v)

def display_all_posts(data: pd.DataFrame):
    data_to_dict = data.to_dict(orient="records")
    for post in data_to_dict:
        display_post(post)
        st.markdown("---")

