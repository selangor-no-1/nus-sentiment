import streamlit as st

from utils.model import LABELS, download_model

model, tokenizer, nlp = download_model()

hide_streamlit_style = """
            <style>
            code, h1 {color: #ff5138;}
            h3, p {color: #fff;}
            footer {visibility: hidden;}
            input {color: #fff !important;}
            button:hover {background-color: #ff5138;}
            button:focus {box-shadow: #ff5138;}
            </style>
            <h1>NUS Sentiment</h1>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 
text = st.text_input(label="Input the text you want to analyse")
st.write(f"You inputted: \n {text}")
